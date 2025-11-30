from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
import os
import json
from datetime import datetime

from config import SECRET_KEY, ALLOWED_EXTENSIONS
from utils.pinecone_db import get_relevant_context, store_conversation, store_embedding
from utils.prompt_builder import (
    get_system_prompt,
    get_embedding, 
    generate_learner_response
)
from utils.document_loader import process_document

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

users_db = {}
sessions_db = {}
conversations_db = {}


def login_required(f):
    """Requires login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('chat'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            return render_template('login.html', error='Username and password required')
        
        if username not in users_db:
            users_db[username] = {'password': password, 'created_at': datetime.now().isoformat()}
        elif users_db[username]['password'] != password:
            return render_template('login.html', error='Invalid password')
        
        session['username'] = username
        return redirect(url_for('chat'))
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Handles User logout"""
    session.clear()
    return redirect(url_for('login'))


@app.route('/chat')
@login_required
def chat():
    """Chat Interface"""
    username = session['username']
    return render_template('chat.html', username=username)


@app.route('/history')
@login_required
def history():
    """Past sessions"""
    username = session['username']
    user_sessions = sessions_db.get(username, [])
    return render_template('history.html', username=username, sessions=user_sessions)


@app.route('/api/sessions', methods=['GET', 'POST'])
@login_required
def manage_sessions():
    """Creates sessions or retrieves them"""
    username = session['username']
    
    if request.method == 'POST':
        data = request.get_json()
        title = data.get('title', 'Untitled Session')
        topic = data.get('topic', '')
        
        session_id = f"{username}_{len(sessions_db.get(username, []))}"
        new_session = {
            'id': session_id,
            'title': title,
            'topic': topic,
            'created_at': datetime.now().isoformat(),
            'messages': []
        }
        
        if username not in sessions_db:
            sessions_db[username] = []
        sessions_db[username].append(new_session)
        
        return jsonify(new_session), 201
    
    user_sessions = sessions_db.get(username, [])
    return jsonify(user_sessions)


@app.route('/api/sessions/<session_id>/messages', methods=['GET', 'POST'])
@login_required
def manage_messages(session_id):
    """Session logic"""
    username = session['username']
    
    user_sessions = sessions_db.get(username, [])
    current_session = next((s for s in user_sessions if s['id'] == session_id), None)
    
    if not current_session:
        return jsonify({'error': 'Session not found'}), 404
    
    if request.method == 'POST':
        data = request.get_json()
        student_input = data.get('message', '').strip()
        
        if not student_input:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        try:
            conversation_history = current_session['messages'].copy()
            
            student_msg = {
                'role': 'student',
                'content': student_input,
                'timestamp': datetime.now().isoformat()
            }
            current_session['messages'].append(student_msg)
            
            student_embedding = get_embedding(student_input)
            
            if student_embedding:
                relevant_context = get_relevant_context(student_embedding)
                system_prompt = get_system_prompt()
                
                ai_response = generate_learner_response(
                    student_input=student_input,
                    context=relevant_context,
                    system_prompt=system_prompt,
                    conversation_history=conversation_history
                )
                
                ai_msg = {
                    'role': 'learner',
                    'content': ai_response,
                    'timestamp': datetime.now().isoformat()
                }
                current_session['messages'].append(ai_msg)
                
                response_embedding = get_embedding(ai_response)
                if response_embedding:
                    store_conversation(
                        student_input, 
                        ai_response, 
                        response_embedding, 
                        session_id, 
                        username
                    )
                
                return jsonify({
                    'student_message': student_msg,
                    'ai_message': ai_msg
                }), 201
            else:
                return jsonify({'error': 'Failed to process message'}), 500
        
        except Exception as e:
            print(f"Error processing message: {e}")
            return jsonify({'error': str(e)}), 500
    
    return jsonify(current_session['messages'])


@app.route('/api/materials', methods=['GET', 'POST'])
@login_required
def manage_materials():
    """Upload/retrieve course materials"""
    username = session['username']
    
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        if file_ext not in ALLOWED_EXTENSIONS:
            return jsonify({'error': 'File type not allowed'}), 400
        
        try:
            os.makedirs('course_materials', exist_ok=True)
            file_path = os.path.join('course_materials', file.filename)
            file.save(file_path)
            
            chunks = process_document(file_path, file_ext)
            
            if not chunks:
                return jsonify({'error': 'Failed to process document'}), 500
            
            stored_ids = []
            for i, chunk in enumerate(chunks):
                embedding = get_embedding(chunk)
                if embedding:
                    metadata = {
                        'type': 'course_material',
                        'source_file': file.filename,
                        'chunk_id': str(i),
                        'content': chunk
                    }
                    vector_id = store_embedding(embedding, metadata, 'course_materials')
                    if vector_id:
                        stored_ids.append(vector_id)
            
            return jsonify({
                'filename': file.filename,
                'chunks_processed': len(chunks),
                'vectors_stored': len(stored_ids)
            }), 201
        
        except Exception as e:
            print(f"Error uploading material: {e}")
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'message': 'Upload course materials using POST'})


if __name__ == '__main__':
    app.run(debug=True, port=5000)