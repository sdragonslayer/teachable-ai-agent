let currentSessionId = null;

// Load sessions on page load
document.addEventListener('DOMContentLoaded', () => {
    loadSessions();
});

async function loadSessions() {
    try {
        const response = await fetch('/api/sessions');
        const sessions = await response.json();
        
        const sessionsList = document.getElementById('sessions-list');
        sessionsList.innerHTML = '';
        
        if (sessions.length === 0) {
            sessionsList.innerHTML = '<p style="color: #9ca3af; font-size: 0.9rem;">No sessions yet</p>';
            return;
        }
        
        sessions.forEach(session => {
            const div = document.createElement('div');
            div.className = 'session-item';
            div.textContent = session.title;
            div.onclick = () => selectSession(session.id, session);
            sessionsList.appendChild(div);
        });
    } catch (error) {
        console.error('Error loading sessions:', error);
    }
}

async function createNewSession() {
    const title = prompt('Enter session title:', 'New Teaching Session');
    if (!title) return;
    
    const topic = prompt('Enter topic (optional):', '');
    
    try {
        const response = await fetch('/api/sessions', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, topic })
        });
        
        if (response.ok) {
            const session = await response.json();
            selectSession(session.id, session);
            loadSessions();
        }
    } catch (error) {
        console.error('Error creating session:', error);
        alert('Failed to create session');
    }
}

function selectSession(sessionId, session) {
    currentSessionId = sessionId;
    
    document.getElementById('current-session').style.display = 'flex';
    document.getElementById('no-session').style.display = 'none';
    
    document.getElementById('session-title').textContent = session.title;
    document.getElementById('session-topic').textContent = session.topic || 'No topic specified';
    
    loadMessages(sessionId);
    
    // Highlight active session
    document.querySelectorAll('.session-item').forEach(item => {
        item.classList.remove('active');
    });
    event.target.classList.add('active');
}

async function loadMessages(sessionId) {
    try {
        const response = await fetch(`/api/sessions/${sessionId}/messages`);
        const messages = await response.json();
        
        const container = document.getElementById('messages-container');
        container.innerHTML = '';
        
        messages.forEach(msg => {
            addMessageToUI(msg);
        });
        
        // Scroll to bottom
        container.scrollTop = container.scrollHeight;
    } catch (error) {
        console.error('Error loading messages:', error);
    }
}

function addMessageToUI(message) {
    const container = document.getElementById('messages-container');
    
    const div = document.createElement('div');
    div.className = `message ${message.role}`;
    
    const content = document.createElement('div');
    content.className = 'message-content';
    content.textContent = message.content;
    
    div.appendChild(content);
    
    const timestamp = document.createElement('div');
    timestamp.className = 'message-timestamp';
    timestamp.textContent = new Date(message.timestamp).toLocaleTimeString();
    
    div.appendChild(timestamp);
    container.appendChild(div);
    
    // Scroll to bottom
    container.scrollTop = container.scrollHeight;
}

async function sendMessage(event) {
    event.preventDefault();
    
    if (!currentSessionId) {
        alert('Please select or create a session first');
        return;
    }
    
    const input = document.getElementById('message-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Clear input
    input.value = '';
    
    // Add loading indicator
    const container = document.getElementById('messages-container');
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message learner';
    loadingDiv.innerHTML = '<div class="message-content"><span class="loading"></span> AI is thinking...</div>';
    container.appendChild(loadingDiv);
    container.scrollTop = container.scrollHeight;
    
    try {
        const response = await fetch(`/api/sessions/${currentSessionId}/messages`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });
        
        if (response.ok) {
            const data = await response.json();
            
            // Remove loading indicator
            loadingDiv.remove();
            
            // Add student message
            addMessageToUI(data.student_message);
            
            // Add AI response
            addMessageToUI(data.ai_message);
        } else {
            loadingDiv.remove();
            const error = await response.json();
            alert('Error: ' + (error.error || 'Failed to send message'));
        }
    } catch (error) {
        console.error('Error sending message:', error);
        loadingDiv.remove();
        alert('Failed to send message');
    }
}

async function uploadMaterial(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/api/materials', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const data = await response.json();
            alert(`Successfully uploaded "${data.filename}"\nProcessed ${data.chunks_processed} chunks`);
            // Reset file input
            document.getElementById('file-input').value = '';
        } else {
            const error = await response.json();
            alert('Error: ' + (error.error || 'Failed to upload material'));
        }
    } catch (error) {
        console.error('Error uploading material:', error);
        alert('Failed to upload material');
    }
}