# Pronunciation Scoring

Azure Speech Pronunciation Assessment integration.

## API

- `POST /api/assess` — Evaluate pronunciation of a known reference text
  - Input: `audio` (file), `reference_text` (str)
  - Output: `PronunciationScore` (accuracy, fluency, completeness, per-word scores)

## Implementation

Uses Azure Cognitive Services Speech SDK for phoneme-level assessment.
Scoring dimensions: accuracy, fluency, completeness, prosody.
