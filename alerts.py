# =============================================================================
#  alerts.py — SysGuard AI
#  Sends desktop push notifications via plyer and writes every alert to the
#  log file. Tracks cooldown state so the same metric is not spammed.
# =============================================================================

import logging
import time

from plyer import notification   # pip install plyer

from config import (
    NOTIFICATION_TITLE,
    NOTIFICATION_TIMEOUT,
    ALERT_COOLDOWN_SECONDS,
)

logger = logging.getLogger(__name__)

# ── Cooldown tracker ──────────────────────────────────────────────────────────
# Maps metric name → unix timestamp of the last alert sent for that metric.
_last_alert_time: dict[str, float] = {}


def _is_on_cooldown(metric: str) -> bool:
    """Return True if the given metric is still within its cooldown window."""
    last = _last_alert_time.get(metric, 0.0)
    return (time.time() - last) < ALERT_COOLDOWN_SECONDS


def _mark_alerted(metrics_exceeded: list[str]) -> None:
    """Record the current time as the last alert time for each metric."""
    now = time.time()
    for metric in metrics_exceeded:
        _last_alert_time[metric] = now


def send_alert(message: str, exceeded: list[str]) -> bool:
    """
    Fire a desktop notification and log the alert.

    Parameters
    ----------
    message  : str  — the AI-generated explanation from analyzer.py
    exceeded : list — metric names that triggered the alert (for cooldown logic)

    Returns
    -------
    bool — True if the notification was sent, False if suppressed by cooldown
    """
    # Check if ALL exceeded metrics are still on cooldown
    all_on_cooldown = all(_is_on_cooldown(m) for m in exceeded)
    if all_on_cooldown:
        logger.debug(
            "Alert suppressed by cooldown (exceeded: %s)", exceeded
        )
        return False

    # Fire the desktop notification
    try:
        notification.notify(
            title=NOTIFICATION_TITLE,
            message=message,
            app_name="SysGuard AI",
            timeout=NOTIFICATION_TIMEOUT,
        )
        logger.warning("ALERT SENT — %s | %s", exceeded, message)
        _mark_alerted(exceeded)
        return True

    except Exception as e:
        # plyer can fail on headless systems or unsupported platforms
        logger.error("Failed to send desktop notification: %s", e)
        # Still log the alert content even if the notification failed
        logger.warning("ALERT (no notification) — %s | %s", exceeded, message)
        _mark_alerted(exceeded)
        return False


def send_info(message: str) -> None:
    """
    Send a non-critical informational notification (no cooldown applied).
    Useful for startup messages or recovery notices.
    """
    try:
        notification.notify(
            title="SysGuard AI",
            message=message,
            app_name="SysGuard AI",
            timeout=NOTIFICATION_TIMEOUT,
        )
        logger.info("INFO notification sent: %s", message)
    except Exception as e:
        logger.debug("Info notification failed: %s", e)
