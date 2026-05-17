# ⚡ API Data Monitor + Alerter

A Python-based monitoring daemon that polls APIs on a schedule, detects anomalies in the data, and sends alerts via Email or Telegram. Includes a live web dashboard to visualize monitor status and history.

---

## 🔍 What It Does

- **Polls any JSON API** on a configurable interval (every N minutes)
- **Detects anomalies** using three rules: percentage spike, min/max bounds, and statistical z-score
- **Sends alerts** via Gmail (SMTP) or Telegram Bot when anomalies are detected
- **Logs all events** to console and a rotating log file
- **Serves a live dashboard** at `http://localhost:5050` with sparkline charts and status badges

---

## 🗂️ Project Structure

```
api-monitor/
├── monitor/
│   ├── __init__.py
│   ├── poller.py          # Fetches API data on schedule
│   ├── detector.py        # Anomaly detection logic
│   ├── alerter.py         # Email + Telegram alerts
│   └── logger.py          # Centralized logging
├── dashboard/
│   ├── app.py             # Flask dashboard server
│   └── templates/
│       └── index.html     # Live status page
├── config/
│   └── monitors.yaml      # Define what APIs to watch
├── data/
│   └── history.json       # Rolling data store (auto-created)
├── logs/
│   └── monitor.log        # Auto-created
├── .env                   # Your real secrets (never committed)
├── .env.example           # Safe template for collaborators
├── .gitignore
├── requirements.txt
├── main.py                # Entry point
└── README.md
```

---

## ⚙️ How It Works

```
Poll API → Extract Value → Store in history.json
                                    ↓
                          Run Anomaly Detection
                          ┌─────────────────────┐
                          │ • % spike check      │
                          │ • min/max bounds     │
                          │ • z-score check      │
                          └─────────────────────┘
                                    ↓
                     Anomaly found? → Send Alert
                     (Email and/or Telegram)
                                    ↓
                     Dashboard reads history.json
                     → Renders live at :5050
```

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/api-monitor.git
cd api-monitor
```

### 2. Create and activate virtual environment

```bash
python -m venv venv

# Mac/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in your real credentials (see Configuration section below).

### 5. Initialize history file

```bash
echo {} > data/history.json
```

### 6. Run the monitor

```bash
python main.py
```

### 7. Open the dashboard

Visit **http://localhost:5050** in your browser.

---

## 🔧 Configuration

### `.env` — Alert Credentials

```env
# Email (Gmail)
EMAIL_ENABLED=true
EMAIL_SENDER=your_gmail@gmail.com
EMAIL_PASSWORD=your_16_char_app_password
EMAIL_RECIPIENT=recipient@example.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587

# Telegram Bot
TELEGRAM_ENABLED=false
TELEGRAM_BOT_TOKEN=123456:ABC-your-token
TELEGRAM_CHAT_ID=your_chat_id

# Dashboard
DASHBOARD_PORT=5050
```

> You can enable one or both alert channels independently.

### Getting a Gmail App Password

1. Go to [myaccount.google.com](https://myaccount.google.com) → Security
2. Enable **2-Step Verification**
3. Search for **App Passwords** → create one named `api-monitor`
4. Paste the 16-character password into `EMAIL_PASSWORD` (no spaces)

### Getting a Telegram Bot Token

1. Message `@BotFather` on Telegram → `/newbot`
2. Copy the bot token into `TELEGRAM_BOT_TOKEN`
3. Send your bot any message, then visit:
   `https://api.telegram.org/bot<TOKEN>/getUpdates`
4. Copy `chat.id` into `TELEGRAM_CHAT_ID`

---

### `config/monitors.yaml` — What to Monitor

```yaml
monitors:
  - name: "USD to EUR Rate"
    enabled: true
    url: "https://open.er-api.com/v6/latest/USD"
    interval_minutes: 2
    value_path: "rates.EUR"       # dot-notation path into JSON response
    alert_rules:
      spike_percent: 1.0          # alert if changes more than 1% since last check
      min_value: 0.80             # alert if below this
      max_value: 1.20             # alert if above this
```

| Field | Description |
|---|---|
| `url` | Any public JSON API endpoint |
| `interval_minutes` | How often to poll |
| `value_path` | Dot-notation path to the numeric value in the response |
| `spike_percent` | Alert if value changes by this % since last poll |
| `min_value` / `max_value` | Hard bounds — alert if breached |
| `zscore_threshold` | Alert if z-score exceeds this (requires 10+ data points) |

---

## 📊 Anomaly Detection Rules

| Rule | How It Works |
|---|---|
| **Spike %** | Compares current value to last reading. Alerts if change ≥ threshold. |
| **Min/Max bounds** | Alerts if value goes outside defined absolute limits. |
| **Z-score** | Compares value to statistical mean of last 50 readings. Alerts if z-score ≥ threshold. Needs at least 10 data points to activate. |

---

## 🖥️ Dashboard

The dashboard auto-refreshes every 30 seconds and shows:

- Current value for each monitor
- Status badge (`OK` / `ERROR` / `PENDING`)
- Poll interval and last check time
- Sparkline chart of recent values
- JSON API available at `/api/status`

---

## ➕ Adding Your Own API

Add a new block to `config/monitors.yaml`:

```yaml
- name: "My Custom API"
  enabled: true
  url: "https://yourapi.com/endpoint"
  interval_minutes: 5
  value_path: "data.count"
  alert_rules:
    spike_percent: 10.0
    zscore_threshold: 3.0
```

No code changes needed — the poller handles it automatically.

---

## 🔗 Data Engineering Concepts Demonstrated

| This Project | Real-World Equivalent |
|---|---|
| `poller.py` — API polling | Airbyte / Kafka Connect ingestion |
| `history.json` — append-only store | S3 Bronze layer / Delta Lake |
| `detector.py` — anomaly rules | Great Expectations / dbt tests |
| `alerter.py` — notifications | Monte Carlo / PagerDuty |
| `main.py` — scheduler | Apache Airflow DAGs / Prefect flows |
| Flask dashboard | Metabase / Superset serving layer |

This project demonstrates the full DE pipeline lifecycle: **Ingest → Store → Validate → Alert → Serve**

---

## 📁 Key Files

| File | Purpose |
|---|---|
| `main.py` | Entry point. Loads config, schedules monitors, starts dashboard. |
| `monitor/poller.py` | Fetches API data, stores to history, triggers detection. |
| `monitor/detector.py` | Runs spike, bounds, and z-score anomaly checks. |
| `monitor/alerter.py` | Sends email and/or Telegram alerts. |
| `dashboard/app.py` | Flask server for the live dashboard. |
| `config/monitors.yaml` | Declarative config — define monitors without touching code. |

---

## 🛠️ Requirements

- Python 3.10+
- Internet access to target APIs
- Gmail account with App Password (for email alerts)
- Telegram account + Bot (for Telegram alerts)

---

## 📄 License

MIT License — free to use, modify, and distribute.
