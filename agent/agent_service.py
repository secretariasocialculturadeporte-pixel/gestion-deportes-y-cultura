import os
import sqlite3
from typing import TypedDict, Annotated, Sequence
import operator
from langchain_core.messages import BaseMessage, FunctionMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools.render import format_tool_to_google_genai_function
from langgraph.prebuilt import ToolExecutor
from langgraph.graph import StateGraph, END

from agent.tools import available_tools

# --- 1. Define the Agent's State ---
# The state is a dictionary that will be passed between nodes in the graph.
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

# --- 2. Define the Graph Nodes ---

def create_agent_node(llm, tools):
    """A node that represents the agent's 'brain'."""
    def agent_node(state):
        # Get the last message
        last_message = state['messages'][-1]

        # Add a system prompt to guide the LLM
        system_prompt = """
        Eres un asistente útil para una aplicación de gestión.
        Responde al usuario de forma concisa y amigable.
        Usa las herramientas disponibles cuando necesites obtener información específica o realizar una acción.
        """
        messages_with_prompt = [HumanMessage(content=system_prompt), last_message]

        # Call the LLM with the tools
        response = llm.invoke(messages_with_prompt, functions=format_tool_to_google_genai_function(tools))
        return {"messages": [response]}
    return agent_node

def create_tool_node(tool_executor):
    """A node that executes the tools chosen by the agent."""
    def tool_node(state):
        agent_message = state['messages'][-1]
        tool_calls = agent_message.additional_kwargs.get("function_call", [])

        if tool_calls:
            # The agent decided to use a tool
            responses = tool_executor.batch([
                (tool_call["name"], tool_call["arguments"]) for tool_call in tool_calls
            ])
            # Convert responses to FunctionMessage to feed back to the agent
            function_messages = [
                FunctionMessage(content=str(r), name=tool_call["name"])
                for r, tool_call in zip(responses, tool_calls)
            ]
            return {"messages": function_messages}

        # The agent did not use a tool
        return {"messages": []}
    return tool_node

# --- 3. Define the Graph's Logic ---

def should_continue(state):
    """Conditional edge: decides whether to continue or end the graph."""
    last_message = state['messages'][-1]
    # If there is no function call, we are done
    if "function_call" not in last_message.additional_kwargs:
        return "end"
    # Otherwise, we continue
    return "continue"

# --- 4. Main Service Function ---

def get_google_api_key_for_tenant(tenant_id: int) -> str:
    """Fetches the Google API key for a given tenant from the database."""
    conn = sqlite3.connect("formacion.db")
    cursor = conn.cursor()
    cursor.execute("SELECT google_api_key FROM inquilinos WHERE id = ?", (tenant_id,))
    result = cursor.fetchone()
    conn.close()
    if result and result[0]:
        return result[0]
    # Fallback to environment variable if not set for tenant
    return os.getenv("GOOGLE_API_KEY", "YOUR_GOOGLE_API_KEY_HERE")

def run_agent(state, llm, tool_executor):
    """Compiles and runs the LangGraph agent."""
    # Create the graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("agent", create_agent_node(llm, available_tools))
    workflow.add_node("action", create_tool_node(tool_executor))

    # Add edges
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "continue": "action",
            "end": END,
        },
    )
    workflow.add_edge("action", "agent")

    # Compile and run
    runnable = workflow.compile()
    final_state = runnable.invoke(state)
    return final_state['messages'][-1].content # Return the final response

def process_command_langchain(command: str, tenant_id: int, pubsub_instance) -> dict:
    """
    Main entry point for processing a command using the LangChain agent.
    """
    # 1. Get the API key for the current tenant
    api_key = get_google_api_key_for_tenant(tenant_id)
    if "YOUR_GOOGLE_API_KEY" in api_key:
        return {"error": "Google API Key no está configurada para este inquilino."}

    # 2. Initialize the LLM and tools
    llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=api_key)
    tool_executor = ToolExecutor(available_tools)

    # 3. Define the initial state for the graph
    initial_state = {"messages": [HumanMessage(content=command)]}

    # 4. Run the agent graph
    try:
        final_response = run_agent(initial_state, llm, tool_executor)

        # The agent's response can be directly sent to the user,
        # or we can use Pub/Sub for more complex UI updates if needed.
        # For now, we'll just return the text response.

        return {
            "command_received": command,
            "agent_response": final_response
        }
    except Exception as e:
        print(f"Error en el agente LangChain: {e}")
        return {"error": "El agente de IA encontró un problema.", "details": str(e)}
