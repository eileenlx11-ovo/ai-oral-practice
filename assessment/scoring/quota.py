"""Azure pronunciation-assessment quota guard.

Azure Speech free tier (F0) allows ~5 audio hours/month. Each assessment call
bills against that. This module tracks monthly usage and, once a soft cap is
reached, lets the dispatcher skip Azure so it falls back to SOE instead of
failing or silently overrunning into paid (S0) territory.

Usage is persisted under data/ so it survives container restarts. Counting is
approximate (we estimate seconds from the wav size, since Azure does not return
billed duration), which is fine for a safety margin, not billing.

Env:
  AZURE_MONTHLY_SECONDS_CAP  soft cap in seconds (default 16200 = 4.5h, leaving
                             headroom under the 5h F0 limit).
"""
import json
import os
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

_DATA_DIR = Path(__file__).parent.parent / "data"
_USAGE_FILE = _DATA_DIR / "azure_usage.json"
_DEFAULT_CAP_SECONDS = 16200  # 4.5h, under the 5h F0 free-tier limit
_lock = threading.Lock()


def _cap_seconds() -> int:
    try:
        return int(os.getenv("AZURE_MONTHLY_SECONDS_CAP", _DEFAULT_CAP_SECONDS))
    except ValueError:
        return _DEFAULT_CAP_SECONDS


def _current_month() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m")


def _load() -> dict:
    try:
        with open(_USAGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save(data: dict) -> None:
    try:
        _DATA_DIR.mkdir(parents=True, exist_ok=True)
        tmp = _USAGE_FILE.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f)
        tmp.replace(_USAGE_FILE)
    except OSError:
        pass  # usage tracking must never break scoring


def seconds_used() -> float:
    """Seconds of Azure assessment consumed in the current month."""
    data = _load()
    if data.get("month") != _current_month():
        return 0.0
    return float(data.get("seconds", 0.0))


def under_cap() -> bool:
    """True if Azure still has monthly headroom (or tracking is disabled)."""
    return seconds_used() < _cap_seconds()


def record(seconds: float) -> None:
    """Add `seconds` to the current month's usage, resetting on month rollover."""
    if seconds <= 0:
        return
    with _lock:
        data = _load()
        month = _current_month()
        if data.get("month") != month:
            data = {"month": month, "seconds": 0.0}
        data["seconds"] = float(data.get("seconds", 0.0)) + seconds
        data["updated_at"] = time.time()
        _save(data)


def estimate_seconds(reference_text: str) -> float:
    """Estimate spoken duration from reference word count (~2 words/sec for a
    learner, rounded up). Audio-format independent, unlike a byte-size estimate
    which under-counts compressed webm/opus. Min 2s so very short refs still
    register against the cap."""
    words = len(reference_text.split())
    return max(2.0, words / 2.0)


def status() -> dict:
    """Human-readable quota snapshot for the /api/assess/status endpoint."""
    used = seconds_used()
    cap = _cap_seconds()
    return {
        "month": _current_month(),
        "azure_seconds_used": round(used, 1),
        "azure_seconds_cap": cap,
        "azure_under_cap": used < cap,
    }
