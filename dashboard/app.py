import json
import os
import yaml
from flask import Flask, render_template, jsonify
from monitor.logger import get_logger

log = get_logger("dashboard")
app = Flask(__name__)

HISTORY_FILE = "data/history.json"
CONFIG_FILE = "config/monitors.yaml"


def load_data():
    history = {}
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE) as f:
            history = json.load(f)

    with open(CONFIG_FILE) as f:
        cfg = yaml.safe_load(f)

    monitors = []
    for m in cfg.get("monitors", []):
        name = m["name"]
        entries = history.get(name, [])
        last = entries[-1] if entries else {}
        monitors.append({
            "name": name,
            "enabled": m.get("enabled", True),
            "interval": m.get("interval_minutes", 5),
            "url": m["url"],
            "current_value": last.get("value"),
            "last_check": last.get("timestamp"),
            "status": last.get("status", "pending"),
            "history": entries[-30:],  # last 30 for sparkline
        })
    return monitors


@app.route("/")
def index():
    monitors = load_data()
    return render_template("index.html", monitors=monitors)


@app.route("/api/status")
def api_status():
    return jsonify(load_data())


def run_dashboard():
    port = int(os.getenv("DASHBOARD_PORT", 5050))
    log.info(f"Dashboard starting on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)