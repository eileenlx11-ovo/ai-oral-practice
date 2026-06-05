<template>
  <div class="chat-view">
    <header class="chat-header">
      <button @click="$router.push('/')" class="back-btn">← 返回</button>
      <h2>{{ scenarioName }}</h2>
      <span class="status" :class="{ recording: isRecording, processing: isProcessing }">
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
          <span v-if="msg.audio" class="play-btn" @click="handlePlay(msg.audio)">
            {{ ttsPlaying === msg.audio ? '⏸️' : '🔊' }}
          </span>
          <!-- 语法纠错 -->
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
        :class="{ active: isRecording }"
        :disabled="isProcessing"
        @mousedown="startRecording"
        @mouseup="stopRecording"
        @touchstart.prevent="startRecording"
        @touchend.prevent="stopRecording"
      >
        🎙️ {{ isRecording ? '松开发送' : isProcessing ? '处理中...' : '按住说话' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useRecorder } from '../../voice/audio/useRecorder'
import { useTTS } from '../../voice/tts/useTTS'
import { sendAudioForChat } from '../../voice/asr/service'
import { CONFIG } from '../../shared/config'

const route = useRoute()
const scenarioId = route.params.scenario
const scenario = CONFIG.SCENARIOS.find((s) => s.id === scenarioId)
const scenarioName = scenario ? `${scenario.icon} ${scenario.name}` : scenarioId

const messages = ref([])
const messagesRef = ref(null)
const isProcessing = ref(false)
const ttsPlaying = ref(null)

const { start, stop, isRecording } = useRecorder({
  silenceMs: CONFIG.AUDIO.VAD_SILENCE_MS,
  onSilence: () => stopRecording(),
})
const { play, stopCurrent, isPlaying } = useTTS()

const statusText = computed(() => {
  if (isRecording.value) return '🔴 录音中...'
  if (isProcessing.value) return '⏳ 识别中...'
  return '⏸️ 等待录音'
})

async function startRecording() {
  if (isProcessing.value) return
  await start()
}

async function stopRecording() {
  if (!isRecording.value) return
  const blob = await stop()
  if (!blob) return

  isProcessing.value = true
  messages.value.push({ role: 'user', text: '语音识别中...' })
  scrollToBottom()

  try {
    const history = messages.value.slice(0, -1).map((m) => ({
      role: m.role,
      content: m.text,
    }))

    const data = await sendAudioForChat(blob, scenarioId, history)

    // 更新用户消息
    const userMsg = messages.value[messages.value.length - 1]
    userMsg.text = data.user_text
    userMsg.corrections = data.corrections

    // AI 回复
    const audioUrl = data.reply_audio_url
      ? `${CONFIG.API.BASE_URL}${data.reply_audio_url}`
      : null

    messages.value.push({
      role: 'assistant',
      text: data.reply_text,
      audio: audioUrl,
    })

    // 自动播放回复
    if (audioUrl) {
      handlePlay(audioUrl)
    }
  } catch (err) {
    messages.value[messages.value.length - 1].text = `❌ ${err.message}`
  } finally {
    isProcessing.value = false
    scrollToBottom()
  }
}

async function handlePlay(url) {
  if (ttsPlaying.value === url) {
    stopCurrent()
    ttsPlaying.value = null
    return
  }
  ttsPlaying.value = url
  try {
    await play(url)
  } finally {
    ttsPlaying.value = null
  }
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

onMounted(async () => {
  // 尝试从后端获取开场白，失败则使用本地配置
  try {
    const res = await fetch(`${CONFIG.API.BASE_URL}/api/scenarios/${scenarioId}`)
    const data = await res.json()
    messages.value.push({ role: 'assistant', text: data.greeting })
  } catch {
    messages.value.push({
      role: 'assistant',
      text: `Welcome! Let's practice English in a ${scenarioId} scenario. Press and hold the button to speak.`,
    })
  }
})
</script>

<style scoped>
.chat-view {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 120px);
}

.chat-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e0e0e0;
}

.back-btn {
  background: none;
  border: none;
  font-size: 1rem;
  cursor: pointer;
  color: #1f4e79;
}

.status {
  margin-left: auto;
  font-size: 0.85rem;
  color: #666;
}

.status.recording { color: #e53935; font-weight: 600; }
.status.processing { color: #f57c00; }

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem 0;
}

.message {
  display: flex;
  margin-bottom: 1rem;
}

.message.user { justify-content: flex-end; }

.bubble {
  max-width: 70%;
  padding: 0.8rem 1.2rem;
  border-radius: 12px;
  line-height: 1.5;
}

.user .bubble {
  background: #1f4e79;
  color: white;
  border-bottom-right-radius: 4px;
}

.assistant .bubble {
  background: white;
  border: 1px solid #e0e0e0;
  border-bottom-left-radius: 4px;
}

.play-btn {
  cursor: pointer;
  margin-left: 0.5rem;
}

.corrections {
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px dashed rgba(255,255,255,0.3);
  font-size: 0.85rem;
}

.correction-title { font-weight: 600; margin-bottom: 0.3rem; }
.correction-item { margin-bottom: 0.3rem; }
.original { text-decoration: line-through; opacity: 0.7; }
.arrow { margin: 0 0.3rem; }
.corrected { font-weight: 600; }
.explanation { opacity: 0.8; font-size: 0.8rem; margin-top: 0.1rem; }

.controls {
  padding-top: 1rem;
  text-align: center;
}

.record-btn {
  padding: 1rem 2.5rem;
  border-radius: 50px;
  border: 2px solid #1f4e79;
  background: white;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.2s;
  user-select: none;
}

.record-btn.active {
  background: #e53935;
  border-color: #e53935;
  color: white;
  transform: scale(1.05);
}

.record-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
