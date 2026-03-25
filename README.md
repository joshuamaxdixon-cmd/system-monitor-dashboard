# System Monitor Dashboard

A Flask-based system monitoring dashboard that displays live CPU, memory, and disk usage with dynamic color alerts and automatic refresh.

Features:
- Real-time system monitoring (CPU, Memory)
- CloudWatch integration (custom metrics + EC2 metrics)
- Dashboard UI (Flask + Chart.js)
- Historical logging (SQLite/Postgres)
- Production deployment with Gunicorn + systemd
- AWS CloudWatch dashboards + alarms

Tech:
Python, Flask, AWS EC2, CloudWatch, Gunicorn, SQLite/Postgres

## Tech Stack

- Python
- Flask
- psutil
- HTML/CSS

## How to Run

python3 app.py

Then open:

http://127.0.0.1:5000

## Purpose

This project demonstrates real-time infrastructure monitoring concepts relevant to cloud engineering, DevOps, and data center operations.
