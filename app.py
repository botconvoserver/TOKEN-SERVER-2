from flask import Flask, request, render_template_string, jsonify
import requests
import time
import threading
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# Global variables for controlling the sending process
sending_active = False
sending_thread = None
current_status = {
    'active': False,
    'total_sent': 0,
    'total_failed': 0,
    'current_message': '',
    'start_time': None,
    'thread_id': '',
    'hater_name': ''
}

headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
    'referer': 'www.google.com'
}

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Xmarty Ayush King - Advanced Messenger Tool</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background: linear-gradient(135deg, #1a1a2e 0%, #0d1b1a 100%);
            font-family: 'Courier New', monospace;
            padding: 20px;
            min-height: 100vh;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        /* Header Styles */
        .header {
            text-align: center;
            margin-bottom: 30px;
            animation: glow 2s ease-in-out infinite alternate;
        }

        @keyframes glow {
            from { text-shadow: 0 0 5px pink; }
            to { text-shadow: 0 0 20px darkyellow, 0 0 30px darkgreen; }
        }

        .header h1 {
            font-size: 2.5em;
            background: linear-gradient(45deg, pink, darkyellow, darkwhite);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            animation: colorChange 3s infinite;
        }

        @keyframes colorChange {
            0% { color: pink; }
            50% { color: darkyellow; }
            100% { color: darkwhite; }
        }

        /* Feature Menu */
        .feature-menu {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .feature-card {
            background: rgba(0, 0, 0, 0.7);
            border-radius: 15px;
            padding: 20px;
            cursor: pointer;
            transition: all 0.3s ease;
            border: 2px solid darkyellow;
            text-align: center;
        }

        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            border-color: pink;
        }

        .feature-card.active {
            border-color: pink;
            background: rgba(255, 20, 147, 0.2);
        }

        .feature-card h3 {
            color: pink;
            margin-bottom: 10px;
            font-size: 1.3em;
        }

        .feature-card p {
            color: darkwhite;
            font-size: 0.9em;
        }

        /* Main Content Area */
        .main-content {
            background: rgba(0, 0, 0, 0.8);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 20px;
            border: 1px solid darkyellow;
        }

        .form-group {
            margin-bottom: 20px;
        }

        label {
            color: pink;
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
        }

        input, select, textarea {
            width: 100%;
            padding: 12px;
            background: rgba(255, 255, 255, 0.1);
            border: 2px solid darkyellow;
            border-radius: 10px;
            color: darkwhite;
            font-size: 14px;
            transition: all 0.3s ease;
        }

        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: pink;
            box-shadow: 0 0 10px rgba(255, 20, 147, 0.5);
        }

        button {
            background: linear-gradient(45deg, darkgreen, darkyellow);
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            transition: all 0.3s ease;
            margin: 5px;
        }

        button:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }

        .btn-stop {
            background: linear-gradient(45deg, #ff4444, #cc0000);
        }

        .btn-check {
            background: linear-gradient(45deg, #4CAF50, #45a049);
        }

        /* Status Panel */
        .status-panel {
            background: rgba(0, 0, 0, 0.6);
            border-radius: 15px;
            padding: 20px;
            margin-top: 20px;
            border: 1px solid darkyellow;
        }

        .status-item {
            color: darkwhite;
            padding: 10px;
            margin: 5px 0;
            border-left: 3px solid pink;
        }

        .uptime {
            color: #00ff00;
            font-weight: bold;
            animation: pulse 1s infinite;
        }

        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }

        .result-box {
            background: rgba(0,0,0,0.5);
            border-radius: 10px;
            padding: 15px;
            max-height: 300px;
            overflow-y: auto;
            margin-top: 15px;
        }

        .result-line {
            color: darkwhite;
            padding: 5px;
            font-size: 12px;
            border-bottom: 1px solid #333;
        }

        .success {
            color: #00ff00;
        }

        .error {
            color: #ff4444;
        }

        @media (max-width: 768px) {
            .feature-menu {
                grid-template-columns: 1fr;
            }
            
            .container {
                padding: 10px;
            }
        }
    </style>
    <script>
        let currentFeature = 'sender';
        
        function showFeature(feature) {
            currentFeature = feature;
            document.querySelectorAll('.feature-card').forEach(card => {
                card.classList.remove('active');
            });
            event.currentTarget.classList.add('active');
            
            document.getElementById('sender-section').style.display = feature === 'sender' ? 'block' : 'none';
            document.getElementById('checker-section').style.display = feature === 'checker' ? 'block' : 'none';
            document.getElementById('extractor-section').style.display = feature === 'extractor' ? 'block' : 'none';
            document.getElementById('status-section').style.display = feature === 'status' ? 'block' : 'none';
        }
        
        function updateStatus() {
            fetch('/get_status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('status-text').innerHTML = `
                        <div class="status-item">Status: ${data.active ? '🟢 RUNNING' : '🔴 STOPPED'}</div>
                        <div class="status-item">Messages Sent: ${data.total_sent}</div>
                        <div class="status-item">Failed: ${data.total_failed}</div>
                        <div class="status-item">Current Message: ${data.current_message || 'None'}</div>
                        <div class="status-item">Running Since: ${data.start_time || 'Not started'}</div>
                    `;
                });
        }
        
        setInterval(updateStatus, 2000);
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🦁 XMARTY AYUSH KING - ULTIMATE TOOL 🦁</h1>
            <p style="color: darkwhite; margin-top: 10px;">⚡ 365 Days Uptime - Non-Stop Operation ⚡</p>
        </div>
        
        <div class="feature-menu">
            <div class="feature-card active" onclick="showFeature('sender')">
                <h3>📨 Message Sender</h3>
                <p>Send messages continuously</p>
            </div>
            <div class="feature-card" onclick="showFeature('checker')">
                <h3>✅ Token Checker</h3>
                <p>Check token validity</p>
            </div>
            <div class="feature-card" onclick="showFeature('extractor')">
                <h3>💬 Messenger Extractor</h3>
                <p>Extract chat data</p>
            </div>
            <div class="feature-card" onclick="showFeature('status')">
                <h3>📊 Status Check</h3>
                <p>Monitor system status</p>
            </div>
        </div>
        
        <div class="main-content">
            <!-- Message Sender Section -->
            <div id="sender-section">
                <form action="/start_sender" method="post" enctype="multipart/form-data">
                    <div class="form-group">
                        <label>🔑 Convo ID:</label>
                        <input type="text" name="threadId" required>
                    </div>
                    <div class="form-group">
                        <label>📁 Tokens File (.txt):</label>
                        <input type="file" name="txtFile" accept=".txt" required>
                    </div>
                    <div class="form-group">
                        <label>💬 Messages File (.txt):</label>
                        <input type="file" name="messagesFile" accept=".txt" required>
                    </div>
                    <div class="form-group">
                        <label>👤 Hater Name:</label>
                        <input type="text" name="kidx" required>
                    </div>
                    <div class="form-group">
                        <label>⏱️ Speed (seconds):</label>
                        <input type="number" name="time" value="60" required>
                    </div>
                    <button type="submit">▶ START SENDING</button>
                    <button type="button" class="btn-stop" onclick="location.href='/stop_sender'">⏹ STOP SENDING</button>
                </form>
            </div>
            
            <!-- Token Checker Section -->
            <div id="checker-section" style="display:none">
                <form action="/check_tokens" method="post" enctype="multipart/form-data">
                    <div class="form-group">
                        <label>📁 Tokens File:</label>
                        <input type="file" name="tokenFile" accept=".txt" required>
                    </div>
                    <button type="submit">🔍 CHECK TOKENS</button>
                </form>
                <div id="checker-result" class="result-box"></div>
            </div>
            
            <!-- Messenger Extractor Section -->
            <div id="extractor-section" style="display:none">
                <form action="/extract_messages" method="post">
                    <div class="form-group">
                        <label>🔑 Thread/Convo ID:</label>
                        <input type="text" name="threadId" required>
                    </div>
                    <div class="form-group">
                        <label>🔑 Access Token:</label>
                        <input type="text" name="accessToken" required>
                    </div>
                    <button type="submit">📥 EXTRACT MESSAGES</button>
                </form>
                <div id="extractor-result" class="result-box"></div>
            </div>
            
            <!-- Status Check Section -->
            <div id="status-section" style="display:none">
                <h3 style="color: pink">System Status</h3>
                <div id="status-text"></div>
                <button onclick="location.href='/system_status'">🔄 Refresh Status</button>
            </div>
        </div>
        
        <div class="status-panel">
            <div class="status-item">🕐 Uptime: <span id="uptime" class="uptime">Calculating...</span></div>
            <div class="status-item">💻 Server Status: 🟢 ONLINE</div>
            <div class="status-item">📅 365 Days Uptime Guarantee: ✅ ACTIVE</div>
        </div>
    </div>
    
    <script>
        function updateUptime() {
            fetch('/get_uptime')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('uptime').innerText = data.uptime;
                });
        }
        setInterval(updateUptime, 1000);
        updateUptime();
        
        // Auto-refresh results for extractor and checker
        setInterval(() => {
            if (currentFeature === 'checker') {
                fetch('/get_checker_results')
                    .then(r => r.json())
                    .then(data => {
                        if(data.results) {
                            document.getElementById('checker-result').innerHTML = data.results.map(r => 
                                `<div class="result-line ${r.status === 'Valid' ? 'success' : 'error'}">${r.token}: ${r.status}</div>`
                            ).join('');
                        }
                    });
            } else if (currentFeature === 'extractor') {
                fetch('/get_extractor_results')
                    .then(r => r.json())
                    .then(data => {
                        if(data.messages) {
                            document.getElementById('extractor-result').innerHTML = data.messages.map(m => 
                                `<div class="result-line">${m}</div>`
                            ).join('');
                        }
                    });
            }
        }, 3000);
    </script>
</body>
</html>
'''

# Store results for different features
checker_results = []
extractor_messages = []
server_start_time = datetime.now()

def send_messages_loop(thread_id, access_tokens, messages, haters_name, time_interval):
    global sending_active, current_status
    num_comments = len(messages)
    max_tokens = len(access_tokens)
    post_url = f'https://graph.facebook.com/v15.0/t_{thread_id}/'
    
    message_index = current_status['total_sent'] % num_comments if current_status['total_sent'] > 0 else 0
    
    while sending_active:
        try:
            token_index = message_index % max_tokens
            access_token = access_tokens[token_index]
            message = messages[message_index].strip()
            full_message = haters_name + ' ' + message
            
            current_status['current_message'] = full_message
            parameters = {'access_token': access_token, 'message': full_message}
            response = requests.post(post_url, json=parameters, headers=headers)
            
            if response.ok:
                current_status['total_sent'] += 1
                print(f"[+] SUCCESS: {full_message}")
            else:
                current_status['total_failed'] += 1
                print(f"[-] FAILED: {full_message}")
            
            message_index = (message_index + 1) % num_comments
            time.sleep(time_interval)
            
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(30)

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/start_sender', methods=['POST'])
def start_sender():
    global sending_active, sending_thread, current_status
    
    if sending_active:
        return jsonify({'error': 'Sender already running'}), 400
    
    thread_id = request.form.get('threadId')
    haters_name = request.form.get('kidx')
    time_interval = int(request.form.get('time'))
    
    txt_file = request.files['txtFile']
    access_tokens = txt_file.read().decode().splitlines()
    
    messages_file = request.files['messagesFile']
    messages = messages_file.read().decode().splitlines()
    
    sending_active = True
    current_status = {
        'active': True,
        'total_sent': 0,
        'total_failed': 0,
        'current_message': '',
        'start_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'thread_id': thread_id,
        'hater_name': haters_name
    }
    
    sending_thread = threading.Thread(
        target=send_messages_loop,
        args=(thread_id, access_tokens, messages, haters_name, time_interval)
    )
    sending_thread.daemon = True
    sending_thread.start()
    
    return redirect(url_for('index'))

@app.route('/stop_sender')
def stop_sender():
    global sending_active
    sending_active = False
    return redirect(url_for('index'))

@app.route('/check_tokens', methods=['POST'])
def check_tokens():
    global checker_results
    token_file = request.files['tokenFile']
    tokens = token_file.read().decode().splitlines()
    checker_results = []
    
    for token in tokens:
        try:
            url = f"https://graph.facebook.com/me?access_token={token}"
            response = requests.get(url)
            if response.ok:
                checker_results.append({'token': token[:20] + '...', 'status': 'Valid'})
            else:
                checker_results.append({'token': token[:20] + '...', 'status': 'Invalid'})
        except:
            checker_results.append({'token': token[:20] + '...', 'status': 'Error'})
    
    return redirect(url_for('index'))

@app.route('/extract_messages', methods=['POST'])
def extract_messages():
    global extractor_messages
    thread_id = request.form.get('threadId')
    access_token = request.form.get('accessToken')
    
    extractor_messages = []
    try:
        url = f"https://graph.facebook.com/v15.0/t_{thread_id}/messages?access_token={access_token}&limit=50"
        response = requests.get(url)
        if response.ok:
            data = response.json()
            if 'data' in data:
                for msg in data['data']:
                    if 'message' in msg:
                        extractor_messages.append(f"{msg.get('created_time', 'Unknown')}: {msg['message']}")
    except Exception as e:
        extractor_messages.append(f"Error: {str(e)}")
    
    return redirect(url_for('index'))

@app.route('/get_status')
def get_status():
    return jsonify(current_status)

@app.route('/get_uptime')
def get_uptime():
    uptime = datetime.now() - server_start_time
    days = uptime.days
    hours = uptime.seconds // 3600
    minutes = (uptime.seconds % 3600) // 60
    seconds = uptime.seconds % 60
    return jsonify({'uptime': f"{days}d {hours}h {minutes}m {seconds}s"})

@app.route('/get_checker_results')
def get_checker_results():
    return jsonify({'results': checker_results})

@app.route('/get_extractor_results')
def get_extractor_results():
    return jsonify({'messages': extractor_messages})

@app.route('/system_status')
def system_status():
    return jsonify({
        'server_status': 'online',
        'sending_active': sending_active,
        'total_sent': current_status['total_sent'],
        'total_failed': current_status['total_failed']
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
