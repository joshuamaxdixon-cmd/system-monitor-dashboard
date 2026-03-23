from flask import Flask
import psutil
import datetime

app = Flask(__name__)

# LOG STORAGE (simple version)
logs = []

def add_log(message):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    logs.insert(0, f"[{timestamp}] {message}")

@app.route("/")
def dashboard():
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent

    # LOG EVENTS
    add_log(f"CPU: {cpu}% | Memory: {memory}% | Disk: {disk}%")

    # COLORS
    def color(value):
        if value < 70:
            return "green"
        elif value < 85:
            return "orange"
        return "red"

    cpu_color = color(cpu)
    memory_color = color(memory)
    disk_color = color(disk)

    # ALERTS
    alerts = []
    if cpu > 80:
        alerts.append("🚨 High CPU Usage")
    if memory > 75:
        alerts.append("⚠️ High Memory Usage")
    if disk > 80:
        alerts.append("⚠️ Low Disk Space")

    alerts_html = "".join(f"<p>{a}</p>" for a in alerts) or "<p style='color:green;'>System Healthy</p>"

    # LOG DISPLAY
    log_html = "".join(f"<p>{log}</p>" for log in logs[:10])

    return f"""
    <html>
    <head>
        <title>Cloud Monitoring Platform</title>
        <meta http-equiv="refresh" content="5">
        <style>
            body {{ font-family: Arial; background:#f4f6f8; text-align:center; }}
            .card {{ background:white; width:600px; margin:auto; padding:25px; border-radius:12px; box-shadow:0 4px 12px rgba(0,0,0,0.1); }}
            .section {{ margin-top:20px; }}
            .alerts {{ background:#fff3f3; padding:10px; border-radius:10px; }}
            .logs {{ background:#eef; padding:10px; border-radius:10px; text-align:left; height:150px; overflow:auto; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Cloud Monitoring Platform</h1>

            <div class="section">
                <p style="color:{cpu_color}"><b>CPU:</b> {cpu}%</p>
                <p style="color:{memory_color}"><b>Memory:</b> {memory}%</p>
                <p style="color:{disk_color}"><b>Disk:</b> {disk}%</p>
            </div>

            <div class="section alerts">
                <h2>Alerts</h2>
                {alerts_html}
            </div>

            <div class="section logs">
                <h2>Logs</h2>
                {log_html}
            </div>

        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)