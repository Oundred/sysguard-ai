# =============================================================================
#  actions.py — SysGuard AI
#  Optional automatic actions the agent can suggest or perform.
#  All actions that modify the system REQUIRE explicit user confirmation.
#  Keep this module simple and safe — never kill a process without asking.
# =============================================================================

import logging
import os
import platform
import subprocess

logger = logging.getLogger(__name__)


# ── Safe read-only actions ────────────────────────────────────────────────────

def open_task_manager() -> None:
    """
    Open the native system process viewer.
    Windows → Task Manager, macOS → Activity Monitor, Linux → gnome-system-monitor.
    """
    system = platform.system()
    try:
        if system == "Windows":
            subprocess.Popen(["taskmgr"])
            logger.info("Action: opened Task Manager (Windows)")
        elif system == "Darwin":
            subprocess.Popen(["open", "-a", "Activity Monitor"])
            logger.info("Action: opened Activity Monitor (macOS)")
        else:
            # Try common Linux process viewers
            for viewer in ["gnome-system-monitor", "ksysguard", "htop"]:
                try:
                    subprocess.Popen([viewer])
                    logger.info("Action: opened %s (Linux)", viewer)
                    return
                except FileNotFoundError:
                    continue
            logger.warning("No supported process viewer found on Linux.")
    except Exception as e:
        logger.error("Failed to open task manager: %s", e)


def log_snapshot(metrics: dict) -> None:
    """
    Write a full metric snapshot to the log file at WARNING level.
    Useful for post-mortem analysis of what the system looked like during an alert.
    """
    procs = "; ".join(
        f"{p['name']} mem={p['mem_percent']}% cpu={p['cpu_percent']}%"
        for p in metrics.get("top_processes", [])
    )
    logger.warning(
        "SNAPSHOT — CPU=%.1f%% RAM=%.1f%% DISK=%.1f%% | Procs: %s",
        metrics["cpu"], metrics["ram"], metrics["disk"], procs,
    )


# ── Destructive actions (always require confirmation) ─────────────────────────

def suggest_kill(process_name: str, mem_percent: float) -> bool:
    """
    Ask the user via terminal whether to terminate a specific process.
    Returns True if the user confirmed and the process was killed, False otherwise.

    Parameters
    ----------
    process_name : str   — display name of the process (e.g. "chrome")
    mem_percent  : float — how much RAM it was using

    Notes
    -----
    This function uses a simple terminal prompt. In a full application you would
    replace this with a GUI dialog. The function never kills silently.
    """
    print(
        f"\n[SysGuard AI]  '{process_name}' is using {mem_percent:.1f}% of your RAM.\n"
        f"  Would you like to terminate it? (yes / no): ",
        end="",
    )
    try:
        answer = input().strip().lower()
    except (EOFError, KeyboardInterrupt):
        # Non-interactive environment — skip
        return False

    if answer not in ("yes", "y"):
        logger.info("User declined to kill process: %s", process_name)
        return False

    # Find and terminate the process by name
    import psutil
    killed = 0
    for proc in psutil.process_iter(["name", "pid"]):
        if proc.info["name"] == process_name:
            try:
                proc.terminate()
                killed += 1
                logger.warning(
                    "Action: terminated %s (PID %s) on user request",
                    process_name, proc.info["pid"],
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                logger.error("Could not terminate %s: %s", process_name, e)

    if killed:
        print(f"  Done — {killed} instance(s) of '{process_name}' terminated.")
        return True
    else:
        print(f"  '{process_name}' was not found or could not be terminated.")
        return False


def suggest_disk_cleanup() -> None:
    """
    Print a simple disk cleanup suggestion to the terminal.
    Does not delete anything — education only.
    """
    system = platform.system()
    print("\n[SysGuard AI — Disk Cleanup Suggestions]")
    if system == "Windows":
        print("  • Empty your Recycle Bin")
        print("  • Run Disk Cleanup: Start → search 'Disk Cleanup'")
        print("  • Delete files in C:\\Users\\<you>\\Downloads you no longer need")
    elif system == "Darwin":
        print("  • Empty Trash (right-click Trash icon → Empty Trash)")
        print("  • Check ~/Downloads and ~/Desktop for large old files")
        print("  • Use Finder → About This Mac → Storage → Manage for recommendations")
    else:
        print("  • Run: du -sh ~/* | sort -rh | head -10  to find large folders")
        print("  • Clear package cache: sudo apt clean  (Debian/Ubuntu)")
        print("  • Check /var/log for large log files")
    logger.info("Action: disk cleanup suggestions displayed")
