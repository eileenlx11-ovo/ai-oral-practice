<template>
  <div class="story-play">
    <div v-if="loading" class="state">{{ t('story.loading') }}</div>
    <div v-else-if="error" class="state error">{{ error }}</div>

    <template v-else>
      <header class="play-header">
        <button class="back-btn" @click="$router.push('/stories')">← {{ t('story.backStories') }}</button>
        <div class="title-block">
          <span class="cover">{{ story.cover_emoji }}</span>
          <div>
            <p class="eyebrow">{{ story.character.name }} · {{ story.character.role }}</p>
            <h1>{{ locale === 'zh' ? story.title_zh : story.title }}</h1>
          </div>
        </div>
        <div class="progress-meta">
          <span>{{ sceneIndex + 1 }}/{{ story.scenes.length }}</span>
          <div class="progress-track">
            <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
          </div>
        </div>
      </header>

      <main class="play-shell">
        <aside class="scene-panel">
          <p class="panel-label">{{ t('story.currentScene') }}</p>
          <h2>{{ currentScene.id }}</h2>
          <div class="scene-box">
            <span>{{ t('story.situation') }}</span>
            <p>{{ locale === 'zh' ? currentScene.setup_zh : currentScene.setup }}</p>
          </div>
          <div class="scene-box goal">
            <span>{{ t('story.goal') }}</span>
            <p>{{ currentScene.goal }}</p>
          </div>
        </aside>

        <section class="dialogue">
          <div ref="messagesEl" class="messages">
            <article v-for="(msg, idx) in messages" :key="idx" class="bubble" :class="msg.role">
              <p>{{ msg.text }}</p>
              <ul v-if="msg.corrections?.length" class="corrections">
                <li v-for="(c, cIdx) in msg.corrections" :key="cIdx">
                  {{ c.original }} → {{ c.corrected }}
                </li>
              </ul>
            </article>
          </div>

          <div v-if="transitionText" class="transition-banner">
            {{ transitionText }}
          </div>

          <footer class="controls">
            <button class="record-btn" :class="{ active: state === 'RECORDING' }" :disabled="busy && state !== 'RECORDING'" @click="toggleRecord">
              <span class="record-dot"></span>
              {{ buttonText }}
            </button>
            <button class="end-btn" :disabled="messages.length <= 1" @click="showComplete = true">
              {{ t('story.finish') }}
            </button>
          </footer>
        </section>
      </main>

      <div v-if="showComplete" class="modal-backdrop" @click.self="showComplete = false">
        <div class="complete-card">
          <span class="complete-icon">✓</span>
          <h2>{{ t('story.completeTitle') }}</h2>
          <p>{{ t('story.completeText') }}</p>
          <div class="complete-stats">
            <span>{{ userTurns }} {{ t('chat.turns') }}</span>
            <span>{{ correctionCount }} {{ t('chat.corrections') }}</span>
          </div>
          <button @click="$router.push('/stories')">{{ t('story.chooseAnother') }}</button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useRecorder } from '../../voice/audio/useRecorder'
import { streamChat } from '../../voice/asr/service'
import { useI18n } from '../composables/useI18n'

const route = useRoute()
const { t, locale } = useI18n()

const story = ref(null)
const sceneIndex = ref(0)
const sessionId = ref('')
const messages = ref([])
const loading = ref(true)
const error = ref('')
const state = ref('IDLE')
const messagesEl = ref(null)
const transitionText = ref('')
const showComplete = ref(false)

let currentAbort = null
let currentAudio = null
let audioQueue = []

const currentScene = computed(() => story.value.scenes[sceneIndex.value])
const progressPercent = computed(() => Math.round(((sceneIndex.value + 1) / story.value.scenes.length) * 100))
const busy = computed(() => ['PROCESSING', 'STREAMING', 'PLAYING'].includes(state.value))
const userTurns = computed(() => messages.value.filter((m) => m.role === 'user').length)
const correctionCount = computed(() => messages.value.reduce((sum, m) => sum + (m.corrections?.length || 0), 0))
const buttonText = computed(() => {
  if (state.value === 'RECORDING') return t('chat.status.stop')
  if (state.value === 'PROCESSING') return t('chat.status.processingButton')
  if (state.value === 'STREAMING') return t('chat.status.streamingButton')
  if (state.value === 'PLAYING') return t('chat.status.interrupt')
  return t('chat.status.idle')
})

const { start, stop, isRecording } = useRecorder({
  silenceMs: 1800,
  onSilence: async () => {
    if (state.value !== 'RECORDING' || !isRecording.value) return
    const blob = await stop()
    if (blob) sendStreaming(blob)
    else state.value = 'IDLE'
  },
})

onMounted(async () => {
  try {
    const storyId = route.params.storyId
    const storyRes = await fetch(`/api/stories/${storyId}`)
    if (!storyRes.ok) throw new Error(t('story.loadFailed'))
    story.value = await storyRes.json()

    const startRes = await fetch(`/api/stories/${storyId}/start`, { method: 'POST' })
    if (!startRes.ok) throw new Error(t('story.startFailed'))
    const startData = await startRes.json()
    sessionId.value = startData.session_id
    sceneIndex.value = startData.scene_index || 0
    messages.value = [{ role: 'assistant', text: startData.ai_opening, corrections: [] }]
  } catch (e) {
    error.value = e.message || t('story.startFailed')
  } finally {
    loading.value = false
    scrollToBottom()
  }
})

onUnmounted(() => {
  if (currentAbort) currentAbort.abort()
  if (currentAudio) currentAudio.pause()
})

async function toggleRecord() {
  if (state.value === 'PLAYING') {
    interrupt()
    return
  }
  if (state.value === 'RECORDING') {
    const blob = await stop()
    if (blob) sendStreaming(blob)
    else state.value = 'IDLE'
    return
  }
  if (state.value !== 'IDLE') return

  state.value = 'RECORDING'
  try {
    await start()
  } catch {
    state.value = 'IDLE'
    error.value = t('chat.errors.micDenied')
  }
}

function sendStreaming(blob) {
  state.value = 'PROCESSING'
  transitionText.value = ''
  let aiMsgIndex = -1
  audioQueue = []

  const history = messages.value.map((m) => ({
    role: m.role === 'user' ? 'user' : 'assistant',
    content: m.text,
  }))

  currentAbort = streamChat(blob, story.value.id, history, sessionId.value, {
    onASR(text) {
      messages.value.push({ role: 'user', text, corrections: [] })
      state.value = 'STREAMING'
      scrollToBottom()
    },
    onSentence(data) {
      if (aiMsgIndex === -1) {
        messages.value.push({ role: 'assistant', text: data.text, corrections: [] })
        aiMsgIndex = messages.value.length - 1
      } else {
        messages.value[aiMsgIndex].text += ` ${data.text}`
      }
      if (data.audio_url) {
        audioQueue.push(data.audio_url)
        if (!currentAudio) {
          state.value = 'PLAYING'
          playNext()
        }
      }
      scrollToBottom()
    },
    onCorrections(corrections) {
      if (aiMsgIndex !== -1) messages.value[aiMsgIndex].corrections = corrections
    },
    onDone(data) {
      sessionId.value = data.session_id || sessionId.value
      currentAbort = null
      if (data.scene_advanced) {
        sceneIndex.value = Math.min(data.story_scene_index ?? sceneIndex.value + 1, story.value.scenes.length - 1)
        transitionText.value = data.story_completed ? t('story.finalScene') : t('story.sceneAdvanced')
        setTimeout(() => { transitionText.value = '' }, 2800)
      }
      if (data.story_completed) showComplete.value = true
      if (!currentAudio && state.value !== 'IDLE') state.value = 'IDLE'
    },
    onError(msg) {
      error.value = msg || t('chat.errors.network')
      state.value = 'IDLE'
      currentAbort = null
    },
  })
}

function playNext() {
  if (audioQueue.length === 0) {
    currentAudio = null
    state.value = 'IDLE'
    return
  }
  currentAudio = new Audio(audioQueue.shift())
  currentAudio.onended = () => { currentAudio = null; playNext() }
  currentAudio.onerror = () => { currentAudio = null; playNext() }
  currentAudio.play().catch(() => playNext())
}

function interrupt() {
  if (currentAbort) currentAbort.abort()
  if (currentAudio) currentAudio.pause()
  currentAbort = null
  currentAudio = null
  audioQueue = []
  state.value = 'IDLE'
}

async function scrollToBottom() {
  await nextTick()
  if (messagesEl.value) messagesEl.value.scrollTop = messagesEl.value.scrollHeight
}
</script>

<style scoped>
.story-play {
  min-height: calc(100vh - 160px);
}

.state {
  padding: var(--space-12);
  color: var(--color-text-secondary);
  text-align: center;
}

.state.error {
  color: var(--color-error);
}

.play-header {
  display: grid;
  grid-template-columns: auto 1fr minmax(160px, 220px);
  gap: var(--space-4);
  align-items: center;
  margin-bottom: var(--space-6);
}

.back-btn,
.end-btn {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-full);
  color: var(--color-text-secondary);
  padding: var(--space-2) var(--space-4);
}

.title-block {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.cover {
  width: 52px;
  height: 52px;
  display: grid;
  place-items: center;
  border-radius: var(--radius-md);
  background: var(--color-primary-50);
  font-size: 1.8rem;
}

.eyebrow {
  color: var(--color-primary);
  font-size: var(--text-xs);
  font-weight: 700;
  margin-bottom: var(--space-1);
}

.title-block h1 {
  color: var(--color-text);
  font-size: var(--text-2xl);
}

.progress-meta {
  color: var(--color-text-secondary);
  font-size: var(--text-sm);
  font-weight: 700;
}

.progress-track {
  height: 8px;
  margin-top: var(--space-2);
  background: var(--color-border-light);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-primary), var(--color-accent));
  transition: width var(--transition-base);
}

.play-shell {
  display: grid;
  grid-template-columns: minmax(220px, 300px) minmax(0, 1fr);
  gap: var(--space-5);
}

.scene-panel,
.dialogue {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
}

.scene-panel {
  padding: var(--space-5);
  align-self: start;
}

.panel-label,
.scene-box span {
  color: var(--color-text-muted);
  font-size: var(--text-xs);
  font-weight: 700;
  text-transform: uppercase;
}

.scene-panel h2 {
  color: var(--color-text);
  font-size: var(--text-xl);
  margin: var(--space-2) 0 var(--space-4);
}

.scene-box {
  background: var(--color-border-light);
  border-radius: var(--radius-md);
  padding: var(--space-4);
  margin-bottom: var(--space-3);
}

.scene-box.goal {
  background: var(--color-primary-50);
}

.scene-box p {
  color: var(--color-text-secondary);
  margin-top: var(--space-2);
}

.dialogue {
  min-height: 560px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-5);
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.bubble {
  max-width: 78%;
  border-radius: var(--radius-lg);
  padding: var(--space-3) var(--space-4);
  color: var(--color-text);
}

.bubble.assistant {
  align-self: flex-start;
  background: var(--color-border-light);
}

.bubble.user {
  align-self: flex-end;
  background: var(--color-primary);
  color: white;
}

.corrections {
  margin-top: var(--space-2);
  padding-left: var(--space-4);
  font-size: var(--text-xs);
  color: inherit;
  opacity: 0.8;
}

.transition-banner {
  margin: 0 var(--space-5) var(--space-3);
  border: 1px solid var(--color-success);
  border-radius: var(--radius-md);
  background: var(--color-success-light);
  color: var(--color-success);
  font-weight: 700;
  padding: var(--space-3);
  text-align: center;
}

.controls {
  display: flex;
  justify-content: center;
  gap: var(--space-3);
  border-top: 1px solid var(--color-border);
  padding: var(--space-4);
}

.record-btn {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  min-width: 160px;
  justify-content: center;
  border-radius: var(--radius-full);
  background: var(--color-primary);
  color: white;
  font-weight: 700;
  padding: var(--space-3) var(--space-5);
}

.record-btn.active {
  background: var(--color-error);
}

.record-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: currentColor;
  opacity: 0.85;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: var(--z-modal);
  display: grid;
  place-items: center;
  background: rgba(15, 23, 42, 0.45);
  padding: var(--space-4);
}

.complete-card {
  width: min(420px, 100%);
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-8);
  text-align: center;
  box-shadow: var(--shadow-xl);
}

.complete-icon {
  display: inline-grid;
  place-items: center;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--color-success-light);
  color: var(--color-success);
  font-weight: 900;
  margin-bottom: var(--space-3);
}

.complete-card h2 {
  color: var(--color-text);
  margin-bottom: var(--space-2);
}

.complete-card p {
  color: var(--color-text-secondary);
}

.complete-stats {
  display: flex;
  justify-content: center;
  gap: var(--space-3);
  margin: var(--space-5) 0;
  color: var(--color-text-secondary);
  font-size: var(--text-sm);
}

.complete-card button {
  background: var(--color-primary);
  color: white;
  border-radius: var(--radius-full);
  font-weight: 700;
  padding: var(--space-3) var(--space-5);
}

@media (max-width: 860px) {
  .play-header,
  .play-shell {
    grid-template-columns: 1fr;
  }

  .progress-meta {
    width: 100%;
  }

  .dialogue {
    min-height: 520px;
  }

  .bubble {
    max-width: 90%;
  }
}
</style>
