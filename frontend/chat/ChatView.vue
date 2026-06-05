<template>
  <div class="chat-view">
    <!-- Toast notification -->
    <Toast :message="toast.message" :type="toast.type" @close="toast.message = ''" />

    <header class="chat-header">
      <button @click="$router.push('/')" class="back-btn">← 返回</button>
      <h2>{{ scenarioName }}</h2>
      <span class="status" :class="statusClass">
        {{ statusText }}
      </span>
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
        </div>
      </div>

      <!-- Processing indicator -->
      <div v-if="state === 'PROCESSING'" class="message assistant">
        <div class="bubble typing-indicator">
          <span></span><span></span><span></span>
        </div>
      </div>
    </div>

    <div class="controls">
      <button
        class="record-btn"
        :class="{ active: isRecording, playing: state === 'PLAYING' }"
        :disabled="state === 'PROCESSING' || state === 'STREAMING'"
        @click="handleToggle"
      >
        🎙️ {{ buttonText }}
      </button>
      <!-- Retry button on error -->
      <button
        v-if="showRetry"
        class="retry-btn"
        @click="retryLast"
      >
        🔄 重试
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useRecorder } from '../../voice/audio/useRecorder'
import { streamChat } from '../../voice/asr/service'
import { CONFIG } from '../../shared/config'
import Toast from '../components/Toast.vue'

const route = useRoute()
const scenarioId = route.params.scenario
const scenario = CONFIG.SCENARIOS.find((s) => s.id === scenarioId)
const scenarioName = scenario ? `${scenario.icon} ${scenario.name}` : scenarioId

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

// Toast state
const toast = reactive({ message: '', type: 'info' })

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
    case 'RECORDING': return '🔴 录音中（点击或静音自动停止）'
    case 'PROCESSING': return '⏳ 识别中...'
    case 'STREAMING': return '💬 生成中...'
    case 'PLAYING': return '🔊 回复中（点击打断）'
    default: return '⏸️ 点击开始录音'
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

async function handleToggle() {
  console.log('[toggle] state:', state.value, 'isRecording:', isRecording.value)
  if (state.value === 'PLAYING') {
    interrupt()
    return
  }
  if (state.value === 'RECORDING') {
    const blob = await stop()
    console.log('[toggle] stopped, blob:', blob?.size)
    if (!blob) { state.value = 'IDLE'; return }
    state.value = 'PROCESSING'
    sendStreaming(blob)
    return
  }
  if (state.value === 'IDLE') {
    showRetry.value = false
    state.value = 'RECORDING'
    try {
      await start()
      console.log('[toggle] recording started')
    } catch (err) {
      console.error('[toggle] mic error:', err)
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
  lastBlob = blob // Save for retry
  console.log('[stream] sending blob:', blob.size, 'bytes')
  const history = messages.value
    .filter((m) => m.text && !m.text.startsWith('❌'))
    .map((m) => ({ role: m.role, content: m.text }))

  let aiMsgIndex = -1
  audioQueue = []

  currentAbort = streamChat(blob, scenarioId, history, sessionId, {
    onASR(text) {
      console.log('[stream] ASR:', text)
      messages.value.push({ role: 'user', text, corrections: [] })
      scrollToBottom()
      state.value = 'STREAMING'
    },
    onSentence(data) {
      console.log('[stream] sentence:', data.text)
      if (aiMsgIndex === -1) {
        messages.value.push({ role: 'assistant', text: data.text, audio: data.audio_url, corrections: [] })
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
    onDone(data) {
      sessionId = data.session_id || sessionId
      currentAbort = null
      if (audioQueue.length === 0 && state.value !== 'PLAYING') state.value = 'IDLE'
    },
    onError(msg) {
      console.error('[stream] ERROR:', msg)
      showToast(msg || '网络请求失败，请检查网络连接', 'error')
      showRetry.value = true
      state.value = 'IDLE'
      currentAbort = null
    },
  })
}

function playNext() {
  if (audioQueue.length === 0) { state.value = 'IDLE'; currentAudio = null; return }
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

onMounted(async () => {
  try {
    const res = await fetch(`/api/scenarios/${scenarioId}`)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    messages.value.push({ role: 'assistant', text: data.greeting })
  } catch {
    messages.value.push({ role: 'assistant', text: `Welcome! Let's practice English. Press the button to speak.` })
  } finally {
    loadingGreeting.value = false
  }
})

onUnmounted(() => { interrupt() })
</script>

<style scoped>
.chat-view { display: flex; flex-direction: column; height: calc(100vh - 120px); }

.chat-header {
  display: flex; align-items: center; gap: 1rem;
  padding-bottom: 1rem; border-bottom: 1px solid #e0e0e0;
}
.back-btn { background: none; border: none; font-size: 1rem; cursor: pointer; color: #1f4e79; }
.status { margin-left: auto; font-size: 0.85rem; color: #666; }
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

.controls { padding-top: 1rem; text-align: center; display: flex; justify-content: center; gap: 0.75rem; }

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
</style>