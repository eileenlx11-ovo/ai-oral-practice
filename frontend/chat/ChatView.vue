<template>
  <div class="chat-view" :style="{ '--scene-accent': scene.accent, '--scene-grad': sceneBg }">
    <!-- Scene backdrop: gradient base + optional Unsplash overlay (fills shell),
         topped by a darkening scrim so the foreground app card reads cleanly -->
    <div class="scene-backdrop">
      <div
        v-if="sceneImageOk"
        class="scene-image"
        :style="{ backgroundImage: `url(${scene.image})` }"
      ></div>
      <div class="scene-scrim"></div>
    </div>

    <!-- Toast notification -->
    <Toast :message="toast.message" :type="toast.type" @close="toast.message = ''" />

    <!-- Centered glass app card: header + body + controls all live inside one
         bounded container so nothing floats on the bare background -->
    <div class="chat-card">
    <!-- Pinned top bar -->
    <header class="chat-header">
      <button @click="$router.push('/')" class="icon-btn back-btn" :title="t('chat.back')">
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
      </button>

      <!-- Current character card (click to expand personality) -->
      <button class="char-card" @click="showCharCard = !showCharCard">
        <span class="char-avatar">{{ characterAvatar }}</span>
        <div class="char-meta">
          <span class="char-line1">{{ characterName || scenarioName }}</span>
          <span class="char-line2">{{ characterRole || scenarioName }}</span>
        </div>
        <svg class="char-caret" :class="{ open: showCharCard }" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6 6-6"/></svg>
      </button>

      <!-- Live stat chips (folded in from the old right gutter) -->
      <div class="stat-chips">
        <span class="chip"><svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>{{ turnCount }}</span>
        <span class="chip"><svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>{{ correctionCount }}</span>
        <span class="chip"><svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>{{ elapsedText }}</span>
      </div>

      <div class="header-right">
        <span class="status" :class="statusClass"><span class="status-dot"></span>{{ statusText }}</span>
        <button class="icon-btn" @click="openCharSwitcher" :title="t('chat.switchCharacter', '切换角色')">
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 1l4 4-4 4"/><path d="M3 11V9a4 4 0 0 1 4-4h14"/><path d="M7 23l-4-4 4-4"/><path d="M21 13v2a4 4 0 0 1-4 4H3"/></svg>
        </button>
        <button class="icon-btn mobile-only" @click="showSidePanels = !showSidePanels" :title="t('chat.togglePanels', '面板')">
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M9 3v18"/></svg>
        </button>
      </div>
    </header>

    <!-- Body: left gutter | conversation -->
    <div class="chat-body">
      <!-- Left gutter: objective + hints -->
      <aside class="side-panel left" :class="{ open: showSidePanels }">
        <div v-if="scenarioObjective" class="panel-card objective-card">
          <h4><svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/></svg>{{ t('chat.objective', '本场目标') }}</h4>
          <p>{{ scenarioObjective }}</p>
        </div>
        <div class="panel-card hint-card">
          <h4><svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18h6"/><path d="M10 22h4"/><path d="M12 2a7 7 0 0 0-4 12.7c.6.5 1 1.3 1 2.3h6c0-1 .4-1.8 1-2.3A7 7 0 0 0 12 2z"/></svg>{{ t('chat.hintTitle') }}</h4>
          <button class="panel-action" :disabled="loadingHints || messages.length === 0" @click="requestHints">
            {{ loadingHints ? t('chat.hintLoading') : t('chat.hintButton') }}
          </button>
          <div v-if="hints.length" class="panel-hints">
            <div v-for="(h, i) in hints" :key="i" class="panel-hint" :class="h.difficulty">
              <p class="ph-text">"{{ h.text }}"</p>
              <p class="ph-zh">{{ h.hint }}</p>
            </div>
          </div>
        </div>
      </aside>

      <!-- Center: conversation (only scrolling region) -->
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
            <div class="bubble-actions">
              <button v-if="msg.audioUrls && msg.audioUrls.length" class="bubble-btn" @click="handleManualPlay(msg.audioUrls)" :title="t('chat.replay', '播放')">
                <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 5L6 9H2v6h4l5 4V5z"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/></svg>
              </button>
              <a v-if="msg.localAudioUrl" class="bubble-btn" :href="msg.localAudioUrl" :download="msg.localAudioName" :title="t('chat.downloadRecording', '下载本轮录音')">
                <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v12"/><path d="M7 10l5 5 5-5"/><path d="M5 21h14"/></svg>
              </a>
              <button v-if="msg.role === 'assistant'" class="bubble-btn" @click="toggleTranslate(msg)" :title="t('chat.translate', '翻译')">
                <span v-if="msg.translating" class="mini-spinner"></span>
                <span v-else>译</span>
              </button>
            </div>
            <p v-if="msg.showTranslation && msg.translation" class="bubble-translation">{{ msg.translation }}</p>
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
      </div>
    </div>

    <!-- Pinned control bar -->
    <div class="controls">
      <button
        class="record-btn"
        :class="{ active: isRecording, playing: state === 'PLAYING', offline: !isOnline }"
        :disabled="state === 'PROCESSING' || state === 'STREAMING' || !isOnline"
        @click="handleToggle"
      >
        <svg v-if="state === 'PLAYING'" viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>
        <svg v-else viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><path d="M12 19v4M8 23h8"/></svg>
        <span>{{ !isOnline ? t('chat.status.offline') : buttonText }}</span>
      </button>

      <!-- Retry button on error -->
      <button v-if="showRetry" class="retry-btn" @click="retryLast">↻ {{ t('chat.retry') }}</button>

      <!-- VAD settings -->
      <button class="icon-btn vad-btn" @click="showVadSettings = !showVadSettings" :title="t('chat.recordSettings', '录音设置')">
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
      </button>

      <!-- End session button -->
      <button v-if="state === 'IDLE' && turnCount >= 3" class="end-btn" @click="endSession">
        {{ t('chat.endSession') }}
      </button>
    </div>

    <!-- === Overlays (top layer, escape stacking trap) === -->
    <!-- Personality popover -->
    <div v-if="showCharCard && characterPersonality" class="overlay-mask" @click="showCharCard = false"></div>
    <div v-if="showCharCard && characterPersonality" class="char-popover">
      <p class="pop-name">{{ characterAvatar }} {{ characterName }}</p>
      <p class="pop-role">{{ characterRole }}</p>
      <p class="pop-personality">"{{ characterPersonality }}"</p>
    </div>

    <!-- Character switcher dropdown -->
    <div v-if="showCharSwitcher" class="overlay-mask" @click="showCharSwitcher = false"></div>
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

    <!-- VAD settings popover -->
    <div v-if="showVadSettings" class="overlay-mask" @click="showVadSettings = false"></div>
    <div v-if="showVadSettings" class="vad-popover">
      <p class="vad-title">{{ t('chat.pauseSensitivity', '停顿灵敏度') }}</p>
      <p class="vad-hint">{{ t('chat.pauseHint', '静音多久后自动结束录音') }}</p>
      <div class="vad-options" :class="{ disabled: longFormMode }">
        <button
          v-for="ms in VAD_OPTIONS"
          :key="ms"
          class="vad-opt"
          :class="{ active: vadSilenceMs === ms }"
          :disabled="longFormMode"
          @click="setVadSilence(ms)"
        >{{ (ms / 1000).toFixed(1) }}s</button>
      </div>
      <label class="vad-longform">
        <input type="checkbox" :checked="longFormMode" @change="toggleLongForm" />
        <span>
          <strong>{{ t('chat.longForm', '长句模式') }}</strong>
          <small>{{ t('chat.longFormHint', '关闭自动停止，手动点击结束录音（适合说长段话）') }}</small>
        </span>
      </label>
    </div>
    </div><!-- /chat-card -->

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
        <div class="modal-actions">
          <button v-if="isInterviewSession" class="modal-secondary-btn" :disabled="syncingTalent || talentSynced" @click="syncToTalentAgent">
            {{ talentSynced ? t('chat.talentSynced', '已同步到 Talent Agent') : syncingTalent ? t('chat.syncingTalent', '同步中...') : t('chat.syncTalent', '同步到 Talent Agent') }}
          </button>
          <button class="modal-close-btn" @click="showReport = false; $router.push('/')">
            {{ t('chat.backHome') }}
          </button>
        </div>
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
const scenarioObjective = ref('')

// Side panels (desktop gutters / mobile drawers)
// Side panels: shown by default on desktop, collapsed into a drawer on mobile
const showSidePanels = ref(typeof window !== 'undefined' ? window.innerWidth > 768 : true)

// Elapsed session timer (pure frontend)
const elapsedSec = ref(0)
let elapsedTimer = null
const elapsedText = computed(() => {
  const m = Math.floor(elapsedSec.value / 60)
  const s = elapsedSec.value % 60
  return `${m}:${String(s).padStart(2, '0')}`
})

// VAD / recording control (persisted)
const VAD_OPTIONS = [500, 1000, 1500, 2000]
const vadSilenceMs = ref(Number(localStorage.getItem('vadSilenceMs')) || CONFIG.AUDIO.VAD_SILENCE_MS)
const longFormMode = ref(localStorage.getItem('longFormMode') === '1')
const showVadSettings = ref(false)
function setVadSilence(ms) {
  vadSilenceMs.value = ms
  localStorage.setItem('vadSilenceMs', String(ms))
}
function toggleLongForm() {
  longFormMode.value = !longFormMode.value
  localStorage.setItem('longFormMode', longFormMode.value ? '1' : '0')
}

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
const localAudioUrls = []

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
const syncingTalent = ref(false)
const talentSynced = ref(false)
const isInterviewSession = computed(() => scenarioId === 'interview' || reportData.value?.scenario === 'interview')

function showToast(message, type = 'error') {
  toast.message = message
  toast.type = type
}

const { start, stop, isRecording } = useRecorder({
  // Pass refs so changes apply to the next recording without re-instantiating.
  // Long-form mode disables auto-stop entirely (user taps to stop).
  silenceMs: vadSilenceMs,
  vadEnabled: computed(() => !longFormMode.value),
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
    case 'RECORDING': return t('chat.status.recording')
    case 'PROCESSING': return t('chat.status.processing')
    case 'STREAMING': return t('chat.status.streaming')
    case 'PLAYING': return t('chat.status.playing')
    default: return t('chat.status.idle')
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
  const localAudio = createLocalAudio(blob)
  showHintPanel.value = false
  const history = messages.value
    .filter((m) => m.text && !m.text.startsWith('❌'))
    .map((m) => ({ role: m.role, content: m.text }))

  let aiMsgIndex = -1
  audioQueue = []

  currentAbort = streamChat(blob, scenarioId, history, sessionId, {
    onASR(text) {
      messages.value.push({ role: 'user', text, corrections: [], feedback: null, ...localAudio })
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

function createLocalAudio(blob) {
  if (!blob) return {}
  const url = URL.createObjectURL(blob)
  localAudioUrls.push(url)
  const ext = blob.type.includes('webm') ? 'webm' : 'wav'
  return {
    localAudioUrl: url,
    localAudioName: `speakflow-${new Date().toISOString().replace(/[:.]/g, '-')}.${ext}`,
  }
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
      talentSynced.value = false
      showReport.value = true
    } else {
      showToast(t('chat.errors.reportFailed'), 'error')
    }
  } catch {
    showToast(t('chat.errors.network'), 'error')
  }
}

async function syncToTalentAgent() {
  if (!sessionId || syncingTalent.value) return
  syncingTalent.value = true
  try {
    const fd = new FormData()
    fd.append('session_id', sessionId)
    const res = await fetch('/api/integrations/talent-agent/sync', { method: 'POST', body: fd })
    const data = await res.json().catch(() => ({}))
    if (!res.ok || data.synced === false) {
      throw new Error(data.error || t('chat.talentSyncFailed', '同步失败'))
    }
    talentSynced.value = true
    showToast(t('chat.talentSyncSuccess', '已同步到 Talent Agent'), 'success')
  } catch (e) {
    showToast(`${t('chat.talentSyncFailed', '同步失败')}：${e.message || ''}`, 'error')
  } finally {
    syncingTalent.value = false
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
    if (data.objective) scenarioObjective.value = data.objective
  } catch {
    messages.value.push({ role: 'assistant', text: t('chat.fallbackGreeting') })
  } finally {
    loadingGreeting.value = false
    resetHintTimer()
  }
  // Start elapsed timer
  elapsedTimer = setInterval(() => { elapsedSec.value += 1 }, 1000)
})

onUnmounted(() => {
  interrupt()
  if (hintTimer) clearTimeout(hintTimer)
  if (elapsedTimer) clearInterval(elapsedTimer)
  localAudioUrls.forEach((url) => URL.revokeObjectURL(url))
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

// --- Translation (on-demand, cached per message) ---
async function toggleTranslate(msg) {
  if (msg.translation) { msg.showTranslation = !msg.showTranslation; return }
  msg.translating = true
  try {
    const fd = new FormData()
    fd.append('text', msg.text)
    const res = await fetch('/api/translate', { method: 'POST', body: fd })
    if (res.ok) {
      const data = await res.json()
      msg.translation = data.translation || ''
      msg.showTranslation = true
    } else {
      showToast(t('chat.translateFailed', '翻译失败'), 'error')
    }
  } catch {
    showToast(t('chat.translateFailed', '翻译失败'), 'error')
  } finally {
    msg.translating = false
  }
}
</script>

<style scoped>
.chat-view {
  position: relative;
  display: flex;
  justify-content: center;
  /* Flex-fills <main> (itself flex:1 = viewport minus navbar). The global
     `main:has(.chat-view)` rule zeroes padding and makes main a flex column.
     The scene fills the whole shell; the app card centers on top of it. */
  flex: 1;
  min-height: 0;
  overflow: hidden;
  padding: var(--space-4);
  animation: fade-in var(--transition-base) both;
}

/* Centered glass app card — one bounded container holding header/body/controls
   so no element floats on the bare background. */
.chat-card {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 1080px;
  min-height: 0;
  background: color-mix(in srgb, var(--color-surface) 78%, transparent);
  backdrop-filter: blur(18px) saturate(1.2);
  border: 1px solid color-mix(in srgb, var(--color-surface) 60%, transparent);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  overflow: hidden;
}

/* Scene backdrop fills the whole shell, with a scrim to anchor the card */
.scene-backdrop {
  position: absolute;
  inset: 0;
  z-index: 0;
  background: var(--scene-grad);
  pointer-events: none;
  overflow: hidden;
}

.scene-image {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center;
  opacity: 0.55;
  animation: fade-in 600ms ease both;
}

/* Darkening + vignette scrim: lowers background visual weight, lifts contrast */
.scene-scrim {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(120% 90% at 50% 0%, transparent 40%, rgba(15, 23, 42, 0.28) 100%),
    linear-gradient(180deg, rgba(15, 23, 42, 0.12), rgba(15, 23, 42, 0.32));
}

[data-theme="dark"] .scene-backdrop { opacity: 0.5; }
[data-theme="dark"] .scene-scrim {
  background:
    radial-gradient(120% 90% at 50% 0%, transparent 30%, rgba(0, 0, 0, 0.5) 100%),
    linear-gradient(180deg, rgba(0, 0, 0, 0.3), rgba(0, 0, 0, 0.55));
}

.record-btn.offline { opacity: 0.5; cursor: not-allowed; }

/* === Pinned top bar (inside the card, transparent) === */
.chat-header {
  position: relative;
  z-index: 5;
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  background: color-mix(in srgb, var(--color-surface) 55%, transparent);
  border-bottom: 1px solid var(--color-border-light);
  flex-shrink: 0;
}

/* Live stat chips (replaces the old right gutter) */
.stat-chips {
  display: flex;
  gap: var(--space-2);
  margin-left: var(--space-2);
}
.chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px var(--space-2);
  border-radius: var(--radius-full);
  background: color-mix(in srgb, var(--color-surface) 70%, transparent);
  border: 1px solid var(--color-border-light);
  font-size: var(--text-xs);
  font-weight: 600;
  color: var(--color-text-secondary);
}
.chip svg { color: var(--scene-accent); }

/* Generic icon button (line-art SVG) */
.icon-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  transition: all var(--transition-fast);
}
.icon-btn:hover { background: var(--color-primary-50); color: var(--color-primary); }
.back-btn { color: var(--color-text-secondary); }
.mobile-only { display: none; }

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
.char-caret { color: var(--color-text-muted); transition: transform var(--transition-fast); }
.char-caret.open { transform: rotate(180deg); }

.header-right { margin-left: auto; display: flex; align-items: center; gap: var(--space-2); }

.status {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  font-weight: 500;
  white-space: nowrap;
}
.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-text-muted);
  flex-shrink: 0;
}
.status.recording { color: var(--color-error); }
.status.recording .status-dot { background: var(--color-error); animation: dot-pulse 1.2s infinite; }
.status.processing { color: var(--color-warning); }
.status.processing .status-dot { background: var(--color-warning); animation: dot-pulse 1.2s infinite; }
.status.playing { color: var(--color-primary); }
.status.playing .status-dot { background: var(--color-primary); animation: dot-pulse 1.2s infinite; }

@keyframes dot-pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.4; transform: scale(0.7); }
}
@media (prefers-reduced-motion: reduce) {
  .status-dot { animation: none !important; }
}

/* === Overlays: masks + popovers escape the stacking trap === */
.overlay-mask {
  position: absolute;
  inset: 0;
  z-index: 40;
  background: transparent;
}

/* Personality popover */
.char-popover {
  position: absolute;
  top: 64px;
  left: var(--space-5);
  z-index: 50;
  max-width: 300px;
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
  top: 64px;
  right: var(--space-5);
  z-index: 50;
  width: min(440px, 92vw);
  padding: var(--space-4);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xl, var(--shadow-lg));
  animation: scale-in var(--transition-fast) both;
}
.switcher-title { font-weight: 600; font-size: var(--text-sm); margin-bottom: var(--space-3); }
.switcher-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: var(--space-2);
  max-height: min(60vh, 360px);
  overflow-y: auto;
  overscroll-behavior: contain;
  padding-right: var(--space-1);
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

/* === Body: left gutter | conversation === */
.chat-body {
  position: relative;
  z-index: 1;
  flex: 1;
  min-height: 0;
  display: grid;
  grid-template-columns: 256px minmax(0, 1fr);
  /* Single row locked to the free space so panel content can NEVER push the
     control bar out of view. Children must opt into shrinking via min-height:0. */
  grid-template-rows: minmax(0, 1fr);
  gap: var(--space-4);
  padding: var(--space-4);
  overflow: hidden;
}

/* Side panels live in the left gutter; they scroll internally, never grow the row */
.side-panel {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  min-height: 0;
  overflow-y: auto;
  overscroll-behavior: contain;
  padding-right: 2px;
}

.panel-card {
  background: color-mix(in srgb, var(--color-surface) 92%, transparent);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  flex-shrink: 0;
}
/* The hint card may hold many hints — let it shrink and scroll its own list */
.hint-card { display: flex; flex-direction: column; min-height: 0; }
.panel-card h4 {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: var(--text-sm);
  font-weight: 700;
  margin-bottom: var(--space-2);
}
.panel-card h4 svg { color: var(--scene-accent); flex-shrink: 0; }
.objective-card { border-left: 3px solid var(--scene-accent); }
.objective-card p { font-size: var(--text-sm); color: var(--color-text-secondary); line-height: 1.5; }

.panel-action {
  width: 100%;
  padding: var(--space-2);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-primary);
  transition: all var(--transition-fast);
  flex-shrink: 0;
}
.panel-action:hover:not(:disabled) { background: var(--color-primary-50); }
.panel-action:disabled { opacity: 0.5; cursor: not-allowed; }
.panel-hints {
  margin-top: var(--space-3);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  min-height: 0;
  overflow-y: auto;
  overscroll-behavior: contain;
}
.panel-hint { padding: var(--space-2); border-radius: var(--radius-md); background: var(--color-bg); flex-shrink: 0; }
.ph-text { font-size: var(--text-sm); color: var(--color-text); }
.ph-zh { font-size: var(--text-xs); color: var(--color-text-muted); }

/* Messages (the only scrolling region) */
.messages {
  height: 100%;
  overflow-y: auto;
  overscroll-behavior: contain;
  padding: var(--space-2) var(--space-2) var(--space-4);
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

/* Bubble action buttons (replay / translate) */
.bubble-actions {
  display: flex;
  gap: var(--space-1);
  margin-top: var(--space-2);
}
.bubble-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 26px;
  height: 26px;
  padding: 0 var(--space-2);
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  background: var(--color-bg);
  transition: all var(--transition-fast);
}
.bubble-btn:visited { color: var(--color-text-muted); }
.bubble-btn:hover { color: var(--color-primary); background: var(--color-primary-50); }
.bubble-translation {
  margin-top: var(--space-2);
  padding-top: var(--space-2);
  border-top: 1px dashed var(--color-border);
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
}
.mini-spinner {
  width: 12px;
  height: 12px;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

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

/* === Pinned control bar (inside the card) === */
.controls {
  position: relative;
  z-index: 5;
  padding: var(--space-3) var(--space-5);
  display: flex;
  justify-content: center;
  gap: var(--space-3);
  align-items: center;
  background: color-mix(in srgb, var(--color-surface) 55%, transparent);
  border-top: 1px solid var(--color-border-light);
  flex-shrink: 0;
}

.vad-btn { border: 1px solid var(--color-border); }

/* VAD settings popover (anchored to control bar) */
.vad-popover {
  position: absolute;
  bottom: 72px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 50;
  width: min(340px, 92vw);
  padding: var(--space-4);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  animation: scale-in var(--transition-fast) both;
}
.vad-title { font-weight: 700; font-size: var(--text-sm); }
.vad-hint { font-size: var(--text-xs); color: var(--color-text-muted); margin-bottom: var(--space-3); }
.vad-options { display: flex; gap: var(--space-2); margin-bottom: var(--space-3); }
.vad-options.disabled { opacity: 0.4; }
.vad-opt {
  flex: 1;
  padding: var(--space-2);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text-secondary);
  transition: all var(--transition-fast);
}
.vad-opt.active { background: var(--color-primary); color: white; border-color: var(--color-primary); }
.vad-longform {
  display: flex;
  gap: var(--space-2);
  align-items: flex-start;
  padding-top: var(--space-3);
  border-top: 1px solid var(--color-border-light);
  cursor: pointer;
}
.vad-longform input { margin-top: 3px; }
.vad-longform strong { display: block; font-size: var(--text-sm); }
.vad-longform small { font-size: var(--text-xs); color: var(--color-text-muted); }

.record-btn {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-6);
  border-radius: var(--radius-full);
  border: 2px solid var(--color-primary);
  background: var(--color-surface);
  font-size: var(--text-base);
  font-weight: 600;
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

.modal-actions {
  display: grid;
  gap: var(--space-3);
}
.modal-close-btn,
.modal-secondary-btn {
  width: 100%;
  padding: var(--space-3);
  border-radius: var(--radius-md);
  font-size: var(--text-base);
  font-weight: 600;
  transition: background var(--transition-fast);
}
.modal-close-btn {
  background: var(--color-primary);
  color: white;
}
.modal-close-btn:hover { background: var(--color-primary-dark); }
.modal-secondary-btn {
  background: var(--color-surface);
  color: var(--color-primary);
  border: 1px solid var(--color-primary);
}
.modal-secondary-btn:hover:not(:disabled) { background: var(--color-primary-50); }
.modal-secondary-btn:disabled { opacity: 0.65; cursor: not-allowed; }

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
@media (max-width: 1024px) {
  .chat-body { grid-template-columns: 210px minmax(0, 1fr); }
}

@media (max-width: 768px) {
  .mobile-only { display: flex; }
  .chat-view { padding: 0; }
  .chat-card { border-radius: 0; border: none; max-width: none; }
  .stat-chips { display: none; }
  .chat-body {
    grid-template-columns: 1fr;
    grid-template-rows: minmax(0, 1fr);
    padding: var(--space-3);
  }
  /* Side panels collapse into a slide-down drawer toggled by showSidePanels */
  .side-panel {
    position: absolute;
    left: var(--space-3);
    right: var(--space-3);
    z-index: 6;
    max-height: 0;
    overflow: hidden;
    padding: 0;
    background: color-mix(in srgb, var(--color-surface) 94%, transparent);
    backdrop-filter: blur(8px);
    border-radius: var(--radius-lg);
    transition: max-height var(--transition-base), padding var(--transition-base);
  }
  .side-panel.left { top: 0; }
  .side-panel.open { max-height: 45vh; padding: var(--space-3); overflow-y: auto; }
  .messages { grid-column: 1; }
  .bubble { max-width: 85%; }
  .char-line2 { display: none; }
  .char-switcher, .char-popover { left: var(--space-3); right: var(--space-3); width: auto; }
}
</style>
