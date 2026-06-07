<template>
  <div class="pronunciation-view">
    <Toast :message="toast.message" :type="toast.type" @close="toast.message = ''" />

    <header class="page-header">
      <button @click="$router.push('/')" class="back-btn">← 返回</button>
      <h1>🎯 发音练习</h1>
    </header>

    <!-- Scenario selection -->
    <div v-if="!selectedScenario" class="scenario-picker">
      <p class="subtitle">选择一个场景，练习该场景下的常用句子</p>
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
          <p class="label">跟读这句话：</p>
          <p class="text">{{ sentences[currentIndex] }}</p>
          <button class="listen-btn" @click="listenReference" :disabled="isPlaying">
            🔊 听示范
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
              <span class="score-label">总分</span>
            </div>
            <div class="score-item">
              <span class="score-value" :class="scoreClass(result.accuracy_score)">
                {{ result.accuracy_score?.toFixed(0) }}
              </span>
              <span class="score-label">准确度</span>
            </div>
            <div class="score-item">
              <span class="score-value" :class="scoreClass(result.fluency_score)">
                {{ result.fluency_score?.toFixed(0) }}
              </span>
              <span class="score-label">流利度</span>
            </div>
            <div class="score-item">
              <span class="score-value" :class="scoreClass(result.completeness_score)">
                {{ result.completeness_score?.toFixed(0) }}
              </span>
              <span class="score-label">完整度</span>
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
            {{ currentIndex < sentences.length - 1 ? '下一句 →' : '🎉 完成！' }}
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
import { CONFIG } from '../../shared/config'
import Toast from '../components/Toast.vue'

const scenarios = CONFIG.SCENARIOS
const selectedScenario = ref(null)
const sentences = ref([])
const currentIndex = ref(-1)
const results = ref({})
const result = ref(null)
const isProcessing = ref(false)
const isPlaying = ref(false)
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
  if (isProcessing.value) return '评分中...'
  if (isRecording.value) return '停止录音'
  return '开始跟读'
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
      toast.message = '麦克风权限被拒绝'
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
      throw new Error(err.detail || 'Assessment failed')
    }
    const data = await res.json()
    result.value = data
    results.value[currentIndex.value] = data
  } catch (e) {
    toast.message = e.message || '发音评测失败'
    toast.type = 'error'
  } finally {
    isProcessing.value = false
  }
}

async function listenReference() {
  const text = sentences.value[currentIndex.value]
  if (!text) return

  // Use browser speech synthesis as quick demo (or could call TTS endpoint)
  if (currentAudio) { currentAudio.pause(); currentAudio = null }
  isPlaying.value = true

  if ('speechSynthesis' in window) {
    const utter = new SpeechSynthesisUtterance(text)
    utter.lang = 'en-US'
    utter.rate = 0.9
    utter.onend = () => { isPlaying.value = false }
    utter.onerror = () => { isPlaying.value = false }
    speechSynthesis.speak(utter)
  } else {
    isPlaying.value = false
  }
}

function nextSentence() {
  if (currentIndex.value < sentences.value.length - 1) {
    currentIndex.value++
    result.value = results.value[currentIndex.value] || null
  } else {
    // All done — show summary
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
}

.page-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}
.page-header h1 { font-size: 1.5rem; color: #1f4e79; }
.back-btn { background: none; border: none; font-size: 1rem; cursor: pointer; color: #1f4e79; }

.subtitle { color: #666; margin-bottom: 1rem; text-align: center; }

.scenario-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  justify-content: center;
}
.scenario-chip {
  padding: 0.5rem 1rem;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}
.scenario-chip:hover { border-color: #1f4e79; color: #1f4e79; }

.scenario-badge {
  display: inline-block;
  padding: 0.4rem 1rem;
  background: #f0f7ff;
  border-radius: 20px;
  font-size: 0.9rem;
  color: #1f4e79;
  cursor: pointer;
  margin-bottom: 1rem;
}

.sentence-list { margin-bottom: 1.5rem; }
.sentence-card {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 0.8rem 1rem;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  margin-bottom: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}
.sentence-card.active { border-color: #1f4e79; background: #f0f7ff; }
.sentence-card.done { border-left: 3px solid #4caf50; }
.sent-num { font-weight: 600; color: #999; min-width: 20px; }
.sent-text { flex: 1; font-size: 0.9rem; }
.sent-score { font-weight: 700; color: #1f4e79; }

.active-practice { text-align: center; }
.reference-text {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}
.reference-text .label { font-size: 0.85rem; color: #888; margin-bottom: 0.5rem; }
.reference-text .text { font-size: 1.2rem; color: #333; line-height: 1.6; }
.listen-btn {
  margin-top: 0.8rem;
  padding: 0.4rem 1rem;
  border: 1px solid #e0e0e0;
  border-radius: 20px;
  background: white;
  cursor: pointer;
  font-size: 0.85rem;
}
.listen-btn:hover { border-color: #1f4e79; }
.listen-btn:disabled { opacity: 0.5; }

.record-area { margin-bottom: 1.5rem; }
.record-btn {
  padding: 1rem 2.5rem;
  border-radius: 50px;
  border: 2px solid #1f4e79;
  background: white;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.2s;
}
.record-btn.active { background: #e53935; border-color: #e53935; color: white; }
.record-btn.processing { opacity: 0.6; cursor: not-allowed; }
.record-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.result-panel {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  border: 1px solid #e0e0e0;
}

.scores-row {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  margin-bottom: 1.2rem;
}
.score-item { text-align: center; }
.score-value { display: block; font-size: 1.8rem; font-weight: 700; }
.score-value.good { color: #4caf50; }
.score-value.ok { color: #ff9800; }
.score-value.poor { color: #e53935; }
.score-label { font-size: 0.75rem; color: #888; }

.word-breakdown {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  justify-content: center;
  margin-bottom: 1.2rem;
  padding: 1rem;
  background: #f9f9f9;
  border-radius: 8px;
}
.word {
  padding: 0.3rem 0.5rem;
  border-radius: 4px;
  font-size: 0.95rem;
}
.word-good { background: #e8f5e9; color: #2e7d32; }
.word-ok { background: #fff3e0; color: #e65100; }
.word-poor { background: #fce4ec; color: #c62828; }
.word-error { background: #fce4ec; color: #c62828; text-decoration: underline; }

.next-btn {
  padding: 0.7rem 1.5rem;
  background: #1f4e79;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.95rem;
}
.next-btn:hover { background: #2a6399; }

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
