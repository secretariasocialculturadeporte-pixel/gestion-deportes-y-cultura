document.addEventListener('DOMContentLoaded', () => {
    // --- PWA Service Worker Registration ---
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/service-worker.js')
        .then(function(registration) {
            console.log('Service Worker registered with scope:', registration.scope);
        })
        .catch(function(error) {
            console.log('Service Worker registration failed:', error);
        });
    }

    // --- Scroll-in Animation Logic ---
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, {
        threshold: 0.1 // Trigger when 10% of the element is visible
    });

    // Observe all cards
    const cards = document.querySelectorAll('.feature-card, .plan-card');
    cards.forEach(card => {
        observer.observe(card);
    });

    // --- AI Agent Logic ---
    const toggleButton = document.getElementById('ai-agent-toggle');
    const chatbox = document.getElementById('ai-agent-chatbox');
    const messagesContainer = document.getElementById('chatbox-messages');
    const sendButton = document.getElementById('chatbox-send');
    const inputField = document.getElementById('chatbox-input');

    // --- Event Listeners ---
    toggleButton.addEventListener('click', () => {
        chatbox.classList.toggle('hidden');
        if (!chatbox.classList.contains('hidden')) {
            addMessage('agent', '¡Hola! Soy el asistente virtual. ¿Cómo puedo ayudarte a conocer nuestra plataforma?');
        }
    });

    sendButton.addEventListener('click', sendMessage);
    inputField.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // --- Functions ---
    function sendMessage() {
        const messageText = inputField.value.trim();
        if (messageText === '') return;

        addMessage('user', messageText);
        inputField.value = '';

        // Send to backend and get response
        sendMessageToAgent(messageText);
    }

    function addMessage(sender, text) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('chat-message', `${sender}-message`);
        messageElement.textContent = text;
        messagesContainer.appendChild(messageElement);
        // Scroll to the bottom
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    async function sendMessageToAgent(message) {
        const API_ENDPOINT = '/api/sales_agent'; // We will create this endpoint in Flask

        // Add a "thinking" message
        addMessage('agent', '...');

        try {
            const response = await fetch(API_ENDPOINT, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: message }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            // Remove "thinking" message
            messagesContainer.removeChild(messagesContainer.lastChild);

            addMessage('agent', data.reply);

        } catch (error) {
            console.error('Error sending message to agent:', error);
             // Remove "thinking" message
            messagesContainer.removeChild(messagesContainer.lastChild);
            addMessage('agent', 'Lo siento, estoy teniendo problemas para conectarme. Por favor, intenta de nuevo más tarde.');
        }
    }
});
