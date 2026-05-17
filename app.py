from flask import Flask, request, render_template_string, jsonify
import requests
import time
import threading
import os
import re
from datetime import datetime
import json
import uuid

app = Flask(__name__)
app.secret_key = 'xmarty-ayush-king-secret-key-2026'

# Global variables
active_tasks = {}  # TaskID -> {task_thread, owner_id, task_data, active_flag}
headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'referer': 'https://www.google.com'
}

# HTML Template with Dark Pink + Dark Yellow Theme
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>⭐️ EKKU GILL BRAND🔥</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: linear-gradient(135deg, #800020 0%, #8B0000 25%, #B8860B 50%, #DAA520 75%, #800020 100%);
            background-attachment: fixed;
            font-family: 'Courier New', 'Segoe UI', monospace;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1300px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            padding: 30px;
            background: linear-gradient(135deg, rgba(139,0,0,0.9) 0%, rgba(184,134,11,0.9) 100%);
            border-radius: 20px;
            margin-bottom: 30px;
            border: 2px solid #FFD700;
            box-shadow: 0 0 30px rgba(255,215,0,0.5);
            backdrop-filter: blur(5px);
        }
        
        .header h1 {
            background: linear-gradient(135deg, #FFD700 0%, #FF69B4 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 2.8em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            letter-spacing: 2px;
        }
        
        .header p {
            color: #FFD700;
            margin-top: 10px;
            font-size: 1.1em;
            text-shadow: 1px 1px 2px #800020;
        }
        
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }
        
        .feature-btn {
            background: linear-gradient(135deg, rgba(139,0,0,0.85) 0%, rgba(184,134,11,0.85) 100%);
            border: 2px solid #FFD700;
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            backdrop-filter: blur(5px);
        }
        
        .feature-btn:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(255,215,0,0.5);
            background: linear-gradient(135deg, rgba(184,134,11,0.95) 0%, rgba(139,0,0,0.95) 100%);
        }
        
        .feature-btn.active {
            background: linear-gradient(135deg, #FFD700 0%, #FF69B4 100%);
            border-color: #fff;
        }
        
        .feature-btn.active h3,
        .feature-btn.active p {
            color: #800020;
        }
        
        .feature-btn h3 {
            color: #FFD700;
            font-size: 1.8em;
            margin-bottom: 10px;
        }
        
        .feature-btn p {
            color: #FFB6C1;
            font-size: 0.9em;
        }
        
        .panel {
            background: linear-gradient(135deg, rgba(139,0,0,0.9) 0%, rgba(184,134,11,0.9) 100%);
            border-radius: 20px;
            padding: 30px;
            border: 2px solid #FFD700;
            margin-top: 20px;
            display: none;
            backdrop-filter: blur(5px);
            box-shadow: 0 0 20px rgba(255,215,0,0.3);
        }
        
        .panel h2 {
            color: #FFD700;
            margin-bottom: 25px;
            font-size: 2em;
            border-left: 5px solid #FF69B4;
            padding-left: 15px;
            text-shadow: 1px 1px 2px #800020;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            color: #FFD700;
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            font-size: 1.1em;
        }
        
        input, select, textarea, input[type="file"] {
            width: 100%;
            padding: 12px;
            background: rgba(0,0,0,0.5);
            border: 1px solid #FFD700;
            border-radius: 10px;
            color: #FFD700;
            font-size: 14px;
        }
        
        input:focus, select:focus {
            outline: none;
            border-color: #FF69B4;
            background: rgba(0,0,0,0.7);
            box-shadow: 0 0 10px rgba(255,105,180,0.5);
        }
        
        button {
            background: linear-gradient(135deg, #FFD700 0%, #FF69B4 100%);
            color: #800020;
            padding: 12px 30px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            transition: all 0.3s;
            margin-right: 10px;
        }
        
        button:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 20px rgba(255,215,0,0.5);
        }
        
        button.danger {
            background: linear-gradient(135deg, #DC143C 0%, #8B0000 100%);
            color: #FFD700;
        }
        
        button.success {
            background: linear-gradient(135deg, #228B22 0%, #DAA520 100%);
            color: #FFD700;
        }
        
        .status-card {
            background: rgba(0,0,0,0.6);
            padding: 20px;
            border-radius: 15px;
            margin-top: 20px;
            border-left: 4px solid #FF69B4;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        
        .stat-item {
            text-align: center;
            padding: 15px;
            background: linear-gradient(135deg, rgba(139,0,0,0.5) 0%, rgba(184,134,11,0.5) 100%);
            border-radius: 10px;
            border: 1px solid #FFD700;
        }
        
        .stat-value {
            color: #FFD700;
            font-size: 2em;
            font-weight: bold;
        }
        
        .stat-label {
            color: #FFB6C1;
            margin-top: 5px;
            font-size: 0.85em;
        }
        
        .results-area {
            margin-top: 20px;
            max-height: 400px;
            overflow-y: auto;
        }
        
        .message-item {
            background: rgba(0,0,0,0.5);
            padding: 10px;
            margin: 5px 0;
            border-radius: 8px;
            border-left: 3px solid #FF69B4;
            color: #FFD700;
        }
        
        .sending-active {
            animation: pulse 1s infinite;
            color: #FF69B4 !important;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; text-shadow: 0 0 5px #FFD700; }
            50% { opacity: 0.7; text-shadow: 0 0 15px #FF69B4; }
        }
        
        .task-card {
            background: rgba(0,0,0,0.5);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
            border: 1px solid #FFD700;
        }
        
        .task-id {
            font-family: monospace;
            color: #FF69B4;
            font-size: 12px;
        }
        
        .footer {
            text-align: center;
            margin-top: 30px;
            padding: 20px;
            color: #FFD700;
            border-top: 1px solid #FF69B4;
        }
        
        ::-webkit-scrollbar {
            width: 10px;
        }
        
        ::-webkit-scrollbar-track {
            background: #800020;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #FFD700;
            border-radius: 5px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #FF69B4;
        }
        
        @media (max-width: 768px) {
            .feature-grid {
                grid-template-columns: 1fr;
            }
            
            .panel {
                padding: 20px;
            }
            
            .header h1 {
                font-size: 1.8em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⭐️ EKKU GILL BRAND🔥</h1>
            <p>FACEBOOK MASSAGE SENDER</p>
            <p style="font-size: 12px; margin-top: 10px;">⚜️9MAN-x-YAMDHUD⚜️</p>
        </div>
        
        <div class="feature-grid">
            <div class="feature-btn" onclick="showPanel('sender')">
                <h3>📨MASSAGE SENDER</h3>
                <p>Mass message sender with multi-token support</p>
            </div>
            <div class="feature-btn" onclick="showPanel('checker')">
                <h3>✅TOKEN CHECKER</h3>
                <p>Validate Facebook access tokens</p>
            </div>
            <div class="feature-btn" onclick="showPanel('extractor')">
                <h3>💬CHAT EXTRACTOR</h3>
                <p>Extract messages from any conversation</p>
            </div>
            <div class="feature-btn" onclick="showPanel('tasks')">
                <h3>📋ACTIVE TASKS</h3>
                <p>View and manage your tasks</p>
            </div>
        </div>
        
        <!-- Sender Panel -->
        <div id="senderPanel" class="panel">
            <h2>📨MESSAGE SENDER</h2>
            <form id="senderForm" enctype="multipart/form-data">
                <div class="form-group">
                    <label>🔑 Conversation group ID:</label>
                    <input type="text" name="threadId" required placeholder="Enter thread/conversation ID">
                </div>
                <div class="form-group">
                    <label>📄 Tokens File (.txt):</label>
                    <input type="file" name="txtFile" accept=".txt" required>
                </div>
                <div class="form-group">
                    <label>💬 Messages File (.txt):</label>
                    <input type="file" name="messagesFile" accept=".txt" required>
                </div>
                <div class="form-group">
                    <label>👤 Name/Prefix:</label>
                    <input type="text" name="kidx" required placeholder="Enter prefix name">
                </div>
                <div class="form-group">
                    <label>⏱ Speed (seconds):</label>
                    <input type="number" name="time" value="60" required>
                </div>
                <div class="form-group">
                    <label>👤 Your User ID (for task ownership):</label>
                    <input type="text" name="userId" required placeholder="Enter your unique user ID">
                </div>
                <button type="submit" class="success">🚀 START TASK</button>
            </form>
            <div id="senderMessage"></div>
        </div>
        
        <!-- Token Checker Panel -->
        <div id="checkerPanel" class="panel">
            <h2>✅ TOKEN CHECKER</h2>
            <form id="checkerForm" enctype="multipart/form-data">
                <div class="form-group">
                    <label>📄 Tokens File (.txt):</label>
                    <input type="file" name="txtFile" accept=".txt" required>
                </div>
                <button type="submit">🔍 CHECK TOKENS</button>
            </form>
            <div id="checkerResults" class="results-area"></div>
        </div>
        
        <!-- Extractor Panel -->
        <div id="extractorPanel" class="panel">
            <h2>💬 CHAT EXTRACTOR</h2>
            <form id="extractorForm">
                <div class="form-group">
                    <label>🔑Access Token:</label>
                    <input type="text" name="accessToken" required placeholder="Enter Facebook access token">
                </div>
                <div class="form-group">
                    <label>💬Thread ID:</label>
                    <input type="text" name="threadId" required placeholder="Enter thread/conversation ID">
                </div>
                <div class="form-group">
                    <label>📊 Messages Limit:</label>
                    <select name="limit">
                        <option value="10">10 messages</option>
                        <option value="25">25 messages</option>
                        <option value="50" selected>50 messages</option>
                        <option value="100">100 messages</option>
                    </select>
                </div>
                <button type="submit">📥 EXTRACT MESSAGES</button>
            </form>
            <div id="extractorResults" class="results-area"></div>
        </div>
        
        <!-- Tasks Panel -->
        <div id="tasksPanel" class="panel">
            <h2>📋 ACTIVE TASKS</h2>
            <div class="form-group">
                <label>👤 Your User ID:</label>
                <input type="text" id="viewerUserId" placeholder="Enter your user ID to see your tasks">
                <button onclick="loadTasks()" style="margin-top: 10px;">🔍 LOAD MY TASKS</button>
            </div>
            <div id="tasksList" class="results-area"></div>
        </div>
        
        <div class="footer">
            <p>© made by ⭐️ EKKU GILL BRAND🔥</p>
        </div>
    </div>
    
    <script>
        let currentPanel = 'sender';
        
        function showPanel(panel) {
            document.getElementById('senderPanel').style.display = 'none';
            document.getElementById('checkerPanel').style.display = 'none';
            document.getElementById('extractorPanel').style.display = 'none';
            document.getElementById('tasksPanel').style.display = 'none';
            
            document.getElementById(panel + 'Panel').style.display = 'block';
            currentPanel = panel;
            
            if (panel === 'tasks') {
                loadTasks();
            }
        }
        
        document.getElementById('senderForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            
            const response = await fetch('/start_task', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            alert(result.message);
            if (result.status === 'success') {
                document.getElementById('senderMessage').innerHTML = `<div class="message-item" style="border-left-color: #228B22;">✅ Task Created! Task ID: ${result.task_id}</div>`;
            } else {
                document.getElementById('senderMessage').innerHTML = `<div class="message-item" style="border-left-color: #DC143C;">❌ ${result.message}</div>`;
            }
        });
        
        document.getElementById('checkerForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            
            const response = await fetch('/check_tokens', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            const resultsDiv = document.getElementById('checkerResults');
            
            if (result.status === 'success') {
                let html = `<h3 style="color:#FFD700;">✅ ${result.valid}/${result.total} Valid Tokens</h3>`;
                result.results.forEach(token => {
                    if (token.valid) {
                        html += `<div class="message-item" style="border-left-color: #228B22;">✅ Token ${token.index}: VALID (${token.name})</div>`;
                    } else {
                        html += `<div class="message-item" style="border-left-color: #DC143C;">❌ Token ${token.index}: INVALID</div>`;
                    }
                });
                resultsDiv.innerHTML = html;
            }
        });
        
        document.getElementById('extractorForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            
            const response = await fetch('/extract_messages', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            const resultsDiv = document.getElementById('extractorResults');
            
            if (result.status === 'success') {
                let html = `<h3 style="color:#FFD700;">📥 ${result.count} Messages Extracted</h3>`;
                result.messages.forEach(msg => {
                    html += `<div class="message-item">
                        <strong style="color:#FF69B4;">${msg.from || 'Unknown'}</strong> <span style="color:#FFD700;">-</span> ${new Date(msg.time).toLocaleString()}<br>
                        ${msg.message || '[No Text]'}
                    </div>`;
                });
                resultsDiv.innerHTML = html;
            } else {
                resultsDiv.innerHTML = `<div class="message-item" style="border-left-color:#DC143C;">❌ ${result.message}</div>`;
            }
        });
        
        async function stopTask(taskId, userId) {
            const response = await fetch('/stop_task', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    task_id: taskId,
                    user_id: userId
                })
            });
            
            const result = await response.json();
            alert(result.message);
            loadTasks();
        }
        
        async function loadTasks() {
            const userId = document.getElementById('viewerUserId').value;
            if (!userId) {
                alert('Please enter your user ID');
                return;
            }
            
            const response = await fetch(`/list_tasks?user_id=${userId}`);
            const data = await response.json();
            const tasksDiv = document.getElementById('tasksList');
            
            if (data.tasks.length === 0) {
                tasksDiv.innerHTML = '<div class="message-item">📭 No active tasks found for this user</div>';
                return;
            }
            
            let html = '<h3 style="color:#FFD700;">📋 Your Active Tasks:</h3>';
            data.tasks.forEach(task => {
                html += `
                    <div class="task-card">
                        <div><strong style="color:#FF69B4;">Task ID:</strong> <span class="task-id">${task.task_id}</span></div>
                        <div><strong style="color:#FF69B4;">Started:</strong> ${task.start_time}</div>
                        <div><strong style="color:#FF69B4;">Status:</strong> <span style="color:#FFD700;">${task.active ? '🟢 RUNNING' : '🔴 STOPPED'}</span></div>
                        <div><strong style="color:#FF69B4;">Stats:</strong> Sent: ${task.stats.total_sent || 0} | Success: ${task.stats.success || 0} | Failed: ${task.stats.failed || 0}</div>
                        ${task.active ? `<button onclick="stopTask('${task.task_id}', '${userId}')" class="danger" style="margin-top: 10px;">⏹ STOP TASK</button>` : ''}
                    </div>
                `;
            });
            tasksDiv.innerHTML = html;
        }
        
        showPanel('sender');
    </script>
</body>
</html>
'''

# Helper Functions
def check_token_validity(access_token):
    """Check if Facebook access token is valid"""
    try:
        url = f"https://graph.facebook.com/v15.0/me?access_token={access_token}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return True, data.get('name', 'Unknown')
        return False, None
    except:
        return False, None

def extract_chat_messages(access_token, thread_id, limit=50):
    """Extract messages from a thread"""
    try:
        url = f"https://graph.facebook.com/v15.0/t_{thread_id}/messages"
        params = {
            'access_token': access_token,
            'limit': limit,
            'fields': 'message,created_time,from'
        }
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            messages = []
            for msg in data.get('data', []):
                messages.append({
                    'message': msg.get('message', ''),
                    'time': msg.get('created_time', ''),
                    'time': msg.get('created_time', ''),
                    'from': msg.get('from', {}).get('name', 'Unknown')
                })
            return True, messages
        return False, []
    except Exception as e:
        return False, []

def send_messages_worker(task_id, thread_id, haters_name, speed, tokens, messages, owner_id):
    """Background worker for sending messages"""
    global active_tasks
    
    post_url = f'https://graph.facebook.com/v15.0/t_{thread_id}/'
    msg_count = len(messages)
    token_count = len(tokens)
    
    while active_tasks[task_id]['active']:
        try:
            for i in range(msg_count):
                if not active_tasks[task_id]['active']:
                    break
                
                token = tokens[i % token_count]
                message = messages[i].strip()
                full_message = f"{haters_name} {message}"
                
                params = {
                    'access_token': token,
                    'message': full_message
                }
                
                response = requests.post(post_url, json=params, headers=headers, timeout=30)
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                active_tasks[task_id]['task_data']['total_sent'] = active_tasks[task_id]['task_data'].get('total_sent', 0) + 1
                
                if response.status_code == 200:
                    active_tasks[task_id]['task_data']['success'] = active_tasks[task_id]['task_data'].get('success', 0) + 1
                    print(f"[+] TASK {task_id}: SUCCESS: {full_message[:50]}...")
                else:
                    active_tasks[task_id]['task_data']['failed'] = active_tasks[task_id]['task_data'].get('failed', 0) + 1
                    print(f"[-] TASK {task_id}: FAILED: {full_message[:50]}...")
                
                active_tasks[task_id]['task_data']['last_message'] = full_message[:100]
                active_tasks[task_id]['task_data']['last_time'] = current_time
                
                time.sleep(speed)
                
        except Exception as e:
            active_tasks[task_id]['task_data']['errors'] = active_tasks[task_id]['task_data'].get('errors', 0) + 1
            print(f"[!] TASK {task_id}: ERROR: {str(e)}")
            time.sleep(30)

# Routes
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/start_task', methods=['POST'])
def start_task():
    global active_tasks
    
    thread_id = request.form.get('threadId')
    haters_name = request.form.get('kidx')
    speed = int(request.form.get('time'))
    owner_id = request.form.get('userId')
    
    if not owner_id:
        return jsonify({'status': 'error', 'message': 'User ID is required!'})
    
    txt_file = request.files['txtFile']
    tokens = txt_file.read().decode().splitlines()
    
    msg_file = request.files['messagesFile']
    messages = msg_file.read().decode().splitlines()
    
    # Validate tokens
    valid_tokens = []
    for token in tokens[:10]:
        is_valid, name = check_token_validity(token)
        if is_valid:
            valid_tokens.append(token)
    
    if not valid_tokens:
        return jsonify({'status': 'error', 'message': 'No valid tokens found!'})
    
    task_id = str(uuid.uuid4())[:8]  # Generate short unique task ID
    
    task_data = {
        'total_sent': 0,
        'success': 0,
        'failed': 0,
        'errors': 0,
        'valid_tokens': len(valid_tokens),
        'messages_count': len(messages),
        'last_message': '-',
        'last_time': '-'
    }
    
    active_tasks[task_id] = {
        'task_thread': None,
        'owner_id': owner_id,
        'task_data': task_data,
        'active': True,
        'start_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    task_thread = threading.Thread(
        target=send_messages_worker,
        args=(task_id, thread_id, haters_name, speed, valid_tokens, messages, owner_id)
    )
    task_thread.daemon = True
    task_thread.start()
    
    active_tasks[task_id]['task_thread'] = task_thread
    
    return jsonify({
        'status': 'success', 
        'message': f'Task started successfully! Task ID: {task_id}',
        'task_id': task_id
    })

@app.route('/stop_task', methods=['POST'])
def stop_task():
    global active_tasks
    
    data = request.get_json()
    task_id = data.get('task_id')
    requester_id = data.get('user_id')
    
    # Error handling: Invalid Task ID
    if task_id not in active_tasks:
        return jsonify({
            'status': 'error', 
            'message': f'Invalid Task ID: {task_id} - Task not found'
        }), 404
    
    task = active_tasks[task_id]
    
    # Error handling: Already stopped
    if not task['active']:
        return jsonify({
            'status': 'error', 
            'message': f'Task {task_id} is already stopped'
        }), 400
    
    # Security: Check if owner matches
    if task['owner_id'] != requester_id:
        return jsonify({
            'status': 'error', 
            'message': 'Unauthorized: You do not own this task'
        }), 403
    
    # Stop the task
    task['active'] = False
    task['task_data']['active'] = False
    
    return jsonify({
        'status': 'success', 
        'message': f'Task {task_id} stopped successfully',
        'stats': task['task_data']
    })

@app.route('/list_tasks', methods=['GET'])
def list_tasks():
    global active_tasks
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({'status': 'error', 'message': 'User ID required'}), 400
    
    user_tasks = []
    for task_id, task in active_tasks.items():
        if task['owner_id'] == user_id:
            user_tasks.append({
                'task_id': task_id,
                'owner_id': task['owner_id'],
                'active': task['active'],
                'start_time': task['start_time'],
                'stats': task['task_data']
            })
    
    return jsonify({
        'status': 'success',
        'tasks': user_tasks
    })

@app.route('/check_tokens', methods=['POST'])
def check_tokens():
    if 'txtFile' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file uploaded!'})
    
    txt_file = request.files['txtFile']
    tokens = txt_file.read().decode().splitlines()
    
    results = []
    valid_count = 0
    
    for i, token in enumerate(tokens[:20]):
        is_valid, name = check_token_validity(token)
        if is_valid:
            valid_count += 1
            results.append({'index': i+1, 'valid': True, 'name': name})
        else:
            results.append({'index': i+1, 'valid': False, 'name': None})
    
    return jsonify({
        'status': 'success',
        'total': len(tokens[:20]),
        'valid': valid_count,
        'results': results
    })

@app.route('/extract_messages', methods=['POST'])
def extract_messages():
    thread_id = request.form.get('threadId')
    access_token = request.form.get('accessToken')
    limit = int(request.form.get('limit', 50))
    
    is_valid, name = check_token_validity(access_token)
    if not is_valid:
        return jsonify({'status': 'error', 'message': 'Invalid access token!'})
    
    success, messages = extract_chat_messages(access_token, thread_id, limit)
    
    if success:
        return jsonify({
            'status': 'success',
            'count': len(messages),
            'messages': messages
        })
    else:
        return jsonify({'status': 'error', 'message': 'Failed to extract messages!'})

if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════════╗
    ║     ⭐️ EKKU GILL BRAND🔥 - SERVER v3.0      ║
    ║     Dark Pink & Dark Yellow Edition      ║
    ║     Task System with Ownership           ║
    ║     Port: 5000 | 24/7 Operation         ║
    ╚══════════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
