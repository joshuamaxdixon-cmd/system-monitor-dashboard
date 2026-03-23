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
        {"name": "Web Server", "role": "Handles frontend traffic and user requests."},
        {"name": "Database Server", "role": "Stores and serves application data."},
        {"name": "API Server", "role": "Processes backend logic and integrations."}
    ]

    results = []

    for server in servers:
        cpu = round(random.uniform(10, 95), 1)
        memory = round(random.uniform(20, 95), 1)

        status = "Healthy"
        color = "#22c55e"

        if cpu > 80 or memory > 80:
            status = "Warning"
            color = "#f59e0b"
        if cpu > 90 or memory > 90:
            status = "Critical"
            color = "#ef4444"

        results.append({
            "name": server["name"],
            "role": server["role"],
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
        <div class="server">
            <h3>{server['name']}</h3>
            <p class="role">{server['role']}</p>
            <p style="color:{server['color']};">
                <strong>CPU:</strong> {server['cpu']}%
                &nbsp; | &nbsp;
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
                background: linear-gradient(135deg, #0f172a, #1e293b);
                color: white;
                margin: 0;
                padding: 30px;
            }}

            .container {{
                max-width: 950px;
                margin: auto;
            }}

            .card {{
                background: #1e293b;
                padding: 30px;
                border-radius: 16px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.35);
            }}

            h1 {{
                color: #38bdf8;
                margin-bottom: 10px;
                text-align: center;
            }}

            h2 {{
                margin-top: 30px;
                color: #e2e8f0;
                text-align: center;
            }}

            .subtitle {{
                color: #94a3b8;
                text-align: center;
                margin-bottom: 30px;
            }}

            .note-box {{
                background: #0f172a;
                border: 1px solid #334155;
                border-radius: 12px;
                padding: 18px;
                margin-bottom: 24px;
                color: #cbd5e1;
                line-height: 1.6;
            }}

            .server {{
                background: #0f172a;
                margin: 16px 0;
                padding: 18px;
                border-radius: 12px;
                border: 1px solid #334155;
                text-align: center;
            }}

            .server h3 {{
                margin-bottom: 8px;
                color: #f8fafc;
            }}

            .role {{
                color: #94a3b8;
                margin-bottom: 12px;
            }}

            .links {{
                margin-top: 28px;
                text-align: center;
            }}

            .links a {{
                display: inline-block;
                margin: 8px 10px;
                color: #38bdf8;
                text-decoration: none;
                font-weight: bold;
            }}

            .links a:hover {{
                text-decoration: underline;
            }}

            .legend {{
                background: #0f172a;
                border: 1px solid #334155;
                border-radius: 12px;
                padding: 18px;
                margin-top: 24px;
                color: #cbd5e1;
                line-height: 1.7;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="card">
                <h1>Cloud Monitoring Platform</h1>
                <p class="subtitle">Real-time monitoring of distributed cloud infrastructure</p>

                <div class="note-box">
                    <strong>Overview:</strong> This dashboard simulates a cloud monitoring platform that tracks
                    CPU and memory usage across multiple servers, assigns health status levels, and stores
                    historical monitoring data in a SQLite database for later analysis.
                </div>

                <h2>Servers</h2>
                {server_html}

                <div class="legend">
                    <strong>Status Guide</strong><br>
                    Healthy = operating within safe thresholds<br>
                    Warning = approaching resource limits<br>
                    Critical = system at risk and may require immediate action
                    <br><br>
                    <strong>API Endpoints</strong><br>
                    /api/servers → returns current server metrics<br>
                    /api/health → returns environment health summary<br>
                    /api/history → returns stored historical server logs
                </div>

                <div class="links">
                    <a href="/api/servers" target="_blank">View /api/servers</a>
                    <a href="/api/health" target="_blank">View /api/health</a>
                    <a href="/api/history" target="_blank">View /api/history</a>
                </div>
            </div>
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