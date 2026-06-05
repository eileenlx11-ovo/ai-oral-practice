<template>
  <div class="chat-view">
    <header class="chat-header">
      <button @click="$router.push('/')" class="back-btn">← 返回</button>
      <h2>{{ scenarioName }}</h2>
      <span class="status" :class="{ recording: isRecording }">
        {{ isRecording ? '🔴 录音中...' : '⏸️ 等待录音' }}
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
          <span v-if="msg.audio" class="play-btn" @click="playAudio(msg.audio)">🔊</span>
        </div>
      </div>
    </div>

    <div class="controls">
      <button
        class="record-btn"
        :class="{ active: isRecording }"
        @mousedown="startRecording"
        @mouseup="stopRecording"
        @touchstart.prevent="startRecording"
        @touchend.prevent="stopRecording"
      >
        🎙️ {{ isRecording ? '松开发送' : '按住说话' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useRecorder } from '../composables/useRecorder'

const route = useRoute()
const scenarioId = route.params.scenario

const scenarioNames = {
  interview: '💼 Job Interview',
  restaurant: '🍽️ Restaurant',
  meeting: '📋 Business Meeting',
  travel: '✈️ Travel',
  smalltalk: '💬 Small Talk',
}
const scenarioName = scenarioNames[scenarioId] || scenarioId

const messages = ref([])
const messagesRef = ref(null)
const isRecording = ref(false)

const { start, stop, getBlob } = useRecorder()

async function startRecording() {
  isRecording.value = true
  await start()
}

async function stopRecording() {
  isRecording.value = false
  const blob = await stop()
  if (!blob) return

  // 添加用户消息（占位）
  messages.value.push({ role: 'user', text: '语音识别中...' })
  scrollToBottom()

  // TODO: 发送到后端 ASR → LLM → TTS
  // const formData = new FormData()
  // formData.append('audio', blob, 'recording.webm')
  // formData.append('scenario', scenarioId)
  // const res = await fetch('/api/chat', { method: 'POST', body: formData })
  // const data = await res.json()
  // messages.value[messages.value.length - 1].text = data.user_text
  // messages.value.push({ role: 'assistant', text: data.reply_text, audio: data.reply_audio_url })

  // 暂时用模拟数据
  setTimeout(() => {
    messages.value[messages.value.length - 1].text = '[Your speech will appear here]'
    messages.value.push({
      role: 'assistant',
      text: 'This is a placeholder AI response. The backend will provide real responses once connected.',
    })
    scrollToBottom()
  }, 1000)
}

function playAudio(url) {
  const audio = new Audio(url)
  audio.play()
}

function scrollToBottom() {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}

onMounted(() => {
  messages.value.push({
    role: 'assistant',
    text: `Welcome! Let's practice English in a ${scenarioId} scenario. Press and hold the button to speak.`,
  })
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

.status.recording {
  color: #e53935;
  font-weight: 600;
}

.messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem 0;
}

.message {
  display: flex;
  margin-bottom: 1rem;
}

.message.user {
  justify-content: flex-end;
}

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
</style>
