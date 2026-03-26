from flask import Flask, jsonify, request, redirect
import boto3
import time
import os
import json
import random
import sqlite3
import psutil
from functools import wraps

cloudwatch = boto3.client("cloudwatch", region_name="us-east-2")

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    psycopg2 = None
    RealDictCursor = None

app = Flask(__name__)

SQLITE_DB = "monitoring.db"
DATABASE_URL = os.environ.get("DATABASE_URL")
USING_POSTGRES = bool(DATABASE_URL and psycopg2)

_db_initialized = False


def get_system_metrics():
    return {
        "cpu": round(psutil.cpu_percent(interval=1), 1),
        "memory": round(psutil.virtual_memory().percent, 1)
    }


@app.before_request
def start_timer():
    request.start_time = time.time()


@app.after_request
def log_metrics(response):
    try:
        if hasattr(request, "start_time"):
            latency = time.time() - request.start_time

            cloudwatch.put_metric_data(
                Namespace="MyApp",
                MetricData=[
                    {
                        "MetricName": "RequestCount",
                        "Value": 1,
                        "Unit": "Count"
                    },
                    {
                        "MetricName": "ResponseTime",
                        "Value": latency,
                        "Unit": "Seconds"
                    }
                ]
            )
    except Exception as e:
        print(f"CloudWatch metric error: {e}")

    return response


def get_db_connection():
    if USING_POSTGRES:
        return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

    conn = sqlite3.connect(SQLITE_DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    global _db_initialized
    if _db_initialized:
        return

    conn = get_db_connection()
    cur = conn.cursor()

    if USING_POSTGRES:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS server_logs (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                server_name TEXT NOT NULL,
                cpu FLOAT NOT NULL,
                memory FLOAT NOT NULL,
                status TEXT NOT NULL
            )
        """)
    else:
        cur.execute("""
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
    cur.close()
    conn.close()
    _db_initialized = True


def with_db_init(route_func):
    @wraps(route_func)
    def wrapper(*args, **kwargs):
        init_db()
        return route_func(*args, **kwargs)
    return wrapper


def save_server_log(server):
    conn = get_db_connection()
    cur = conn.cursor()

    if USING_POSTGRES:
        cur.execute("""
            INSERT INTO server_logs (server_name, cpu, memory, status)
            VALUES (%s, %s, %s, %s)
        """, (
            server["name"],
            server["cpu"],
            server["memory"],
            server["status"]
        ))
    else:
        cur.execute("""
            INSERT INTO server_logs (timestamp, server_name, cpu, memory, status)
            VALUES (datetime('now'), ?, ?, ?, ?)
        """, (
            server["name"],
            server["cpu"],
            server["memory"],
            server["status"]
        ))

    conn.commit()
    cur.close()
    conn.close()


def generate_servers():
    servers = [
        {"name": "Web Server", "role": "Handles frontend traffic and user requests."},
        {"name": "Database Server", "role": "Stores and serves application data."},
        {"name": "API Server", "role": "Processes backend logic and integrations."}
    ]

    results = []

    for server in servers:
        metrics = get_system_metrics()

        cpu = metrics["cpu"]
        memory = metrics["memory"]

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


def get_history(limit=50, server_name=None, status=None):
    conn = get_db_connection()
    cur = conn.cursor()

    if USING_POSTGRES:
        query = """
            SELECT timestamp, server_name, cpu, memory, status
            FROM server_logs
            WHERE 1=1
        """
        params = []

        if server_name:
            query += " AND server_name = %s"
            params.append(server_name)

        if status:
            query += " AND status = %s"
            params.append(status)

        query += " ORDER BY id DESC LIMIT %s"
        params.append(limit)

        cur.execute(query, params)
        rows = cur.fetchall()
        result = [dict(row) for row in rows]
    else:
        query = """
            SELECT timestamp, server_name, cpu, memory, status
            FROM server_logs
            WHERE 1=1
        """
        params = []

        if server_name:
            query += " AND server_name = ?"
            params.append(server_name)

        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)

        cur.execute(query, params)
        rows = cur.fetchall()
        result = [dict(row) for row in rows]

    cur.close()
    conn.close()
    return result


def get_summary():
    history = get_history(limit=200)
    if not history:
        return {
            "total_records": 0,
            "healthy": 0,
            "warning": 0,
            "critical": 0
        }

    return {
        "total_records": len(history),
        "healthy": sum(1 for row in history if row["status"] == "Healthy"),
        "warning": sum(1 for row in history if row["status"] == "Warning"),
        "critical": sum(1 for row in history if row["status"] == "Critical")
    }


def get_alerts(servers):
    alerts = []
    for server in servers:
        if server["cpu"] > 90:
            alerts.append(f"🚨 {server['name']} CPU is critical at {server['cpu']}%")
        elif server["cpu"] > 80:
            alerts.append(f"⚠️ {server['name']} CPU is high at {server['cpu']}%")

        if server["memory"] > 90:
            alerts.append(f"🚨 {server['name']} memory is critical at {server['memory']}%")
        elif server["memory"] > 80:
            alerts.append(f"⚠️ {server['name']} memory is high at {server['memory']}%")
    return alerts


def base_styles():
    return """
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #0f172a, #1e293b);
            color: white;
            margin: 0;
            padding: 30px;
        }

        .container {
            max-width: 1150px;
            margin: auto;
        }

        .card {
            background: #1e293b;
            padding: 30px;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.35);
        }

        h1 {
            color: #38bdf8;
            margin-bottom: 10px;
            text-align: center;
        }

        h2 {
            margin-top: 30px;
            color: #e2e8f0;
            text-align: center;
        }

        .subtitle {
            color: #94a3b8;
            text-align: center;
            margin-bottom: 30px;
        }

        .top-nav {
            text-align: center;
            margin-bottom: 25px;
        }

        .top-nav a {
            display: inline-block;
            margin: 6px 10px;
            color: #38bdf8;
            text-decoration: none;
            font-weight: bold;
        }

        .top-nav a:hover {
            text-decoration: underline;
        }

        .note-box {
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 18px;
            margin-bottom: 24px;
            color: #cbd5e1;
            line-height: 1.6;
        }

        .summary-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 25px;
        }

        .summary-card {
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 18px;
            text-align: center;
        }

        .summary-card h3 {
            margin: 0 0 8px 0;
            color: #94a3b8;
            font-size: 15px;
        }

        .summary-card p {
            margin: 0;
            font-size: 28px;
            font-weight: bold;
        }

        .alerts-box {
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 18px;
            margin-bottom: 24px;
            color: #e2e8f0;
        }

        .alerts-box ul {
            margin: 12px 0 0 20px;
            text-align: left;
        }

        .server {
            background: #0f172a;
            margin: 16px 0;
            padding: 18px;
            border-radius: 12px;
            border: 1px solid #334155;
            text-align: center;
        }

        .server h3 {
            margin-bottom: 8px;
            color: #f8fafc;
        }

        .role {
            color: #94a3b8;
            margin-bottom: 12px;
        }

        .legend {
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 18px;
            margin-top: 24px;
            color: #cbd5e1;
            line-height: 1.7;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            background: #0f172a;
            border-radius: 12px;
            overflow: hidden;
        }

        th, td {
            padding: 12px;
            border-bottom: 1px solid #334155;
            text-align: center;
        }

        th {
            background: #111827;
            color: #e2e8f0;
        }

        tr:hover {
            background: #1f2937;
        }

        .filter-box {
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 18px;
            margin-bottom: 20px;
            text-align: center;
        }

        .filter-box label {
            margin-right: 8px;
            color: #cbd5e1;
            font-weight: bold;
        }

        .filter-box select,
        .filter-box input,
        .filter-box button {
            margin: 6px;
            padding: 10px 12px;
            border-radius: 8px;
            border: 1px solid #334155;
            background: #111827;
            color: white;
        }

        .filter-box button {
            cursor: pointer;
            background: #2563eb;
            border: none;
            font-weight: bold;
        }

        .filter-box button:hover {
            background: #1d4ed8;
        }

        .chart-box {
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 20px;
            margin-top: 24px;
        }

        .muted {
            color: #94a3b8;
        }

        .hero {
            text-align: center;
            padding: 20px 0 10px 0;
        }

        .hero h1 {
            font-size: 44px;
            margin-bottom: 12px;
        }

        .hero p {
            color: #cbd5e1;
            font-size: 18px;
            max-width: 760px;
            margin: 0 auto 24px auto;
            line-height: 1.7;
        }

        .hero-buttons {
            display: flex;
            justify-content: center;
            gap: 14px;
            flex-wrap: wrap;
            margin-bottom: 30px;
        }

        .hero-buttons a {
            text-decoration: none;
            padding: 12px 18px;
            border-radius: 10px;
            font-weight: bold;
            display: inline-block;
        }

        .btn-primary {
            background: #2563eb;
            color: white;
        }

        .btn-primary:hover {
            background: #1d4ed8;
        }

        .btn-secondary {
            background: #0f172a;
            color: #38bdf8;
            border: 1px solid #334155;
        }

        .btn-secondary:hover {
            background: #111827;
        }

        .section {
            margin-top: 28px;
        }

        .section-title {
            text-align: center;
            color: #e2e8f0;
            margin-bottom: 16px;
        }

        .project-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 18px;
            margin-top: 18px;
        }

        .project-card {
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 14px;
            padding: 20px;
        }

        .project-card h3 {
            margin-top: 0;
            color: #f8fafc;
        }

        .project-card p {
            color: #cbd5e1;
            line-height: 1.6;
        }

        .project-card a {
            color: #38bdf8;
            text-decoration: none;
            font-weight: bold;
        }

        .project-card a:hover {
            text-decoration: underline;
        }

        .skills-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 14px;
            margin-top: 18px;
        }

        .skill-box {
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 16px;
            text-align: center;
            color: #e2e8f0;
            font-weight: bold;
        }

        .footer-note {
            text-align: center;
            color: #94a3b8;
            margin-top: 28px;
            line-height: 1.7;
        }

        @media (max-width: 900px) {
            .summary-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }

        @media (max-width: 600px) {
            .summary-grid {
                grid-template-columns: 1fr;
            }

            .hero h1 {
                font-size: 34px;
            }

            .hero p {
                font-size: 16px;
            }
        }
    </style>
    """


@app.route("/")
def home():
    return f"""
    <html>
    <head>
        <title>Cloud With Josh | AWS Cloud & DevOps Portfolio</title>
        {base_styles()}
    </head>
    <body>
        <div class="container">
            <div class="card">
                <div class="top-nav">
                    <a href="/">Home</a>
                    <a href="/projects/cloud-monitor">Cloud Monitor</a>
                    <a href="/history">History</a>
                    <a href="/charts">Charts</a>
                </div>

                <div class="hero">
                    <h1>Josh | Cloud & DevOps Engineer</h1>
                    <p>
                        I build production-style cloud systems on AWS with scalable infrastructure,
                        monitoring, automation, and secure public deployments.
                    </p>

                    <div class="hero-buttons">
                        <a class="btn-primary" href="/projects/cloud-monitor">View Live Project</a>
                        <a class="btn-secondary" href="https://github.com" target="_blank">GitHub</a>
                        <a class="btn-secondary" href="https://www.linkedin.com" target="_blank">LinkedIn</a>
                    </div>
                </div>

                <div class="note-box">
                    <strong>About this site:</strong> This domain is my personal portfolio hub. Each project
                    lives under one main brand so recruiters and hiring managers can explore my work from a
                    single place.
                </div>

                <div class="section">
                    <h2 class="section-title">Featured Project</h2>

                    <div class="project-grid">
                        <div class="project-card">
                            <h3>Cloud Monitoring Platform on AWS</h3>
                            <p>
                                A production-style AWS deployment using EC2, Application Load Balancer,
                                Auto Scaling, CloudWatch metrics and alarms, custom domain routing, HTTPS,
                                and CI/CD automation.
                            </p>
                            <p><strong>Tech:</strong> AWS, Flask, Gunicorn, CloudWatch, ALB, Auto Scaling, GitHub Actions</p>
                            <a href="/projects/cloud-monitor">Open Project →</a>
                        </div>
                    </div>
                </div>

                <div class="section">
                    <h2 class="section-title">Upcoming Projects</h2>

                    <div class="project-grid">
                        <div class="project-card">
                            <h3>DevSecOps Pipeline</h3>
                            <p>
                                CI/CD pipeline with infrastructure automation, containerization, and security checks.
                            </p>
                            <a href="#">Coming soon</a>
                        </div>

                        <div class="project-card">
                            <h3>Terraform Infrastructure</h3>
                            <p>
                                Infrastructure as Code project for repeatable AWS environments and deployment workflows.
                            </p>
                            <a href="#">Coming soon</a>
                        </div>

                        <div class="project-card">
                            <h3>Cloud Operations Toolkit</h3>
                            <p>
                                Monitoring, troubleshooting, and operational automation tools for AWS workloads.
                            </p>
                            <a href="#">Coming soon</a>
                        </div>
                    </div>
                </div>

                <div class="section">
                    <h2 class="section-title">Core Skills</h2>

                    <div class="skills-grid">
                        <div class="skill-box">AWS EC2</div>
                        <div class="skill-box">Load Balancing</div>
                        <div class="skill-box">Auto Scaling</div>
                        <div class="skill-box">CloudWatch</div>
                        <div class="skill-box">CI/CD</div>
                        <div class="skill-box">Python / Flask</div>
                        <div class="skill-box">Linux</div>
                        <div class="skill-box">DNS / HTTPS</div>
                    </div>
                </div>

                <div class="footer-note">
                    Built to showcase real-world cloud engineering work, hands-on AWS architecture,
                    and deployment skills in a single portfolio hub.
                </div>
            </div>
        </div>
    </body>
    </html>
    """


@app.route("/projects/cloud-monitor")
@app.route("/app")
@with_db_init
def dashboard():
    servers = generate_servers()

    for server in servers:
        save_server_log(server)

    summary = get_summary()
    alerts = get_alerts(servers)

    server_html = ""
    for server in servers:
        server_html += f"""
        <div class="server">
            <h3>{server['name']}</h3>
            <p class="role">{server['role']}</p>
            <p style="color:{server['color']}; font-size:22px; font-weight:bold;">
                CPU: {server['cpu']}% &nbsp; | &nbsp; Memory: {server['memory']}%
            </p>
            <p><strong>Status:</strong> {server['status']}</p>
        </div>
        """

    if alerts:
        alerts_html = "<ul>" + "".join(f"<li>{a}</li>" for a in alerts) + "</ul>"
    else:
        alerts_html = "<p class='muted'>No active alerts right now.</p>"

    db_label = "PostgreSQL" if USING_POSTGRES else "SQLite"

    return f"""
    <html>
    <head>
        <meta http-equiv="refresh" content="2">
        <title>Cloud Monitoring Platform</title>
        {base_styles()}
    </head>
    <body>
        <div class="container">
            <div class="card">
                <div class="top-nav">
                    <a href="/">Home</a>
                    <a href="/projects/cloud-monitor">Dashboard</a>
                    <a href="/history">History</a>
                    <a href="/charts">Charts</a>
                    <a href="/api/servers" target="_blank">API Servers</a>
                    <a href="/api/health" target="_blank">API Health</a>
                    <a href="/api/history" target="_blank">API History</a>
                </div>

                <h1>Cloud Monitoring Platform</h1>
                <p class="subtitle">Real-time monitoring of distributed cloud infrastructure</p>

                <div class="note-box">
                    <strong>Overview:</strong> This dashboard simulates a cloud monitoring platform that tracks CPU
                    and memory usage across multiple servers, assigns health status levels, stores historical
                    monitoring records in {db_label}, and exposes API endpoints for system data retrieval.
                </div>

                <div class="summary-grid">
                    <div class="summary-card">
                        <h3>Total Records</h3>
                        <p>{summary['total_records']}</p>
                    </div>
                    <div class="summary-card">
                        <h3>Healthy</h3>
                        <p style="color:#22c55e;">{summary['healthy']}</p>
                    </div>
                    <div class="summary-card">
                        <h3>Warning</h3>
                        <p style="color:#f59e0b;">{summary['warning']}</p>
                    </div>
                    <div class="summary-card">
                        <h3>Critical</h3>
                        <p style="color:#ef4444;">{summary['critical']}</p>
                    </div>
                </div>

                <div class="alerts-box">
                    <h2 style="margin-top:0;">Active Alerts</h2>
                    {alerts_html}
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
                    /api/servers → current server metrics<br>
                    /api/health → environment health summary<br>
                    /api/history → stored historical monitoring logs
                </div>
            </div>
        </div>
    </body>
    </html>
    """


@app.route("/history")
@with_db_init
def history_page():
    server_name = request.args.get("server")
    status = request.args.get("status")
    limit = request.args.get("limit", default=50, type=int)

    history = get_history(limit=limit, server_name=server_name, status=status)

    rows_html = ""
    for row in history:
        status_color = "#22c55e"
        if row["status"] == "Warning":
            status_color = "#f59e0b"
        elif row["status"] == "Critical":
            status_color = "#ef4444"

        rows_html += f"""
        <tr>
            <td>{row['timestamp']}</td>
            <td>{row['server_name']}</td>
            <td>{row['cpu']}%</td>
            <td>{row['memory']}%</td>
            <td style="color:{status_color}; font-weight:bold;">{row['status']}</td>
        </tr>
        """

    return f"""
    <html>
    <head>
        <title>Monitoring History</title>
        {base_styles()}
    </head>
    <body>
        <div class="container">
            <div class="card">
                <div class="top-nav">
                    <a href="/">Home</a>
                    <a href="/projects/cloud-monitor">Dashboard</a>
                    <a href="/history">History</a>
                    <a href="/charts">Charts</a>
                </div>

                <h1>Monitoring History</h1>
                <p class="subtitle">Stored monitoring records from the database</p>

                <div class="filter-box">
                    <form method="GET" action="/history">
                        <label for="server">Server</label>
                        <select name="server" id="server">
                            <option value="">All</option>
                            <option value="Web Server" {"selected" if server_name == "Web Server" else ""}>Web Server</option>
                            <option value="Database Server" {"selected" if server_name == "Database Server" else ""}>Database Server</option>
                            <option value="API Server" {"selected" if server_name == "API Server" else ""}>API Server</option>
                        </select>

                        <label for="status">Status</label>
                        <select name="status" id="status">
                            <option value="">All</option>
                            <option value="Healthy" {"selected" if status == "Healthy" else ""}>Healthy</option>
                            <option value="Warning" {"selected" if status == "Warning" else ""}>Warning</option>
                            <option value="Critical" {"selected" if status == "Critical" else ""}>Critical</option>
                        </select>

                        <label for="limit">Limit</label>
                        <input type="number" name="limit" id="limit" value="{limit}" min="1" max="200">

                        <button type="submit">Apply Filters</button>
                    </form>
                </div>

                <table>
                    <thead>
                        <tr>
                            <th>Timestamp</th>
                            <th>Server</th>
                            <th>CPU</th>
                            <th>Memory</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    """


@app.route("/charts")
@with_db_init
def charts_page():
    history = get_history(60)
    history = list(reversed(history))

    labels = [str(row["timestamp"]) for row in history]
    cpu_values = [row["cpu"] for row in history]
    memory_values = [row["memory"] for row in history]

    web_cpu = [row["cpu"] for row in history if row["server_name"] == "Web Server"]
    web_mem = [row["memory"] for row in history if row["server_name"] == "Web Server"]

    db_cpu = [row["cpu"] for row in history if row["server_name"] == "Database Server"]
    db_mem = [row["memory"] for row in history if row["server_name"] == "Database Server"]

    api_cpu = [row["cpu"] for row in history if row["server_name"] == "API Server"]
    api_mem = [row["memory"] for row in history if row["server_name"] == "API Server"]

    web_labels = [str(row["timestamp"]) for row in history if row["server_name"] == "Web Server"]
    db_labels = [str(row["timestamp"]) for row in history if row["server_name"] == "Database Server"]
    api_labels = [str(row["timestamp"]) for row in history if row["server_name"] == "API Server"]

    return f"""
    <html>
    <head>
        <title>Monitoring Charts</title>
        {base_styles()}
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>
        <div class="container">
            <div class="card">
                <div class="top-nav">
                    <a href="/">Home</a>
                    <a href="/projects/cloud-monitor">Dashboard</a>
                    <a href="/history">History</a>
                    <a href="/charts">Charts</a>
                </div>

                <h1>Monitoring Charts</h1>
                <p class="subtitle">CPU and Memory trends from stored monitoring records</p>

                <div class="chart-box">
                    <h2>Overall CPU Usage</h2>
                    <canvas id="cpuChart"></canvas>
                </div>

                <div class="chart-box">
                    <h2>Overall Memory Usage</h2>
                    <canvas id="memoryChart"></canvas>
                </div>

                <div class="chart-box">
                    <h2>Web Server Trends</h2>
                    <canvas id="webChart"></canvas>
                </div>

                <div class="chart-box">
                    <h2>Database Server Trends</h2>
                    <canvas id="dbChart"></canvas>
                </div>

                <div class="chart-box">
                    <h2>API Server Trends</h2>
                    <canvas id="apiChart"></canvas>
                </div>
            </div>
        </div>

        <script>
            const labels = {json.dumps(labels)};
            const cpuData = {json.dumps(cpu_values)};
            const memoryData = {json.dumps(memory_values)};

            const webLabels = {json.dumps(web_labels)};
            const webCpu = {json.dumps(web_cpu)};
            const webMem = {json.dumps(web_mem)};

            const dbLabels = {json.dumps(db_labels)};
            const dbCpu = {json.dumps(db_cpu)};
            const dbMem = {json.dumps(db_mem)};

            const apiLabels = {json.dumps(api_labels)};
            const apiCpu = {json.dumps(api_cpu)};
            const apiMem = {json.dumps(api_mem)};

            const sharedOptions = {{
                responsive: true,
                plugins: {{
                    legend: {{
                        labels: {{ color: 'white' }}
                    }}
                }},
                scales: {{
                    x: {{
                        ticks: {{ color: 'white' }}
                    }},
                    y: {{
                        ticks: {{ color: 'white' }},
                        beginAtZero: true
                    }}
                }}
            }};

            new Chart(document.getElementById('cpuChart'), {{
                type: 'line',
                data: {{
                    labels: labels,
                    datasets: [{{
                        label: 'CPU %',
                        data: cpuData,
                        borderColor: '#38bdf8',
                        backgroundColor: 'rgba(56, 189, 248, 0.2)',
                        tension: 0.3,
                        fill: true
                    }}]
                }},
                options: sharedOptions
            }});

            new Chart(document.getElementById('memoryChart'), {{
                type: 'line',
                data: {{
                    labels: labels,
                    datasets: [{{
                        label: 'Memory %',
                        data: memoryData,
                        borderColor: '#22c55e',
                        backgroundColor: 'rgba(34, 197, 94, 0.2)',
                        tension: 0.3,
                        fill: true
                    }}]
                }},
                options: sharedOptions
            }});

            new Chart(document.getElementById('webChart'), {{
                type: 'line',
                data: {{
                    labels: webLabels,
                    datasets: [
                        {{
                            label: 'Web CPU %',
                            data: webCpu,
                            borderColor: '#60a5fa',
                            backgroundColor: 'rgba(96, 165, 250, 0.15)',
                            tension: 0.3,
                            fill: true
                        }},
                        {{
                            label: 'Web Memory %',
                            data: webMem,
                            borderColor: '#34d399',
                            backgroundColor: 'rgba(52, 211, 153, 0.15)',
                            tension: 0.3,
                            fill: true
                        }}
                    ]
                }},
                options: sharedOptions
            }});

            new Chart(document.getElementById('dbChart'), {{
                type: 'line',
                data: {{
                    labels: dbLabels,
                    datasets: [
                        {{
                            label: 'DB CPU %',
                            data: dbCpu,
                            borderColor: '#f59e0b',
                            backgroundColor: 'rgba(245, 158, 11, 0.15)',
                            tension: 0.3,
                            fill: true
                        }},
                        {{
                            label: 'DB Memory %',
                            data: dbMem,
                            borderColor: '#f472b6',
                            backgroundColor: 'rgba(244, 114, 182, 0.15)',
                            tension: 0.3,
                            fill: true
                        }}
                    ]
                }},
                options: sharedOptions
            }});

            new Chart(document.getElementById('apiChart'), {{
                type: 'line',
                data: {{
                    labels: apiLabels,
                    datasets: [
                        {{
                            label: 'API CPU %',
                            data: apiCpu,
                            borderColor: '#a78bfa',
                            backgroundColor: 'rgba(167, 139, 250, 0.15)',
                            tension: 0.3,
                            fill: true
                        }},
                        {{
                            label: 'API Memory %',
                            data: apiMem,
                            borderColor: '#fb7185',
                            backgroundColor: 'rgba(251, 113, 133, 0.15)',
                            tension: 0.3,
                            fill: true
                        }}
                    ]
                }},
                options: sharedOptions
            }});
        </script>
    </body>
    </html>
    """


@app.route("/api/servers")
@with_db_init
def api_servers():
    return jsonify(generate_servers())


@app.route("/api/health")
@with_db_init
def api_health():
    servers = generate_servers()

    total_servers = len(servers)
    healthy = sum(1 for s in servers if s["status"] == "Healthy")
    warning = sum(1 for s in servers if s["status"] == "Warning")
    critical = sum(1 for s in servers if s["status"] == "Critical")

    return jsonify({
        "database": "postgres" if USING_POSTGRES else "sqlite",
        "total_servers": total_servers,
        "healthy": healthy,
        "warning": warning,
        "critical": critical
    })


@app.route("/api/history")
@with_db_init
def api_history():
    server_name = request.args.get("server")
    status = request.args.get("status")
    limit = request.args.get("limit", default=50, type=int)

    return jsonify(get_history(limit=limit, server_name=server_name, status=status))


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)