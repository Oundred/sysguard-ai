# =============================================================================
#  main.py — SysGuard AI
#  Entry point. Starts the monitoring loop that:
#    1. Samples system metrics every POLL_INTERVAL_SECONDS
#    2. Checks whether any metric exceeds its configured threshold
#    3. If so, asks Claude to explain the problem in plain English
#    4. Sends a desktop notification with Claude's recommendation
#    5. Logs every event to logs/sysguard.log
#
#  Usage:
#    python main.py
#  Stop with:
#    Ctrl+C
# =============================================================================

import logging
import os
import sys
import time

import schedule   # pip install schedule

from config import (
    POLL_INTERVAL_SECONDS,
    THRESHOLDS,
    LOG_FILE,
    LOG_LEVEL,
    ANTHROPIC_API_KEY,
)
from monitor  import get_metrics, format_metrics_summary
from analyzer import analyze
from alerts   import send_alert, send_info
from actions  import log_snapshot, open_task_manager, suggest_disk_cleanup


# ── Logging setup ─────────────────────────────────────────────────────────────
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),   # also print to terminal
    ],
)
logger = logging.getLogger("main")


# ── Pre-flight checks ─────────────────────────────────────────────────────────

def _check_config() -> bool:
    """Validate that required configuration is present before starting."""
    if not ANTHROPIC_API_KEY:
        logger.error(
            "ANTHROPIC_API_KEY is not set. "
            "Add it to a .env file or export it as an environment variable."
        )
        return False
    return True


# ── Core agent tick ───────────────────────────────────────────────────────────

def run_agent() -> None:
    """
    One full monitoring cycle:
      collect → check thresholds → (if exceeded) analyse → alert → log
    """
    metrics = get_metrics()
    summary = format_metrics_summary(metrics)
    logger.info(summary)

    # Find which metrics have exceeded their thresholds
    exceeded = [
        key for key, threshold in THRESHOLDS.items()
        if metrics.get(key, 0.0) > threshold
    ]

    if not exceeded:
        # System is healthy — nothing to do
        print(f"  ✓  {summary}")
        return

    # ── Something is wrong — get Claude's explanation ──────────────────────
    print(f"\n  ⚠  Alert triggered: {exceeded}")
    logger.warning("Threshold exceeded: %s | %s", exceeded, summary)

    # Take a full snapshot for the log (useful for later review)
    log_snapshot(metrics)

    # Get the AI explanation from Claude
    explanation = analyze(metrics, exceeded)

    # Send the desktop notification
    sent = send_alert(explanation, exceeded)
    if sent:
        print(f"  → Notification sent:\n     \"{explanation}\"")

    # ── Optional automatic actions ─────────────────────────────────────────
    # Suggest disk cleanup if disk usage is one of the exceeded metrics
    if "disk" in exceeded:
        suggest_disk_cleanup()

    # Open the system task manager if CPU or RAM is critically high (>= 95%)
    if metrics.get("cpu", 0) >= 95 or metrics.get("ram", 0) >= 95:
        logger.info("Critical usage detected — opening task manager")
        open_task_manager()

    print()


# ── Main entry point ──────────────────────────────────────────────────────────

def main() -> None:
    logger.info("=" * 60)
    logger.info("SysGuard AI — starting up")
    logger.info("Poll interval : %d seconds", POLL_INTERVAL_SECONDS)
    logger.info("Thresholds    : %s", THRESHOLDS)
    logger.info("=" * 60)

    if not _check_config():
        sys.exit(1)

    # Send a startup notification so the user knows the agent is running
    send_info(
        f"SysGuard AI is now monitoring your system "
        f"(CPU > {THRESHOLDS['cpu']}%, RAM > {THRESHOLDS['ram']}%, "
        f"Disk > {THRESHOLDS['disk']}%)."
    )

    # ── Schedule the agent tick ────────────────────────────────────────────
    schedule.every(POLL_INTERVAL_SECONDS).seconds.do(run_agent)

    # Run once immediately so there is no wait at startup
    run_agent()

    print(
        f"\nSysGuard AI is running. "
        f"Checking every {POLL_INTERVAL_SECONDS}s. "
        "Press Ctrl+C to stop.\n"
    )

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("SysGuard AI stopped by user.")
        print("\nSysGuard AI stopped.")


if __name__ == "__main__":
    main()
