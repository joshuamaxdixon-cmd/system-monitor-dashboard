from flask import Flask, jsonify
import random
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB_NAME = "monitoring.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS server_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            server_name TEXT NOT NULL,
            cpu REAL NOT NULL,
            memory REAL NOT NULL,
            status TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_server_log(server):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO server_logs (timestamp, server_name, cpu, memory, status)
        VALUES (?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        server["name"],
        server["cpu"],
        server["memory"],
        server["status"]
    ))
    conn.commit()
    conn.close()

def generate_servers():
    servers = [
        {"name": "Web Server"},
        {"name": "Database Server"},
        {"name": "API Server"}
    ]

    results = []

    for server in servers:
        cpu = round(random.uniform(10, 90), 1)
        memory = round(random.uniform(20, 90), 1)

        status = "Healthy"
        color = "green"

        if cpu > 80 or memory > 80:
            status = "Warning"
            color = "orange"
        if cpu > 90 or memory > 90:
            status = "Critical"
            color = "red"

        results.append({
            "name": server["name"],
            "cpu": cpu,
            "memory": memory,
            "status": status,
            "color": color
        })

    return results

@app.route("/")
def dashboard():
    servers = generate_servers()

    for server in servers:
        save_server_log(server)

    server_html = ""

    for server in servers:
        server_html += f"""
        <div style="margin-bottom:15px; padding:10px; border:1px solid #ddd; border-radius:8px;">
            <h3>{server['name']}</h3>
            <p style="color:{server['color']};">
                <strong>CPU:</strong> {server['cpu']}%
                |
                <strong>Memory:</strong> {server['memory']}%
            </p>
            <p><strong>Status:</strong> {server['status']}</p>
        </div>
        """

    return f"""
    <html>
    <head>
        <title>Cloud Monitoring Platform</title>
        <meta http-equiv="refresh" content="5">
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #f4f6f8;
                text-align: center;
                padding: 30px;
            }}
            .card {{
                background: white;
                width: 700px;
                margin: auto;
                padding: 25px;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Cloud Monitoring Platform</h1>
            <h2>Servers</h2>
            {server_html}
            <p><a href="/api/servers">View /api/servers</a></p>
            <p><a href="/api/health">View /api/health</a></p>
            <p><a href="/api/history">View /api/history</a></p>
        </div>
    </body>
    </html>
    """

@app.route("/api/servers")
def api_servers():
    return jsonify(generate_servers())

@app.route("/api/health")
def api_health():
    servers = generate_servers()

    total_servers = len(servers)
    healthy = sum(1 for s in servers if s["status"] == "Healthy")
    warning = sum(1 for s in servers if s["status"] == "Warning")
    critical = sum(1 for s in servers if s["status"] == "Critical")

    return jsonify({
        "total_servers": total_servers,
        "healthy": healthy,
        "warning": warning,
        "critical": critical
    })

@app.route("/api/history")
def api_history():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT timestamp, server_name, cpu, memory, status
        FROM server_logs
        ORDER BY id DESC
        LIMIT 50
    """)
    rows = cursor.fetchall()
    conn.close()

    history = [dict(row) for row in rows]
    return jsonify(history)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)