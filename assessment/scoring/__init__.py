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
import logging
import os

from . import azure, tencent, mock

# Self-contained logger with its own stream handler. app.py's lifespan only wires
# the `assessment` logger to uvicorn handlers IF they already exist at startup,
# which on this deploy they don't — so request-flow INFO logs were invisible. This
# dedicated handler guarantees provider/score diagnostics reach `docker logs`.
logger = logging.getLogger("assessment.scoring")
if not logger.handlers:
    _h = logging.StreamHandler()
    _h.setFormatter(logging.Formatter("%(levelname)s:%(name)s:%(message)s"))
    logger.addHandler(_h)
    logger.setLevel(logging.INFO)
    logger.propagate = False

# Standard: Azure first. The VPS->Tencent SOE path has 4-20s TLS handshakes
# (measured) and SOE's completeness multiplier crushes scores when the flaky link
# truncates audio; Azure (koreacentral) handshakes in ~0.1s and scores reliably.
# SOE stays as fallback, mock last.
_STANDARD_PROVIDERS = [azure, tencent, mock]
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
        try:
            result = await p.assess(audio_path, reference_text)
        except Exception as exc:
            logger.info("provider %s raised %s: %s",
                        p.__name__.rsplit(".", 1)[-1], type(exc).__name__, str(exc)[:200])
            continue
        if result is not None:
            n_phones = sum(len(w.get("phones", [])) for w in result.get("words", []))
            logger.info("ASSESS provider=%s score=%s completeness=%s words=%d phones=%d",
                        result.get("provider"), result.get("pronunciation_score"),
                        result.get("completeness_score"), len(result.get("words", [])), n_phones)
            return result
    return None
