# Contributing to SysGuard AI

Thank you for your interest in contributing! This document explains how to
report bugs, suggest features, and submit pull requests.

---

## 🐛 Reporting a Bug

1. Check [existing issues](../../issues) — it may already be reported.
2. Open a **new issue** and include:
   - Your OS and Python version (`python --version`)
   - The exact error message or unexpected behaviour
   - Steps to reproduce the problem
   - The relevant section of `logs/sysguard.log` if available

---

## 💡 Suggesting a Feature

Open an issue with the label **enhancement** and describe:
- What you want the agent to do
- Why it would be useful
- Any libraries or approaches you have in mind

---

## 🔧 Submitting a Pull Request

1. **Fork** the repository and create your branch from `main`:

   ```bash
   git checkout -b feature/short-description
   ```

2. **Make your changes** — keep each commit focused on one thing.

3. **Follow the code style:**
   - PEP 8 formatting
   - Descriptive variable names
   - Docstrings on every public function (Google style)
   - Type hints where practical

4. **Test your changes** manually:
   - Run `python main.py` and confirm the agent loop starts cleanly
   - Lower a threshold in `config.py` temporarily to trigger and verify an alert

5. **Commit** with a clear message:

   ```
   feat: add Telegram alert support
   fix: prevent duplicate alerts on startup
   docs: update README installation steps
   ```

6. **Push** and open a Pull Request against `main`.

---

## 📁 Key Files to Know

| File | What it does |
|---|---|
| `config.py` | All settings — start here before touching other files |
| `monitor.py` | All psutil calls — add new metrics here |
| `analyzer.py` | Claude prompt — improve the AI output here |
| `alerts.py` | Notification logic — add new notification channels here |
| `actions.py` | Optional actions — safe and user-confirmed only |

---

## 🙏 Code of Conduct

Be respectful, constructive, and patient. This is a student project — all skill
levels are welcome.
