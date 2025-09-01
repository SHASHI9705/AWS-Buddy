from flask import Flask, render_template_string, request, redirect, url_for
import threading
import subprocess
import os

app = Flask(__name__)

buddy_process = None

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Buddy Control</title>
    <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            text-align: center;
            margin: 0;
            min-height: 100vh;
            background: linear-gradient(135deg, #0d1b2a 0%, #1b263b 50%, #274472 100%);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }
        .container {
            background: rgba(255,255,255,0.85);
            border-radius: 18px;
            box-shadow: 0 8px 32px 0 rgba(60,60,60,0.18);
            padding: 10px 32px 32px 32px;
            max-width: 400px;
        }
        h1 {
            font-size: 2.1em;
            margin-bottom: 30px;
            background: linear-gradient(90deg, #757575, #212121);
            color: transparent;
            background-clip: text;
            -webkit-background-clip: text;
            font-weight: 700;
        }
        .button-row {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 25px;
        }
        button {
            font-size: 1.15em;
            padding: 12px 36px;
            border: none;
            border-radius: 8px;
            background: linear-gradient(90deg, #616161 0%, #9e9e9e 100%);
            color: #fff;
            font-weight: 600;
            box-shadow: 0 2px 8px rgba(60,60,60,0.12);
            cursor: pointer;
            transition: background 0.2s, transform 0.2s;
        }
        button:disabled {
            background: #bdbdbd;
            color: #757575;
            cursor: not-allowed;
            transform: none;
        }
        button:not(:disabled):hover {
            background: linear-gradient(90deg, #424242 0%, #757575 100%);
            transform: translateY(-2px) scale(1.04);
        }
        .status {
            font-size: 1.1em;
            margin-top: 10px;
            color: #424242;
            letter-spacing: 0.5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Control your system by commanding your "Buddy"</h1>
        <div class="button-row">
            <form method="POST" action="/start" style="display:inline;">
                <button type="submit" {% if running %}disabled{% endif %}>Start</button>
            </form>
            <form method="POST" action="/stop" style="display:inline;">
                <button type="submit" {% if not running %}disabled{% endif %}>Stop</button>
            </form>
        </div>
        <div class="status">
            Status: <strong>{{ 'Running' if running else 'Stopped' }}</strong>
        </div>
        <div style="display:flex; justify-content:center; align-items:center; margin-top:38px; margin-bottom:10px;">
            <span style="display:inline-block; background:linear-gradient(90deg,#274472 0%,#1b263b 100%); color:#fff; font-size:1.18em; font-weight:700; letter-spacing:1.3px; border-radius:24px; padding:10px 32px; box-shadow:0 2px 12px #0d1b2a44;">
                <svg xmlns='http://www.w3.org/2000/svg' width='22' height='22' viewBox='0 0 24 24' fill='none' style='vertical-align:middle; margin-right:10px; margin-bottom:3px;'><circle cx='12' cy='12' r='12' fill='#7eb6ff'/><path d='M8 12h8M12 8v8' stroke='#fff' stroke-width='2' stroke-linecap='round'/></svg>
                Examples
            </span>
        </div>
        <ul style="list-style:none; padding:0; margin-top:18px;">
            <li style="margin-bottom:12px; font-size:1.12em; background: linear-gradient(90deg, #274472 0%, #1b263b 100%); border-radius: 8px; padding: 10px 0; color:#eaf6ff; box-shadow: 0 2px 8px #0d1b2a33;">
                <span style="color:#7eb6ff; font-weight:600;">Say:</span> <span style="color:#f7b801; font-weight:500;">open new tab</span>
            </li>
            <li style="margin-bottom:12px; font-size:1.12em; background: linear-gradient(90deg, #274472 0%, #1b263b 100%); border-radius: 8px; padding: 10px 0; color:#eaf6ff; box-shadow: 0 2px 8px #0d1b2a33;">
                <span style="color:#7eb6ff; font-weight:600;">Say:</span> <span style="color:#f7b801; font-weight:500;">close it</span>
            </li>
            <li style="margin-bottom:12px; font-size:1.12em; background: linear-gradient(90deg, #274472 0%, #1b263b 100%); border-radius: 8px; padding: 10px 0; color:#eaf6ff; box-shadow: 0 2px 8px #0d1b2a33;">
                <span style="color:#7eb6ff; font-weight:600;">Say:</span> <span style="color:#f7b801; font-weight:500;">increase volume</span>
            </li>
            <li style="margin-bottom:12px; font-size:1.12em; background: linear-gradient(90deg, #274472 0%, #1b263b 100%); border-radius: 8px; padding: 10px 0; color:#eaf6ff; box-shadow: 0 2px 8px #0d1b2a33;">
                <span style="color:#7eb6ff; font-weight:600;">Say:</span> <span style="color:#f7b801; font-weight:500;">type hello world</span>
            </li>
            <li style="margin-bottom:12px; font-size:1.12em; background: linear-gradient(90deg, #274472 0%, #1b263b 100%); border-radius: 8px; padding: 10px 0; color:#eaf6ff; box-shadow: 0 2px 8px #0d1b2a33;">
                <span style="color:#7eb6ff; font-weight:600;">Say:</span> <span style="color:#f7b801; font-weight:500;">Open youtube</span>
            </li>
        </ul>
    </div>
</body>
</html>
'''

@app.route("/", methods=["GET"])
def index():
    running = buddy_process is not None and buddy_process.poll() is None
    return render_template_string(HTML, running=running)

@app.route("/start", methods=["POST"])
def start():
    global buddy_process
    if buddy_process is None or buddy_process.poll() is not None:
        buddy_process = subprocess.Popen(["python", "buddy.py"], cwd=os.path.dirname(os.path.abspath(__file__)))
    return redirect(url_for('index'))

@app.route("/stop", methods=["POST"])
def stop():
    global buddy_process
    if buddy_process is not None and buddy_process.poll() is None:
        buddy_process.terminate()
        buddy_process = None
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
