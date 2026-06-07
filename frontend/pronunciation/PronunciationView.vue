<template>
  <div class="pronunciation-view">
    <Toast :message="toast.message" :type="toast.type" @close="toast.message = ''" />

    <header class="page-header">
      <button @click="$router.push('/')" class="back-btn">← {{ t('chat.back') }}</button>
      <h1>🎯 {{ t('pronunciation.title') }}</h1>
    </header>

    <!-- Scenario selection -->
    <div v-if="!selectedScenario" class="scenario-picker">
      <p class="subtitle">{{ t('pronunciation.subtitle') }}</p>
      <div class="scenario-grid">
        <div
          v-for="s in scenarios"
          :key="s.id"
          class="scenario-chip"
          @click="selectScenario(s)"
        >
          {{ s.icon }} {{ s.name }}
        </div>
      </div>
    </div>

    <!-- Practice area -->
    <div v-else class="practice-area">
      <div class="scenario-badge" @click="selectedScenario = null">
        {{ selectedScenario.icon }} {{ selectedScenario.name }} ✕
      </div>

      <!-- Sentence list -->
      <div class="sentence-list">
        <div
          v-for="(sent, i) in sentences"
          :key="i"
          class="sentence-card"
          :class="{ active: currentIndex === i, done: hasResult(i) }"
          @click="selectSentence(i)"
        >
          <span class="sent-num">{{ i + 1 }}</span>
          <span class="sent-text">{{ sent }}</span>
          <span v-if="scoringStates[i] === 'scoring'" class="sent-spinner" :title="t('pronunciation.processing')"></span>
          <span v-else-if="hasResult(i)" class="sent-score">{{ latestScore(i)?.toFixed(0) }}</span>
        </div>
      </div>

      <!-- Active sentence practice -->
      <div v-if="currentIndex >= 0" class="active-practice">
        <div class="reference-text">
          <p class="label">{{ t('pronunciation.readThis') }}</p>
          <p class="text">{{ sentences[currentIndex] }}</p>
          <button class="demo-btn" :disabled="playingDemo" @click="playDemo">
            {{ playingDemo ? t('pronunciation.playing') : t('pronunciation.listenDemo') }}
          </button>
        </div>

        <div class="record-area">
          <button
            class="record-btn"
            :class="{ active: isRecording }"
            @click="handleRecord"
          >
            🎙️ {{ recordBtnText }}
          </button>
          <p v-if="scoringStates[currentIndex] === 'scoring'" class="scoring-hint">
            {{ t('pronunciation.scoringInBackground') }}
          </p>
        </div>

        <!-- Result display -->
        <div v-if="result" class="result-panel">
          <!-- History selector: shown once the sentence has 2+ attempts -->
          <div v-if="currentAttempts.length > 1" class="history-bar">
            <label class="history-label">{{ t('pronunciation.history') }}</label>
            <select class="history-select" :value="viewAttempt[currentIndex] ?? currentAttempts.length - 1" @change="selectHistory">
              <option v-for="(a, k) in currentAttempts" :key="k" :value="k">
                #{{ k + 1 }} · {{ a.pronunciation_score?.toFixed(0) }}{{ t('pronunciation.scoreUnit') }}
              </option>
            </select>
          </div>

          <div class="scores-row">
            <div class="score-item">
              <span class="score-value" :class="scoreClass(result.pronunciation_score)">
                {{ result.pronunciation_score?.toFixed(0) }}
              </span>
              <span class="score-label">{{ t('pronunciation.total') }}</span>
            </div>
            <div class="score-item">
              <span class="score-value" :class="scoreClass(result.accuracy_score)">
                {{ result.accuracy_score?.toFixed(0) }}
              </span>
              <span class="score-label">{{ t('pronunciation.accuracy') }}</span>
            </div>
            <div class="score-item">
              <span class="score-value" :class="scoreClass(result.fluency_score)">
                {{ result.fluency_score?.toFixed(0) }}
              </span>
              <span class="score-label">{{ t('pronunciation.fluency') }}</span>
            </div>
            <div class="score-item">
              <span class="score-value" :class="scoreClass(result.completeness_score)">
                {{ result.completeness_score?.toFixed(0) }}
              </span>
              <span class="score-label">{{ t('pronunciation.completeness') }}</span>
            </div>
          </div>

          <!-- Per-word breakdown: click a word to see its phonetics + tip -->
          <div v-if="result.words && result.words.length" class="word-breakdown">
            <span
              v-for="(w, j) in result.words"
              :key="j"
              class="word"
              :class="[wordClass(w), { 'word-active': expandedWordIdx === j, 'word-clickable': w.phones?.length }]"
              @click="w.phones?.length && toggleWord(j)"
            >
              {{ w.word }}
            </span>
          </div>

          <!-- Phonetic detail for the selected word -->
          <div
            v-if="expandedWordIdx >= 0 && result.words[expandedWordIdx]?.phones?.length"
            class="phone-detail"
          >
            <div class="phone-detail-head">
              <strong>{{ result.words[expandedWordIdx].word }}</strong>
              <span class="phone-detail-ipa">
                /<template v-for="(p, k) in result.words[expandedWordIdx].phones" :key="k"><span :class="phoneClass(p)">{{ p.phone }}</span></template>/
              </span>
            </div>
            <p v-if="result.words[expandedWordIdx].tip" class="phone-tip">
              💡 {{ t('pronunciation.focusPhone') }} <span class="phone-poor">/{{ result.words[expandedWordIdx].tip }}/</span> — {{ t('pronunciation.tipHint') }}
            </p>
          </div>

          <button class="next-btn" @click="nextSentence">
            {{ currentIndex < sentences.length - 1 ? t('pronunciation.next') : `🎉 ${t('pronunciation.done')}` }}
          </button>
        </div>
      </div>

      <!-- Summary panel (shown after all sentences are done) -->
      <div v-if="showSummary" class="summary-panel">
        <h3>📊 本次练习总结</h3>
        <div class="summary-scores">
          <div class="summary-item">
            <span class="summary-value" :class="scoreClass(avgScore('pronunciation_score'))">{{ avgScore('pronunciation_score') }}</span>
            <span class="summary-label">平均总分</span>
          </div>
          <div class="summary-item">
            <span class="summary-value" :class="scoreClass(avgScore('accuracy_score'))">{{ avgScore('accuracy_score') }}</span>
            <span class="summary-label">平均准确度</span>
          </div>
          <div class="summary-item">
            <span class="summary-value" :class="scoreClass(avgScore('fluency_score'))">{{ avgScore('fluency_score') }}</span>
            <span class="summary-label">平均流利度</span>
          </div>
          <div class="summary-item">
            <span class="summary-value" :class="scoreClass(avgScore('completeness_score'))">{{ avgScore('completeness_score') }}</span>
            <span class="summary-label">平均完整度</span>
          </div>
        </div>
        <div class="summary-detail">
          <p>共练习 <strong>{{ practicedCount }}</strong> / {{ sentences.length }} 句</p>
          <p v-if="weakWords.length">
            <span class="weak-title">需加强的单词：</span>
            <span v-for="w in weakWords" :key="w" class="weak-word">{{ w }}</span>
          </p>
        </div>
        <button class="summary-btn" @click="selectedScenario = null; showSummary = false">
          返回选择场景
        </button>
      </div>
    </div>

    <!-- Realtime Mode -->
    <div class="realtime-section">
      <h2>🎙️ 实时纠音模式</h2>
      <p class="realtime-desc">边说边看发音反馈，实时高亮每个词的发音质量</p>
      <button class="realtime-btn" :class="{ active: realtimeActive }" @click="toggleRealtime">
        <span class="rt-btn-dot" :class="{ active: realtimeActive }"></span>
        {{ realtimeActive ? '停止' : '开始实时纠音' }}
      </button>

      <div v-if="realtimeActive || realtimeWords.length" class="realtime-display">
        <div class="realtime-words" v-if="realtimeWords.length">
          <span v-for="(w, i) in realtimeWords" :key="i" class="rt-word" :class="rtWordClass(w)" :title="'Score: ' + w.score">{{ w.word }}</span>
        </div>
        <div v-if="realtimeScore !== null" class="realtime-score">
          总分: <strong :class="scoreClass(realtimeScore)">{{ realtimeScore }}</strong>
        </div>
        <div v-if="realtimeActive" class="realtime-listening">
          <span class="pulse-dot"></span> 正在倾听...
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRecorder } from '../../voice/audio/useRecorder'
import { classifyError } from '../composables/useErrorHandler'
import { useI18n } from '../composables/useI18n'
import { CONFIG } from '../../shared/config'
import Toast from '../components/Toast.vue'

const { t } = useI18n()
const scenarios = CONFIG.SCENARIOS
const selectedScenario = ref(null)
const sentences = ref([])
const currentIndex = ref(-1)
// Per-sentence scoring history: { index: [attempt, attempt, ...] }.
// Each attempt is a full assess result; we keep every retry so the user can
// compare progress via the history dropdown.
const attempts = ref({})
// Transient per-sentence state for async scoring: { index: 'scoring'|'done'|'error' }.
const scoringStates = ref({})
// Which history entry is being viewed per sentence (default: latest).
const viewAttempt = ref({})
const expandedWordIdx = ref(-1)
const isPlaying = ref(false)
const playingDemo = ref(false)
const demoAudio = ref(null)
const showSummary = ref(false)
let currentAudio = null

const toast = reactive({ message: '', type: 'info' })

const { start, stop, isRecording } = useRecorder({
  silenceMs: CONFIG.AUDIO.VAD_SILENCE_MS,
  onSilence: async () => {
    if (isRecording.value) await finishRecording()
  },
})

// Attempts for the active sentence, and the one currently shown (selected or latest).
const currentAttempts = computed(() => attempts.value[currentIndex.value] || [])
const result = computed(() => {
  const list = currentAttempts.value
  if (!list.length) return null
  const idx = viewAttempt.value[currentIndex.value]
  return idx != null && list[idx] ? list[idx] : list[list.length - 1]
})

const recordBtnText = computed(() => {
  if (isRecording.value) return t('pronunciation.stop')
  return t('pronunciation.start')
})

async function selectScenario(s) {
  selectedScenario.value = s
  attempts.value = {}
  scoringStates.value = {}
  viewAttempt.value = {}
  currentIndex.value = 0

  try {
    const res = await fetch(`/api/scenarios/${s.id}/sentences`)
    if (res.ok) {
      const data = await res.json()
      sentences.value = data.sentences
    } else {
      throw new Error()
    }
  } catch {
    // Fallback
    sentences.value = [
      "This is a practice sentence for pronunciation.",
      "Could you help me with this, please?",
      "I would like to improve my English speaking.",
    ]
  }
}

function selectSentence(i) {
  currentIndex.value = i
  expandedWordIdx.value = -1
}

async function handleRecord() {
  if (isRecording.value) {
    await finishRecording()
  } else {
    try {
      await start()
    } catch {
      toast.message = t('pronunciation.micDenied')
      toast.type = 'warning'
    }
  }
}

async function finishRecording() {
  const blob = await stop()
  if (!blob) return
  // Fire scoring in the background so the user can move to the next sentence
  // immediately; the score backfills onto this sentence's card when it returns.
  const idx = currentIndex.value
  submitForScoring(idx, blob, sentences.value[idx])
}

async function submitForScoring(idx, blob, referenceText) {
  scoringStates.value[idx] = 'scoring'

  const formData = new FormData()
  formData.append('audio', blob, 'recording.webm')
  formData.append('reference_text', referenceText)

  try {
    const res = await fetch('/api/assess', { method: 'POST', body: formData })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      const error = new Error(err.detail || 'Assessment failed')
      error.status = res.status
      throw error
    }
    const data = await res.json()
    if (!attempts.value[idx]) attempts.value[idx] = []
    attempts.value[idx].push(data)
    viewAttempt.value[idx] = attempts.value[idx].length - 1
    scoringStates.value[idx] = 'done'
    if (idx === currentIndex.value) expandedWordIdx.value = -1
  } catch (e) {
    const err = classifyError(e, e.status)
    toast.message = `${err.title}：${err.message}`
    toast.type = 'error'
    scoringStates.value[idx] = 'error'
  }
}

function latestScore(i) {
  const list = attempts.value[i]
  if (!list?.length) return null
  return list[list.length - 1].pronunciation_score
}

function hasResult(i) {
  return (attempts.value[i]?.length || 0) > 0
}

function selectHistory(event) {
  viewAttempt.value[currentIndex.value] = Number(event.target.value)
  expandedWordIdx.value = -1
}

function toggleWord(j) {
  expandedWordIdx.value = expandedWordIdx.value === j ? -1 : j
}

async function playDemo() {
  const text = sentences.value[currentIndex.value]
  if (!text) return

  if (currentAudio) { currentAudio.pause(); currentAudio = null }
  if (demoAudio.value) { demoAudio.value.pause(); demoAudio.value = null }
  isPlaying.value = true
  playingDemo.value = true

  try {
    const formData = new FormData()
    formData.append('text', text)
    const res = await fetch('/api/tts', { method: 'POST', body: formData })
    if (!res.ok) throw new Error('TTS failed')
    const blob = await res.blob()
    const url = URL.createObjectURL(blob)
    demoAudio.value = new Audio(url)
    demoAudio.value.onended = () => {
      URL.revokeObjectURL(url)
      isPlaying.value = false
      playingDemo.value = false
    }
    demoAudio.value.onerror = () => {
      URL.revokeObjectURL(url)
      isPlaying.value = false
      playingDemo.value = false
    }
    await demoAudio.value.play()
  } catch {
    isPlaying.value = false
    playingDemo.value = false
    toast.message = t('pronunciation.demoFailed')
    toast.type = 'warning'
  }
}

function nextSentence() {
  if (currentIndex.value < sentences.value.length - 1) {
    currentIndex.value++
    expandedWordIdx.value = -1
  } else {
    // All done — show summary
    toast.message = t('pronunciation.allDone')
    toast.type = 'success'
    showSummary.value = true
    currentIndex.value = -1
  }
}

const practicedCount = computed(() => Object.keys(attempts.value).length)

function avgScore(key) {
  const vals = Object.values(attempts.value)
    .map(list => list[list.length - 1]?.[key])
    .filter(v => v != null)
  if (!vals.length) return '--'
  return Math.round(vals.reduce((a, b) => a + b, 0) / vals.length)
}

const weakWords = computed(() => {
  const words = []
  Object.values(attempts.value).forEach(list => {
    const r = list[list.length - 1]
    if (r?.words) {
      r.words.forEach(w => {
        if (w.accuracy_score != null && w.accuracy_score < 60 && w.word) {
          words.push(w.word)
        }
      })
    }
  })
  // Deduplicate
  return [...new Set(words)].slice(0, 15)
})

function scoreClass(score) {
  if (score == null) return ''
  if (score >= 80) return 'good'
  if (score >= 60) return 'ok'
  return 'poor'
}

function wordClass(w) {
  if (w.error_type && w.error_type !== 'none' && w.error_type !== 'None') return 'word-error'
  if (w.accuracy_score >= 80) return 'word-good'
  if (w.accuracy_score >= 60) return 'word-ok'
  return 'word-poor'
}

function phoneClass(p) {
  if (p.accuracy_score == null) return ''
  if (p.accuracy_score >= 80) return 'phone-good'
  if (p.accuracy_score >= 60) return 'phone-ok'
  return 'phone-poor'
}

// --- Realtime Mode ---
const realtimeActive = ref(false)
const realtimeWords = ref([])
const realtimeScore = ref(null)
let rtWebSocket = null
let rtMediaRecorder = null
let rtStream = null

function rtWordClass(w) {
  if (w.score >= 80) return 'rt-good'
  if (w.score >= 60) return 'rt-ok'
  return 'rt-poor'
}

async function toggleRealtime() {
  if (realtimeActive.value) { stopRealtime() } else { await startRealtime() }
}

async function startRealtime() {
  realtimeWords.value = []
  realtimeScore.value = null
  try { rtStream = await navigator.mediaDevices.getUserMedia({ audio: true }) }
  catch { toast.message = '麦克风权限被拒绝'; toast.type = 'warning'; return }

  const wsProto = location.protocol === 'https:' ? 'wss:' : 'ws:'
  rtWebSocket = new WebSocket(`${wsProto}//${location.host}/ws/realtime-pronunciation`)
  rtWebSocket.onopen = () => {
    rtWebSocket.send(JSON.stringify({ reference_text: sentences.value[currentIndex.value] || '' }))
    realtimeActive.value = true
    rtMediaRecorder = new MediaRecorder(rtStream, { mimeType: 'audio/webm;codecs=opus' })
    rtMediaRecorder.ondataavailable = (e) => { if (e.data.size > 0 && rtWebSocket?.readyState === WebSocket.OPEN) rtWebSocket.send(e.data) }
    rtMediaRecorder.start(2500)
  }
  rtWebSocket.onmessage = (event) => {
    const msg = JSON.parse(event.data)
    if (msg.type === 'assessment' && msg.words?.length) {
      realtimeWords.value = [...realtimeWords.value, ...msg.words]
      if (msg.overall_score != null) realtimeScore.value = msg.overall_score
    }
  }
  rtWebSocket.onerror = () => { toast.message = 'WebSocket 连接失败'; toast.type = 'error'; stopRealtime() }
  rtWebSocket.onclose = () => { realtimeActive.value = false }
}

function stopRealtime() {
  realtimeActive.value = false
  if (rtMediaRecorder?.state !== 'inactive') rtMediaRecorder?.stop()
  rtWebSocket?.close(); rtWebSocket = null
  rtStream?.getTracks().forEach(t => t.stop()); rtStream = null
}
</script>

<style scoped>
.pronunciation-view {
  max-width: 700px;
  margin: 0 auto;
  animation: fade-in var(--transition-base) both;
}

/* Header */
.page-header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-6);
}

.page-header h1 { font-size: var(--text-2xl); font-weight: 700; color: var(--color-text); }

.back-btn {
  font-size: var(--text-base);
  color: var(--color-primary);
  font-weight: 500;
  padding: var(--space-2);
  border-radius: var(--radius-sm);
  transition: background var(--transition-fast);
}
.back-btn:hover { background: var(--color-primary-50); }

/* Scenario picker */
.subtitle { color: var(--color-text-secondary); margin-bottom: var(--space-4); text-align: center; }

.scenario-grid {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  justify-content: center;
}

.scenario-chip {
  padding: var(--space-2) var(--space-4);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-full);
  cursor: pointer;
  font-size: var(--text-sm);
  transition: all var(--transition-fast);
}
.scenario-chip:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
  background: var(--color-primary-50);
}

/* Practice area */
.scenario-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  background: var(--color-primary-50);
  border: 1px solid var(--color-primary-200);
  border-radius: var(--radius-full);
  font-size: var(--text-sm);
  color: var(--color-primary);
  cursor: pointer;
  margin-bottom: var(--space-4);
  transition: all var(--transition-fast);
}
.scenario-badge:hover { background: var(--color-primary-100); }

/* Sentence list */
.sentence-list { margin-bottom: var(--space-6); }

.sentence-card {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-2);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.sentence-card:hover { border-color: var(--color-primary-200); }
.sentence-card.active {
  border-color: var(--color-primary);
  background: var(--color-primary-50);
  box-shadow: 0 0 0 3px rgba(26, 86, 219, 0.08);
}
.sentence-card.done { border-left: 3px solid var(--color-success); }

.sent-num { font-weight: 700; color: var(--color-text-muted); min-width: 24px; font-size: var(--text-sm); }
.sent-text { flex: 1; font-size: var(--text-sm); line-height: 1.5; }
.sent-score { font-weight: 700; color: var(--color-primary); font-size: var(--text-base); }

/* Active practice */
.active-practice { text-align: center; }

.reference-text {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  margin-bottom: var(--space-6);
  box-shadow: var(--shadow-sm);
}

.reference-text .label {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  margin-bottom: var(--space-2);
  font-weight: 500;
}

.reference-text .text {
  font-size: var(--text-xl);
  color: var(--color-text);
  line-height: 1.7;
  font-weight: 500;
}

.demo-btn {
  margin-top: var(--space-4);
  padding: var(--space-2) var(--space-4);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-full);
  background: var(--color-surface);
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  transition: all var(--transition-fast);
}
.demo-btn:hover { border-color: var(--color-primary); color: var(--color-primary); }
.demo-btn:disabled { opacity: 0.5; cursor: not-allowed; }

/* Record button */
.record-area { margin-bottom: var(--space-6); }

.record-btn {
  padding: var(--space-4) var(--space-8);
  border-radius: var(--radius-full);
  border: 2px solid var(--color-primary);
  background: var(--color-surface);
  font-size: var(--text-lg);
  font-weight: 500;
  color: var(--color-primary);
  transition: all var(--transition-base);
  position: relative;
}

.record-btn:hover:not(:disabled) {
  background: var(--color-primary-50);
  box-shadow: var(--shadow-glow);
}

.record-btn.active {
  background: var(--color-error);
  border-color: var(--color-error);
  color: white;
  transform: scale(1.05);
  box-shadow: 0 0 20px rgba(239, 68, 68, 0.3);
  animation: pulse-ring-outer 1.5s infinite;
}

/* Concentric expanding rings for a sound-wave feel */
.record-btn.active::before,
.record-btn.active::after {
  content: '';
  position: absolute;
  inset: -4px;
  border-radius: var(--radius-full);
  border: 2px solid var(--color-error);
  animation: pulse-ring 1.6s infinite;
  pointer-events: none;
}
.record-btn.active::after { animation-delay: 0.6s; }

.record-btn.processing { opacity: 0.6; }

@keyframes pulse-ring-outer {
  0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
  100% { box-shadow: 0 0 0 16px rgba(239, 68, 68, 0); }
}

@media (prefers-reduced-motion: reduce) {
  .record-btn.active,
  .record-btn.active::before,
  .record-btn.active::after { animation: none; }
}

/* Result panel */
.result-panel {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-md);
  animation: scale-in var(--transition-base) both;
}

/* Circular score display */
.scores-row {
  display: flex;
  justify-content: center;
  gap: var(--space-6);
  margin-bottom: var(--space-5);
}

.score-item {
  text-align: center;
  position: relative;
}

.score-value {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  font-size: var(--text-xl);
  font-weight: 800;
  margin: 0 auto var(--space-1);
  border: 3px solid var(--color-border);
  transition: all var(--transition-base);
}

.score-value.good {
  color: var(--color-score-excellent);
  border-color: var(--color-score-excellent);
  background: rgba(16, 185, 129, 0.08);
}

.score-value.ok {
  color: var(--color-score-fair);
  border-color: var(--color-score-fair);
  background: rgba(245, 158, 11, 0.08);
}

.score-value.poor {
  color: var(--color-score-poor);
  border-color: var(--color-score-poor);
  background: rgba(239, 68, 68, 0.08);
}

.score-label {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  font-weight: 500;
}

/* Word breakdown */
.word-breakdown {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  justify-content: center;
  margin-bottom: var(--space-5);
  padding: var(--space-4);
  background: var(--color-bg);
  border-radius: var(--radius-md);
}

.word {
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  font-size: var(--text-base);
  font-weight: 500;
  transition: transform var(--transition-fast);
}
.word:hover { transform: scale(1.1); }

.word-good { background: var(--color-beginner-bg); color: var(--color-beginner); }
.word-ok { background: var(--color-intermediate-bg); color: #b45309; }
.word-poor { background: var(--color-error-light); color: var(--color-error); }
.word-error { background: var(--color-error-light); color: var(--color-error); text-decoration: underline wavy; }
.word-clickable { cursor: pointer; }
.word-active { box-shadow: 0 0 0 2px var(--color-primary); }

/* Per-sentence scoring spinner (card corner) */
.sent-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: rt-spin 0.7s linear infinite;
}
@keyframes rt-spin { to { transform: rotate(360deg); } }
.scoring-hint {
  margin-top: var(--space-2);
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}
@media (prefers-reduced-motion: reduce) {
  .sent-spinner { animation: none; }
}

/* History selector — native <select> renders above everything, so no
   z-index/pointer-events trap like the old custom slider had. */
.history-bar {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  justify-content: flex-end;
  margin-bottom: var(--space-4);
}
.history-label { font-size: var(--text-xs); color: var(--color-text-muted); font-weight: 500; }
.history-select {
  padding: var(--space-1) var(--space-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-surface);
  color: var(--color-text);
  font-size: var(--text-sm);
  cursor: pointer;
}
.history-select:focus { outline: none; border-color: var(--color-primary); }

/* Phonetic detail panel for the selected word */
.phone-detail {
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  margin-bottom: var(--space-5);
  text-align: left;
  animation: scale-in var(--transition-fast) both;
}
.phone-detail-head {
  display: flex;
  align-items: baseline;
  gap: var(--space-3);
  margin-bottom: var(--space-2);
}
.phone-detail-head strong { font-size: var(--text-lg); color: var(--color-text); }
.phone-detail-ipa { font-size: var(--text-lg); letter-spacing: 1px; color: var(--color-text-secondary); }
.phone-detail-ipa .phone-good { color: var(--color-score-excellent); }
.phone-detail-ipa .phone-ok { color: var(--color-score-fair); }
.phone-detail-ipa .phone-poor { color: var(--color-score-poor); font-weight: 700; }
.phone-tip {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  line-height: 1.6;
}
.phone-tip .phone-poor { color: var(--color-score-poor); font-weight: 700; }

/* Next button */
.next-btn {
  padding: var(--space-3) var(--space-6);
  background: var(--color-primary);
  color: white;
  border-radius: var(--radius-md);
  font-size: var(--text-base);
  font-weight: 600;
  transition: all var(--transition-fast);
}
.next-btn:hover { background: var(--color-primary-dark); transform: translateY(-1px); }

/* Responsive */
@media (max-width: 768px) {
  .scores-row { gap: var(--space-4); }
  .score-value { width: 48px; height: 48px; font-size: var(--text-lg); }
  .reference-text .text { font-size: var(--text-lg); }
}

/* Summary panel */
.summary-panel {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 16px;
  padding: 1.5rem;
  margin-top: 1.5rem;
  text-align: center;
}
.summary-panel h3 {
  color: #1f4e79;
  margin-bottom: 1.2rem;
}
.summary-scores {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  margin-bottom: 1.2rem;
  flex-wrap: wrap;
}
.summary-item { text-align: center; }
.summary-value {
  display: block;
  font-size: 2rem;
  font-weight: 700;
  color: #1f4e79;
}
.summary-value.good { color: #2e7d32; }
.summary-value.ok { color: #f57c00; }
.summary-value.poor { color: #c62828; }
.summary-label {
  font-size: 0.8rem;
  color: #888;
}
.summary-detail {
  margin-bottom: 1rem;
  font-size: 0.9rem;
  color: #555;
}
.weak-title {
  font-weight: 600;
  color: #e65100;
}
.weak-word {
  display: inline-block;
  background: #fce4ec;
  color: #c62828;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  margin: 0.2rem;
  font-size: 0.85rem;
}
.summary-btn {
  padding: 0.7rem 1.5rem;
  background: #1f4e79;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.95rem;
}
.summary-btn:hover { background: #2a6399; }

.realtime-section { margin-top: var(--space-10); padding-top: var(--space-8); border-top: 1px solid var(--color-border); text-align: center; }
.realtime-desc { color: var(--color-text-secondary); font-size: var(--text-sm); margin-bottom: var(--space-4); }
.realtime-btn {
  display: inline-flex; align-items: center; gap: var(--space-2);
  padding: var(--space-3) var(--space-8); background: var(--color-primary); color: #fff;
  border: none; border-radius: var(--radius-full); font-size: var(--text-base); font-weight: 600;
  cursor: pointer; transition: background var(--transition-fast);
}
.realtime-btn:hover { background: var(--color-primary-dark); }
.realtime-btn.active { background: var(--color-error); }
.realtime-btn.active:hover { background: var(--color-error); filter: brightness(0.92); }
.rt-btn-dot { width: 10px; height: 10px; border-radius: var(--radius-full); background: #fff; transition: border-radius var(--transition-fast); }
.rt-btn-dot.active { border-radius: 2px; animation: pulse-anim 1.2s infinite; }
.realtime-display {
  margin-top: var(--space-6); padding: var(--space-6); background: var(--color-bg);
  border-radius: var(--radius-lg); border: 1px solid var(--color-border); text-align: left;
}
.realtime-words { display: flex; flex-wrap: wrap; gap: var(--space-2); margin-bottom: var(--space-4); }
.rt-word { padding: var(--space-1) var(--space-2); border-radius: var(--radius-sm); font-size: var(--text-base); font-weight: 500; }
.rt-good { background: var(--color-success-light); color: var(--color-success); }
.rt-ok { background: var(--color-warning-light); color: #b45309; }
.rt-poor { background: var(--color-error-light); color: var(--color-error); }
.realtime-score { font-size: var(--text-lg); margin-bottom: var(--space-2); color: var(--color-text); }
.realtime-listening { display: flex; align-items: center; gap: var(--space-2); color: var(--color-text-secondary); }
.pulse-dot { width: 10px; height: 10px; background: var(--color-error); border-radius: var(--radius-full); animation: pulse-anim 1.2s infinite; }
@keyframes pulse-anim { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.4;transform:scale(0.8)} }
</style>
