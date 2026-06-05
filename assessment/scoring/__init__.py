"""Pronunciation assessment — multi-provider dispatcher.

Two tiers:
  - Standard (daily practice): Tencent SOE → mock
    Lower latency, generous quota, word-level scoring.
  - Advanced (detailed diagnosis): Azure → SOE → mock
    Prosody + miscue detection + phoneme scoring. Uses Azure F0 quota.

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

# Standard: SOE first (low latency, quota-friendly), mock as fallback.
_STANDARD_PROVIDERS = [tencent, mock]
# Advanced: Azure first (prosody + miscue), SOE and mock as fallback.
_ADVANCED_PROVIDERS = [azure, tencent, mock]


def _allow_mock() -> bool:
    """Mock is a dev/demo convenience. Disable in prod by setting
    PRONUNCIATION_ALLOW_MOCK=0 so a misconfigured deploy fails loudly
    (503) instead of silently serving fake scores."""
    return os.getenv("PRONUNCIATION_ALLOW_MOCK", "1") != "0"


def active_provider(advanced: bool = False) -> str | None:
    """Name of the provider that would handle a request right now (or None)."""
    providers = _ADVANCED_PROVIDERS if advanced else _STANDARD_PROVIDERS
    for p in providers:
        if p is mock and not _allow_mock():
            continue
        if p.available():
            return p.__name__.rsplit(".", 1)[-1]
    return None


async def assess_pronunciation(
    audio_path: str, reference_text: str, *, advanced: bool = False
) -> dict | None:
    """Run assessment through the first available provider.

    advanced=False (default): daily practice, SOE priority.
    advanced=True: detailed diagnosis with prosody/miscue (Azure priority).
    Returns None if no provider can serve.
    """
    providers = _ADVANCED_PROVIDERS if advanced else _STANDARD_PROVIDERS
    for p in providers:
        if p is mock and not _allow_mock():
            continue
        if not p.available():
            continue
        result = await p.assess(audio_path, reference_text)
        if result is not None:
            return result
    return None
