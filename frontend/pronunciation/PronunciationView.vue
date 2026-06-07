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
      <div class="scenario-badge" @click="selectedScenario = null; result = null">
        {{ selectedScenario.icon }} {{ selectedScenario.name }} ✕
      </div>

      <!-- Sentence list -->
      <div class="sentence-list">
        <div
          v-for="(sent, i) in sentences"
          :key="i"
          class="sentence-card"
          :class="{ active: currentIndex === i, done: results[i] }"
          @click="selectSentence(i)"
        >
          <span class="sent-num">{{ i + 1 }}</span>
          <span class="sent-text">{{ sent }}</span>
          <span v-if="results[i]" class="sent-score">{{ results[i].pronunciation_score?.toFixed(0) }}</span>
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
            :class="{ active: isRecording, processing: isProcessing }"
            :disabled="isProcessing"
            @click="handleRecord"
          >
            🎙️ {{ recordBtnText }}
          </button>
        </div>

        <!-- Result display -->
        <div v-if="result" class="result-panel">
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

          <!-- Per-word breakdown -->
          <div v-if="result.words && result.words.length" class="word-breakdown">
            <span
              v-for="(w, j) in result.words"
              :key="j"
              class="word"
              :class="wordClass(w)"
              :title="`${w.accuracy_score?.toFixed(0)} - ${w.error_type}`"
            >
              {{ w.word }}
            </span>
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
          <p>共练习 <strong>{{ Object.keys(results).length }}</strong> / {{ sentences.length }} 句</p>
          <p v-if="weakWords.length">
            <span class="weak-title">需加强的单词：</span>
            <span v-for="w in weakWords" :key="w" class="weak-word">{{ w }}</span>
          </p>
        </div>
        <button class="summary-btn" @click="selectedScenario = null; showSummary = false; result = null">
          返回选择场景
        </button>
      </div>
    </div>

    <!-- Realtime Mode -->
    <div class="realtime-section">
      <h2>🔄 实时纠音模式</h2>
      <p class="realtime-desc">边说边看发音反馈，实时高亮每个词的发音质量</p>
      <button class="realtime-btn" :class="{ active: realtimeActive }" @click="toggleRealtime">
        {{ realtimeActive ? '⏹ 停止' : '▶ 开始实时纠音' }}
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
const results = ref({})
const result = ref(null)
const isProcessing = ref(false)
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

const recordBtnText = computed(() => {
  if (isProcessing.value) return t('pronunciation.processing')
  if (isRecording.value) return t('pronunciation.stop')
  return t('pronunciation.start')
})

async function selectScenario(s) {
  selectedScenario.value = s
  results.value = {}
  result.value = null
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
  result.value = results.value[i] || null
}

async function handleRecord() {
  if (isRecording.value) {
    await finishRecording()
  } else {
    result.value = null
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

  isProcessing.value = true
  const referenceText = sentences.value[currentIndex.value]

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
    result.value = data
    results.value[currentIndex.value] = data
  } catch (e) {
    const err = classifyError(e, e.status)
    toast.message = `${err.title}：${err.message}`
    toast.type = 'error'
  } finally {
    isProcessing.value = false
  }
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
    result.value = results.value[currentIndex.value] || null
  } else {
    // All done — show summary
    toast.message = t('pronunciation.allDone')
    toast.type = 'success'
    showSummary.value = true
    currentIndex.value = -1
    result.value = null
  }
}

function avgScore(key) {
  const vals = Object.values(results.value).map(r => r[key]).filter(v => v != null)
  if (!vals.length) return '--'
  return Math.round(vals.reduce((a, b) => a + b, 0) / vals.length)
}

const weakWords = computed(() => {
  const words = []
  Object.values(results.value).forEach(r => {
    if (r.words) {
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

.realtime-section { margin-top: 2.5rem; padding-top: 2rem; border-top: 1px solid #eee; text-align: center; }
.realtime-desc { color: #666; font-size: 0.9rem; margin-bottom: 1rem; }
.realtime-btn { padding: 0.75rem 2rem; background: #27ae60; color: white; border: none; border-radius: 8px; font-size: 1rem; cursor: pointer; }
.realtime-btn:hover { background: #219a52; }
.realtime-btn.active { background: #e74c3c; }
.realtime-btn.active:hover { background: #c0392b; }
.realtime-display { margin-top: 1.5rem; padding: 1.5rem; background: #fafafa; border-radius: 12px; border: 1px solid #eee; text-align: left; }
.realtime-words { display: flex; flex-wrap: wrap; gap: 0.4rem; margin-bottom: 1rem; }
.rt-word { padding: 0.3rem 0.5rem; border-radius: 4px; font-size: 1.05rem; font-weight: 500; }
.rt-good { background: #d4edda; color: #155724; }
.rt-ok { background: #fff3cd; color: #856404; }
.rt-poor { background: #f8d7da; color: #721c24; }
.realtime-score { font-size: 1.1rem; margin-bottom: 0.5rem; }
.realtime-listening { display: flex; align-items: center; gap: 0.5rem; color: #666; }
.pulse-dot { width: 10px; height: 10px; background: #e74c3c; border-radius: 50%; animation: pulse-anim 1.2s infinite; }
@keyframes pulse-anim { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.4;transform:scale(0.8)} }
</style>
