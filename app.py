from flask import Flask
import psutil

app = Flask(__name__)

@app.route("/")
def dashboard():
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent

    # 🔥 Color logic
    cpu_color = "green" if cpu < 70 else "orange" if cpu < 85 else "red"
    memory_color = "green" if memory < 70 else "orange" if memory < 85 else "red"
    disk_color = "green" if disk < 70 else "orange" if disk < 85 else "red"

    return f"""
    <html>
    <head>
        <title>System Monitor Dashboard</title>
        <meta http-equiv="refresh" content="5">
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f6f8;
                text-align: center;
                padding-top: 50px;
            }}
            .card {{
                background: white;
                width: 400px;
                margin: auto;
                padding: 30px;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }}
            h1 {{
                margin-bottom: 30px;
            }}
            p {{
                font-size: 20px;
                margin: 15px 0;
            }}
            .cpu {{ color: {cpu_color}; }}
            .memory {{ color: {memory_color}; }}
            .disk {{ color: {disk_color}; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>System Monitor Dashboard</h1>
            <p class="cpu"><strong>CPU Usage:</strong> {cpu}%</p>
            <p class="memory"><strong>Memory Usage:</strong> {memory}%</p>
            <p class="disk"><strong>Disk Usage:</strong> {disk}%</p>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)