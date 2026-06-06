<template>
  <div class="chat-view" :style="{ '--scene-accent': scene.accent, '--scene-grad': sceneBg }">
    <!-- Scene backdrop: gradient base + optional Unsplash overlay -->
    <div class="scene-backdrop">
      <div
        v-if="sceneImageOk"
        class="scene-image"
        :style="{ backgroundImage: `url(${scene.image})` }"
      ></div>
    </div>

    <!-- Toast notification -->
    <Toast :message="toast.message" :type="toast.type" @close="toast.message = ''" />

    <!-- Offline banner -->
    <div v-if="!isOnline" class="offline-banner">
      ⚠️ {{ t('chat.offline') }}
    </div>

    <header class="chat-header">
      <button @click="$router.push('/')" class="back-btn">← {{ t('chat.back') }}</button>

      <!-- Current character card (click to expand personality) -->
      <button class="char-card" @click="showCharCard = !showCharCard">
        <span class="char-avatar">{{ characterAvatar }}</span>
        <div class="char-meta">
          <span class="char-line1">{{ characterName || scenarioName }}</span>
          <span class="char-line2">{{ characterRole || scenarioName }}</span>
        </div>
        <span class="char-caret" :class="{ open: showCharCard }">▾</span>
      </button>

      <div class="header-right">
        <span class="stats-mini" v-if="messages.length > 1">
          💬 {{ turnCount }} | ✏️ {{ correctionCount }}
        </span>
        <button class="switch-btn" @click="openCharSwitcher" :title="t('chat.switchCharacter', '切换角色')">🔄</button>
        <span class="status" :class="statusClass">
          {{ statusText }}
        </span>
      </div>

      <!-- Expanded personality popover -->
      <div v-if="showCharCard && characterPersonality" class="char-popover">
        <p class="pop-name">{{ characterAvatar }} {{ characterName }}</p>
        <p class="pop-role">{{ characterRole }}</p>
        <p class="pop-personality">"{{ characterPersonality }}"</p>
      </div>

      <!-- Character switcher dropdown -->
      <div v-if="showCharSwitcher" class="char-switcher">
        <p class="switcher-title">{{ t('chat.chooseCharacter', '换一个聊天对象') }}</p>
        <div v-if="allCharacters.length" class="switcher-grid">
          <button
            v-for="c in allCharacters"
            :key="c.id"
            class="switcher-item"
            :class="{ current: c.id === scenarioId }"
            @click="switchCharacter(c.id)"
          >
            <span class="si-avatar">{{ c.avatar }}</span>
            <span class="si-name">{{ c.name }}</span>
            <span class="si-role">{{ c.role }}</span>
          </button>
        </div>
        <p v-else class="switcher-empty">{{ t('chat.switcherEmpty', '角色列表暂不可用') }}</p>
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
          <span v-if="msg.audioUrls && msg.audioUrls.length" class="play-btn" @click="handleManualPlay(msg.audioUrls)">
            🔊
          </span>
          <!-- Grammar corrections -->
          <div v-if="msg.corrections && msg.corrections.length" class="corrections">
            <p class="correction-title">📝 {{ t('chat.grammarSuggestions') }}</p>
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
        <p class="hint-title">💡 {{ t('chat.hintTitle') }}</p>
        <div
          v-for="(h, i) in hints"
          :key="i"
          class="hint-item"
          :class="h.difficulty"
        >
          <p class="hint-text">"{{ h.text }}"</p>
          <p class="hint-zh">{{ h.hint }}</p>
        </div>
        <button class="hint-dismiss" @click="showHintPanel = false">{{ t('chat.hintDismiss') }}</button>
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
        💡 {{ loadingHints ? t('chat.hintLoading') : t('chat.hintButton') }}
      </button>

      <button
        class="record-btn"
        :class="{ active: isRecording, playing: state === 'PLAYING', offline: !isOnline }"
        :disabled="state === 'PROCESSING' || state === 'STREAMING' || !isOnline"
        @click="handleToggle"
      >
        🎙️ {{ !isOnline ? t('chat.status.offline') : buttonText }}
      </button>
      <!-- Retry button on error -->
      <button
        v-if="showRetry"
        class="retry-btn"
        @click="retryLast"
      >
        🔄 {{ t('chat.retry') }}
      </button>

      <!-- End session button -->
      <button
        v-if="state === 'IDLE' && turnCount >= 3"
        class="end-btn"
        @click="endSession"
      >
        📋 {{ t('chat.endSession') }}
      </button>
    </div>

    <!-- Session Report Modal -->
    <div v-if="showReport" class="modal-overlay" @click.self="showReport = false">
      <div class="modal">
        <h3>📋 {{ t('chat.reportTitle') }}</h3>
        <div class="report-stats">
          <div class="stat">
            <span class="stat-value">{{ reportData.total_turns || 0 }}</span>
            <span class="stat-label">{{ t('chat.turns') }}</span>
          </div>
          <div class="stat">
            <span class="stat-value">{{ reportData.total_corrections || 0 }}</span>
            <span class="stat-label">{{ t('chat.corrections') }}</span>
          </div>
          <div class="stat" v-if="reportData.avg_pronunciation">
            <span class="stat-value">{{ reportData.avg_pronunciation?.toFixed(0) }}</span>
            <span class="stat-label">{{ t('chat.pronunciationScore') }}</span>
          </div>
        </div>
        <div v-if="reportData.report" class="report-narrative">
          <p>{{ reportData.report }}</p>
        </div>
        <div v-if="reportData.common_errors?.length" class="report-errors">
          <h4>{{ t('chat.commonIssues') }}</h4>
          <ul>
            <li v-for="e in reportData.common_errors" :key="e.pattern">
              {{ e.pattern }} (×{{ e.count }})
            </li>
          </ul>
        </div>
        <button class="modal-close-btn" @click="showReport = false; $router.push('/')">
          {{ t('chat.backHome') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useRecorder } from '../../voice/audio/useRecorder'
import { streamChat } from '../../voice/asr/service'
import { useNetwork } from '../composables/useNetwork'
import { classifyError } from '../composables/useErrorHandler'
import { useI18n } from '../composables/useI18n'
import { CONFIG } from '../../shared/config'
import { getScene, sceneGradient } from '../styles/scenes'
import Toast from '../components/Toast.vue'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const { isOnline } = useNetwork()
const scenarioId = route.params.scenario
const scenario = CONFIG.SCENARIOS.find((s) => s.id === scenarioId)
const scenarioName = scenario ? scenario.name : scenarioId
const characterAvatar = ref(scenario?.icon || '💬')
const characterName = ref('')
const characterRole = ref('')
const characterPersonality = ref('')

// Scene visuals (pure frontend, no backend dependency)
const scene = getScene(scenarioId)
const sceneBg = sceneGradient(scenarioId)
const sceneImageOk = ref(false)
// Probe the Unsplash backdrop; only overlay it once it loads, else stay on gradient
if (scene.image) {
  const probe = new Image()
  probe.onload = () => { sceneImageOk.value = true }
  probe.src = scene.image
}

// Character/voice switcher (consumes Codex's /api/characters + switch endpoint;
// degrades gracefully when those routes are absent)
const showCharSwitcher = ref(false)
const showCharCard = ref(false)
const allCharacters = ref([])

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
    case 'RECORDING': return `🔴 ${t('chat.status.recording')}`
    case 'PROCESSING': return `⏳ ${t('chat.status.processing')}`
    case 'STREAMING': return `💬 ${t('chat.status.streaming')}`
    case 'PLAYING': return `🔊 ${t('chat.status.playing')}`
    default: return `⏸️ ${t('chat.status.idle')}`
  }
})

const buttonText = computed(() => {
  switch (state.value) {
    case 'RECORDING': return t('chat.status.stop')
    case 'PROCESSING': return t('chat.status.processingButton')
    case 'STREAMING': return t('chat.status.streamingButton')
    case 'PLAYING': return t('chat.status.interrupt')
    default: return t('chat.status.idle')
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
      showToast(t('chat.errors.micDenied'), 'warning')
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
        messages.value.push({ role: 'assistant', text: data.text, audioUrls: [], corrections: [], feedback: null })
        aiMsgIndex = messages.value.length - 1
      } else {
        messages.value[aiMsgIndex].text += ' ' + data.text
      }
      if (data.audio_url) {
        messages.value[aiMsgIndex].audioUrls.push(data.audio_url)
        audioQueue.push(data.audio_url)
        if (!currentAudio && state.value !== 'IDLE') {
          state.value = 'PLAYING'
          playNext()
        }
      }
      scrollToBottom()
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
        setTimeout(() => { if (confirm(t('chat.errors.refreshConfirm'))) location.reload() }, 5000)
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

function handleManualPlay(urls) {
  if (currentAudio) { currentAudio.pause(); currentAudio = null }
  if (!urls || !urls.length) return
  const queue = [...urls]
  function playFromQueue() {
    if (queue.length === 0) { currentAudio = null; return }
    const url = queue.shift()
    currentAudio = new Audio(url)
    currentAudio.onended = () => { currentAudio = null; playFromQueue() }
    currentAudio.onerror = () => { currentAudio = null; playFromQueue() }
    currentAudio.play().catch(() => { currentAudio = null; playFromQueue() })
  }
  playFromQueue()
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
      showToast(t('chat.errors.reportFailed'), 'error')
    }
  } catch {
    showToast(t('chat.errors.network'), 'error')
  }
}

onMounted(async () => {
  try {
    const res = await fetch(sessionId ? `/api/sessions/${sessionId}/handoff` : `/api/scenarios/${scenarioId}`)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    messages.value.push({ role: 'assistant', text: data.greeting || t('chat.fallbackGreeting') })
    if (data.character) {
      characterName.value = data.character.name
      characterAvatar.value = data.character.avatar || scenario?.icon || '💬'
      characterRole.value = data.character.role || ''
      characterPersonality.value = data.character.personality || ''
    }
  } catch {
    messages.value.push({ role: 'assistant', text: t('chat.fallbackGreeting') })
  } finally {
    loadingGreeting.value = false
    resetHintTimer()
  }
})

onUnmounted(() => {
  interrupt()
  if (hintTimer) clearTimeout(hintTimer)
})

// --- Character / voice switcher ---
async function openCharSwitcher() {
  showCharSwitcher.value = !showCharSwitcher.value
  if (showCharSwitcher.value && allCharacters.value.length === 0) {
    try {
      const res = await fetch('/api/characters')
      if (res.ok) allCharacters.value = await res.json()
    } catch { /* endpoint not deployed yet — keep list empty */ }
  }
}

async function switchCharacter(charId) {
  if (charId === scenarioId) { showCharSwitcher.value = false; return }
  // If we have a live session, ask the backend to swap the character on it.
  if (sessionId) {
    try {
      const fd = new FormData()
      fd.append('scenario', charId)
      const res = await fetch(`/api/sessions/${sessionId}/character`, { method: 'POST', body: fd })
      if (res.ok) {
        showCharSwitcher.value = false
        router.push(`/chat/${charId}?session_id=${sessionId}`).then(() => router.go(0))
        return
      }
    } catch { /* fall through to fresh navigation */ }
  }
  // No session or endpoint absent: start fresh with the new character.
  showCharSwitcher.value = false
  router.push(`/chat/${charId}`).then(() => router.go(0))
}
</script>

<style scoped>
.chat-view {
  position: relative;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 120px);
  animation: fade-in var(--transition-base) both;
}

/* Scene backdrop sits behind all chat content */
.scene-backdrop {
  position: absolute;
  inset: 0;
  z-index: 0;
  background: var(--scene-grad);
  opacity: 0.35;
  border-radius: var(--radius-lg);
  pointer-events: none;
  overflow: hidden;
}

[data-theme="dark"] .scene-backdrop { opacity: 0.18; }

.scene-image {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center;
  opacity: 0.22;
  mix-blend-mode: multiply;
  animation: fade-in 600ms ease both;
}

/* Lift actual content above the backdrop */
.chat-view > *:not(.scene-backdrop) { position: relative; z-index: 1; }

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
  position: relative;
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

/* Current character card */
.char-card {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  transition: all var(--transition-fast);
}
.char-card:hover { border-color: var(--scene-accent); box-shadow: var(--shadow-sm); }

.char-avatar {
  font-size: 1.6rem;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--scene-grad);
  flex-shrink: 0;
}

.char-meta { display: flex; flex-direction: column; align-items: flex-start; line-height: 1.2; }
.char-line1 { font-size: var(--text-sm); font-weight: 600; color: var(--color-text); }
.char-line2 { font-size: var(--text-xs); color: var(--color-text-muted); }
.char-caret { font-size: var(--text-xs); color: var(--color-text-muted); transition: transform var(--transition-fast); }
.char-caret.open { transform: rotate(180deg); }

.header-right { margin-left: auto; display: flex; align-items: center; gap: var(--space-3); }

.switch-btn {
  font-size: 1.1rem;
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}
.switch-btn:hover { background: var(--color-primary-50); transform: rotate(90deg); }

/* Personality popover */
.char-popover {
  position: absolute;
  top: calc(100% + 4px);
  left: 80px;
  z-index: 20;
  max-width: 280px;
  padding: var(--space-3) var(--space-4);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  animation: scale-in var(--transition-fast) both;
}
.pop-name { font-weight: 700; font-size: var(--text-base); }
.pop-role { font-size: var(--text-xs); color: var(--scene-accent); margin-bottom: var(--space-2); }
.pop-personality { font-size: var(--text-sm); color: var(--color-text-secondary); font-style: italic; }

/* Character switcher dropdown */
.char-switcher {
  position: absolute;
  top: calc(100% + 4px);
  right: 0;
  z-index: 20;
  width: min(420px, 90vw);
  padding: var(--space-4);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  animation: scale-in var(--transition-fast) both;
}
.switcher-title { font-weight: 600; font-size: var(--text-sm); margin-bottom: var(--space-3); }
.switcher-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: var(--space-2);
  max-height: 320px;
  overflow-y: auto;
}
.switcher-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: var(--space-3) var(--space-2);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  transition: all var(--transition-fast);
  text-align: center;
}
.switcher-item:hover { border-color: var(--color-primary); transform: translateY(-2px); box-shadow: var(--shadow-sm); }
.switcher-item.current { border-color: var(--scene-accent); background: var(--color-primary-50); }
.si-avatar { font-size: 1.6rem; }
.si-name { font-size: var(--text-sm); font-weight: 600; color: var(--color-text); }
.si-role { font-size: var(--text-xs); color: var(--color-text-muted); }
.switcher-empty { font-size: var(--text-sm); color: var(--color-text-muted); text-align: center; padding: var(--space-4); }

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

/* Second, offset ring for a layered sound-wave effect */
.record-btn.active::after {
  content: '';
  position: absolute;
  inset: -4px;
  border-radius: var(--radius-full);
  border: 2px solid var(--color-error);
  animation: pulse-ring 1.5s infinite 0.5s;
}

@media (prefers-reduced-motion: reduce) {
  .record-btn.active::before,
  .record-btn.active::after { animation: none; }
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
  .record-btn { padding: var(--space-4) var(--space-6); font-size: var(--text-base); min-height: 52px; min-width: 52px; }
  .chat-header { padding: var(--space-2) 0; }
}
</style>
