// IMPORTANT: Replace this with your actual API Gateway Invoke URL
const API_ENDPOINT = 'https://8nhf6c469i.execute-api.us-east-1.amazonaws.com/prod/chat';

const chatForm = document.getElementById('chat-form');
const promptInput = document.getElementById('prompt-input');
const chatWindow = document.getElementById('chat-window');

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const userInput = promptInput.value.trim();
    if (!userInput) return;

    // Display user's message
    appendMessage(userInput, 'user-message');
    promptInput.value = '';

    // Show a loading indicator
    const loadingIndicator = appendMessage('...', 'bot-message loading');

    try {
        const response = await fetch(API_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                prompt: userInput
            }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        // Remove loading indicator and display bot's response
        loadingIndicator.remove();
        appendMessage(data.response, 'bot-message');

    } catch (error) {
        console.error('Error:', error);
        loadingIndicator.remove();
        appendMessage('Sorry, something went wrong. Please check the console for errors.', 'bot-message');
    }
});

function appendMessage(text, className) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${className}`;
    
    const p = document.createElement('p');
    p.textContent = text;
    
    messageDiv.appendChild(p);
    chatWindow.appendChild(messageDiv);
    
    // Scroll to the latest message
    chatWindow.scrollTop = chatWindow.scrollHeight;
    
    return messageDiv; // Return the element for potential modification (like removing it)
}