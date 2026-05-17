import json
import os
import time
import requests
from datetime import datetime
from functools import reduce
from monitor.detector import detect_anomalies
from monitor.alerter import dispatch_alert
from monitor.logger import get_logger


log = get_logger("poller")
HISTORY_FILE = "data/history.json"
MAX_HISTORY = 200

os.makedirs("data", exist_ok=True)

def _load_history() -> dict:
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE) as f:
            return json.load(f)
    return {}

def _save_history(history: dict):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def _extract_value(data: dict, path: str) -> float:
    """Traverse dot-notation path in nested dict, e.g. 'bitcoin.usd"""
    keys = path.split(".")
    value = reduce(lambda d, k: d[k], keys, data)
    return float(value)

def poll_monitor(monitor: dict):
    name = monitor["name"]
    url = monitor["url"]
    path = monitor["value_path"]
    rules = monitor.get("alert_rules", {})

    log.info(f"Polling [{name}] -> {url}")

    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": "api-monitor/1.0"})
        resp.raise_for_status()
        data = resp.json()
        value = _extract_value(data, path)
        status = "ok"
        log.info(f"[{name}] value = {value:,.4g}")
    except Exception as e:
        log.error(f"[{name}] fetch error: {e}")
        value = None
        status = "error"

    # Load history, append, trim
    history = _load_history()
    key = name
    if key not in history:
        history[key] = []

    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "value": value,
        "status": status
    }
    history[key].append(entry)
    history[key] = history[key][-MAX_HISTORY:]
    _save_history(history)

    # Run anamoly detection
    if value is not None:
        alerts = detect_anomalies(name, value, history[key][:-1], rules)
        for alert in alerts:
            dispatch_alert(alert, name)

    return entry
