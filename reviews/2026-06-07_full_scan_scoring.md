# Full Scan & Diagnosis — ai-oral-practice

Scope: backend scoring path (`/api/assess` + SOE/ASR), realtime WS, and cross-cutting
correctness/security/stability. Frontend i18n / dark-mode / realtime-removal handled
separately by Codex (commit `ed8b5af`). This pass is **diagnosis only — no code edits**.

Reviewer: claude · Date: 2026-06-07 · Base: `ed8b5af`

## Review - claude - 2026-06-07

### Hard Critical
- None (no data-loss / auth-bypass / irreversible migration found).

### Soft Critical (need user decision — cost / behavior / abuse surface)

- [ ] **C1 — `/api/assess` has no auth and no rate limit** [assessment/app.py:987-1015]
  The endpoint signature takes only `audio / reference_text / advanced` — no
  `Depends(get_current_user)`. Every POST runs ffmpeg + a paid SOE/Azure/DashScope
  call. On a public competition deploy (speak.projfit.top) this is an open quota-burn
  vector: an anonymous loop can exhaust Tencent SOE / Azure F0 quota and run up cost.
  → fix options: (a) require `get_optional_user` + per-IP rate limit; (b) gate behind
  auth like `/api/me`. **Recommend (a)** to keep the demo open but capped.

- [ ] **C2 — `/ws/realtime-pronunciation` is now orphan + unauthenticated dead code**
  [assessment/app.py:1590-1594, assessment/realtime.py]
  Codex removed the realtime UI from the frontend (`ed8b5af`), so nothing calls this
  WS route anymore. It is still registered, still unauthenticated, and still runs
  ASR + SOE on arbitrary streamed audio (same quota-burn surface as C1, no size cap on
  the buffered audio). → recommend **delete** `realtime.py` + the route (dead +
  abusable). Confirm before removing since it's a backend file deletion.

### Important

- [ ] **I1 — score "0" is SOE-genuine and surfaced rawly (root cause of issue 1)**
  [assessment/scoring/tencent.py:286-317, frontend/.../PronunciationView.vue:327-329]
  Mock never scores below 60 (`mock.py:20`), so the "0" in the screenshot is a real
  SOE `suggested_score`. SOE returns a near-0 overall when **completeness fails** —
  i.e. the spoken audio doesn't match `ref_text` (words omitted / wrong sentence /
  too short / silence captured). `hasUsableScore` accepts the result as long as *any*
  one sub-score is `> 0` (e.g. fluency 85 but completeness 0 → low/0 suggested),
  so a near-empty utterance shows a bare confusing **"0"** instead of an
  actionable "完整度过低，请重读整句" message.
  → fix: when `completeness_score` is very low or `pronunciation_score == 0` while
  other sub-scores exist, surface a "didn't catch the full sentence, retry" hint
  rather than a naked 0. (Frontend-side messaging — coordinate with Codex.)

- [ ] **I2 — per-sentence latency can spike to tens of seconds (issue 1 "整个时间很长")**
  [assessment/scoring/tencent.py:32-35,74-83,198-200]
  Worst case per sentence: up to 3 attempts, each `_OPEN_TIMEOUT=25s` +
  `_DONE_TIMEOUT=60s`. On a jittery VPS→SOE path a single sentence can hang ~30-60s,
  and 3 retries stack. `_DONE_TIMEOUT_SECONDS = 60` is far longer than any real SOE
  response and just turns a dead socket into a 60s spinner.
  → fix: cut `_DONE_TIMEOUT` to ~15s, cap total wall-clock budget across retries
  (e.g. 30s hard ceiling), and return a typed timeout the frontend renders as
  "评分超时，请重试" instead of an endless spinner.

- [ ] **I3 — `_transcribe._last_words` is shared mutable function-attribute state**
  [assessment/app.py:805-841]
  `_transcribe._last_words` is read/written on the function object itself. Two
  concurrent `/api/chat` or `/api/stream` requests race on it — request A's word
  timestamps can leak into request B's turn. → fix: return words alongside text
  (tuple / dataclass) instead of stashing on the function.

### Minor

- [ ] **M1 — SOE `nonce` is not random** [assessment/scoring/tencent.py:236-237]
  `nonce` and `timestamp` are both `str(int(time.time()))`. A nonce is meant to be
  unguessable/unique per request; reusing the timestamp defeats replay protection and
  two requests in the same second collide. → use `uuid4().int` or `random`.

- [ ] **M2 — `_eval_mode` splits the IPA-prefixed text correctly but is fragile**
  [assessment/scoring/tencent.py:219-222,260-262]
  `eval_mode` is computed from the *raw* `reference_text` before the `{::cmd{...}}`
  prefix is prepended — correct today, but a comment-only safeguard; a future edit that
  reorders these lines silently flips word/sentence mode. Low risk, note only.

- [ ] **M3 — `assess()` writes tmp with `.webm` suffix from content-type guess**
  [assessment/app.py:1000] If a browser sends `audio/ogg` or no content-type, suffix
  falls to `.webm` and ffmpeg still handles it, so harmless — note only.

## Deep-dive — "连续3句0分 / 同设备之前能评70-80" (claude, 2026-06-07)

User counter-evidence: same recording device, SOE returned 70-80 reliably before,
now returns **0 on three consecutive sentences**. That is a runtime **regression**,
not a pronunciation problem — genuine bad pronunciation does not collapse an entire
session to exactly 0.

### Root-cause chain (confirmed against Tencent official docs)
- Tencent SOE New Edition scoring formula (官方 1774/107384):
  **SuggestedScore = PronAccuracy × PronCompletion × (2 − PronCompletion)**.
  PronCompletion is a 0-1 ratio. So **PronCompletion = 0 ⇒ SuggestedScore = 0**,
  regardless of how good the accuracy is.
- Therefore "0" means **SOE received no usable/matching audio** (completeness 0),
  i.e. the audio never reached SOE intact — NOT that the user mispronounced.
- `rec_mode=1` (官方 1774/107372) = 同步录音模式 = "一次性传完整个音频". Our single-
  packet send matches the protocol — framing is NOT the bug.
- Response field names verified (官方 1774/107388): `result.Words`, `SuggestedScore`,
  `PronAccuracy`, `PronCompletion`, `final==1`. `_normalize` already handles both
  `word_list`/`Words` casings — parsing is NOT the bug.

### Regression archaeology (git)
- Working baseline = `dacc504` (per-sentence scoring; sent audio on **main thread**
  after `opened` via `ws.sock.send_binary()`).
- `7dd191d` (send-on-open) moved the send into `on_open` but called
  `ws.send_binary(...)` — **WebSocketApp has no `send_binary`** (that's only on the
  low-level `ws.sock`), so on_open raised AttributeError → "Failed to send audio"
  every time. This is a real regression window.
- `73a64dc` fixed it to `ws.send(audio_bytes, ABNF.OPCODE_BINARY)`, which on the
  installed `websocket-client==1.8.0` is equivalent to `sock.send(data, opcode)` —
  verified by inspecting `WebSocketApp.send` source. So the **current** code's send
  path is correct.
- Net: the *code on disk now* (`fcc24f5`) sends correctly. The 0-score regression
  is therefore happening at **runtime on the VPS**, in a path with zero logging.

### Leading runtime hypotheses (need VPS evidence to disambiguate)
1. **end-frame timing race** — `on_open` does `ws.send(audio)` then immediately
   `ws.send({"type":"end"})`. With New Edition rec_mode=1 over a jittery VPS link,
   firing `end` in the same callback before the audio frame is flushed can make SOE
   finalize on an empty/partial buffer → PronCompletion 0. The old working version
   sent audio+end from the **main thread after** `opened`, a different ordering.
2. **ffmpeg conversion producing empty/near-empty wav on the VPS** — `_ensure_wav`
   shells out to ffmpeg; if the container's ffmpeg fails silently on the browser's
   `webm/opus` (codec/build mismatch) the wav could be empty → SOE completeness 0.
   `_ensure_wav` uses `check=True` so a hard failure raises, but a 0-duration success
   would slip through. **This newly matters because Codex's `ed8b5af` started passing
   real `language` into ASR but the assess path's ffmpeg is unchanged — still worth
   confirming the VPS ffmpeg actually decodes the current frontend's webm.**
3. **`end` payload format** — we send `{"type":"end"}`; New Edition may expect a
   different terminator. If SOE never sees a valid end-of-stream it may time out and
   finalize with completeness 0 rather than erroring.

### Why we can't close it statically
`_run_ws_assessment` logs nothing. The single highest-value next step is to add
temporary structured logging (raw SOE `final` payload: code, message, PronCompletion,
PronAccuracy, len(audio_bytes), wav duration) and run ONE real sentence on the VPS.
That instantly tells us which hypothesis is true. **Needs user approval to touch the
VPS / add logging — deferred, not done.**

## Fix Pass — claude — 2026-06-07 (diagnostic instrumentation only)

User approved adding logging. Added zero-risk, additive logging to `tencent.py`
(claimed I-DIAG). No scoring/send logic changed. This converts the black-box SOE call
into observable evidence so the next VPS run pinpoints the 0-score root cause.

### Applied
- [x] **I-DIAG** [assessment/scoring/tencent.py]
  - module logger `assessment.tencent` (propagates to parent `assessment`, which
    app.py wires to uvicorn handlers → visible in `docker compose logs`; verified).
  - `_ensure_wav`: logs the **passthrough .wav** case (size) — catches the "suffix
    guessed wrong → non-wav forwarded to SOE" path — and logs post-ffmpeg **wav size
    + estimated duration + stderr tail** — catches the "ffmpeg decoded 0s" path.
  - `on_open`: logs bytes of audio actually sent.
  - `on_message`: logs **every raw SOE frame** (truncated 500 chars) — the core
    signal: SOE's real `code`/`message`/completeness.
  - `_normalize`: logs parsed `suggested/accuracy/fluency/completeness/words` —
    confirms whether completeness collapsed to 0.

### Audio-format diff conclusion (answers user's "格式有没有问题 / 充分 diff 过吗")
- ffmpeg params (`-ar 16000 -ac 1`) **unchanged across all of git history** (`-S`).
- `voice_format=1` **unchanged since the SOE New Edition migration** (`c9f6c4c`).
- Official audio-format doc (1774/107376): SOE wants 16k/mono/16bit and treats **PCM
  (headerless) and WAV (with RIFF header) as distinct formats**. If `voice_format=1`
  actually expects raw PCM while we send a header-bearing `.wav`, SOE would parse the
  44-byte header as samples → completeness 0. This is a **latent** suspect but NOT the
  regression variable (the param never changed). Flagged for the VPS log run to
  confirm/deny via the real `code`/completeness.
- `/api/assess` tmp-suffix default flipped `.wav`→`.webm` long ago in `17b6466`
  (Azure era), not recently — ruled out as the regression trigger.

### Verification
- `python -m py_compile assessment/scoring/tencent.py`: OK
- `python -m pytest assessment/tests/test_scoring.py -q`: 14 passed
- Logger propagation `assessment.tencent` → parent `assessment` (uvicorn handlers):
  verified by isolated repro.

### Next (needs user/owner action — NOT done)
- Deploy this logging build to the VPS, run ONE real pronunciation sentence, capture
  `docker compose logs`, and read the `SOE on_message` + `SOE parsed` lines. Expected
  to show completeness=0 (or a non-zero `code`) and instantly disambiguate:
  end-frame race vs empty wav vs wrong audio format vs SOE account/quota.

## VPS Live Evidence — claude — 2026-06-07 (deployed + captured)

Deployed logging build to VPS (backup `tencent.py.bak.diag_20260607_204215`, only
tencent.py synced — did NOT carry Codex's uncommitted app.py/CustomTopicView changes).
Direct in-container `_run_ws_assessment` call captured the real SOE round-trip:

```
SOE on_open: sent 64078B audio + end frame
SOE on_message: {"code":0,"message":"success","result":null,"final":0}
SOE on_message: {"code":0,...,"result":{"SuggestedScore":0,"PronAccuracy":0,
  "PronFluency":-1,"PronCompletion":0,"Words":[],...},"final":1}
ELAPSED 8.7s
```

(That input was a synthetic sine tone, so completeness 0 / empty Words is EXPECTED —
SOE matched no real words. The value is the *structure + timing* it revealed.)

### Confirmed root causes (all three user-reported symptoms)

1. **慢 — single SOE round-trip = 8.7s.** `Websocket connected` itself takes several
   seconds (VPS→Tencent SOE handshake is slow/jittery, 2-9s as the code comments note).
   One sentence ≈ 8-9s; 4 sentences fired concurrently from the UI + retries stack into
   the "很慢" feeling. The send/protocol is correct — the latency is the network path,
   amplified by `_DONE_TIMEOUT=60s` turning any stalled socket into a 60s spinner.

2. **分偏低 / 偶尔0 — `PronCompletion` is a punishing multiplier.**
   SuggestedScore = PronAccuracy × PronCompletion × (2 − PronCompletion). Confirmed the
   formula live (completeness 0 → score 0). On the real VPS link, dropped/garbled audio
   frames make SOE match fewer words → completeness < 1 → score multiplied down; total
   loss of match → 0. The score is genuine SOE output, depressed by incomplete audio
   reaching SOE over the flaky link — NOT a parsing/display bug.

3. **音标(IPA)消失 — code path is CORRECT, IPA prefix lands in the signed URL.**
   Verified in-container: `_ipa_enabled()=True`, signed URL contains
   `ref_text={::cmd{F_IPA=true}}hello world`. The empty `PhoneInfos` in the sine-tone
   run was because `Words:[]` (no match → no phones). IPA phones only appear when SOE
   actually matches words. So "no IPA" co-occurs with low completeness: when audio is
   incomplete, SOE returns few/no Words → no PhoneInfos → UI shows no phonetics. **IPA
   disappearance is a downstream symptom of the SAME completeness problem, not a
   separate IPA bug.**

### Logging gotcha found (why the live monitor saw nothing)
In-container: `assessment.tencent` effective level = **30 (WARNING)**, parent
`assessment` handlers = **[]**. The lifespan hook only copies uvicorn handlers *if they
exist at startup*, and never lowers the child level, so my `logger.info(...)` lines were
filtered out in normal request flow. They only appeared when I forced
`basicConfig(level=INFO)` in a manual `exec`. → If we want these logs in normal request
flow, app.py must set the `assessment` logger to INFO unconditionally (separate minor).

### The real fix direction (for next pass / user decision)
The bottleneck is **audio integrity + latency over the VPS→SOE path**, not the scoring
code. Options:
- (a) Send audio in small ordered chunks with brief pacing instead of one 64KB blast,
  so a jittery link is less likely to truncate the buffer before `end`.
- (b) Cut `_DONE_TIMEOUT` 60s→~15s and cap total retry wall-clock so a bad socket fails
  fast instead of a 60s spinner.
- (c) Surface low-completeness as "没听清整句，请重读" instead of a bare low/0 number,
  and only show IPA when phones exist.
- (d) Consider routing SOE through a closer region / the proxy already used for the
  pronunciation-scoring network fix, to cut the 8.7s handshake.

### Verification (initial diagnosis pass)
- Static read-only diagnosis + official-doc cross-check + git archaeology. No edits.
- Confirmed: `git show ed8b5af` touches ASR language plumbing + frontend, **not** the
  `/api/assess` → SOE scoring path. The 0-score regression is unaddressed.
- `websocket-client==1.8.0` `WebSocketApp.send(bytes, OPCODE_BINARY)` == low-level
  `sock.send(data, opcode)` — verified by source inspection.

### Gate
- Status: **Not approved for sync** — C1/C2 (auth + orphan WS) and I1/I2 (score-0 UX +
  latency) need user decision/fixes first. Diagnosis handed off; awaiting user call on
  C1/C2 fix approach and whether to delete realtime.py.
