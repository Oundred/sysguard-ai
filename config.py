# =============================================================================
#  config.py — SysGuard AI
#  Central configuration: thresholds, API key, and agent settings.
#  Edit this file to tune the agent behaviour without touching other modules.
# =============================================================================

import os
from dotenv import load_dotenv   # pip install python-dotenv

# Load ANTHROPIC_API_KEY from a .env file if present
load_dotenv()

# ── Claude API ────────────────────────────────────────────────────────────────
# Set ANTHROPIC_API_KEY in your environment or in a .env file:
#   ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL: str = "claude-sonnet-4-5"  # fast and cost-effective for alerts

# ── Alert thresholds (%) ──────────────────────────────────────────────────────
# The agent fires an alert only when a metric exceeds these values.
THRESHOLDS: dict[str, float] = {
    "cpu":  85.0,   # CPU usage  (%)
    "ram":  80.0,   # RAM usage  (%)
    "disk": 90.0,   # Disk usage (%)
}

# ── Agent loop settings ───────────────────────────────────────────────────────
POLL_INTERVAL_SECONDS: int = 30   # how often to sample the system
TOP_PROCESS_COUNT:     int = 5    # how many top processes to report

# ── Alert cooldown ────────────────────────────────────────────────────────────
# Minimum seconds between two alerts for the same metric.
# Prevents the agent from spamming notifications every 30 s.
ALERT_COOLDOWN_SECONDS: int = 120

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_FILE: str = "logs/sysguard.log"
LOG_LEVEL: str = "INFO"   # DEBUG | INFO | WARNING | ERROR

# ── Notification settings ─────────────────────────────────────────────────────
NOTIFICATION_TITLE:   str = "⚠  SysGuard AI Alert"
NOTIFICATION_TIMEOUT: int = 8   # seconds the desktop notification stays visible
