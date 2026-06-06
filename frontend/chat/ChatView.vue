<template>
  <div class="chat-view">
    <!-- Toast notification -->
    <Toast :message="toast.message" :type="toast.type" @close="toast.message = ''" />

    <!-- Offline banner -->
    <div v-if="!isOnline" class="offline-banner">
      ⚠️ 网络已断开，录音功能暂不可用
    </div>

    <header class="chat-header">
      <button @click="$router.push('/')" class="back-btn">← 返回</button>
      <div class="header-info">
        <h2>{{ characterAvatar }} {{ scenarioName }}</h2>
        <span v-if="characterName" class="char-name">{{ characterName }}</span>
      </div>
      <div class="header-right">
        <span class="stats-mini" v-if="messages.length > 1">
          💬 {{ turnCount }} | ✏️ {{ correctionCount }}
        </span>
        <span class="status" :class="statusClass">
          {{ statusText }}
        </span>
      </div>
    </header>

    <div class="messages" ref="messagesRef">
      <!-- Loading skeleton for initial greeting -->
      <div v-if="loadingGreeting" class="message assistant">
        <div class="bubble skeleton">
          <div class="skeleton-line"></div>
          <div class="skeleton-line short"></div>
        </div>
      </div>

      <div
        v-for="(msg, i) in messages"
        :key="i"
        class="message"
        :class="msg.role"
      >
        <div class="bubble">
          <p>{{ msg.text }}</p>
          <span v-if="msg.audio" class="play-btn" @click="handleManualPlay(msg.audio)">
            🔊
          </span>
          <!-- Grammar corrections -->
          <div v-if="msg.corrections && msg.corrections.length" class="corrections">
            <p class="correction-title">📝 语法建议：</p>
            <div v-for="(c, j) in msg.corrections" :key="j" class="correction-item">
              <span class="original">{{ c.original }}</span>
              <span class="arrow">→</span>
              <span class="corrected">{{ c.corrected }}</span>
              <p class="explanation">{{ c.explanation }}</p>
            </div>
          </div>
          <!-- Feedback -->
          <div v-if="msg.feedback" class="feedback-line">
            {{ msg.feedback }}
          </div>
        </div>
      </div>

      <!-- Processing indicator -->
      <div v-if="state === 'PROCESSING'" class="message assistant">
        <div class="bubble typing-indicator">
          <span></span><span></span><span></span>
        </div>
      </div>

      <!-- Hint panel -->
      <div v-if="showHintPanel && hints.length" class="hint-panel">
        <p class="hint-title">💡 不知道说什么？试试这些：</p>
        <div
          v-for="(h, i) in hints"
          :key="i"
          class="hint-item"
          :class="h.difficulty"
        >
          <p class="hint-text">"{{ h.text }}"</p>
          <p class="hint-zh">{{ h.hint }}</p>
        </div>
        <button class="hint-dismiss" @click="showHintPanel = false">知道了</button>
      </div>
    </div>

    <div class="controls">
      <!-- Hint button -->
      <button
        v-if="state === 'IDLE' && messages.length > 0"
        class="hint-btn"
        :class="{ pulse: showHintPrompt }"
        :disabled="loadingHints"
        @click="requestHints"
      >
        💡 {{ loadingHints ? '...' : '提示' }}
      </button>

      <button
        class="record-btn"
        :class="{ active: isRecording, playing: state === 'PLAYING', offline: !isOnline }"
        :disabled="state === 'PROCESSING' || state === 'STREAMING' || !isOnline"
        @click="handleToggle"
      >
        🎙️ {{ !isOnline ? '离线中' : buttonText }}
      </button>
      <!-- Retry button on error -->
      <button
        v-if="showRetry"
        class="retry-btn"
        @click="retryLast"
      >
        🔄 重试
      </button>

      <!-- End session button -->
      <button
        v-if="state === 'IDLE' && turnCount >= 3"
        class="end-btn"
        @click="endSession"
      >
        📋 结束练习
      </button>
    </div>

    <!-- Session Report Modal -->
    <div v-if="showReport" class="modal-overlay" @click.self="showReport = false">
      <div class="modal">
        <h3>📋 本次练习报告</h3>
        <div class="report-stats">
          <div class="stat">
            <span class="stat-value">{{ reportData.total_turns || 0 }}</span>
            <span class="stat-label">对话轮次</span>
          </div>
          <div class="stat">
            <span class="stat-value">{{ reportData.total_corrections || 0 }}</span>
            <span class="stat-label">语法建议</span>
          </div>
          <div class="stat" v-if="reportData.avg_pronunciation">
            <span class="stat-value">{{ reportData.avg_pronunciation?.toFixed(0) }}</span>
            <span class="stat-label">发音评分</span>
          </div>
        </div>
        <div v-if="reportData.report" class="report-narrative">
          <p>{{ reportData.report }}</p>
        </div>
        <div v-if="reportData.common_errors?.length" class="report-errors">
          <h4>常见问题：</h4>
          <ul>
            <li v-for="e in reportData.common_errors" :key="e.pattern">
              {{ e.pattern }} (×{{ e.count }})
            </li>
          </ul>
        </div>
        <button class="modal-close-btn" @click="showReport = false; $router.push('/')">
          返回首页
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useRecorder } from '../../voice/audio/useRecorder'
import { streamChat } from '../../voice/asr/service'
import { useNetwork } from '../composables/useNetwork'
import { classifyError } from '../composables/useErrorHandler'
import { CONFIG } from '../../shared/config'
import Toast from '../components/Toast.vue'

const route = useRoute()
const { isOnline } = useNetwork()
const scenarioId = route.params.scenario
const scenario = CONFIG.SCENARIOS.find((s) => s.id === scenarioId)
const scenarioName = scenario ? scenario.name : scenarioId
const characterAvatar = ref(scenario?.icon || '💬')
const characterName = ref('')

// State machine: IDLE → RECORDING → PROCESSING → STREAMING → PLAYING → IDLE
const state = ref('IDLE')
const messages = ref([])
const messagesRef = ref(null)
const loadingGreeting = ref(true)
const showRetry = ref(false)
// Accept a pre-created session handed off from an external tool (e.g.
// talent-agent's custom interview). When present, /api/stream reuses this
// session and honors its custom interviewer prompt.
let sessionId = route.query.session_id || ''
let currentAbort = null
let audioQueue = []
let currentAudio = null
let lastBlob = null // For retry

// Hint system
const showHintPrompt = ref(false)
const showHintPanel = ref(false)
const hints = ref([])
const loadingHints = ref(false)
let hintTimer = null

// Stats
const turnCount = computed(() => messages.value.filter((m) => m.role === 'user').length)
const correctionCount = computed(() =>
  messages.value.reduce((sum, m) => sum + (m.corrections?.length || 0), 0)
)

// Toast state
const toast = reactive({ message: '', type: 'info' })

// Session report
const showReport = ref(false)
const reportData = ref({})

function showToast(message, type = 'error') {
  toast.message = message
  toast.type = type
}

const { start, stop, isRecording } = useRecorder({
  silenceMs: CONFIG.AUDIO.VAD_SILENCE_MS,
  onSilence: async () => {
    if (state.value !== 'RECORDING' || !isRecording.value) return
    const blob = await stop()
    if (!blob) { state.value = 'IDLE'; return }
    state.value = 'PROCESSING'
    sendStreaming(blob)
  },
})

const statusClass = computed(() => ({
  recording: state.value === 'RECORDING',
  processing: state.value === 'PROCESSING' || state.value === 'STREAMING',
  playing: state.value === 'PLAYING',
}))

const statusText = computed(() => {
  switch (state.value) {
    case 'RECORDING': return '🔴 录音中'
    case 'PROCESSING': return '⏳ 识别中...'
    case 'STREAMING': return '💬 生成中...'
    case 'PLAYING': return '🔊 回复中'
    default: return '⏸️ 点击录音'
  }
})

const buttonText = computed(() => {
  switch (state.value) {
    case 'RECORDING': return '点击停止'
    case 'PROCESSING': return '处理中...'
    case 'STREAMING': return '生成中...'
    case 'PLAYING': return '点击打断'
    default: return '点击录音'
  }
})

// --- Hint system ---
function resetHintTimer() {
  showHintPrompt.value = false
  if (hintTimer) clearTimeout(hintTimer)
  hintTimer = setTimeout(() => {
    if (state.value === 'IDLE' && messages.value.length > 0) {
      showHintPrompt.value = true
    }
  }, CONFIG.HINT.SILENCE_TRIGGER_MS)
}

async function requestHints() {
  loadingHints.value = true
  showHintPanel.value = false
  try {
    const history = messages.value
      .filter((m) => m.text && !m.text.startsWith('❌'))
      .map((m) => ({ role: m.role, content: m.text }))

    const formData = new FormData()
    formData.append('scenario', scenarioId)
    formData.append('history', JSON.stringify(history))

    const res = await fetch('/api/hint', { method: 'POST', body: formData })
    if (res.ok) {
      const data = await res.json()
      hints.value = data.hints || []
      showHintPanel.value = hints.value.length > 0
    }
  } catch (e) {
    console.error('[hint] error:', e)
  } finally {
    loadingHints.value = false
    showHintPrompt.value = false
  }
}

// --- Core handlers ---
async function handleToggle() {
  if (state.value === 'PLAYING') {
    interrupt()
    return
  }
  if (state.value === 'RECORDING') {
    const blob = await stop()
    if (!blob) { state.value = 'IDLE'; return }
    state.value = 'PROCESSING'
    sendStreaming(blob)
    return
  }
  if (state.value === 'IDLE') {
    showRetry.value = false
    showHintPanel.value = false
    state.value = 'RECORDING'
    try {
      await start()
    } catch (err) {
      state.value = 'IDLE'
      showToast('麦克风权限被拒绝，请在浏览器设置中允许麦克风访问', 'warning')
      scrollToBottom()
    }
  }
}

function interrupt() {
  if (currentAudio) { currentAudio.pause(); currentAudio = null }
  audioQueue = []
  if (currentAbort) { currentAbort.abort(); currentAbort = null }
  state.value = 'IDLE'
}

function retryLast() {
  if (!lastBlob) return
  showRetry.value = false
  state.value = 'PROCESSING'
  sendStreaming(lastBlob)
}

function sendStreaming(blob) {
  lastBlob = blob
  showHintPanel.value = false
  const history = messages.value
    .filter((m) => m.text && !m.text.startsWith('❌'))
    .map((m) => ({ role: m.role, content: m.text }))

  let aiMsgIndex = -1
  audioQueue = []

  currentAbort = streamChat(blob, scenarioId, history, sessionId, {
    onASR(text) {
      messages.value.push({ role: 'user', text, corrections: [], feedback: null })
      scrollToBottom()
      state.value = 'STREAMING'
    },
    onSentence(data) {
      if (aiMsgIndex === -1) {
        messages.value.push({ role: 'assistant', text: data.text, audio: data.audio_url, corrections: [], feedback: null })
        aiMsgIndex = messages.value.length - 1
      } else {
        messages.value[aiMsgIndex].text += ' ' + data.text
        messages.value[aiMsgIndex].audio = data.audio_url
      }
      scrollToBottom()
      if (data.audio_url) {
        audioQueue.push(data.audio_url)
        if (audioQueue.length === 1 && state.value === 'STREAMING') {
          state.value = 'PLAYING'
          playNext()
        }
      }
    },
    onCorrections(corrections) {
      const userMsg = messages.value.filter((m) => m.role === 'user').pop()
      if (userMsg) userMsg.corrections = corrections
      scrollToBottom()
    },
    onFeedback(data) {
      // Attach feedback to the last user message
      const userMsg = messages.value.filter((m) => m.role === 'user').pop()
      if (userMsg) userMsg.feedback = data.text
      scrollToBottom()
    },
    onDone(data) {
      sessionId = data.session_id || sessionId
      currentAbort = null
      if (audioQueue.length === 0 && state.value !== 'PLAYING') state.value = 'IDLE'
      resetHintTimer()
    },
    onError(msg) {
      const err = classifyError(msg)
      showToast(`${err.title}：${err.message}`, 'error')
      if (err.action === 'refresh') {
        setTimeout(() => { if (confirm('是否刷新页面？')) location.reload() }, 5000)
      }
      showRetry.value = true
      state.value = 'IDLE'
      currentAbort = null
    },
  })
}

function playNext() {
  if (audioQueue.length === 0) { state.value = 'IDLE'; currentAudio = null; resetHintTimer(); return }
  const url = audioQueue.shift()
  currentAudio = new Audio(url)
  currentAudio.onended = () => { currentAudio = null; playNext() }
  currentAudio.onerror = () => { currentAudio = null; playNext() }
  currentAudio.play().catch(() => playNext())
}

function handleManualPlay(url) {
  if (currentAudio) { currentAudio.pause(); currentAudio = null }
  currentAudio = new Audio(url)
  currentAudio.play().catch(() => {})
  currentAudio.onended = () => { currentAudio = null }
}

function scrollToBottom() {
  nextTick(() => { if (messagesRef.value) messagesRef.value.scrollTop = messagesRef.value.scrollHeight })
}

async function endSession() {
  if (!sessionId) return
  try {
    const res = await fetch(`/api/sessions/${sessionId}/end`, { method: 'POST' })
    if (res.ok) {
      reportData.value = await res.json()
      showReport.value = true
    } else {
      showToast('获取报告失败', 'error')
    }
  } catch {
    showToast('网络错误', 'error')
  }
}

onMounted(async () => {
  try {
    const res = await fetch(`/api/scenarios/${scenarioId}`)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    messages.value.push({ role: 'assistant', text: data.greeting })
    if (data.character) {
      characterName.value = data.character.name
      characterAvatar.value = data.character.avatar || scenario?.icon || '💬'
    }
  } catch {
    messages.value.push({ role: 'assistant', text: `Welcome! Let's practice English. Press the button to speak.` })
  } finally {
    loadingGreeting.value = false
    resetHintTimer()
  }
})

onUnmounted(() => {
  interrupt()
  if (hintTimer) clearTimeout(hintTimer)
})
</script>

<style scoped>
.chat-view { display: flex; flex-direction: column; height: calc(100vh - 120px); }

.offline-banner {
  background: #fff3cd;
  color: #856404;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  text-align: center;
  font-size: 0.85rem;
  margin-bottom: 0.5rem;
}

.record-btn.offline {
  opacity: 0.5;
  cursor: not-allowed;
}

.chat-header {
  display: flex; align-items: center; gap: 1rem;
  padding-bottom: 1rem; border-bottom: 1px solid #e0e0e0;
}
.back-btn { background: none; border: none; font-size: 1rem; cursor: pointer; color: #1f4e79; }
.header-info h2 { margin: 0; font-size: 1.1rem; }
.char-name { font-size: 0.8rem; color: #888; }
.header-right { margin-left: auto; display: flex; align-items: center; gap: 0.8rem; }
.stats-mini { font-size: 0.8rem; color: #666; background: #f5f5f5; padding: 0.2rem 0.6rem; border-radius: 10px; }
.status { font-size: 0.85rem; color: #666; }
.status.recording { color: #e53935; font-weight: 600; }
.status.processing { color: #f57c00; }
.status.playing { color: #1f4e79; font-weight: 600; }

.messages { flex: 1; overflow-y: auto; padding: 1rem 0; }
.message { display: flex; margin-bottom: 1rem; }
.message.user { justify-content: flex-end; }

.bubble { max-width: 70%; padding: 0.8rem 1.2rem; border-radius: 12px; line-height: 1.5; }
.user .bubble { background: #1f4e79; color: white; border-bottom-right-radius: 4px; }
.assistant .bubble { background: white; border: 1px solid #e0e0e0; border-bottom-left-radius: 4px; }

.play-btn { cursor: pointer; margin-left: 0.5rem; }

.corrections {
  margin-top: 0.5rem; padding-top: 0.5rem;
  border-top: 1px dashed rgba(255,255,255,0.3); font-size: 0.85rem;
}
.correction-title { font-weight: 600; margin-bottom: 0.3rem; }
.correction-item { margin-bottom: 0.3rem; }
.original { text-decoration: line-through; opacity: 0.7; }
.arrow { margin: 0 0.3rem; }
.corrected { font-weight: 600; }
.explanation { opacity: 0.8; font-size: 0.8rem; margin-top: 0.1rem; }

.feedback-line {
  margin-top: 0.5rem;
  padding: 0.3rem 0.6rem;
  background: rgba(255,255,255,0.15);
  border-radius: 6px;
  font-size: 0.82rem;
  font-style: italic;
}

/* Hint system */
.hint-panel {
  background: #f8f9ff;
  border: 1px solid #e3e8f0;
  border-radius: 12px;
  padding: 1rem;
  margin: 0.5rem 0;
}
.hint-title { font-size: 0.9rem; font-weight: 600; margin-bottom: 0.6rem; color: #333; }
.hint-item {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 0.6rem 0.8rem;
  margin-bottom: 0.5rem;
}
.hint-item.easy { border-left: 3px solid #4caf50; }
.hint-item.medium { border-left: 3px solid #ff9800; }
.hint-item.hard { border-left: 3px solid #e91e63; }
.hint-text { font-size: 0.9rem; color: #1f4e79; font-weight: 500; margin-bottom: 0.2rem; }
.hint-zh { font-size: 0.8rem; color: #888; }
.hint-dismiss {
  margin-top: 0.5rem;
  padding: 0.3rem 0.8rem;
  border: none;
  background: #e0e0e0;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.8rem;
}

.controls { padding-top: 1rem; text-align: center; display: flex; justify-content: center; gap: 0.75rem; align-items: center; }

.hint-btn {
  padding: 0.6rem 1rem;
  border-radius: 50px;
  border: 1px solid #e0e0e0;
  background: white;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
}
.hint-btn:hover { border-color: #1f4e79; color: #1f4e79; }
.hint-btn.pulse { animation: hint-pulse 2s infinite; }
.hint-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.record-btn {
  padding: 1rem 2.5rem; border-radius: 50px; border: 2px solid #1f4e79;
  background: white; font-size: 1.1rem; cursor: pointer;
  transition: all 0.2s; user-select: none;
}
.record-btn.active { background: #e53935; border-color: #e53935; color: white; transform: scale(1.05); }
.record-btn.playing { background: #1f4e79; border-color: #1f4e79; color: white; }
.record-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.retry-btn {
  padding: 0.75rem 1.5rem; border-radius: 50px; border: 2px solid #f57c00;
  background: #fff3e0; color: #e65100; font-size: 0.95rem; cursor: pointer;
  transition: all 0.2s;
}
.retry-btn:hover { background: #ffe0b2; }

/* Loading skeleton */
.skeleton { min-width: 200px; }
.skeleton-line {
  height: 0.9rem; background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%; animation: shimmer 1.5s infinite;
  border-radius: 4px; margin-bottom: 0.5rem;
}
.skeleton-line.short { width: 60%; }

/* Typing indicator */
.typing-indicator {
  display: flex; gap: 4px; padding: 0.8rem 1.2rem; align-items: center;
}
.typing-indicator span {
  width: 8px; height: 8px; border-radius: 50%; background: #999;
  animation: typing 1.2s infinite;
}
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
@keyframes typing {
  0%, 60%, 100% { opacity: 0.3; transform: scale(0.8); }
  30% { opacity: 1; transform: scale(1); }
}
@keyframes hint-pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(31,78,121,0.4); }
  50% { box-shadow: 0 0 0 8px rgba(31,78,121,0); }
}

.end-btn {
  padding: 0.6rem 1rem;
  border-radius: 50px;
  border: 1px solid #e0e0e0;
  background: white;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
}
.end-btn:hover { border-color: #1f4e79; color: #1f4e79; }

/* Report modal */
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 100;
}
.modal {
  background: white; border-radius: 16px; padding: 2rem; max-width: 500px; width: 90%; max-height: 80vh; overflow-y: auto;
}
.modal h3 { color: #1f4e79; margin-bottom: 1.2rem; }
.report-stats { display: flex; justify-content: center; gap: 2rem; margin-bottom: 1.5rem; }
.stat { text-align: center; }
.stat-value { display: block; font-size: 1.8rem; font-weight: 700; color: #1f4e79; }
.stat-label { font-size: 0.8rem; color: #888; }
.report-narrative {
  background: #f8f9ff; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;
  font-size: 0.9rem; line-height: 1.6; color: #333;
}
.report-errors { margin-bottom: 1rem; }
.report-errors h4 { font-size: 0.9rem; color: #e65100; margin-bottom: 0.5rem; }
.report-errors ul { padding-left: 1.2rem; }
.report-errors li { font-size: 0.85rem; color: #555; margin-bottom: 0.3rem; }
.modal-close-btn {
  width: 100%; padding: 0.7rem; background: #1f4e79; color: white;
  border: none; border-radius: 8px; cursor: pointer; font-size: 0.95rem;
}
.modal-close-btn:hover { background: #2a6399; }
</style>
