import os
import threading
import schedule
import time
import yaml
from dotenv import load_dotenv
from monitor.poller import poll_monitor
from monitor.logger import get_logger
from dashboard.app import run_dashboard

load_dotenv()
log = get_logger("main")

def load_config(path="config/monitors.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)
    
def schedule_monitors(monitors: list):
    for m in monitors:
        if not m.get("enabled", True):
            log.info(f"Skipping disabled monitor: {m['name']}")
            continue
        interval = m.get("interval_minutes", 5)

        poll_monitor(m)
        schedule.every(interval).minutes.do(poll_monitor, monitor = m)
        log.info(f"Scheduled [{m['name']}] every {interval} minutes")

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(10)

if __name__ == "__main__":
    log.info("=== API Monitor Starting ===")
    cfg = load_config()
    monitors = cfg.get("monitors", [])

    schedule_monitors(monitors)

    # Dashboard in background thread
    dash_thread = threading.Thread(target=run_dashboard, daemon=True)
    dash_thread.start()

    log.info("Scheduler running. Press Ctrl + C to stop.")
    try:
        run_scheduler()
    except KeyboardInterrupt:
        log.info("Monitor Stopped")