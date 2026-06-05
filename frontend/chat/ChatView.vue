<template>
  <div class="chat-view">
    <header class="chat-header">
      <button @click="$router.push('/')" class="back-btn">← 返回</button>
      <h2>{{ scenarioName }}</h2>
      <span class="status" :class="statusClass">
        {{ statusText }}
      </span>
    </header>

    <div class="messages" ref="messagesRef">
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
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useRecorder } from '../../voice/audio/useRecorder'
import { streamChat } from '../../voice/asr/service'
import { CONFIG } from '../../shared/config'

const route = useRoute()
const scenarioId = route.params.scenario
const scenario = CONFIG.SCENARIOS.find((s) => s.id === scenarioId)
const scenarioName = scenario ? `${scenario.icon} ${scenario.name}` : scenarioId

// State machine: IDLE → RECORDING → PROCESSING → STREAMING → PLAYING → IDLE
const state = ref('IDLE')
const messages = ref([])
const messagesRef = ref(null)
let sessionId = ''
let currentAbort = null
let audioQueue = []
let currentAudio = null

const { start, stop, isRecording } = useRecorder({
  silenceMs: CONFIG.AUDIO.VAD_SILENCE_MS,
  onSilence: async () => {
    if (state.value !== 'RECORDING') return
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
  if (state.value === 'PLAYING') {
    interrupt()
    return
  }
  if (state.value === 'RECORDING') {
    // Stop recording and send
    const blob = await stop()
    if (!blob) { state.value = 'IDLE'; return }
    state.value = 'PROCESSING'
    sendStreaming(blob)
    return
  }
  // Start recording
  if (state.value === 'IDLE') {
    state.value = 'RECORDING'
    await start()
  }
}

function interrupt() {
  if (currentAudio) { currentAudio.pause(); currentAudio = null }
  audioQueue = []
  if (currentAbort) { currentAbort.abort(); currentAbort = null }
  state.value = 'IDLE'
}

function sendStreaming(blob) {
  const history = messages.value
    .filter((m) => m.text && !m.text.startsWith('❌'))
    .map((m) => ({ role: m.role, content: m.text }))

  let aiMsgIndex = -1
  audioQueue = []

  currentAbort = streamChat(blob, scenarioId, history, sessionId, {
    onASR(text) {
      messages.value.push({ role: 'user', text, corrections: [] })
      scrollToBottom()
      state.value = 'STREAMING'
    },
    onSentence(data) {
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
      messages.value.push({ role: 'user', text: `❌ ${msg}` })
      state.value = 'IDLE'
      currentAbort = null
      scrollToBottom()
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
    const data = await res.json()
    messages.value.push({ role: 'assistant', text: data.greeting })
  } catch {
    messages.value.push({ role: 'assistant', text: `Welcome! Let's practice English. Press and hold the button to speak.` })
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

.controls { padding-top: 1rem; text-align: center; }

.record-btn {
  padding: 1rem 2.5rem; border-radius: 50px; border: 2px solid #1f4e79;
  background: white; font-size: 1.1rem; cursor: pointer;
  transition: all 0.2s; user-select: none;
}
.record-btn.active { background: #e53935; border-color: #e53935; color: white; transform: scale(1.05); }
.record-btn.playing { background: #1f4e79; border-color: #1f4e79; color: white; }
.record-btn:disabled { opacity: 0.6; cursor: not-allowed; }
</style>