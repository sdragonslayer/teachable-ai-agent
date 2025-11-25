document.addEventListener('DOMContentLoaded', () => {
    loadSessionHistory();
});

async function loadSessionHistory() {
    try {
        const response = await fetch('/api/sessions');
        const sessions = await response.json();
        
        const container = document.getElementById('sessions-history');
        container.innerHTML = '';
        
        if (sessions.length === 0) {
            container.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: #9ca3af;">No sessions yet</p>';
            return;
        }
        
        sessions.forEach(session => {
            const card = document.createElement('div');
            card.className = 'session-card';
            
            const title = document.createElement('h3');
            title.textContent = session.title;
            
            const topic = document.createElement('p');
            topic.textContent = `Topic: ${session.topic || 'Not specified'}`;
            
            const messageCount = document.createElement('p');
            messageCount.textContent = `Messages: ${session.messages.length}`;
            
            const meta = document.createElement('div');
            meta.className = 'session-meta';
            
            const created = document.createElement('span');
            created.textContent = `Created: ${new Date(session.created_at).toLocaleDateString()}`;
            
            const link = document.createElement('span');
            link.style.cursor = 'pointer';
            link.style.color = 'var(--primary-color)';
            link.textContent = 'View';
            link.onclick = () => viewSessionDetails(session);
            
            meta.appendChild(created);
            meta.appendChild(link);
            
            card.appendChild(title);
            card.appendChild(topic);
            card.appendChild(messageCount);
            card.appendChild(meta);
            
            container.appendChild(card);
        });
    } catch (error) {
        console.error('Error loading session history:', error);
    }
}

function viewSessionDetails(session) {
    // Create a modal or redirect to view session details
    const modal = document.createElement('div');
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    `;
    
    const content = document.createElement('div');
    content.style.cssText = `
        background: white;
        border-radius: 8px;
        padding: 2rem;
        max-width: 600px;
        max-height: 80vh;
        overflow-y: auto;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
    `;
    
    const title = document.createElement('h2');
    title.textContent = session.title;
    title.style.marginBottom = '1rem';
    
    const topic = document.createElement('p');
    topic.textContent = `Topic: ${session.topic || 'Not specified'}`;
    topic.style.color = '#6b7280';
    topic.style.marginBottom = '1rem';
    
    const messagesDiv = document.createElement('div');
    messagesDiv.style.marginBottom = '1rem';
    
    const messagesTitle = document.createElement('h3');
    messagesTitle.textContent = 'Conversation';
    messagesTitle.style.marginBottom = '1rem';
    messagesDiv.appendChild(messagesTitle);
    
    session.messages.forEach(msg => {
        const msgDiv = document.createElement('div');
        msgDiv.style.cssText = `
            margin-bottom: 1rem;
            padding: 0.75rem;
            background: ${msg.role === 'student' ? '#dbeafe' : '#f0fdf4'};
            border-radius: 4px;
            border-left: 4px solid ${msg.role === 'student' ? '#3b82f6' : '#10b981'};
        `;
        
        const role = document.createElement('strong');
        role.textContent = msg.role === 'student' ? 'You: ' : 'AI Learner: ';
        role.style.color = msg.role === 'student' ? '#3b82f6' : '#10b981';
        
        const text = document.createElement('span');
        text.textContent = msg.content;
        
        msgDiv.appendChild(role);
        msgDiv.appendChild(text);
        messagesDiv.appendChild(msgDiv);
    });
    
    const closeBtn = document.createElement('button');
    closeBtn.textContent = 'Close';
    closeBtn.className = 'btn btn-primary';
    closeBtn.onclick = () => modal.remove();
    
    content.appendChild(title);
    content.appendChild(topic);
    content.appendChild(messagesDiv);
    content.appendChild(closeBtn);
    
    modal.appendChild(content);
    document.body.appendChild(modal);
}