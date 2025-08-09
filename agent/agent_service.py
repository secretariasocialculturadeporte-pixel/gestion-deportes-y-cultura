import json

def detect_intent(command: str) -> str:
    """
    Detects the user's intent based on keywords in the command.
    This is a simplified version. A real implementation would use a proper NLU engine.
    """
    command = command.lower()

    # --- Intent: View Attendance Report ---
    # Keywords: "reporte", "asistencia", "asistencias", "inasistencias"
    report_keywords = ["reporte", "asistencia", "asistencias", "inasistencias", "listado"]

    if any(keyword in command for keyword in report_keywords):
        # A secondary check to make sure we are talking about attendance
        if "asistencia" in command or "asistencias" in command or "inasistencias" in command:
            return "ver_reporte_asistencia"

    # --- Intent: Greet ---
    greet_keywords = ["hola", "buenos días", "buenas tardes"]
    if any(keyword in command for keyword in greet_keywords):
        return "saludar"

    # --- Fallback Intent ---
    return "desconocido"


import requests

# --- Configuration ---
API_BASE_URL = "http://127.0.0.1:5001"
API_KEY = "super_secret_api_key"

def get_attendance_report_from_api():
    """Calls the backend API to get the attendance report."""
    headers = {"X-API-KEY": API_KEY}
    try:
        res = requests.get(f"{API_BASE_URL}/api/reportes/asistencia", headers=headers)
        res.raise_for_status() # Raises an exception for bad status codes (4xx or 5xx)
        return {"status": "success", "data": res.json()}
    except requests.exceptions.RequestException as e:
        print(f"API call failed: {e}")
        return {"status": "error", "message": str(e)}

def process_command(command: str, pubsub_instance) -> dict:
    """
    Processes a user command, detects intent, executes actions, and publishes results.
    """
    intent = detect_intent(command)

    # This response is for direct feedback, e.g., showing the raw result.
    response = {
        "command_received": command,
        "detected_intent": intent,
        "handler_result": None
    }

    if intent == "saludar":
        response["handler_result"] = {"message": "¡Hola! ¿En qué puedo ayudarte?"}

    elif intent == "ver_reporte_asistencia":
        api_result = get_attendance_report_from_api()
        response["handler_result"] = api_result

        # If the API call was successful, publish the data to the UI
        if api_result.get("status") == "success":
            message_to_ui = {
                "topic": "update_attendance_report",
                "data": api_result["data"]
            }
            pubsub_instance.send_all(message_to_ui)
            print(f"Published message to topic: {message_to_ui['topic']}")

    elif intent == "desconocido":
        response["handler_result"] = {"message": "No he entendido tu comando. Por favor, intenta de nuevo."}

    return response


# --- Example Usage ---
if __name__ == '__main__':
    test_commands = [
        "muéstrame el reporte de asistencia",
        "necesito el listado de inasistencias",
        "hola agente",
        "qué día es hoy"
    ]

    for cmd in test_commands:
        result = process_command(cmd)
        print(f"--- Command: '{cmd}' ---")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("\n")
