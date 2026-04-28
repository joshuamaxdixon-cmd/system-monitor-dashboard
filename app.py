from flask import Flask, jsonify, request, redirect, render_template
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


def portfolio_template_context(page_title):
    return {
        "page_title": page_title,
        "base_styles": base_styles(),
        "site_name": SITE_NAME,
        "owner_name": OWNER_NAME,
        "owner_title": OWNER_TITLE,
        "owner_email": OWNER_EMAIL,
        "github_profile": GITHUB_PROFILE,
        "linkedin_profile": LINKEDIN_PROFILE,
        "nav_links": [
            {"href": "/", "label": "Home"},
            {"href": "/projects", "label": "Projects"},
            {"href": "/contact", "label": "Contact"},
            {"href": GITHUB_PROFILE, "label": "GitHub", "target": "_blank"},
            {"href": LINKEDIN_PROFILE, "label": "LinkedIn", "target": "_blank"},
        ],
    }


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
            "architecture_intro": "NexGEN is structured as a workflow-first application stack where the Flask backend, canonical visit lifecycle, role-based workspaces, and deployment controls operate as one coordinated system.",
            "architecture_layers": [
                {
                    "title": "Application Layer",
                    "items": [
                        "Flask application backend",
                        "Gunicorn application server",
                        "Role-based UI/workspace flows",
                        "Patient, provider, and staff profile views",
                    ],
                },
                {
                    "title": "Workflow Layer",
                    "items": [
                        "Canonical visit lifecycle / state engine",
                        "Front desk, nurse, provider, admin, and patient portal workspace routing",
                        "Internal visit-linked care coordination messaging",
                        "Feature-toggle / product control layer",
                    ],
                },
                {
                    "title": "Deployment Layer",
                    "items": [
                        "AWS EC2 hosting",
                        "GitHub Actions deployment pipeline",
                        "systemd-managed service lifecycle",
                        "Flask + Gunicorn production-style serving stack",
                    ],
                },
                {
                    "title": "Operational Controls",
                    "items": [
                        "Deployment verification",
                        "Restart and recovery handling",
                        "Controlled release changes",
                        "Troubleshooting-oriented workflow",
                    ],
                },
            ],
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
            "slug": "age-evolution",
            "title": "Age Evolution — Production Frontend Infrastructure",
            "subtitle": "Live AWS-hosted landing page infrastructure with secure HTTPS and integrated waitlist capture.",
            "status": "LIVE",
            "status_color": "#22c55e",
            "description": "Built and deployed a production-grade frontend infrastructure on AWS for the Age Evolution platform.",
            "tech_stack": "Amazon S3, Amazon CloudFront, Amazon Route 53, AWS Certificate Manager (ACM), Formspree",
            "github": None,
            "project_url": "/projects/age-evolution",
            "live_url": "https://ageevolutionhq.com",
            "primary_button_text": "Live Site",
            "project_highlights": [
                "Static Hosting on S3",
                "CloudFront CDN Delivery",
                "Route 53 DNS Routing",
                "HTTPS with ACM",
                "Waitlist Capture Flow",
            ],
            "overview": "Age Evolution is a production frontend infrastructure build focused on reliable content delivery, secure HTTPS, and a working waitlist capture path without a custom backend.",
            "what_makes_it_different": "Instead of treating the landing page as a simple static upload, the project was built as a real deployment stack with custom domain routing, CDN-backed delivery, TLS configuration, and user capture wired end-to-end.",
            "core_systems": [
                {
                    "title": "Static Delivery Layer",
                    "body": "Amazon S3 serves the frontend as a production-ready static site with a clean deployment target for the landing page.",
                },
                {
                    "title": "Global CDN Distribution",
                    "body": "Amazon CloudFront distributes the site through a CDN layer so the landing page is delivered through a real edge-backed frontend path.",
                },
                {
                    "title": "Domain and HTTPS Control",
                    "body": "Amazon Route 53 and AWS Certificate Manager handle domain routing, TLS certificate management, and secure HTTPS access.",
                },
                {
                    "title": "Waitlist Capture Workflow",
                    "body": "Formspree powers a serverless waitlist flow with successful submission handling so user capture works without a custom backend service.",
                },
                {
                    "title": "Production Frontend Operations",
                    "body": "The stack was validated as a live deployment path with end-to-end checks across domain resolution, HTTPS, and form submission behavior.",
                },
            ],
            "demo_flow": "Visitor → Landing Page → Waitlist Form → Submission Handling → Captured Lead",
            "demo_flow_description": "The landing page is designed to take a visitor from first load through secure form submission with a validated waitlist capture path.",
            "architecture_intro": "Age Evolution is structured as a production frontend delivery stack where static hosting, CDN distribution, DNS, HTTPS, and waitlist capture work together as one deployment path.",
            "architecture_layers": [
                {
                    "title": "Application Layer",
                    "items": [
                        "Static landing page frontend",
                        "Production-ready frontend deployment target",
                        "Integrated waitlist submission flow",
                        "Successful submission handling for user capture",
                    ],
                },
                {
                    "title": "Delivery Layer",
                    "items": [
                        "Amazon S3 static website hosting",
                        "Amazon CloudFront global CDN delivery",
                        "Amazon Route 53 DNS routing and domain management",
                        "AWS Certificate Manager (ACM) for TLS/SSL and HTTPS",
                    ],
                },
                {
                    "title": "Growth Layer",
                    "items": [
                        "Formspree serverless form handling",
                        "Waitlist capture for user acquisition",
                        "End-to-end lead capture validation",
                        "No custom backend required for submission flow",
                    ],
                },
                {
                    "title": "Operational Controls",
                    "items": [
                        "Custom domain configuration",
                        "HTTPS verification",
                        "Deployment validation across the live stack",
                        "Production-oriented frontend infrastructure checks",
                    ],
                },
            ],
            "why_it_matters": "This project demonstrates production frontend infrastructure work across AWS delivery services, HTTPS configuration, DNS, and practical user-capture implementation. It shows real deployment ownership rather than a local-only landing page build.",
            "architecture": "Age Evolution uses Amazon S3 for static hosting, Amazon CloudFront for CDN-backed delivery, Amazon Route 53 for domain routing, AWS Certificate Manager for HTTPS, and Formspree for serverless waitlist capture. The result is a production-grade frontend path that supports secure delivery and real user acquisition without a custom backend.",
            "final_status": "The landing page infrastructure is live with HTTPS, custom domain routing, CDN delivery, and working waitlist capture. The deployment path was validated end-to-end for real user submissions.",
            "key_features": [
                "Live custom domain with HTTPS",
                "Globally distributed frontend delivery",
                "Production-ready static hosting architecture",
                "Working waitlist capture flow",
                "Validated end-to-end user submission path",
            ],
            "outcomes": [
                "Configured a live custom domain with HTTPS",
                "Deployed a globally distributed frontend through CloudFront",
                "Implemented a production-ready static hosting architecture",
                "Added a real waitlist capture flow with successful submission handling",
                "Verified end-to-end user capture without needing a custom backend",
            ],
        },
        {
            "slug": "cloud-monitor",
            "title": "Cloud Monitoring Platform on AWS",
            "subtitle": "Production-style AWS monitoring and infrastructure visibility platform",
            "status": "Live",
            "status_color": "#22c55e",
            "description": "Production-style monitoring system deployed on AWS that tracks system health, logs, and infrastructure metrics.",
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
            "description": "Tool for analyzing CPU, memory, and disk usage to provide real-time system visibility.",
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
            "description": "Log analysis tool for detecting errors, warnings, and generating structured operational insights.",
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
            "description": "Tool for scanning and extracting meaningful operational data from raw log files.",
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
            width: min(1380px, calc(100vw - 48px));
            margin: auto;
        }

        .card {
            background: #1e293b;
            padding: 38px 42px 42px 42px;
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
            margin-top: 54px;
        }

        .section-title {
            text-align: center;
            color: #e2e8f0;
            margin-bottom: 20px;
            font-size: 28px;
        }

        .section-lead {
            max-width: 920px;
            margin: -2px auto 0 auto;
            text-align: center;
            color: #94a3b8;
            line-height: 1.75;
        }

        .project-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 24px;
            margin-top: 24px;
            align-items: stretch;
        }

        .featured-project-grid {
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
        }

        .catalog-grid {
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        }

        .project-card {
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 14px;
            padding: 24px;
            height: 100%;
            box-sizing: border-box;
        }

        .featured-card {
            background: linear-gradient(180deg, rgba(15, 23, 42, 0.98), rgba(15, 23, 42, 0.92));
            border: 1px solid #3b82f6;
            box-shadow: 0 14px 36px rgba(15, 23, 42, 0.28);
            padding: 28px;
        }

        .featured-eyebrow {
            display: inline-block;
            margin-bottom: 10px;
            color: #7dd3fc;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
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

        .project-stack {
            margin-top: 16px;
            padding-top: 14px;
            border-top: 1px solid rgba(148, 163, 184, 0.18);
            color: #cbd5e1;
            line-height: 1.7;
        }

        .project-support {
            color: #94a3b8;
            line-height: 1.7;
            margin-top: -6px;
            margin-bottom: 16px;
        }

        .project-highlights {
            margin-top: 18px;
            padding-top: 16px;
            border-top: 1px solid rgba(148, 163, 184, 0.24);
        }

        .project-meta-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 14px;
            margin-top: 20px;
        }

        .project-meta-card {
            background: rgba(15, 23, 42, 0.9);
            border: 1px solid rgba(51, 65, 85, 0.9);
            border-radius: 12px;
            padding: 16px;
        }

        .project-meta-card h4 {
            margin: 0 0 10px 0;
            color: #e2e8f0;
            font-size: 15px;
        }

        .project-meta-card ul {
            margin: 0;
            padding-left: 18px;
            color: #cbd5e1;
            line-height: 1.75;
        }

        .project-highlights strong {
            display: block;
            color: #e2e8f0;
            margin-bottom: 10px;
        }

        .project-highlight-list {
            margin: 0;
            padding-left: 18px;
            color: #cbd5e1;
            line-height: 1.8;
        }

        .credibility-line {
            text-align: center;
            color: #cbd5e1;
            background: rgba(15, 23, 42, 0.75);
            border: 1px solid rgba(59, 130, 246, 0.2);
            border-radius: 12px;
            padding: 16px 20px;
            margin-top: 16px;
            line-height: 1.7;
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

        .focus-grid,
        .skills-category-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
            margin-top: 18px;
        }

        .focus-card,
        .skill-category {
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 14px;
            padding: 20px;
            color: #cbd5e1;
            line-height: 1.7;
        }

        .focus-card {
            font-weight: 600;
            color: #dbeafe;
        }

        .skill-category h3 {
            margin: 0 0 12px 0;
            color: #e2e8f0;
            font-size: 18px;
        }

        .skill-category p {
            margin: 0;
            color: #cbd5e1;
            line-height: 1.7;
        }

        .skill-category ul {
            margin: 0;
            padding-left: 18px;
            color: #cbd5e1;
            line-height: 1.75;
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

        .architecture-intro {
            margin: 0 0 18px 0;
            color: #cbd5e1;
            line-height: 1.8;
        }

        .architecture-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
            gap: 16px;
            margin-top: 16px;
        }

        .architecture-card {
            background: linear-gradient(180deg, rgba(30, 41, 59, 0.88), rgba(15, 23, 42, 0.95));
            border: 1px solid #334155;
            border-radius: 14px;
            padding: 18px;
        }

        .architecture-card h3 {
            margin: 0 0 12px 0;
            color: #e2e8f0;
            font-size: 18px;
        }

        .architecture-card ul {
            margin: 0;
            padding-left: 18px;
            color: #cbd5e1;
            line-height: 1.75;
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
            body {
                padding: 22px;
            }

            .container {
                width: min(100%, calc(100vw - 24px));
            }

            .card {
                padding: 28px 24px 30px 24px;
            }

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
            body {
                padding: 14px;
            }

            .container {
                width: 100%;
            }

            .card {
                padding: 22px 16px 24px 16px;
            }

            .section {
                margin-top: 40px;
            }

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
def render_project_detail_page(project):
    return render_template(
        "project_detail.html",
        **portfolio_template_context(f"{SITE_NAME} | {project['title']}"),
        project=project,
        tech_stack_items=[skill.strip() for skill in project["tech_stack"].split(",")],
    )


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
    featured = get_project_by_slug("nexgen-healthcare")
    featured_infrastructure = get_project_by_slug("age-evolution")
    additional_projects = [
        project for project in projects
        if project["slug"] != "nexgen-healthcare"
    ]
    return render_template(
        "home.html",
        **portfolio_template_context(f"{SITE_NAME} | {OWNER_NAME}"),
        featured=featured,
        featured_infrastructure=featured_infrastructure,
        projects=additional_projects,
        focus_items=[
            "Designing systems, not just features",
            "Building state-driven workflows",
            "Deploying real infrastructure on AWS",
            "Creating reliable, production-style applications",
        ],
        skill_groups=[
            {
                "title": "AWS",
                "skills": [
                    "Amazon S3",
                    "Amazon CloudFront",
                    "Amazon Route 53",
                    "AWS Certificate Manager (ACM)",
                ],
            },
            {
                "title": "Web / Deployment",
                "skills": [
                    "Static website hosting",
                    "CDN delivery",
                    "DNS routing",
                    "HTTPS / SSL configuration",
                    "Custom domain setup",
                    "Production frontend deployment",
                ],
            },
            {
                "title": "Product / Growth",
                "skills": [
                    "Waitlist capture",
                    "Serverless form integration",
                    "Landing page deployment",
                    "User acquisition flow",
                ],
            },
            {
                "title": "Cloud Infrastructure",
                "skills": [
                    "AWS EC2",
                    "Linux server setup",
                    "Security groups",
                    "Public/private networking basics",
                    "SSH access management",
                    "Systemd service management",
                ],
            },
            {
                "title": "Deployment & DevOps",
                "skills": [
                    "GitHub Actions CI/CD",
                    "Automated EC2 deployment",
                    "Git/GitHub workflow management",
                    "Environment setup and recovery",
                    "Release/debug workflow",
                    "Production deploy troubleshooting",
                ],
            },
            {
                "title": "Monitoring & Reliability",
                "skills": [
                    "Amazon CloudWatch",
                    "Log inspection",
                    "Service health checks",
                    "Failure diagnosis",
                    "Runtime troubleshooting",
                    "Deployment verification",
                ],
            },
            {
                "title": "Backend Development",
                "skills": [
                    "Python",
                    "Flask",
                    "REST-style backend patterns",
                    "Gunicorn",
                    "SQLAlchemy",
                    "Workflow-driven application logic",
                ],
            },
            {
                "title": "Systems & Networking",
                "skills": [
                    "Reverse-proxy/app path awareness",
                    "Port/service troubleshooting",
                    "502/debug workflow",
                    "Process/service restart flow",
                    "Server-side dependency repair",
                    "CLI-based troubleshooting",
                ],
            },
            {
                "title": "Operational Product Thinking",
                "skills": [
                    "Role-based workflow design",
                    "State-driven systems",
                    "Internal tooling mindset",
                    "Reliability-first changes",
                    "Controlled feature rollout",
                    "Real-world debugging discipline",
                ],
            },
        ],
    )


@app.route("/projects")
def projects_page():
    return render_template(
        "projects.html",
        **portfolio_template_context(f"{SITE_NAME} | Projects"),
        projects=get_projects(),
    )


@app.route("/projects/nexgen-healthcare")
def nexgen_project():
    project = get_project_by_slug("nexgen-healthcare")
    return render_project_detail_page(project)


@app.route("/projects/age-evolution")
def age_evolution_project():
    project = get_project_by_slug("age-evolution")
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
    return render_template(
        "contact.html",
        **portfolio_template_context(f"{SITE_NAME} | Contact"),
    )


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
