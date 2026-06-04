# =============================================================================
#  analyzer.py — SysGuard AI
#  Sends system metrics to the Claude API and returns a plain-English
#  explanation with actionable recommendations for the user.
#
#  Prompt design follows best practices from:
#  github.com/zubair1811/awesome-ai-research-writing
#  — structured role assignment, explicit output format,
#    constraint-driven style control, and a self-review protocol.
# =============================================================================

import logging
import anthropic   # pip install anthropic

from config import ANTHROPIC_API_KEY, CLAUDE_MODEL

logger = logging.getLogger(__name__)

# Initialise the Anthropic client once at import time.
# The API key is read from the environment via config.py.
_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def _build_prompt(metrics: dict, exceeded: list[str]) -> str:
    """
    Construct the structured prompt sent to Claude.

    Parameters
    ----------
    metrics  : dict  — output of monitor.get_metrics()
    exceeded : list  — list of metric names that breached their threshold
                       e.g. ["cpu", "ram"]

    Returns
    -------
    str — the full prompt text
    """
    # Format the top-process list into a readable string
    proc_lines = "\n".join(
        f"  {i+1}. {p['name']} (PID {p['pid']}) "
        f"— Memory: {p['mem_percent']}%  CPU: {p['cpu_percent']}%"
        for i, p in enumerate(metrics["top_processes"])
    )

    exceeded_str = ", ".join(exceeded).upper()

    prompt = f"""# Role
You are a friendly and helpful system performance assistant running on the user's personal computer.
Your job is to explain computer performance problems in plain, jargon-free language and suggest practical fixes.

# Current System Metrics
- CPU usage:   {metrics['cpu']:.1f}%
- RAM usage:   {metrics['ram']:.1f}%  ({metrics['ram_used_gb']} GB used of {metrics['ram_total_gb']} GB)
- Disk usage:  {metrics['disk']:.1f}%  ({metrics['disk_used_gb']} GB used of {metrics['disk_total_gb']} GB)

Top {len(metrics['top_processes'])} processes by memory:
{proc_lines}

# Alert
The following thresholds have been exceeded: {exceeded_str}

# Task
In exactly 2-3 sentences, explain what is likely causing this problem in plain English — name specific processes if relevant.
Then give exactly 1-2 concrete, actionable steps the user can take right now to improve the situation.

# Constraints
- Friendly, calm tone. No alarm or panic.
- No technical jargon. Write as if explaining to a non-technical friend.
- Do NOT use bullet points or lists. Write in natural prose.
- Keep the entire response under 80 words.
- Do not mention thresholds, percentages, or raw numbers in the recommendation — just the action.

# Self-Review Protocol
Before responding, verify:
1. Is the tone calm and friendly?
2. Are there any jargon words that need replacing?
3. Is the total response under 80 words?
4. Are concrete process names mentioned where relevant?
"""
    return prompt


def analyze(metrics: dict, exceeded: list[str]) -> str:
    """
    Call the Claude API and return a plain-English explanation + recommendation.

    Parameters
    ----------
    metrics  : dict  — output of monitor.get_metrics()
    exceeded : list  — metric names that breached their threshold

    Returns
    -------
    str — the AI-generated explanation (ready to display as a notification)
    """
    prompt = _build_prompt(metrics, exceeded)

    logger.info("Calling Claude API for metrics analysis (exceeded: %s)", exceeded)

    try:
        message = _client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=200,
            messages=[
                {"role": "user", "content": prompt}
            ],
        )
        response_text = message.content[0].text.strip()
        logger.info("Claude response received (%d chars)", len(response_text))
        return response_text

    except anthropic.APIConnectionError as e:
        logger.error("Claude API connection failed: %s", e)
        return (
            f"Your {' and '.join(exceeded)} usage is high. "
            "Consider closing unused applications to free up resources."
        )
    except anthropic.RateLimitError:
        logger.warning("Claude API rate limit hit — using fallback message.")
        return (
            f"Your system is under heavy load ({', '.join(exceeded)} exceeded). "
            "Try closing some background applications."
        )
    except anthropic.APIStatusError as e:
        logger.error("Claude API error %s: %s", e.status_code, e.message)
        return (
            f"High {' and '.join(exceeded)} usage detected. "
            "Restarting heavy applications may help."
        )
