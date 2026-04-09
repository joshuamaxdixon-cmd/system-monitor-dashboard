from flask import Flask, jsonify, request, redirect
import boto3
import time
import os
import json
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

SITE_NAME = "Cloud With Josh"
OWNER_NAME = "Joshua Max-Dixon"
OWNER_TITLE = "Cloud & DevOps Engineer"
OWNER_EMAIL = "Joshuamaxdixon@gmail.com"
GITHUB_PROFILE = "https://github.com/joshuamaxdixon-cmd"
LINKEDIN_PROFILE = "https://www.linkedin.com/in/joshua-max-dixon-6861b01b3"

SYSTEM_MONITOR_REPO = "https://github.com/joshuamaxdixon-cmd/system-monitor-dashboard"
SYSTEM_HEALTH_REPO = "https://github.com/joshuamaxdixon-cmd/system-health-checker.git"
CLOUD_LOG_ANALYZER_REPO = "https://github.com/joshuamaxdixon-cmd/cloud-log-analyzer-python.git"
LOG_FILE_ANALYZER_REPO = "https://github.com/joshuamaxdixon-cmd/log-file-analyzer.git"

_db_initialized = False


def get_projects():
    return [
        {
            "slug": "nexgen-healthcare",
            "title": "NexGEN Healthcare",
            "subtitle": "A multi-role clinical workflow system built to manage patient intake, staff coordination, provider handoffs, and modular product control.",
            "status": "LIVE",
            "status_color": "#22c55e",
            "description": "Workflow-first clinical operations platform built to improve patient intake, staff coordination, and provider handoffs through a structured, state-driven system.",
            "tech_stack": "AWS, EC2, CloudWatch, Python, Flask, SQLAlchemy, Gunicorn, HTML, CSS, JavaScript",
            "github": "https://github.com/joshuamaxdixon-cmd/nexgen-healthcare",
            "project_url": "/projects/nexgen-healthcare",
            "live_url": "https://nexgenhealthapp.com",
            "primary_button_text": "View Live Application",
            "project_highlights": [
                "Canonical Workflow Engine",
                "Multi-Role Dashboards",
                "Internal Visit Messaging",
                "Feature Toggle Control",
                "AWS Deployment",
            ],
            "overview": "NexGEN Healthcare is a workflow-first clinical operations platform built to improve patient intake, staff coordination, and provider handoffs through a structured, state-driven system.",
            "what_makes_it_different": "Unlike a typical CRUD healthcare demo, NexGEN is built around a canonical visit lifecycle and dedicated role-based workspaces for front desk, nurse, provider, admin, and patient portal flows. The system is designed to behave like an operational workflow product, not just a form-based application.",
            "core_systems": [
                {
                    "title": "Canonical Workflow Engine",
                    "body": "A single source of truth for patient movement across the visit lifecycle, ensuring consistent transitions and reliable behavior across all roles.",
                },
                {
                    "title": "Role-Based Workspaces",
                    "body": "Dedicated operational views for front desk, nurse, provider, admin, and patient portal interactions, each tailored to the responsibilities of that role.",
                },
                {
                    "title": "Visit-Linked Messaging",
                    "body": "Internal care coordination tied directly to visit context, combining workflow events and staff communication in a structured visit thread.",
                },
                {
                    "title": "Workflow Hardening",
                    "body": "Protection against stale actions, duplicate submissions, invalid transitions, assignment conflicts, and cross-role misuse.",
                },
                {
                    "title": "Modular Feature Control",
                    "body": "A database-backed feature toggle foundation that allows selected capabilities to be enabled or disabled safely without destabilizing the workflow core.",
                },
            ],
            "demo_flow": "Patient Check-In → Front Desk → Nurse → Provider → Completion",
            "demo_flow_description": "The system is built around a state-driven visit lifecycle that validates handoffs and keeps each role aligned to the correct stage of care.",
            "why_it_matters": "This project demonstrates backend engineering, workflow/system design, cloud deployment, product hardening, and real-world operational thinking. It reflects the kind of architectural work required to build reliable systems, not just isolated app features.",
            "architecture": "NexGEN uses a Flask backend with SQLAlchemy data models and a canonical state-driven workflow layer to manage patient movement across the system. The platform includes hardened route and action validation, internal visit messaging, and database-backed feature governance. It is deployed on AWS EC2 using Gunicorn and production-style service management.",
            "final_status": "NexGEN reached a stable and complete stage for this phase of the product. The workflow was hardened, internal messaging was integrated, modular feature toggles were implemented, and the system was deployed and validated for repeated use.",
            "key_features": [
                "Canonical visit lifecycle management",
                "Role-based operational dashboards",
                "Visit-linked internal messaging",
                "Database-backed feature toggle control",
                "AWS-hosted production-style deployment",
            ]
        },
        {
            "slug": "cloud-monitor",
            "title": "Cloud Monitoring Platform on AWS",
            "subtitle": "Production-style AWS monitoring and infrastructure visibility platform",
            "status": "Live",
            "status_color": "#22c55e",
            "description": "Production-style AWS deployment using EC2, Application Load Balancer, Auto Scaling, CloudWatch, HTTPS, DNS routing, and CI/CD automation.",
            "tech_stack": "AWS, Flask, Gunicorn, CloudWatch, ALB, Auto Scaling, GitHub Actions, Linux, DNS, SSL/TLS",
            "github": SYSTEM_MONITOR_REPO,
            "project_url": "/projects/cloud-monitor",
            "live_url": "/live/cloud-monitor",
            "primary_button_text": "Open Live Dashboard",
            "what_it_does": "Collects and visualizes real-time system metrics, tracks server health states, stores historical logs, exposes API endpoints, and simulates cloud monitoring across multiple server roles.",
            "why_it_matters": "Demonstrates production-style cloud architecture, monitoring, automation, secure deployment, and operational visibility using AWS services and Python.",
            "architecture": "AWS EC2 with Flask and Gunicorn behind an Application Load Balancer, HTTPS-enabled routing, health checks, CloudWatch monitoring, and scaling-ready infrastructure.",
            "key_features": [
                "Live infrastructure monitoring",
                "Historical health records",
                "CloudWatch integration",
                "ALB and HTTPS routing"
            ]
        },
        {
            "slug": "system-health-checker",
            "title": "System Health Checker",
            "subtitle": "Monitoring utility project",
            "status": "Live",
            "status_color": "#22c55e",
            "description": "Python-based monitoring tool that checks CPU, memory, and disk usage and generates a system health summary.",
            "tech_stack": "Python, System Monitoring, Scripting",
            "github": SYSTEM_HEALTH_REPO,
            "project_url": "/projects/system-health-checker",
            "live_url": "https://github.com/joshuamaxdixon-cmd/system-health-checker",
            "primary_button_text": "View Repository",
            "what_it_does": "Checks core system resources and produces a lightweight health report for troubleshooting and infrastructure awareness.",
            "why_it_matters": "Shows practical scripting skills for monitoring and foundational operations workflows used in cloud and DevOps roles.",
            "architecture": "Lightweight Python utility focused on local system inspection, resource analysis, and clear health reporting logic.",
            "key_features": [
                "CPU usage checks",
                "Memory usage checks",
                "Disk usage checks",
                "Simple health summary output"
            ]
        },
        {
            "slug": "cloud-log-analyzer",
            "title": "Cloud Log Analyzer",
            "subtitle": "Log analysis and cloud operations project",
            "status": "Live",
            "status_color": "#22c55e",
            "description": "Python tool for analyzing server logs, detecting warnings and errors, and generating structured cloud operations insights.",
            "tech_stack": "Python, Log Parsing, Infrastructure Analysis",
            "github": CLOUD_LOG_ANALYZER_REPO,
            "project_url": "/projects/cloud-log-analyzer",
            "live_url": "/cloud-log-analyzer",
            "primary_button_text": "View Project",
            "what_it_does": "Parses cloud or server-style logs, extracts useful signal, identifies issues, and summarizes operational events in a readable way.",
            "why_it_matters": "Highlights log analysis and troubleshooting skills that matter in DevOps, cloud operations, and reliability engineering.",
            "architecture": "Python-based log parsing workflow designed to extract operational insights from application and infrastructure logs.",
            "key_features": [
                "Warning and error extraction",
                "Operational event summaries",
                "Readable output for troubleshooting",
                "Log-driven infrastructure insight"
            ]
        },
        {
            "slug": "log-file-analyzer",
            "title": "Log File Analyzer",
            "subtitle": "Foundational log analysis project",
            "status": "Live",
            "status_color": "#22c55e",
            "description": "Foundational Python project for scanning log files, identifying errors, and extracting useful operational information.",
            "tech_stack": "Python, Log Analysis",
            "github": LOG_FILE_ANALYZER_REPO,
            "project_url": "/projects/log-file-analyzer",
            "live_url": "https://github.com/joshuamaxdixon-cmd/log-file-analyzer",
            "primary_button_text": "View Repository",
            "what_it_does": "Analyzes application and system log files to surface errors, warnings, and useful patterns for debugging.",
            "why_it_matters": "Demonstrates strong Python fundamentals and the operational mindset needed for cloud support and DevOps work.",
            "architecture": "Small Python-based log inspection tool focused on parsing files, identifying signal, and surfacing operational patterns.",
            "key_features": [
                "Application log scanning",
                "Error and warning detection",
                "Useful pattern extraction",
                "Foundational Python parsing logic"
            ]
        }
    ]


def get_project_by_slug(slug):
    for project in get_projects():
        if project["slug"] == slug:
            return project
    return None


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
            max-width: 1000px;
            margin: auto;
        }

        .card {
            background: #1e293b;
            padding: 30px;
            border-radius: 18px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.35);
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

        h3 {
            color: #f8fafc;
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
            padding: 18px 22px;
            border-radius: 12px;
            margin-bottom: 16px;
            border: 1px solid rgba(255,255,255,0.06);
            line-height: 1.6;
            font-size: 15px;
            color: #cbd5e1;
        }

        .skill-chip-row {
            margin: 28px 0 24px 0;
            text-align: center;
        }

        .hero {
            text-align: center;
            padding: 16px 0 4px 0;
        }

        .hero h1 {
            font-size: 46px;
            margin-bottom: 12px;
        }

        .hero p {
            color: #cbd5e1;
            font-size: 18px;
            max-width: 780px;
            margin: 0 auto 24px auto;
            line-height: 1.7;
        }

        .hero-buttons {
            display: flex;
            justify-content: center;
            gap: 14px;
            flex-wrap: wrap;
            margin-top: 32px;
        }

        .hero-buttons a,
        .button-link {
            text-decoration: none;
            padding: 12px 18px;
            border-radius: 10px;
            font-weight: bold;
            display: inline-block;
        }

        .btn-primary {
            background: linear-gradient(135deg, #3b82f6, #2563eb);
            border-radius: 10px;
            padding: 10px 18px;
            font-weight: 600;
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

        .btn-ghost {
            background: transparent;
            color: #38bdf8;
            border: 1px solid #334155;
        }

        .btn-ghost:hover {
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

        .project-links {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-top: 16px;
        }

        .status-badge {
            display: inline-block;
            padding: 6px 10px;
            border-radius: 999px;
            font-size: 13px;
            font-weight: bold;
            margin-bottom: 14px;
            color: white;
        }

        .skills-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 14px;
            margin-top: 18px;
        }

        .skill-box {
            display: inline-block;
            margin: 6px 6px;
            padding: 8px 14px;
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 12px;
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

        .project-detail-meta {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 14px;
            margin-top: 22px;
            margin-bottom: 24px;
        }

        .meta-box {
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 16px;
        }

        .meta-box strong {
            display: block;
            margin-bottom: 8px;
            color: #e2e8f0;
        }

        .detail-hero {
            text-align: center;
            padding: 10px 0 4px 0;
        }

        .detail-hero h1 {
            font-size: 44px;
            margin-bottom: 14px;
        }

        .detail-hero .subtitle {
            max-width: 760px;
            margin: 0 auto 26px auto;
            line-height: 1.7;
        }

        .highlight-row {
            display: flex;
            justify-content: center;
            gap: 10px;
            flex-wrap: wrap;
            margin: 8px 0 28px 0;
        }

        .highlight-chip {
            display: inline-flex;
            align-items: center;
            padding: 9px 14px;
            border-radius: 999px;
            background: #0f172a;
            border: 1px solid #334155;
            color: #dbeafe;
            font-size: 14px;
            font-weight: 600;
        }

        .section-panel {
            background: #0f172a;
            padding: 22px 24px;
            border-radius: 14px;
            margin-bottom: 18px;
            border: 1px solid rgba(255,255,255,0.07);
        }

        .section-panel h2 {
            text-align: left;
            margin: 0 0 10px 0;
        }

        .section-panel p {
            margin: 0;
            line-height: 1.75;
            color: #cbd5e1;
        }

        .systems-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 16px;
            margin: 18px 0 6px 0;
        }

        .system-card {
            background: linear-gradient(180deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.95));
            border: 1px solid #334155;
            border-radius: 14px;
            padding: 20px;
        }

        .system-card h3 {
            margin: 0 0 10px 0;
            color: #e2e8f0;
        }

        .system-card p {
            margin: 0;
            color: #cbd5e1;
            line-height: 1.7;
        }

        .flow-panel {
            display: grid;
            grid-template-columns: 1.2fr 1fr;
            gap: 16px;
            margin-bottom: 18px;
        }

        .flow-box {
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 14px;
            padding: 22px 24px;
        }

        .flow-label {
            display: block;
            color: #94a3b8;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 10px;
        }

        .flow-sequence {
            color: #f8fafc;
            font-size: 20px;
            line-height: 1.6;
            font-weight: 700;
        }

        .flow-description {
            color: #cbd5e1;
            line-height: 1.75;
            margin: 0;
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

        a.inline-link {
            color: #38bdf8;
            text-decoration: none;
            font-weight: bold;
        }

        a.inline-link:hover {
            text-decoration: underline;
        }

        @media (max-width: 900px) {
            .summary-grid {
                grid-template-columns: repeat(2, 1fr);
            }

            .flow-panel {
                grid-template-columns: 1fr;
            }

            .hero h1 {
                font-size: 38px;
            }

            .detail-hero h1 {
                font-size: 38px;
            }
        }

        @media (max-width: 600px) {
            .summary-grid {
                grid-template-columns: 1fr;
            }

            .hero h1 {
                font-size: 32px;
            }

            .hero p {
                font-size: 16px;
            }

            .flow-sequence {
                font-size: 18px;
            }
        }
    </style>
    """


def render_nav():
    return f"""
    <div class="top-nav">
        <a href="/">Home</a>
        <a href="/projects">Projects</a>
        <a href="/contact">Contact</a>
        <a href="{GITHUB_PROFILE}" target="_blank">GitHub</a>
        <a href="{LINKEDIN_PROFILE}" target="_blank">LinkedIn</a>
    </div>
    """


def render_live_nav():
    return """
    <div class="top-nav">
        <a href="/">Home</a>
        <a href="/projects">Projects</a>
        <a href="/live/cloud-monitor">Cloud Monitor</a>
        <a href="/history">History</a>
        <a href="/charts">Charts</a>
    </div>
    """


def render_project_card(project):
    return f"""
    <div class="project-card">
        <span class="status-badge" style="background:{project['status_color']};">{project['status']}</span>
        <h3>{project['title']}</h3>
        <p>{project['description']}</p>
        <p><strong>Tech Stack:</strong> {project['tech_stack']}</p>
        <div class="project-links">
            <a class="button-link btn-secondary" href="{project['project_url']}">View Project</a>
            <a class="button-link btn-ghost" href="{project['github']}" target="_blank">GitHub</a>
        </div>
    </div>
    """


def render_project_detail_page(project):
    feature_lines = "".join(f"• {feature}<br>" for feature in project.get("key_features", []))
    skill_chips = "".join(
        f'<span class="skill-box">{skill.strip()}</span>'
        for skill in project["tech_stack"].split(",")
    )
    highlight_chips = "".join(
        f'<span class="highlight-chip">{item}</span>'
        for item in project.get("project_highlights", [])
    )
    core_system_cards = "".join(
        f"""
        <div class="system-card">
            <h3>{system['title']}</h3>
            <p>{system['body']}</p>
        </div>
        """
        for system in project.get("core_systems", [])
    )

    if project.get("core_systems"):
        body = f"""
        {render_nav()}

        <div class="detail-hero">
            <h1>{project['title']}</h1>
            <p class="subtitle">{project.get('subtitle', 'Project detail page')}</p>

            <div style="text-align:center; margin: 18px 0 12px 0;">
                <span class="status-badge" style="background:{project['status_color']};">
                    {project['status']}
                </span>
            </div>

            <div class="highlight-row">
                {highlight_chips}
            </div>
        </div>

        <div class="project-detail-meta">
            <div class="meta-box">
                <strong>Tech Stack</strong>
                {project['tech_stack']}
            </div>
        </div>

        <div class="section-panel">
            <h2>Project Overview</h2>
            <p>{project.get('overview', project['description'])}</p>
        </div>

        <div class="section-panel">
            <h2>What Makes It Different</h2>
            <p>{project.get('what_makes_it_different', project['description'])}</p>
        </div>

        <div class="section-panel">
            <h2>Core Systems</h2>
            <div class="systems-grid">
                {core_system_cards}
            </div>
        </div>

        <div class="flow-panel">
            <div class="flow-box">
                <span class="flow-label">Demo Flow</span>
                <div class="flow-sequence">{project.get('demo_flow', '')}</div>
            </div>
            <div class="flow-box">
                <span class="flow-label">Flow Behavior</span>
                <p class="flow-description">{project.get('demo_flow_description', '')}</p>
            </div>
        </div>

        <div class="section-panel">
            <h2>Architecture / Engineering</h2>
            <p>{project.get('architecture', 'Architecture details coming soon.')}</p>
        </div>

        <div class="section-panel">
            <h2>Why It Matters</h2>
            <p>{project['why_it_matters']}</p>
        </div>

        <div class="section-panel">
            <h2>Final Status</h2>
            <p>{project.get('final_status', '')}</p>
        </div>

        <div class="skill-chip-row">
            {skill_chips}
        </div>

        <div class="hero-buttons">
            <a class="btn-primary" href="{project['live_url']}" target="_blank">{project.get('primary_button_text', 'View Live Application')}</a>
            <a class="btn-secondary" href="{project['github']}" target="_blank">GitHub</a>
            <a class="btn-ghost" href="/projects">Back to Projects</a>
        </div>
        """
        return render_page(f"{SITE_NAME} | {project['title']}", body)

    body = f"""
    {render_nav()}

    <h1>{project['title']}</h1>
    <p class="subtitle">{project.get('subtitle', 'Project detail page')}</p>

    <div style="text-align:center; margin: 18px 0 26px 0;">
        <span class="status-badge" style="background:{project['status_color']};">
            {project['status']}
        </span>
    </div>

    <div class="project-detail-meta">
        <div class="meta-box">
            <strong>Tech Stack</strong>
            {project['tech_stack']}
        </div>
    </div>

    <div class="note-box">
        <strong>Overview:</strong><br>
        {project['description']}
    </div>

    <div class="note-box">
        <strong>What it does:</strong><br>
        {project['what_it_does']}
    </div>

    <div class="note-box">
        <strong>Why it matters:</strong><br>
        {project['why_it_matters']}
    </div>

    <div class="note-box">
        <strong>Architecture:</strong><br>
        {project.get('architecture', 'Architecture details coming soon.')}
    </div>

    <div class="note-box">
        <strong>Key Features:</strong><br>
        {feature_lines}
    </div>

    <div class="skill-chip-row">
        {skill_chips}
    </div>

    <div class="hero-buttons">
        <a class="btn-primary" href="{project['live_url']}" target="_blank">{project.get('primary_button_text', 'View Live Application')}</a>
        <a class="btn-secondary" href="{project['github']}" target="_blank">GitHub</a>
        <a class="btn-ghost" href="/projects">Back to Projects</a>
    </div>
    """

    return render_page(f"{SITE_NAME} | {project['title']}", body)


def render_page(title, body_html):
    return f"""
    <html>
    <head>
        <title>{title}</title>
        {base_styles()}
    </head>
    <body>
        <div class="container">
            <div class="card">
                {body_html}
            </div>
        </div>
    </body>
    </html>
    """


@app.route("/")
def home():
    projects = get_projects()
    featured = projects[0]
    project_cards = "".join(render_project_card(project) for project in projects[1:])

    body = f"""
    {render_nav()}

    <div class="hero">
        <h1>{OWNER_NAME}</h1>
        <p class="subtitle">{OWNER_TITLE}</p>
        <p>
            I build production-minded cloud and backend systems on AWS,
            with a focus on reliable deployment, operational visibility,
            workflow design, and infrastructure-backed application delivery.
        </p>

        <div class="hero-buttons">
            <a class="btn-primary" href="/projects">View Projects</a>
            <a class="btn-secondary" href="{GITHUB_PROFILE}" target="_blank">GitHub</a>
            <a class="btn-secondary" href="{LINKEDIN_PROFILE}" target="_blank">LinkedIn</a>
            <a class="btn-ghost" href="/contact">Contact</a>
        </div>
    </div>

    <div class="note-box">
        <strong>Portfolio Overview.</strong> This site brings together the systems, platform,
        and infrastructure projects I use to demonstrate practical engineering ability across
        AWS deployment, backend application design, monitoring, workflow architecture, and
        production-style operations.
    </div>

    <div class="section">
        <h2 class="section-title">Featured Project</h2>
        <div class="project-grid">
            {render_project_card(featured)}
        </div>
    </div>

    <div class="section">
        <h2 class="section-title">All Projects</h2>
        <div class="project-grid">
            {project_cards}
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

    <div class="section">
        <h2 class="section-title">Contact</h2>
        <div class="note-box">
            Reach me at <a class="inline-link" href="mailto:{OWNER_EMAIL}">{OWNER_EMAIL}</a><br><br>
            <a class="inline-link" href="{GITHUB_PROFILE}" target="_blank">GitHub</a> &nbsp;|&nbsp;
            <a class="inline-link" href="{LINKEDIN_PROFILE}" target="_blank">LinkedIn</a>
        </div>
    </div>

    <div class="footer-note">
        Built to present hands-on systems work across AWS infrastructure, backend engineering,
        deployment pipelines, monitoring, and operational product thinking.
    </div>
    """

    return render_page(f"{SITE_NAME} | {OWNER_NAME}", body)


@app.route("/projects")
def projects_page():
    project_cards = "".join(render_project_card(project) for project in get_projects())

    body = f"""
    {render_nav()}

    <h1>Projects</h1>
    <p class="subtitle">A collection of cloud, monitoring, and automation projects organized under one domain.</p>

    <div class="project-grid">
        {project_cards}
    </div>
    """

    return render_page(f"{SITE_NAME} | Projects", body)


@app.route("/projects/nexgen-healthcare")
def nexgen_project():
    project = get_project_by_slug("nexgen-healthcare")
    return render_project_detail_page(project)


@app.route("/projects/cloud-monitor")
def project_cloud_monitor():
    project = get_project_by_slug("cloud-monitor")
    return render_project_detail_page(project)


@app.route("/projects/system-health-checker")
def project_system_health_checker():
    project = get_project_by_slug("system-health-checker")
    return render_project_detail_page(project)


@app.route("/projects/cloud-log-analyzer")
def project_cloud_log_analyzer():
    project = get_project_by_slug("cloud-log-analyzer")
    return render_project_detail_page(project)


@app.route("/projects/log-file-analyzer")
def project_log_file_analyzer():
    project = get_project_by_slug("log-file-analyzer")
    return render_project_detail_page(project)


@app.route("/contact")
def contact_page():
    body = f"""
    {render_nav()}

    <h1>Contact</h1>
    <p class="subtitle">Let’s connect</p>

    <div class="note-box">
        I’m building cloud and DevOps projects focused on AWS, automation, monitoring,
        secure deployment, and real-world infrastructure. The best way to reach me is by email.
    </div>

    <div class="project-grid">
        <div class="project-card">
            <h3>Email</h3>
            <p><a class="inline-link" href="mailto:{OWNER_EMAIL}">{OWNER_EMAIL}</a></p>
        </div>

        <div class="project-card">
            <h3>GitHub</h3>
            <p><a class="inline-link" href="{GITHUB_PROFILE}" target="_blank">{GITHUB_PROFILE}</a></p>
        </div>

        <div class="project-card">
            <h3>LinkedIn</h3>
            <p><a class="inline-link" href="{LINKEDIN_PROFILE}" target="_blank">{LINKEDIN_PROFILE}</a></p>
        </div>
    </div>
    """

    return render_page(f"{SITE_NAME} | Contact", body)


@app.route("/app")
def app_redirect():
    return redirect("/live/cloud-monitor")


@app.route("/dashboard")
def dashboard_redirect():
    return redirect("/live/cloud-monitor")


@app.route("/live/cloud-monitor")
@with_db_init
def live_cloud_monitor():
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
                {render_live_nav()}

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

    body = f"""
    {render_live_nav()}

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
    """

    return render_page("Monitoring History", body)


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

    body = f"""
    {render_live_nav()}

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

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
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
    """

    return render_page("Monitoring Charts", body)


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
