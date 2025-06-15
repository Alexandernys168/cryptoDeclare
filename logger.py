"""Utility for appending execution logs to logg.md."""

from datetime import datetime

LOG_FILE = "logg.md"


def log_run(message: str) -> None:
    """Append a timestamped message to the log file."""
    timestamp = datetime.utcnow().isoformat()
    entry = f"### {timestamp}\n- {message}\n\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry)


def log_divider() -> None:
    """Add a divider for readability between runs."""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write("---\n")
