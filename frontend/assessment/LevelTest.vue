<template>
  <div class="level-test">
    <Toast :message="toast.message" :type="toast.type" @close="toast.message = ''" />

    <!-- Intro screen -->
    <div v-if="phase === 'intro'" class="intro">
      <h1>🎓 英语水平评估</h1>
      <p>通过 5 个简短的口语问题，快速评估你的英语水平</p>
      <ul class="info-list">
        <li>⏱️ 大约 3 分钟</li>
        <li>🎤 每题录音回答</li>
        <li>📊 获取 CEFR 等级 (A1-C1)</li>
      </ul>
      <button class="start-btn" @click="startTest">开始评估</button>
      <button class="skip-btn" @click="$router.push('/')">跳过，直接练习</button>
    </div>

    <!-- Question screen -->
    <div v-else-if="phase === 'question'" class="question-phase">
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: `${((currentIndex + 1) / questions.length) * 100}%` }"></div>
      </div>
      <p class="question-count">问题 {{ currentIndex + 1 }} / {{ questions.length }}</p>
      <p class="difficulty-label">难度: {{ questions[currentIndex]?.difficulty }}</p>

      <div class="question-card">
        <p class="question-text">{{ questions[currentIndex]?.prompt }}</p>
      </div>

      <div class="recording-area">
        <p class="record-status">{{ recordStatus }}</p>
        <button
          class="record-btn"
          :class="{ active: isRecording }"
          :disabled="isProcessing"
          @click="handleRecord"
        >
          🎙️ {{ isRecording ? '停止录音' : '开始录音' }}
        </button>
        <p v-if="currentTranscript" class="transcript">
          "{{ currentTranscript }}"
        </p>
        <button
          v-if="currentTranscript"
          class="next-btn"
          @click="nextQuestion"
        >
          {{ currentIndex < questions.length - 1 ? '下一题 →' : '提交评估' }}
        </button>
      </div>
    </div>

    <!-- Analyzing screen -->
    <div v-else-if="phase === 'analyzing'" class="analyzing">
      <div class="spinner"></div>
      <p>正在分析你的回答...</p>
    </div>

    <!-- Result screen -->
    <div v-else-if="phase === 'result'" class="result">
      <h1>评估结果</h1>
      <div class="level-badge">{{ result.level }}</div>
      <p class="level-desc">{{ levelDescriptions[result.level] }}</p>
      <p class="summary">{{ result.summary }}</p>

      <!-- Level scale reference -->
      <div class="level-scale">
        <div v-for="lv in levelScale" :key="lv.level" class="level-step" :class="{ active: lv.level === result.level }">
          <span class="step-badge">{{ lv.level }}</span>
          <span class="step-label">{{ lv.label }}</span>
        </div>
      </div>

      <div class="scores-grid">
        <div class="score-item">
          <span class="score-label">语法</span>
          <div class="score-bar"><div :style="{ width: `${(result.scores?.grammar || 0) * 10}%` }"></div></div>
          <span class="score-num">{{ result.scores?.grammar }}/10</span>
        </div>
        <div class="score-item">
          <span class="score-label">词汇</span>
          <div class="score-bar"><div :style="{ width: `${(result.scores?.vocabulary || 0) * 10}%` }"></div></div>
          <span class="score-num">{{ result.scores?.vocabulary }}/10</span>
        </div>
        <div class="score-item">
          <span class="score-label">流利度</span>
          <div class="score-bar"><div :style="{ width: `${(result.scores?.fluency || 0) * 10}%` }"></div></div>
          <span class="score-num">{{ result.scores?.fluency }}/10</span>
        </div>
        <div class="score-item">
          <span class="score-label">任务完成</span>
          <div class="score-bar"><div :style="{ width: `${(result.scores?.task_completion || 0) * 10}%` }"></div></div>
          <span class="score-num">{{ result.scores?.task_completion }}/10</span>
        </div>
      </div>

      <div v-if="result.strengths?.length" class="section">
        <h3>✅ 优势</h3>
        <ul><li v-for="s in result.strengths" :key="s">{{ s }}</li></ul>
      </div>

      <div v-if="result.weaknesses?.length" class="section">
        <h3>🎯 待提升</h3>
        <ul><li v-for="w in result.weaknesses" :key="w">{{ w }}</li></ul>
      </div>

      <div v-if="result.recommendations?.length" class="section">
        <h3>💡 建议</h3>
        <ul><li v-for="r in result.recommendations" :key="r">{{ r }}</li></ul>
      </div>

      <button class="start-btn" @click="$router.push('/')">开始练习 →</button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useRecorder } from '../../voice/audio/useRecorder'
import { recognizeOnly } from '../../voice/asr/service'
import { CONFIG } from '../../shared/config'
import Toast from '../components/Toast.vue'

const router = useRouter()

const phase = ref('intro') // intro | question | analyzing | result
const questions = ref([])
const currentIndex = ref(0)
const responses = ref([])
const currentTranscript = ref('')
const isProcessing = ref(false)
const result = ref({})

const levelScale = [
  { level: 'A1', label: '入门' },
  { level: 'A2', label: '初级' },
  { level: 'B1', label: '中级' },
  { level: 'B2', label: '中高级' },
  { level: 'C1', label: '高级' },
]

const levelDescriptions = {
  A1: '能理解和使用日常基础短语，进行简单自我介绍',
  A2: '能处理简单日常任务，用简短句子描述个人背景和经历',
  B1: '能独立应对旅行中的大部分情况，描述经历和表达观点',
  B2: '能流利自如地与母语者交流，就广泛话题展开详细讨论',
  C1: '能灵活有效地运用语言，表达复杂观点并进行学术/专业讨论',
}
const toast = reactive({ message: '', type: 'info' })

const { start, stop, isRecording } = useRecorder({
  silenceMs: CONFIG.AUDIO.VAD_SILENCE_MS,
  onSilence: async () => {
    if (!isRecording.value) return
    await finishRecording()
  },
})

const recordStatus = ref('点击麦克风开始录音')

async function startTest() {
  try {
    const res = await fetch('/api/level-test/questions')
    if (res.ok) {
      questions.value = await res.json()
    } else {
      throw new Error('Failed to load questions')
    }
  } catch {
    // Fallback questions
    questions.value = [
      { index: 0, difficulty: 'A1', prompt: "Can you introduce yourself? Tell me your name, where you're from, and what you do." },
      { index: 1, difficulty: 'A2', prompt: 'What did you do last weekend? Tell me about it.' },
      { index: 2, difficulty: 'B1', prompt: 'If you could live anywhere in the world, where would you choose and why?' },
      { index: 3, difficulty: 'B2', prompt: "Some people say AI will replace most jobs. What's your opinion?" },
      { index: 4, difficulty: 'C1', prompt: 'Describe a significant challenge you overcame and what it taught you.' },
    ]
  }
  phase.value = 'question'
}

async function handleRecord() {
  if (isRecording.value) {
    await finishRecording()
  } else {
    currentTranscript.value = ''
    recordStatus.value = '🔴 录音中...'
    try {
      await start()
    } catch {
      toast.message = '麦克风权限被拒绝'
      toast.type = 'warning'
      recordStatus.value = '点击麦克风开始录音'
    }
  }
}

async function finishRecording() {
  const blob = await stop()
  if (!blob) {
    recordStatus.value = '点击麦克风开始录音'
    return
  }

  isProcessing.value = true
  recordStatus.value = '⏳ 识别中...'

  try {
    const result = await recognizeOnly(blob)
    currentTranscript.value = result.text
    recordStatus.value = '✅ 识别完成'
  } catch (e) {
    toast.message = '语音识别失败，请重试'
    toast.type = 'error'
    recordStatus.value = '点击麦克风开始录音'
  } finally {
    isProcessing.value = false
  }
}

function nextQuestion() {
  responses.value.push({
    index: currentIndex.value,
    text: currentTranscript.value,
  })
  currentTranscript.value = ''
  recordStatus.value = '点击麦克风开始录音'

  if (currentIndex.value < questions.value.length - 1) {
    currentIndex.value++
  } else {
    submitAssessment()
  }
}

async function submitAssessment() {
  phase.value = 'analyzing'

  const formData = new FormData()
  formData.append('responses', JSON.stringify(responses.value))

  try {
    const res = await fetch('/api/level-test/assess', {
      method: 'POST',
      body: formData,
    })
    if (!res.ok) throw new Error('Assessment failed')
    const data = await res.json()
    result.value = data.assessment
    phase.value = 'result'
  } catch (e) {
    toast.message = '评估失败，请重试'
    toast.type = 'error'
    phase.value = 'question'
  }
}
</script>

<style scoped>
.level-test {
  max-width: 600px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

.intro { text-align: center; }
.intro h1 { color: #1f4e79; margin-bottom: 0.5rem; }
.intro p { color: #666; margin-bottom: 1.5rem; }
.info-list {
  list-style: none;
  padding: 0;
  margin-bottom: 2rem;
}
.info-list li {
  padding: 0.5rem 0;
  font-size: 1rem;
}

.start-btn {
  padding: 0.8rem 2rem;
  background: #1f4e79;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1.1rem;
  cursor: pointer;
  transition: background 0.2s;
}
.start-btn:hover { background: #2a6399; }

.skip-btn {
  display: block;
  margin: 1rem auto 0;
  background: none;
  border: none;
  color: #888;
  cursor: pointer;
  font-size: 0.9rem;
}

/* Question phase */
.progress-bar {
  height: 4px;
  background: #e0e0e0;
  border-radius: 2px;
  margin-bottom: 1rem;
}
.progress-fill {
  height: 100%;
  background: #1f4e79;
  border-radius: 2px;
  transition: width 0.3s;
}
.question-count { font-size: 0.85rem; color: #888; }
.difficulty-label { font-size: 0.8rem; color: #666; margin-bottom: 1rem; }

.question-card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}
.question-text { font-size: 1.1rem; color: #333; line-height: 1.6; }

.recording-area { text-align: center; }
.record-status { font-size: 0.9rem; color: #666; margin-bottom: 0.8rem; }

.record-btn {
  padding: 0.8rem 2rem;
  border-radius: 50px;
  border: 2px solid #1f4e79;
  background: white;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
}
.record-btn.active {
  background: #e53935;
  border-color: #e53935;
  color: white;
}
.record-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.transcript {
  margin-top: 1rem;
  padding: 0.8rem;
  background: #f5f5f5;
  border-radius: 8px;
  font-style: italic;
  color: #333;
}

.next-btn {
  margin-top: 1rem;
  padding: 0.6rem 1.5rem;
  background: #1f4e79;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.95rem;
}

/* Analyzing */
.analyzing { text-align: center; padding: 3rem 0; }
.spinner {
  width: 40px; height: 40px;
  border: 3px solid #e0e0e0;
  border-top-color: #1f4e79;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 1rem;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Result */
.result { text-align: center; }
.result h1 { color: #1f4e79; margin-bottom: 1rem; }

.level-badge {
  display: inline-block;
  font-size: 2.5rem;
  font-weight: bold;
  color: #1f4e79;
  background: #f0f7ff;
  padding: 1rem 2rem;
  border-radius: 12px;
  margin-bottom: 0.5rem;
}

.level-desc {
  color: #555;
  font-size: 0.9rem;
  margin-bottom: 0.8rem;
}

.level-scale {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}
.level-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.2rem;
  padding: 0.4rem 0.6rem;
  border-radius: 8px;
  opacity: 0.5;
  transition: all 0.2s;
}
.level-step.active {
  opacity: 1;
  background: #e3f2fd;
  transform: scale(1.1);
}
.step-badge {
  font-size: 0.9rem;
  font-weight: 700;
  color: #1f4e79;
}
.step-label {
  font-size: 0.7rem;
  color: #888;
}

.summary { color: #666; margin-bottom: 1.5rem; }

.scores-grid { text-align: left; margin-bottom: 1.5rem; }
.score-item {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  margin-bottom: 0.6rem;
}
.score-label { width: 80px; font-size: 0.85rem; color: #666; }
.score-bar {
  flex: 1;
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}
.score-bar div {
  height: 100%;
  background: #1f4e79;
  border-radius: 4px;
  transition: width 0.5s;
}
.score-num { font-size: 0.8rem; color: #888; width: 40px; }

.section { text-align: left; margin-bottom: 1rem; }
.section h3 { font-size: 0.95rem; margin-bottom: 0.5rem; }
.section ul { padding-left: 1.2rem; }
.section li { font-size: 0.9rem; color: #555; margin-bottom: 0.3rem; }
</style>
