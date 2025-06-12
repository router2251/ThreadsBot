from flask import Flask, render_template_string, request, jsonify
from flask_socketio import SocketIO, emit
from auto_comment_bot import AutoCommentBot, GEMINI_API_KEY

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

log_queue = []
bot = None

def log_callback(msg):
    log_queue.append(msg)
    socketio.emit('log', {'msg': msg})

@app.route('/')
def index():
    return render_template_string('''
    <html>
    <head>
        <title>Threads Auto Comment Bot</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.4.1/socket.io.js"></script>
    </head>
    <body>
        <h2>Threads Auto Comment Bot</h2>
        <form id="params">
            <label>Device Serial: <input type="text" name="device_serial" value="usb"></label><br>
            <label>Like Threshold: <input type="number" name="like_threshold" value="100"></label><br>
            <label>Comment Threshold: <input type="number" name="comment_threshold" value="20"></label><br>
            <label>Gemini API Key: <input type="text" name="ai_api_key" value="{{ api_key }}"></label><br>
            <button type="button" onclick="startBot()">Start Bot</button>
            <button type="button" onclick="stopBot()">Stop Bot</button>
        </form>
        <h3>Logs</h3>
        <div id="log" style="background:#222;color:#0f0;padding:10px;height:300px;overflow:auto;"></div>
        <script>
            var socket = io();
            socket.on('log', function(data) {
                var logDiv = document.getElementById('log');
                logDiv.innerHTML += data.msg + '<br>';
                logDiv.scrollTop = logDiv.scrollHeight;
            });
            function startBot() {
                var form = document.getElementById('params');
                var data = {};
                for (var i = 0; i < form.elements.length; i++) {
                    var e = form.elements[i];
                    if (e.name) data[e.name] = e.value;
                }
                fetch('/start', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
            }
            function stopBot() {
                fetch('/stop', {method:'POST'});
            }
        </script>
    </body>
    </html>
    ''', api_key=GEMINI_API_KEY)

@app.route('/start', methods=['POST'])
def start():
    global bot
    data = request.json
    if bot and bot.running:
        return jsonify({'status': 'already running'})
    bot = AutoCommentBot(
        device_serial=data.get('device_serial', 'usb'),
        like_threshold=int(data.get('like_threshold', 100)),
        comment_threshold=int(data.get('comment_threshold', 20)),
        ai_api_key=data.get('ai_api_key', ''),
        log_callback=log_callback
    )
    bot.start()
    return jsonify({'status': 'started'})

@app.route('/stop', methods=['POST'])
def stop():
    global bot
    if bot:
        bot.stop()
    return jsonify({'status': 'stopped'})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000) 