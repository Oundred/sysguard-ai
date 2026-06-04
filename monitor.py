# =============================================================================
#  monitor.py — SysGuard AI
#  Collects CPU, RAM, disk, and process metrics using psutil.
#  Returns a clean dictionary ready to be passed to analyzer.py.
# =============================================================================

import logging
import psutil   # pip install psutil

from config import TOP_PROCESS_COUNT

logger = logging.getLogger(__name__)


def get_metrics() -> dict:
    """
    Sample all system metrics and return them as a structured dictionary.

    Returns
    -------
    dict with keys:
        cpu         (float)  — CPU usage in percent
        ram         (float)  — RAM usage in percent
        ram_used_gb (float)  — RAM used in GB
        ram_total_gb(float)  — RAM total in GB
        disk        (float)  — Disk usage in percent (root partition)
        disk_used_gb(float)  — Disk used in GB
        disk_total_gb(float) — Disk total in GB
        top_processes(list)  — List of dicts {name, pid, mem_percent, cpu_percent}
    """
    # ── CPU ───────────────────────────────────────────────────────────────────
    cpu_percent = psutil.cpu_percent(interval=1)   # 1-second blocking sample

    # ── RAM ───────────────────────────────────────────────────────────────────
    ram = psutil.virtual_memory()
    ram_percent    = ram.percent
    ram_used_gb    = round(ram.used  / (1024 ** 3), 2)
    ram_total_gb   = round(ram.total / (1024 ** 3), 2)

    # ── Disk (root partition) ─────────────────────────────────────────────────
    disk = psutil.disk_usage("/")
    disk_percent   = disk.percent
    disk_used_gb   = round(disk.used  / (1024 ** 3), 2)
    disk_total_gb  = round(disk.total / (1024 ** 3), 2)

    # ── Top processes by memory ───────────────────────────────────────────────
    processes = []
    for proc in psutil.process_iter(["pid", "name", "memory_percent", "cpu_percent"]):
        try:
            info = proc.info
            if info["memory_percent"] is not None:
                processes.append({
                    "name":        info["name"],
                    "pid":         info["pid"],
                    "mem_percent": round(info["memory_percent"], 2),
                    "cpu_percent": round(info["cpu_percent"] or 0.0, 2),
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # Process may have ended between the iter call and info access
            continue

    # Sort by memory usage descending and keep the top N
    top_processes = sorted(processes, key=lambda p: p["mem_percent"], reverse=True)[
        :TOP_PROCESS_COUNT
    ]

    metrics = {
        "cpu":            cpu_percent,
        "ram":            ram_percent,
        "ram_used_gb":    ram_used_gb,
        "ram_total_gb":   ram_total_gb,
        "disk":           disk_percent,
        "disk_used_gb":   disk_used_gb,
        "disk_total_gb":  disk_total_gb,
        "top_processes":  top_processes,
    }

    logger.debug(
        "Metrics sampled — CPU: %.1f%%  RAM: %.1f%%  Disk: %.1f%%",
        cpu_percent, ram_percent, disk_percent,
    )
    return metrics


def format_metrics_summary(metrics: dict) -> str:
    """Return a short human-readable summary string (used in terminal output)."""
    procs = ", ".join(
        f"{p['name']} ({p['mem_percent']}%)" for p in metrics["top_processes"]
    )
    return (
        f"CPU: {metrics['cpu']:.1f}%  |  "
        f"RAM: {metrics['ram']:.1f}% ({metrics['ram_used_gb']} / {metrics['ram_total_gb']} GB)  |  "
        f"Disk: {metrics['disk']:.1f}% ({metrics['disk_used_gb']} / {metrics['disk_total_gb']} GB)  |  "
        f"Top processes: {procs}"
    )
