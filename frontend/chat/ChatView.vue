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
.chat-view {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 120px);
  animation: fade-in var(--transition-base) both;
}

/* Offline banner */
.offline-banner {
  background: var(--color-warning-light);
  color: #92400e;
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-md);
  text-align: center;
  font-size: var(--text-sm);
  margin-bottom: var(--space-2);
  font-weight: 500;
}

.record-btn.offline { opacity: 0.5; cursor: not-allowed; }

/* Header */
.chat-header {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-3) 0;
  border-bottom: 1px solid var(--color-border);
}

.back-btn {
  font-size: var(--text-base);
  color: var(--color-primary);
  font-weight: 500;
  padding: var(--space-2);
  border-radius: var(--radius-sm);
  transition: background var(--transition-fast);
}
.back-btn:hover { background: var(--color-primary-50); }

.header-info h2 { font-size: var(--text-lg); font-weight: 600; }
.char-name { font-size: var(--text-xs); color: var(--color-text-muted); }
.header-right { margin-left: auto; display: flex; align-items: center; gap: var(--space-3); }

.stats-mini {
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
  background: var(--color-border-light);
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
}

.status { font-size: var(--text-sm); color: var(--color-text-muted); font-weight: 500; }
.status.recording { color: var(--color-error); }
.status.processing { color: var(--color-warning); }
.status.playing { color: var(--color-primary); }

/* Messages */
.messages {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-4) 0;
}

.message {
  display: flex;
  margin-bottom: var(--space-4);
  animation: slide-up 300ms ease both;
}

.message.user { justify-content: flex-end; }

.bubble {
  max-width: 75%;
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-lg);
  line-height: 1.6;
  font-size: var(--text-base);
}

.user .bubble {
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  color: white;
  border-bottom-right-radius: var(--radius-sm);
  box-shadow: 0 2px 8px rgba(26, 86, 219, 0.2);
}

.assistant .bubble {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-bottom-left-radius: var(--radius-sm);
  box-shadow: var(--shadow-sm);
}

.play-btn {
  cursor: pointer;
  margin-left: var(--space-2);
  opacity: 0.7;
  transition: opacity var(--transition-fast);
}
.play-btn:hover { opacity: 1; }

/* Corrections */
.corrections {
  margin-top: var(--space-2);
  padding-top: var(--space-2);
  border-top: 1px dashed rgba(255, 255, 255, 0.25);
  font-size: var(--text-sm);
}

.correction-title { font-weight: 600; margin-bottom: var(--space-1); }
.correction-item { margin-bottom: var(--space-1); }
.original { text-decoration: line-through; opacity: 0.6; }
.arrow { margin: 0 var(--space-1); opacity: 0.8; }
.corrected { font-weight: 600; }
.explanation { opacity: 0.75; font-size: var(--text-xs); margin-top: 2px; }

.feedback-line {
  margin-top: var(--space-2);
  padding: var(--space-2) var(--space-3);
  background: rgba(255, 255, 255, 0.12);
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
  font-style: italic;
}

/* Hint system */
.hint-panel {
  background: var(--color-primary-50);
  border: 1px solid var(--color-primary-200);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  margin: var(--space-2) 0;
  animation: scale-in var(--transition-base) both;
}

.hint-title { font-size: var(--text-sm); font-weight: 600; margin-bottom: var(--space-3); color: var(--color-text); }

.hint-item {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-3);
  margin-bottom: var(--space-2);
  transition: border-color var(--transition-fast);
}

.hint-item:hover { border-color: var(--color-primary-200); }
.hint-item.easy { border-left: 3px solid var(--color-success); }
.hint-item.medium { border-left: 3px solid var(--color-warning); }
.hint-item.hard { border-left: 3px solid var(--color-advanced); }
.hint-text { font-size: var(--text-sm); color: var(--color-primary-dark); font-weight: 500; margin-bottom: 2px; }
.hint-zh { font-size: var(--text-xs); color: var(--color-text-muted); }

.hint-dismiss {
  margin-top: var(--space-2);
  padding: var(--space-1) var(--space-3);
  background: var(--color-border);
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  transition: background var(--transition-fast);
}
.hint-dismiss:hover { background: var(--color-text-muted); color: white; }

/* Controls */
.controls {
  padding: var(--space-4) 0;
  display: flex;
  justify-content: center;
  gap: var(--space-3);
  align-items: center;
}

.hint-btn {
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-full);
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text-secondary);
  transition: all var(--transition-fast);
}
.hint-btn:hover { border-color: var(--color-primary); color: var(--color-primary); }
.hint-btn.pulse { animation: hint-pulse 2s infinite; }

.record-btn {
  padding: var(--space-4) var(--space-8);
  border-radius: var(--radius-full);
  border: 2px solid var(--color-primary);
  background: var(--color-surface);
  font-size: var(--text-lg);
  font-weight: 500;
  color: var(--color-primary);
  transition: all var(--transition-base);
  user-select: none;
  position: relative;
}

.record-btn::before {
  content: '';
  position: absolute;
  inset: -4px;
  border-radius: var(--radius-full);
  border: 2px solid transparent;
  transition: border-color var(--transition-fast);
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
}

.record-btn.active::before {
  border-color: var(--color-error);
  animation: pulse-ring 1.5s infinite;
}

.record-btn.playing {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: white;
}

.retry-btn {
  padding: var(--space-3) var(--space-5);
  border-radius: var(--radius-full);
  border: 2px solid var(--color-warning);
  background: var(--color-warning-light);
  color: #92400e;
  font-size: var(--text-sm);
  font-weight: 500;
  transition: all var(--transition-fast);
}
.retry-btn:hover { background: #fde68a; }

/* Skeleton */
.skeleton { min-width: 180px; }
.skeleton-line {
  height: 0.85rem;
  background: linear-gradient(90deg, var(--color-border-light) 25%, var(--color-border) 50%, var(--color-border-light) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: var(--radius-sm);
  margin-bottom: var(--space-2);
}
.skeleton-line.short { width: 60%; }

/* Typing indicator */
.typing-indicator {
  display: flex;
  gap: 5px;
  padding: var(--space-3) var(--space-4);
  align-items: center;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-text-muted);
  animation: typing 1.2s infinite;
}
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

/* End session */
.end-btn {
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-full);
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  transition: all var(--transition-fast);
}
.end-btn:hover { border-color: var(--color-primary); color: var(--color-primary); }

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-modal);
  animation: fade-in 200ms both;
}

.modal {
  background: var(--color-surface);
  border-radius: var(--radius-xl);
  padding: var(--space-8);
  max-width: 480px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  animation: scale-in var(--transition-base) both;
  box-shadow: var(--shadow-xl);
}

.modal h3 { color: var(--color-primary); margin-bottom: var(--space-6); font-size: var(--text-xl); }

.report-stats { display: flex; justify-content: center; gap: var(--space-8); margin-bottom: var(--space-6); }
.stat { text-align: center; }
.stat-value { display: block; font-size: var(--text-3xl); font-weight: 800; color: var(--color-primary); }
.stat-label { font-size: var(--text-xs); color: var(--color-text-muted); font-weight: 500; }

.report-narrative {
  background: var(--color-primary-50);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  margin-bottom: var(--space-4);
  font-size: var(--text-sm);
  line-height: 1.7;
}

.report-errors { margin-bottom: var(--space-4); }
.report-errors h4 { font-size: var(--text-sm); color: var(--color-warning); margin-bottom: var(--space-2); }
.report-errors ul { padding-left: var(--space-5); }
.report-errors li { font-size: var(--text-sm); color: var(--color-text-secondary); margin-bottom: var(--space-1); }

.modal-close-btn {
  width: 100%;
  padding: var(--space-3);
  background: var(--color-primary);
  color: white;
  border-radius: var(--radius-md);
  font-size: var(--text-base);
  font-weight: 600;
  transition: background var(--transition-fast);
}
.modal-close-btn:hover { background: var(--color-primary-dark); }

/* Animations */
@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
@keyframes typing {
  0%, 60%, 100% { opacity: 0.3; transform: scale(0.8); }
  30% { opacity: 1; transform: scale(1); }
}
@keyframes hint-pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(26, 86, 219, 0.3); }
  50% { box-shadow: 0 0 0 8px rgba(26, 86, 219, 0); }
}

/* Responsive */
@media (max-width: 768px) {
  .chat-view { height: calc(100vh - 160px); }
  .bubble { max-width: 85%; }
  .record-btn { padding: var(--space-3) var(--space-6); font-size: var(--text-base); }
  .chat-header { padding: var(--space-2) 0; }
}
</style>
