/**
 * ChatWebSocket - Manages WebSocket connection and chat functionality
 */
class ChatWebSocket {
    constructor(roomName) {
        this.roomName = roomName;
        this.socket = null;
        this.username = null;
        this.isConnected = false;

        // DOM elements
        this.chatMessages = document.getElementById('chatMessages');
        this.messageForm = document.getElementById('messageForm');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.connectionStatus = document.getElementById('connectionStatus');

        // Initialize
        this.init();
    }

    /**
     * Initialize the chat
     */
    init() {
        this.connectWebSocket();
        this.setupEventListeners();
    }

    /**
     * Connect to WebSocket server
     */
    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const url = `${protocol}//${window.location.host}/ws/chat/${this.roomName}/`;

        this.socket = new WebSocket(url);

        this.socket.onopen = () => this.onOpen();
        this.socket.onmessage = (event) => this.onMessage(event);
        this.socket.onclose = () => this.onClose();
        this.socket.onerror = (error) => this.onError(error);
    }

    /**
     * Handle WebSocket open event
     */
    onOpen() {
        console.log('WebSocket connection established');
        this.isConnected = true;
        this.updateConnectionStatus(true);

        // Get username from URL path
        this.username = this.roomName;

        // Send join message
        this.socket.send(JSON.stringify({
            type: 'user_join',
            username: this.username,
        }));

        // Enable input
        this.messageInput.disabled = false;
        this.sendBtn.disabled = false;
        this.messageInput.focus();
    }

    /**
     * Handle incoming messages from WebSocket
     */
    onMessage(event) {
        const data = JSON.parse(event.data);

        switch (data.type) {
            case 'chat_message':
                this.displayMessage(data.username, data.message);
                break;
            case 'user_joined':
                this.displaySystemMessage(`${data.username} joined the chat`);
                break;
            case 'user_left':
                this.displaySystemMessage(`${data.username} left the chat`);
                break;
            default:
                console.warn('Unknown message type:', data.type);
        }
    }

    /**
     * Handle WebSocket close event
     */
    onClose() {
        console.log('WebSocket connection closed');
        this.isConnected = false;
        this.updateConnectionStatus(false);

        // Disable input
        this.messageInput.disabled = true;
        this.sendBtn.disabled = true;
        this.displaySystemMessage('Connection lost. Attempting to reconnect...');

        // Attempt to reconnect after 3 seconds
        setTimeout(() => this.connectWebSocket(), 3000);
    }

    /**
     * Handle WebSocket error event
     */
    onError(error) {
        console.error('WebSocket error:', error);
        this.displaySystemMessage('Connection error occurred');
    }

    /**
     * Setup event listeners
     */
    setupEventListeners() {
        this.messageForm.addEventListener('submit', (e) => this.onFormSubmit(e));
    }

    /**
     * Handle form submit
     */
    onFormSubmit(e) {
        e.preventDefault();

        const message = this.messageInput.value.trim();

        if (message && this.isConnected) {
            // Send message via WebSocket
            this.socket.send(JSON.stringify({
                type: 'chat_message',
                message: message,
            }));

            // Clear input
            this.messageInput.value = '';
            this.messageInput.focus();
        }
    }

    /**
     * Display chat message
     */
    displayMessage(username, content) {
        const messageEl = document.createElement('div');
        messageEl.className = `message ${username === this.username ? 'user' : 'other'}`;

        messageEl.innerHTML = `
            <div class="message-username">${this.escapeHtml(username)}</div>
            <div class="message-content">${this.escapeHtml(content)}</div>
        `;

        this.chatMessages.appendChild(messageEl);
        this.scrollToBottom();
    }

    /**
     * Display system message (user joined/left)
     */
    displaySystemMessage(text) {
        const messageEl = document.createElement('div');
        messageEl.className = 'message system';
        messageEl.textContent = text;

        this.chatMessages.appendChild(messageEl);
        this.scrollToBottom();
    }

    /**
     * Scroll chat to bottom
     */
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    /**
     * Update connection status indicator
     */
    updateConnectionStatus(isConnected) {
        if (isConnected) {
            this.connectionStatus.textContent = 'Connected';
            this.connectionStatus.classList.remove('bg-danger');
            this.connectionStatus.classList.add('connected');
        } else {
            this.connectionStatus.textContent = 'Disconnected';
            this.connectionStatus.classList.remove('connected');
            this.connectionStatus.classList.add('bg-danger');
        }
    }

    /**
     * Escape HTML special characters
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}
