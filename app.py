from flask import Flask
import random

app = Flask(__name__)

@app.route("/")
def dashboard():
    servers = [
        {"name": "Web Server"},
        {"name": "Database Server"},
        {"name": "API Server"},
    ]

    server_html = ""

    for server in servers:
        cpu = round(random.uniform(10, 90), 1)
        memory = round(random.uniform(20, 90), 1)

        status = "Healthy"
        color = "green"

        if cpu > 80 or memory > 80:
            status = "Warning"
            color = "orange"
        if cpu > 90:
            status = "Critical"
            color = "red"

        server_html += f"""
        <div style="margin-bottom:15px;">
            <h3>{server['name']}</h3>
            <p style="color:{color}">CPU: {cpu}% | Memory: {memory}%</p>
            <p>Status: {status}</p>
        </div>
        """

    return f"""
    <html>
    <head>
        <title>Cloud Monitoring Platform</title>
        <meta http-equiv="refresh" content="5">
        <style>
            body {{ font-family: Arial; background:#f4f6f8; text-align:center; }}
            .card {{
                background:white;
                width:600px;
                margin:auto;
                padding:25px;
                border-radius:12px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Cloud Monitoring Platform</h1>
            <h2>Servers</h2>
            {server_html}
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)