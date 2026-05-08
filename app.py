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
OWNER_TITLE = "Cloud & Systems Engineer"
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
            {"href": "/#top", "label": "Home"},
            {"href": "/#projects", "label": "Projects"},
            {"href": "/#architecture", "label": "Architecture"},
            {"href": "/#skills", "label": "Skills"},
            {"href": "/#about", "label": "About"},
            {"href": "/#contact", "label": "Contact"},
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
      :root {
        --bg: #05080f;
        --card: rgba(15,23,42,0.5);
        --card-solid: #0a1322;
        --ink: #e2e8f0;
        --ink-soft: #cbd5e1;
        --muted: #64748b;
        --muted-bright: #94a3b8;
        --accent: #3b82f6;
        --accent-bright: #60a5fa;
        --success: #10b981;
        --success-bright: #34d399;
        --border: rgba(59,130,246,0.15);
        --border-strong: rgba(59,130,246,0.3);
        --border-soft: rgba(148,163,184,0.1);
      }
      *{box-sizing:border-box;margin:0;padding:0}
      html{scroll-behavior:smooth}
      body {
        background:
          radial-gradient(1200px 600px at 80% 0%, rgba(59,130,246,0.08), transparent 60%),
          radial-gradient(900px 500px at 20% 30%, rgba(59,130,246,0.04), transparent 70%),
          var(--bg);
        color: var(--ink);
        font-family: 'Inter', -apple-system, ui-sans-serif, system-ui, sans-serif;
        font-size: 15px;
        line-height: 1.55;
        overflow-x: hidden;
        min-height: 100vh;
      }
      body::before {
        content:"";position:fixed;inset:0;pointer-events:none;z-index:0;opacity:.6;
        background-image:
          radial-gradient(1px 1px at 12% 18%, rgba(255,255,255,0.4), transparent 50%),
          radial-gradient(1px 1px at 28% 42%, rgba(255,255,255,0.25), transparent 50%),
          radial-gradient(1px 1px at 65% 22%, rgba(255,255,255,0.3), transparent 50%),
          radial-gradient(1px 1px at 85% 60%, rgba(255,255,255,0.2), transparent 50%),
          radial-gradient(1px 1px at 45% 80%, rgba(255,255,255,0.3), transparent 50%);
      }
      a{color:inherit}
      a:focus-visible,button:focus-visible{outline:2px solid #67e8f9;outline-offset:4px}

      /* === SKIP LINK === */
      .skip-link{position:fixed;left:20px;top:14px;z-index:100;transform:translateY(-140%);padding:10px 14px;border-radius:10px;background:#e0f2fe;color:#020617;font-weight:800;text-decoration:none}
      .skip-link:focus{transform:translateY(0)}

      /* === NAV OUTER === */
      .site-header-outer{
        position:relative;top:auto;z-index:10;
        backdrop-filter:blur(12px);
        background:rgba(5,8,15,0.7);
        border-bottom:1px solid var(--border-soft);
      }
      .site-header{
        max-width:1280px;margin:0 auto;
        padding:18px 40px;
        display:grid;
        grid-template-columns:auto 1fr auto;
        align-items:center;
        gap:40px;
      }
      .brand-lockup{display:flex;align-items:center;gap:14px;text-decoration:none;color:inherit}
      .brand-mark{
        width:38px;height:38px;border-radius:8px;
        background:linear-gradient(135deg,#3b82f6,#1e40af);
        display:flex;align-items:center;justify-content:center;
        font-weight:800;font-size:13px;letter-spacing:0.02em;color:white;
        box-shadow:0 0 20px rgba(59,130,246,0.3);flex-shrink:0;
      }
      .brand-copy{font-size:14px;color:var(--muted-bright);font-weight:500;white-space:nowrap}
      .top-nav{display:flex;gap:28px;flex:1;justify-content:center}
      .top-nav a{color:var(--ink-soft);text-decoration:none;font-size:14px;padding:6px 2px;transition:color 0.2s;position:relative}
      .top-nav a:hover{color:var(--ink);background:transparent}
      .top-nav a:first-child{color:var(--accent-bright)}
      .top-nav a:first-child::after{content:"";position:absolute;bottom:-2px;left:50%;transform:translateX(-50%);width:4px;height:4px;border-radius:50%;background:var(--accent-bright);display:block}
      .nav-right{display:flex;align-items:center;gap:14px}
      .theme-toggle{
        width:36px;height:36px;border-radius:50%;
        border:1px solid var(--border-soft);background:transparent;cursor:pointer;
        display:flex;align-items:center;justify-content:center;
        color:var(--muted-bright);transition:border-color 0.2s,color 0.2s,transform 0.3s;
      }
      .theme-toggle:hover{border-color:var(--border-strong);color:var(--ink)}
      .theme-toggle svg{width:16px;height:16px}
      .nav-cta{
        display:inline-flex;align-items:center;gap:10px;
        padding:9px 18px;border-radius:10px;
        border:1px solid var(--border-strong);
        background:rgba(59,130,246,0.04);
        color:var(--ink);text-decoration:none;
        font-size:14px;font-weight:500;
        transition:background 0.2s,border-color 0.2s;
      }
      .nav-cta:hover{background:rgba(59,130,246,0.1);border-color:var(--accent)}
      .nav-cta svg{width:16px;height:16px;flex-shrink:0}

      /* === PULSE DOT === */
      .pulse-dot,.status-dot{
        display:inline-block;width:8px;height:8px;border-radius:50%;
        background:var(--success);flex-shrink:0;
        animation:pulse 2s ease-in-out infinite;
        box-shadow:0 0 8px var(--success);
      }
      @keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:0.6;transform:scale(1.15)}}

      /* === CONTAINER / MAIN === */
      .container{max-width:1280px;margin:0 auto;padding:48px 40px 60px;position:relative;z-index:1}
      main{background:transparent}

      /* === HERO === */
      .hero{display:grid;grid-template-columns:minmax(0,1fr) 380px;gap:32px;margin-bottom:56px}
      .hero-main{position:relative;min-height:480px;display:flex;flex-direction:column}
      .hero-content{position:relative;z-index:2;max-width:560px}
      .hero-tagline{font-size:11px;letter-spacing:0.2em;color:var(--muted-bright);font-weight:500;margin-bottom:32px}
      .hero-tagline .dot{color:var(--accent-bright);margin:0 6px}
      h1.hero-name{font-size:clamp(56px,6.4vw,88px);font-weight:700;line-height:0.98;letter-spacing:-0.03em;margin-bottom:24px}
      h1.hero-name .first{color:var(--ink);display:block}
      h1.hero-name .last{background:linear-gradient(180deg,#93c5fd 0%,#3b82f6 100%);-webkit-background-clip:text;background-clip:text;color:transparent;display:block}
      .hero-desc{color:var(--muted-bright);font-size:16px;line-height:1.6;margin-bottom:32px;max-width:460px}
      .hero-ctas{display:flex;gap:14px;flex-wrap:wrap}
      .btn{display:inline-flex;align-items:center;gap:10px;padding:13px 22px;border-radius:10px;font-size:14px;font-weight:500;text-decoration:none;border:none;cursor:pointer;transition:transform 0.15s,background 0.2s,box-shadow 0.2s}
      .btn-primary{background:var(--accent);color:white;box-shadow:0 0 0 1px rgba(59,130,246,0.5),0 8px 24px rgba(59,130,246,0.25)}
      .btn-primary:hover{background:#2563eb;box-shadow:0 0 0 1px rgba(59,130,246,0.7),0 12px 32px rgba(59,130,246,0.35);transform:translateY(-1px)}
      .btn-ghost{background:transparent;color:var(--ink);border:1px solid var(--border-strong)}
      .btn-ghost:hover{background:rgba(59,130,246,0.06);border-color:var(--accent);transform:translateY(-1px)}
      .btn .arrow,.btn:hover .arrow{display:inline}
      .btn:hover .arrow{animation:arrowPop 0.2s ease forwards}
      @keyframes arrowPop{to{transform:translateX(3px)}}
      .hero-visual{position:absolute;right:-40px;top:50%;transform:translateY(-50%);width:520px;height:480px;pointer-events:none}
      .cube-fallback{position:relative;width:100%;height:100%;display:grid;place-items:center;isolation:isolate}
      .cube-fallback::before{content:"";position:absolute;inset:16%;border-radius:50%;background:radial-gradient(circle,rgba(59,130,246,0.25),transparent 62%);filter:blur(12px)}
      .cube-grid{position:absolute;inset:12%;background-image:linear-gradient(rgba(96,165,250,0.12) 1px,transparent 1px),linear-gradient(90deg,rgba(96,165,250,0.12) 1px,transparent 1px);background-size:38px 38px;transform:skewY(-18deg) rotate(2deg);opacity:.72}
      .cube-layer,.cube-core{position:absolute;display:block;border:1px solid rgba(96,165,250,.62);background:linear-gradient(135deg,rgba(59,130,246,.24),rgba(2,6,23,.72));box-shadow:0 0 38px rgba(59,130,246,.22),inset 0 0 32px rgba(96,165,250,.12);transform:rotateX(58deg) rotateZ(45deg)}
      .cube-layer.layer-one{width:190px;height:190px}
      .cube-layer.layer-two{width:138px;height:138px;transform:translateY(-34px) rotateX(58deg) rotateZ(45deg)}
      .cube-layer.layer-three{width:90px;height:90px;transform:translateY(-68px) rotateX(58deg) rotateZ(45deg);background:rgba(59,130,246,.22)}
      .cube-core{width:48px;height:48px;transform:translateY(-102px) rotateX(58deg) rotateZ(45deg);background:rgba(96,165,250,.58)}
      .hero-side{display:grid;gap:14px;align-content:start}

      /* === TRUSTED BY === */
      .trusted{display:flex;align-items:center;gap:32px;margin:32px 0 0;flex-wrap:wrap}
      .trusted-label{font-size:11px;letter-spacing:0.18em;color:var(--muted);text-transform:uppercase;white-space:nowrap}
      .trusted-item{display:inline-flex;align-items:center;gap:8px;color:var(--muted-bright);font-size:13px;transition:color 0.2s}
      .trusted-item:hover{color:var(--ink)}
      .trusted-item svg{width:18px;height:18px;opacity:0.85;flex-shrink:0}

      /* === STATUS PANEL === */
      .status-panel{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:24px;backdrop-filter:blur(8px)}
      .status-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;padding-bottom:18px;border-bottom:1px solid var(--border-soft)}
      .status-title{font-size:11px;letter-spacing:0.18em;font-weight:500;color:var(--muted-bright);text-transform:uppercase}
      .status-badge-pill{display:inline-flex;align-items:center;gap:8px;font-size:12px;color:var(--success-bright)}
      .service-row{display:flex;align-items:center;justify-content:space-between;padding:12px 0;border-bottom:1px solid var(--border-soft)}
      .service-row:last-of-type{border-bottom:none}
      .service-name-wrap{display:flex;align-items:center;gap:10px;font-size:14px;color:var(--ink-soft)}
      .service-icon{width:24px;height:24px;border-radius:6px;background:rgba(59,130,246,0.1);display:flex;align-items:center;justify-content:center;color:var(--accent-bright);flex-shrink:0}
      .service-icon svg{width:13px;height:13px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
      .service-status{font-size:12px;color:var(--success-bright);font-weight:500;white-space:nowrap}
      .deployment-velocity{margin-top:20px;padding-top:20px;border-top:1px solid var(--border-soft)}
      .dv-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;font-size:11px;letter-spacing:0.18em;color:var(--muted-bright);text-transform:uppercase}
      .dv-period{letter-spacing:0;text-transform:none;color:var(--muted)}
      .dv-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px}
      .dv-stat{background:rgba(255,255,255,0.02);border:1px solid var(--border-soft);border-radius:8px;padding:12px 10px}
      .dv-label{font-size:10px;color:var(--muted);margin-bottom:4px}
      .dv-value{font-size:18px;font-weight:600;color:var(--ink)}

      /* === INFRA CARD === */
      .infra-card{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:20px;backdrop-filter:blur(8px)}
      .infra-card-header{font-size:11px;letter-spacing:0.18em;color:var(--muted-bright);margin-bottom:14px;text-transform:uppercase}
      .infra-region{font-size:14px;color:var(--ink-soft);margin-bottom:4px}
      .infra-primary{font-size:12px;color:var(--accent-bright);display:flex;align-items:center;gap:6px}
      .infra-primary::before{content:"";width:6px;height:6px;border-radius:50%;background:var(--accent-bright);flex-shrink:0}
      .map-container{position:relative;height:140px;margin-top:14px}
      #worldMap{width:100%;height:100%}

      /* === SECTIONS === */
      section{margin-top:64px}
      .section-head{display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:24px;gap:16px}
      .section-label{font-size:11px;letter-spacing:0.18em;color:var(--muted-bright);margin-bottom:8px;text-transform:uppercase}
      .section-desc{font-size:13px;color:var(--ink-soft);font-weight:500;line-height:1.5}
      .section-link{font-size:13px;color:var(--accent-bright);text-decoration:none;display:inline-flex;align-items:center;gap:6px;transition:gap 0.2s;white-space:nowrap}
      .section-link:hover{gap:10px}

      /* === FEATURED GRID === */
      .featured-grid{display:grid;grid-template-columns:1fr 1fr;gap:20px}
      .feature-card{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:28px;backdrop-filter:blur(8px);position:relative;overflow:hidden;transition:border-color 0.2s,transform 0.2s}
      .feature-card:hover{border-color:var(--border-strong);transform:translateY(-2px)}
      .feature-inner{display:grid;grid-template-columns:1fr 200px;gap:24px;align-items:start}
      .feature-content{min-width:0}
      .live-badge{display:inline-flex;align-items:center;gap:8px;padding:5px 11px;border-radius:999px;background:rgba(16,185,129,0.12);border:1px solid rgba(16,185,129,0.3);font-size:10.5px;letter-spacing:0.12em;color:var(--success-bright);font-weight:500;margin-bottom:16px;text-transform:uppercase}
      .feature-title{font-size:22px;font-weight:600;letter-spacing:-0.02em;margin-bottom:10px;color:var(--ink)}
      .feature-desc{color:var(--muted-bright);font-size:13.5px;line-height:1.55;margin-bottom:18px}
      .stack-label{font-size:10px;letter-spacing:0.18em;color:var(--muted);margin-bottom:10px;text-transform:uppercase}
      .stack-pills{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:20px}
      .pill{padding:5px 11px;border-radius:6px;background:rgba(255,255,255,0.03);border:1px solid var(--border-soft);font-size:11.5px;color:var(--ink-soft);font-family:'JetBrains Mono','Courier New',monospace}
      .stat-grid{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:14px;margin-bottom:20px}
      .stat-item .stat-label{font-size:10px;color:var(--muted);letter-spacing:0.05em;margin-bottom:4px}
      .stat-item .stat-value{font-size:18px;font-weight:600;color:var(--ink)}
      .feature-cta{display:inline-flex;align-items:center;gap:8px;padding:9px 16px;border-radius:8px;border:1px solid var(--border-strong);background:transparent;color:var(--ink);font-size:13px;font-weight:500;text-decoration:none;transition:background 0.2s}
      .feature-cta:hover{background:rgba(59,130,246,0.08)}
      .feature-cta svg{width:14px;height:14px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;transition:transform 0.2s}
      .feature-cta:hover svg{transform:translateX(2px)}

      /* === NEXGEN MOCKUP === */
      .nexgen-mockup{width:200px;height:260px;background:#0d1424;border:1px solid var(--border-soft);border-radius:8px;display:flex;flex-direction:column;overflow:hidden;box-shadow:0 8px 24px rgba(0,0,0,0.4);font-size:7px;flex-shrink:0}
      .nm-header{background:#080d18;padding:5px 8px;display:flex;align-items:center;gap:5px;border-bottom:1px solid rgba(255,255,255,0.04)}
      .nm-logo{width:9px;height:9px;border-radius:2px;background:linear-gradient(135deg,#3b82f6,#1e40af);flex-shrink:0}
      .nm-title{color:var(--ink);font-weight:600;font-size:7.5px}
      .nm-body{display:flex;flex:1;min-height:0}
      .nm-sidebar{width:42px;background:#080d18;padding:5px 4px;border-right:1px solid rgba(255,255,255,0.04)}
      .nm-nav-item{padding:3px 5px;border-radius:3px;color:var(--muted);font-size:6px;margin-bottom:2px}
      .nm-nav-item.active{background:rgba(59,130,246,0.15);color:var(--accent-bright)}
      .nm-main{flex:1;padding:5px;min-width:0}
      .nm-section-title{color:var(--muted-bright);font-size:6px;font-weight:600;margin-bottom:3px;letter-spacing:0.05em}
      .nm-cards{display:flex;gap:3px;margin-bottom:5px}
      .nm-card{flex:1;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.04);border-radius:3px;padding:3px 4px;min-width:0}
      .nm-card-label{font-size:5px;color:var(--muted)}
      .nm-card-value{font-size:9px;font-weight:600;color:var(--ink);margin-top:1px}
      .nm-list-item{display:flex;align-items:center;justify-content:space-between;padding:2px 3px;background:rgba(255,255,255,0.02);border-radius:2px;margin-bottom:2px;font-size:5.5px;color:var(--ink-soft)}
      .nm-list-status{padding:1px 3px;border-radius:6px;background:rgba(16,185,129,0.15);color:var(--success-bright);font-size:5px}

      /* === AGE EVOLUTION MOCKUP === */
      .ae-mockup{width:200px;height:260px;border-radius:8px;overflow:hidden;position:relative;background:radial-gradient(circle at 50% 50%,rgba(20,55,75,0.4),#04060a);border:1px solid var(--border-soft);box-shadow:0 8px 24px rgba(0,0,0,0.4);flex-shrink:0}
      .ae-globe-fallback{position:absolute;inset:0;display:grid;place-items:center;background:radial-gradient(circle at 50% 40%,rgba(59,130,246,.2),transparent 52%)}
      .globe-shell{width:168px;height:168px;border-radius:50%;border:1px solid rgba(96,165,250,.4);background:radial-gradient(circle at 32% 26%,rgba(255,255,255,.2),transparent 18%),radial-gradient(circle at 68% 58%,rgba(59,130,246,.45),transparent 38%),linear-gradient(135deg,rgba(3,23,50,.92),rgba(2,7,13,.92));box-shadow:0 0 56px rgba(59,130,246,.24)}
      .globe-orbit{position:absolute;width:190px;height:70px;border:1px solid rgba(96,165,250,.24);border-radius:50%;transform:rotate(-17deg)}
      .orbit-two{width:168px;height:58px;transform:rotate(22deg)}
      .globe-dot{position:absolute;width:5px;height:5px;border-radius:50%;background:#fbbf24;box-shadow:0 0 12px #fbbf24}
      .dot-one{left:36%;top:42%}.dot-two{left:52%;top:34%}.dot-three{left:66%;top:58%}.dot-four{left:44%;top:66%}
      .ae-overlay-card{position:absolute;bottom:14px;left:14px;right:14px;background:rgba(8,12,18,0.85);backdrop-filter:blur(8px);border:1px solid rgba(59,130,246,0.2);border-radius:6px;padding:8px 10px;font-size:8px;z-index:2}
      .ae-overlay-label{font-size:6px;color:var(--accent-bright);letter-spacing:0.1em;margin-bottom:3px;text-transform:uppercase}
      .ae-overlay-title{font-size:9px;color:var(--ink);font-weight:600;margin-bottom:5px}
      .ae-overlay-desc{font-size:6.5px;color:var(--muted-bright);line-height:1.4;margin-bottom:6px}
      .ae-overlay-btn{display:inline-block;background:var(--accent);color:white;font-size:6px;padding:3px 7px;border-radius:3px;font-weight:500}

      /* === ALL PROJECTS CAROUSEL === */
      .projects-wrap{position:relative;overflow:hidden}
      .projects-scroll{display:flex;gap:16px;overflow-x:auto;scroll-behavior:smooth;padding-bottom:6px;scrollbar-width:none}
      .projects-scroll::-webkit-scrollbar{display:none}
      .project-card{flex:0 0 240px;background:var(--card);border:1px solid var(--border);border-radius:14px;padding:22px;backdrop-filter:blur(8px);transition:border-color 0.2s,transform 0.2s}
      .project-card:hover{border-color:var(--border-strong);transform:translateY(-2px)}
      .project-icon{width:42px;height:42px;border-radius:10px;background:rgba(59,130,246,0.1);border:1px solid var(--border-soft);display:flex;align-items:center;justify-content:center;margin-bottom:18px;color:var(--accent-bright)}
      .project-icon svg{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
      .project-title{font-size:15px;font-weight:600;color:var(--ink);margin-bottom:8px}
      .project-desc{font-size:12.5px;color:var(--muted-bright);line-height:1.5;margin-bottom:14px;min-height:50px}
      .project-status{display:inline-flex;align-items:center;gap:6px;font-size:11px;color:var(--success-bright)}
      .carousel-arrow{position:absolute;right:-8px;top:50%;transform:translateY(-50%);width:42px;height:42px;border-radius:50%;background:var(--card-solid);border:1px solid var(--border-strong);color:var(--ink);display:flex;align-items:center;justify-content:center;cursor:pointer;transition:background 0.2s,transform 0.15s;z-index:5}
      .carousel-arrow:hover{background:rgba(59,130,246,0.15);transform:translateY(-50%) scale(1.05)}
      .carousel-arrow svg{width:16px;height:16px;fill:none;stroke:currentColor;stroke-width:2.2;stroke-linecap:round}

      /* === CAPABILITIES === */
      .capabilities{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:32px;backdrop-filter:blur(8px)}
      .cap-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:32px}
      .cap-icon{width:36px;height:36px;border-radius:8px;background:rgba(59,130,246,0.08);border:1px solid var(--border-soft);display:flex;align-items:center;justify-content:center;color:var(--accent-bright);margin-bottom:16px}
      .cap-icon svg{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
      .cap-title{font-size:14px;font-weight:600;color:var(--ink);margin-bottom:14px}
      .cap-list{list-style:none}
      .cap-list li{display:flex;align-items:center;gap:8px;font-size:12.5px;color:var(--muted-bright);padding:5px 0}
      .cap-list li::before{content:"";width:5px;height:5px;border-radius:50%;background:var(--success);flex-shrink:0}

      /* === CONTACT === */
      .contact-card{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:32px;backdrop-filter:blur(8px);display:grid;grid-template-columns:1.2fr 1fr 1fr;gap:32px;align-items:center}
      .contact-heading{font-size:22px;font-weight:600;color:var(--ink);letter-spacing:-0.015em;margin-bottom:8px}
      .contact-sub{font-size:13px;color:var(--muted-bright);line-height:1.5}
      .contact-block-label{font-size:11px;letter-spacing:0.18em;color:var(--muted-bright);margin-bottom:8px;text-transform:uppercase}
      .contact-email{font-size:14px;color:var(--accent-bright);text-decoration:none;transition:color 0.2s;display:block}
      .contact-email:hover{color:var(--ink)}
      .social-row{display:flex;gap:10px}
      .social-btn{width:38px;height:38px;border-radius:50%;border:1px solid var(--border-strong);background:rgba(59,130,246,0.04);display:flex;align-items:center;justify-content:center;color:var(--ink-soft);text-decoration:none;transition:background 0.2s,color 0.2s,transform 0.15s}
      .social-btn:hover{background:rgba(59,130,246,0.12);color:var(--accent-bright);transform:translateY(-2px)}
      .social-btn svg{width:16px;height:16px}

      /* === FOOTER === */
      .portfolio-footer{margin-top:48px;padding:24px 0 32px;border-top:1px solid var(--border-soft)}
      .footer-inner{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px;font-size:12px;color:var(--muted)}

      /* === MAP ARCS === */
      .map-arc{fill:none;stroke:rgba(96,165,250,0.74);stroke-width:1;stroke-linecap:round;stroke-dasharray:18 180;animation:mapTrace 3.6s linear infinite}
      .map-arc-base{fill:none;stroke:rgba(96,165,250,0.18);stroke-width:0.7}
      .map-pin{fill:#2f8cff;filter:drop-shadow(0 0 5px rgba(47,140,255,0.9))}
      .map-pin-primary{fill:#93c5fd}
      @keyframes mapTrace{from{stroke-dashoffset:210}to{stroke-dashoffset:-36}}

      /* === REVEAL === */
      .reveal{opacity:0;transform:translateY(16px);transition:opacity 0.7s ease,transform 0.7s ease}
      .reveal.in{opacity:1;transform:translateY(0)}

      /* ============================================================
         OTHER PAGES (project_detail, projects, contact)
      ============================================================ */
      h1{color:var(--ink);font-size:clamp(32px,4vw,56px);font-weight:700;line-height:1.1;margin-bottom:16px}
      h2{color:var(--ink);font-size:clamp(22px,3vw,32px);font-weight:700;margin-bottom:12px}
      h3{color:var(--ink);font-size:18px;font-weight:600;margin-bottom:8px}
      p{color:var(--muted-bright);line-height:1.7}
      .subtitle{color:var(--muted-bright);font-size:16px;line-height:1.6;margin-bottom:24px;max-width:760px}
      .detail-hero{text-align:center;padding:40px 0 20px}
      .highlight-row{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin:16px 0}
      .highlight-chip{padding:6px 12px;border-radius:999px;border:1px solid var(--border-soft);background:rgba(59,130,246,0.08);color:var(--ink-soft);font-size:13px}
      .project-detail-meta{margin:20px 0}
      .meta-box{padding:16px 20px;border-radius:12px;border:1px solid var(--border-soft);background:var(--card);color:var(--muted-bright);font-size:14px}
      .meta-box strong{display:block;color:var(--ink);margin-bottom:6px}
      .section-panel{padding:24px;border-radius:12px;border:1px solid var(--border-soft);background:var(--card);margin:16px 0}
      .section-panel h2{font-size:20px;margin-bottom:10px}
      .section-panel p,.section-panel li{color:var(--muted-bright);line-height:1.7}
      .architecture-intro{color:var(--muted-bright);line-height:1.7;margin-bottom:16px}
      .architecture-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}
      .architecture-card{padding:18px;border-radius:10px;border:1px solid var(--border-soft);background:rgba(255,255,255,0.02)}
      .architecture-card h3{color:var(--accent-bright);font-size:14px;margin-bottom:8px}
      .architecture-card ul{padding-left:16px;color:var(--muted-bright);font-size:13px}
      .architecture-card li{padding:3px 0;line-height:1.5}
      .flow-panel{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:16px 0}
      .flow-box{padding:20px;border-radius:12px;border:1px solid var(--border-soft);background:var(--card)}
      .flow-label{display:block;font-size:11px;letter-spacing:0.18em;color:var(--muted-bright);text-transform:uppercase;margin-bottom:10px}
      .flow-sequence{color:var(--ink-soft);font-size:14px;line-height:1.6}
      .flow-description{color:var(--muted-bright);font-size:14px;line-height:1.6}
      .systems-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin-top:14px}
      .system-card{padding:18px;border-radius:10px;border:1px solid var(--border-soft);background:rgba(255,255,255,0.02)}
      .system-card h3{font-size:15px;margin-bottom:6px}
      .system-card p{font-size:13px}
      .note-box{padding:18px 22px;border-radius:12px;border:1px solid var(--border-soft);background:var(--card);margin-bottom:14px;font-size:14px;color:var(--muted-bright);line-height:1.7}
      .note-box strong{color:var(--ink)}
      .skill-chip-row{display:flex;flex-wrap:wrap;gap:8px;margin:20px 0}
      .skill-box{padding:5px 12px;border-radius:999px;border:1px solid var(--border-soft);background:rgba(59,130,246,0.08);color:var(--ink-soft);font-size:12px}
      .hero-buttons{display:flex;gap:10px;flex-wrap:wrap;margin-top:24px}
      .button-link,.btn-secondary{display:inline-flex;align-items:center;justify-content:center;padding:9px 18px;border-radius:8px;font-size:13px;font-weight:500;text-decoration:none;transition:background 0.2s,transform 0.15s}
      .btn-secondary{background:rgba(59,130,246,0.1);color:var(--accent-bright);border:1px solid var(--border-strong)}
      .btn-secondary:hover{background:rgba(59,130,246,0.2);transform:translateY(-1px)}
      .status-badge{display:inline-flex;align-items:center;gap:6px;padding:5px 12px;border-radius:999px;font-size:11px;font-weight:600;letter-spacing:0.04em;color:white;text-transform:uppercase}
      .project-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:20px}
      .project-grid .project-card{flex:none}
      .inline-link{color:var(--accent-bright);text-decoration:underline}
      .project-links{display:flex;gap:10px;margin-top:14px;flex-wrap:wrap}

      /* === RESPONSIVE === */
      @media(max-width:1100px){
        .site-header{padding:14px 24px;gap:20px}
        .hero{grid-template-columns:1fr}
        .hero-visual{position:relative;right:auto;top:auto;transform:none;width:100%;height:300px;margin-top:-20px}
        .featured-grid{grid-template-columns:1fr}
        .feature-inner{grid-template-columns:1fr}
        .nexgen-mockup,.ae-mockup{width:100%;max-width:280px;height:300px;margin:0 auto}
        .cap-grid{grid-template-columns:repeat(2,1fr);gap:24px}
        .contact-card{grid-template-columns:1fr;gap:20px}
        .systems-grid,.architecture-grid,.flow-panel{grid-template-columns:1fr}
        .project-grid{grid-template-columns:repeat(2,1fr)}
      }
      @media(max-width:900px){
        .top-nav{display:none}
        .brand-copy{display:inline}
      }
      @media(max-width:700px){
        .container{padding:32px 20px 40px}
        .site-header{padding:14px 20px;gap:16px}
        .top-nav{display:none}
        .brand-copy{display:none}
        h1.hero-name{font-size:48px}
        .stat-grid{grid-template-columns:1fr 1fr}
        .cap-grid{grid-template-columns:1fr;gap:20px}
        .trusted{gap:16px}
        .hero-ctas{flex-direction:column}
        .project-grid{grid-template-columns:1fr}
        .carousel-arrow{display:none}
        .hero-buttons{flex-direction:column}
        .footer-inner{flex-direction:column;gap:8px;text-align:center}
      }

      @media (prefers-reduced-motion: reduce) {
        html{scroll-behavior:auto}
        *,*::before,*::after{animation-duration:.001ms!important;animation-iteration-count:1!important;transition-duration:.001ms!important}
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
        if project["slug"] not in ["nexgen-healthcare", "age-evolution"]
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
                "title": "Cloud & Infrastructure",
                "skills": [
                    "AWS Architecture",
                    "EC2 / S3 / CloudFront",
                    "Route 53 / ACM / ALB",
                    "VPC / Security Groups",
                    "System Design",
                ],
            },
            {
                "title": "Backend Engineering",
                "skills": [
                    "Python / Flask / Gunicorn",
                    "REST API Development",
                    "SQLAlchemy",
                    "Workflow & State Engines",
                    "Service Integration",
                ],
            },
            {
                "title": "DevOps & Deployment",
                "skills": [
                    "GitHub Actions CI/CD",
                    "Automated Deployments",
                    "Environment Management",
                    "Rollback & Recovery",
                    "Release Discipline",
                ],
            },
            {
                "title": "Monitoring & Reliability",
                "skills": [
                    "CloudWatch / Logging",
                    "Health Checks / Alerting",
                    "Incident Response",
                    "Failure Diagnosis",
                    "Runtime Troubleshooting",
                ],
            },
            {
                "title": "Product & Operations",
                "skills": [
                    "Workflow Design",
                    "Feature Flag Systems",
                    "User Experience Flow",
                    "Operational Tools",
                    "AI-Assisted Engineering",
                ],
            },
            {
                "title": "Systems & Networking",
                "skills": [
                    "Nginx / reverse proxy awareness",
                    "Port/service troubleshooting",
                    "DNS / SSL/TLS debugging",
                    "Server-side dependency repair",
                    "Process/service restart flow",
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
