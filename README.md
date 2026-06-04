<div align="center">

# 🛡️ SysGuard AI

### An Intelligent System Monitoring Agent

**Python** · **psutil** · **Claude API** · **plyer** · **schedule** · **logging**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Claude API](https://img.shields.io/badge/Claude-API-orange?logo=anthropic&logoColor=white)](https://www.anthropic.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

> *"Your computer, explained in plain English."*

SysGuard AI is a lightweight desktop agent that continuously watches your computer's vital signs — CPU, RAM, and disk usage — detects heavy processes, and uses the **Claude API** to generate plain-English explanations and actionable recommendations whenever something goes wrong.  
Alerts are delivered as native desktop notifications in real time.

---

[Features](#-features) · [Demo](#-demo) · [Installation](#-installation) · [Configuration](#%EF%B8%8F-configuration) · [Usage](#-usage) · [Architecture](#-architecture) · [Project Structure](#-project-structure) · [Roadmap](#-roadmap) · [Author](#-author)

</div>

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔍 **Real-time monitoring** | Samples CPU, RAM, disk, and top processes every 30 seconds |
| 🤖 **AI-powered alerts** | Uses Claude to translate raw numbers into plain-English advice |
| 🖥️ **Desktop notifications** | Native push notifications on Windows, macOS, and Linux |
| ⚙️ **Configurable thresholds** | Tune alert levels for CPU (>85%), RAM (>80%), Disk (>90%) |
| 🔕 **Smart cooldown** | No spam — the same alert won't fire twice within 2 minutes |
| 📋 **Persistent logging** | Every alert and metric snapshot is saved to `logs/sysguard.log` |
| 🛠️ **Optional auto-actions** | Can open Task Manager or suggest disk cleanup steps |
| 🪶 **Zero infrastructure** | Runs entirely on your local machine — no Docker, no cloud needed |

---

## 🎬 Demo

```
[10:42:15]  INFO     main — CPU: 91.0%  |  RAM: 87.3% (13.97 / 16.0 GB)  |  Disk: 72.1%

  ⚠  Alert triggered: ['cpu', 'ram']

  → Notification sent:
     "Chrome is consuming over a third of your available memory, likely due to many
      open tabs or extensions running in the background. Try closing unused tabs or
      restarting Chrome. If your Python script does not need to stay open, closing
      it will also help."
```

**Before SysGuard AI:**  you notice your laptop is slow, spend 5–20 minutes debugging, find nothing useful.

**After SysGuard AI:**  a desktop notification tells you *exactly* which process is causing the problem and what to do about it — within 30 seconds.

---

## 📋 Requirements

- Python **3.10** or higher
- An **Anthropic API key** — get one at [console.anthropic.com](https://console.anthropic.com)
- Operating system: **Windows**, **macOS**, or **Linux**

---

## 🚀 Installation

### 1 — Clone the repository

```bash
git clone https://github.com/your-username/sysguard-ai.git
cd sysguard-ai
```

### 2 — Create a virtual environment (recommended)

```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### 4 — Set up your API key

```bash
# Copy the example environment file
cp .env.example .env

# Open .env and paste your Anthropic API key
# ANTHROPIC_API_KEY=sk-ant-...
```

> **Never commit your `.env` file.** It is already listed in `.gitignore`.

---

## ⚙️ Configuration

All settings live in **`config.py`**. Edit this file to tune the agent without touching any other module.

```python
# Alert thresholds (%)
THRESHOLDS = {
    "cpu":  85.0,   # fire an alert when CPU exceeds this
    "ram":  80.0,   # fire an alert when RAM exceeds this
    "disk": 90.0,   # fire an alert when Disk exceeds this
}

# How often to sample the system (seconds)
POLL_INTERVAL_SECONDS = 30

# Minimum seconds between two alerts for the same metric
ALERT_COOLDOWN_SECONDS = 120

# How many top processes to include in the AI prompt
TOP_PROCESS_COUNT = 5
```

---

## ▶️ Usage

```bash
python main.py
```

The agent will:
1. Send a startup desktop notification confirming it is running.
2. Sample your system every `POLL_INTERVAL_SECONDS` seconds.
3. Silently log metrics when everything is healthy.
4. Call the Claude API and fire a desktop notification when a threshold is exceeded.

**Stop the agent:**

```bash
Ctrl + C
```

**View the log file:**

```bash
# macOS / Linux
tail -f logs/sysguard.log

# Windows
Get-Content logs\sysguard.log -Wait
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  System Hardware                         │
│         CPU  ·  RAM  ·  Disk  ·  Running Processes      │
└──────────┬──────────────┬──────────────┬────────────────┘
           │   psutil     │              │
           ▼              ▼              ▼
┌─────────────────────────────────────────────────────────┐
│                     monitor.py                           │
│         Collect & structure metrics every 30 s           │
└────────────────────────┬────────────────────────────────┘
                         │  metrics dict
                         ▼
┌─────────────────────────────────────────────────────────┐
│              config.py — Threshold Check                 │
│         CPU > 85%  ·  RAM > 80%  ·  Disk > 90%          │
└──────┬──────────────────────────────────────────────────┘
       │ exceeded                         │ OK
       ▼                                  ▼
┌─────────────────────────┐         ┌──────────┐
│  analyzer.py ↔ Claude   │         │  Wait    │
│  Prompt + AI response   │         │  30 s ↺  │
└────────────┬────────────┘         └──────────┘
             │ AI explanation text
             ▼
┌────────────────┬─────────────────┬──────────────────┐
│   alerts.py    │   actions.py    │  sysguard.log     │
│  Notification  │  Auto-actions   │  Event logging    │
└───────┬────────┴─────────────────┴──────────────────┘
        │ desktop notification
        ▼
┌─────────────────────────────────────────────────────────┐
│                        User                              │
│     Reads AI advice  ·  Takes action  ·  System OK       │
└─────────────────────────────────────────────────────────┘

         ↺  main.py orchestrates — loop repeats every 30 s
```

---

## 📁 Project Structure

```
sysguard-ai/
│
├── main.py            ← Entry point — starts the agent loop
├── monitor.py         ← Collects CPU, RAM, disk, and process data (psutil)
├── analyzer.py        ← Builds the Claude prompt and returns AI explanation
├── alerts.py          ← Fires desktop notifications (plyer) + cooldown logic
├── actions.py         ← Optional automatic actions (Task Manager, disk tips)
├── config.py          ← Central settings: thresholds, intervals, API key ref
│
├── requirements.txt   ← Python dependencies
├── .env.example       ← Environment variable template
├── .env               ← Your API key (NOT committed — in .gitignore)
│
├── logs/
│   └── sysguard.log   ← All events and alerts logged here (auto-created)
│
└── README.md
```

---

## 🧰 Tech Stack

| Library | Version | Purpose |
|---|---|---|
| [psutil](https://pypi.org/project/psutil/) | ≥ 5.9 | Collect OS-level system metrics |
| [anthropic](https://pypi.org/project/anthropic/) | ≥ 0.20 | Call the Claude API |
| [plyer](https://pypi.org/project/plyer/) | ≥ 2.1 | Native desktop notifications |
| [schedule](https://pypi.org/project/schedule/) | ≥ 1.2 | Pure-Python job scheduler |
| [python-dotenv](https://pypi.org/project/python-dotenv/) | ≥ 1.0 | Load API key from `.env` file |

---

## 🗺️ Roadmap

- [x] CPU, RAM, disk monitoring
- [x] AI-powered plain-English alerts via Claude
- [x] Desktop push notifications (Windows / macOS / Linux)
- [x] Configurable thresholds
- [x] Alert cooldown to prevent spam
- [x] Persistent event logging
- [x] Optional automatic actions
- [ ] Terminal live dashboard using `rich`
- [ ] Email / Telegram remote alerts
- [ ] Historical CPU & RAM trend charts (`matplotlib`)
- [ ] Process allowlist / blocklist
- [ ] Scheduled quiet hours (e.g. silent between 11 pm and 8 am)

---

## 🤝 Contributing

Contributions, bug reports, and feature suggestions are welcome!  
Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

```bash
# Fork the repo, then:
git checkout -b feature/your-feature-name
git commit -m "feat: add your feature"
git push origin feature/your-feature-name
# Open a Pull Request
```

---

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

## 👤 Author

**André PEAQUIN** · Student ID `26040040`

> University project submission — AI Agent Development  
> Prompt engineering practices based on [zubair1811/awesome-ai-research-writing](https://github.com/zubair1811/awesome-ai-research-writing)

---

<div align="center">

Made with ❤️ and Python · Powered by [Claude](https://www.anthropic.com/)

</div>
