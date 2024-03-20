document.addEventListener("DOMContentLoaded", function() {
    const toggleChatBtn = document.getElementById('toggleChat');
    const chatMessages = document.getElementById('chatMessages');
    const messageInput = document.getElementById('messageInput');
    const sendMessageBtn = document.getElementById('sendMessageBtn');
    const clearMessagesBtn = document.getElementById('clearMessagesBtn');
    const logoutBtn = document.getElementById('logoutBtn');

    // Function to add a message to the chat interface and store it in local storage
    function addMessageToChat(message, type) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', type);
        messageDiv.innerText = message;
        chatMessages.appendChild(messageDiv);
        
        // Store message in local storage
        const messages = JSON.parse(localStorage.getItem('chatMessages')) || [];
        messages.push({ message, type });
        localStorage.setItem('chatMessages', JSON.stringify(messages));
    }

    // Function to fetch and display stored messages from local storage
    function displayStoredMessages() {
        const messages = JSON.parse(localStorage.getItem('chatMessages')) || [];
        messages.forEach(({ message, type }) => {
            addMessageToChat(message, type);
        });
    }

    // Display stored messages when the page loads
    displayStoredMessages();

    // Function to clear all messages from local storage and chat interface
    function clearMessages() {
        localStorage.removeItem('chatMessages');
        chatMessages.innerHTML = ''; // Clear chat interface
    }

    // Event listener for the clear messages button
    clearMessagesBtn.addEventListener('click', clearMessages);

    // Function to send a message
    function sendMessage() {
        const message = messageInput.value.trim();
        if (message === '') return;

        addMessageToChat(message, 'sent');
        messageInput.value = ''; 

        const xhr = new XMLHttpRequest();
        xhr.open('GET', '/get_response/?message=' + encodeURIComponent(message));
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200) {
                    const response = xhr.responseText;
                    addMessageToChat(response, 'received');
                    chatMessages.scrollTop = chatMessages.scrollHeight; 
                } else {
                    console.error('Error:', xhr.statusText);
                }
            }
        };
        xhr.send();
    }

    // Event listener for the send message button
    sendMessageBtn.addEventListener('click', sendMessage);

    // Event listener for the Enter key to send message
    messageInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });

    // Event listener for the toggle chat button
    toggleChatBtn.addEventListener('click', function() {
        const chatbot = new bootstrap.Offcanvas(document.getElementById('staticBackdrop'));
        chatbot.toggle();
    });

    logoutBtn.addEventListener('click', function() {
        console.log('Log out clicked');
        localStorage.removeItem('chatMessages');
        console.log('Logged out');
    });
});
