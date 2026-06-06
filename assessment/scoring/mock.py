"""Mock pronunciation provider.

Deterministic fake scores so the frontend pronunciation UI can be built and
demoed without any API key. Always available — acts as the last-resort fallback.
Scores derive from word length (no RNG), so results are reproducible in tests.
"""


def available() -> bool:
    return True


async def assess(audio_path: str, reference_text: str) -> dict:
    raw_words = [w.strip(".,!?;:\"'").lower() for w in reference_text.split()]
    raw_words = [w for w in raw_words if w]

    words = []
    for w in raw_words:
        # Longer words score slightly lower; clamp to 60-98.
        score = max(60.0, 98.0 - len(w) * 2.5)
        words.append({
            "word": w,
            "accuracy_score": round(score, 1),
            "error_type": "None" if score >= 70 else "Mispronunciation",
        })

    avg = round(sum(x["accuracy_score"] for x in words) / len(words), 1) if words else 0.0
    return {
        "accuracy_score": avg,
        "fluency_score": 85.0,
        "completeness_score": 100.0,
        "pronunciation_score": avg,
        "words": words,
        "provider": "mock",
    }
