"""Pronunciation assessment — multi-provider dispatcher.

Tries providers in priority order and returns the first real result:
    Azure (strongest: prosody + phoneme + miscue)
      → Tencent SOE (domestic fallback, China-accessible)
      → mock (always available; lets the UI work with no keys)

Each provider module exposes:
    available() -> bool
    async assess(audio_path, reference_text) -> dict | None

Returned dict schema (uniform across providers):
    {accuracy_score, fluency_score, completeness_score,
     pronunciation_score, words: [{word, accuracy_score, error_type}],
     provider}
All scores are 0-100.
"""
import os

from . import azure, tencent, mock

# Order = preference. mock is last so it only fires when nothing else can.
_PROVIDERS = [azure, tencent, mock]


def _allow_mock() -> bool:
    """Mock is a dev/demo convenience. Disable in prod by setting
    PRONUNCIATION_ALLOW_MOCK=0 so a misconfigured deploy fails loudly
    (503) instead of silently serving fake scores."""
    return os.getenv("PRONUNCIATION_ALLOW_MOCK", "1") != "0"


def active_provider() -> str | None:
    """Name of the provider that would handle a request right now (or None)."""
    for p in _PROVIDERS:
        if p is mock and not _allow_mock():
            continue
        if p.available():
            return p.__name__.rsplit(".", 1)[-1]
    return None


async def assess_pronunciation(audio_path: str, reference_text: str) -> dict | None:
    """Run assessment through the first available provider. Returns None if
    none can serve (real providers unconfigured AND mock disabled)."""
    for p in _PROVIDERS:
        if p is mock and not _allow_mock():
            continue
        if not p.available():
            continue
        result = await p.assess(audio_path, reference_text)
        if result is not None:
            return result
    return None
