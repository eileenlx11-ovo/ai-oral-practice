<template>
  <div class="pron-view">
    <Toast :message="toast.message" :type="toast.type" @close="toast.message = ''" />

    <header class="pron-header">
      <button @click="$router.push('/')" class="back-btn">← 返回</button>
      <h2>🎯 发音评测</h2>
      <span v-if="status.provider" class="provider-badge" :class="{ mock: status.is_mock }">
        {{ status.is_mock ? 'Demo 模式（模拟分数）' : status.provider }}
      </span>
    </header>

    <p class="hint">朗读下面的句子，AI 会逐词给出发音评分。点句子可换一句。</p>

    <div class="ref-card" @click="nextSentence">
      <p class="ref-text">{{ referenceText }}</p>
      <span class="change-hint">点击换一句 ↻</span>
    </div>

    <div class="controls">
      <button
        class="record-btn"
        :class="{ recording: state === 'RECORDING', busy: state === 'SCORING' }"
        :disabled="state === 'SCORING'"
        @click="handleToggle"
      >
        {{ buttonText }}
      </button>
    </div>

    <!-- Result -->
    <div v-if="result" class="result">
      <div class="scores">
        <div class="score-pill"><span>综合</span><b>{{ round(result.pronunciation_score) }}</b></div>
        <div class="score-pill"><span>准确度</span><b>{{ round(result.accuracy_score) }}</b></div>
        <div class="score-pill"><span>流利度</span><b>{{ round(result.fluency_score) }}</b></div>
        <div class="score-pill"><span>完整度</span><b>{{ round(result.completeness_score) }}</b></div>
      </div>
      <div class="words">
        <span
          v-for="(w, i) in result.words"
          :key="i"
          class="word"
          :style="{ color: wordColor(w.accuracy_score) }"
          :title="`${round(w.accuracy_score)} 分`"
        >{{ w.word }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRecorder } from '../../voice/audio/useRecorder'
import { assessPronunciation, getAssessStatus } from '../../voice/asr/service'
import { CONFIG } from '../../shared/config'

const SENTENCES = [
  'The quick brown fox jumps over the lazy dog.',
  'I would like to schedule a meeting for next Tuesday.',
  'Could you please recommend a good restaurant nearby?',
  'She sells seashells by the seashore.',
  'Thank you for taking the time to interview me today.',
  'The weather is lovely, so let us go for a walk.',
]

const referenceText = ref(SENTENCES[0])
const state = ref('IDLE') // IDLE | RECORDING | SCORING
const result = ref(null)
const status = reactive({ available: true, provider: null, is_mock: false })
const toast = reactive({ message: '', type: 'info' })

const buttonText = computed(() => ({
  IDLE: '🎙️ 开始朗读',
  RECORDING: '⏹️ 停止并评分',
  SCORING: '⏳ 评分中…',
}[state.value]))

const { start, stop } = useRecorder({ silenceMs: CONFIG.AUDIO.VAD_SILENCE_MS })

onMounted(async () => {
  try {
    const s = await getAssessStatus()
    Object.assign(status, s)
    if (!s.available) showToast('发音评测服务暂不可用', 'warning')
  } catch { /* status is best-effort */ }
})

function showToast(message, type = 'error') {
  toast.message = message
  toast.type = type
}

function round(n) {
  return Math.round(n ?? 0)
}

function wordColor(score) {
  if (score >= 80) return '#2e7d32'   // green
  if (score >= 60) return '#ef6c00'   // orange
  return '#c62828'                    // red
}

function nextSentence() {
  if (state.value !== 'IDLE') return
  const idx = SENTENCES.indexOf(referenceText.value)
  referenceText.value = SENTENCES[(idx + 1) % SENTENCES.length]
  result.value = null
}

async function handleToggle() {
  if (state.value === 'IDLE') {
    result.value = null
    state.value = 'RECORDING'
    try {
      await start()
    } catch {
      state.value = 'IDLE'
      showToast('麦克风权限被拒绝，请在浏览器设置中允许麦克风访问', 'warning')
    }
    return
  }
  if (state.value === 'RECORDING') {
    const blob = await stop()
    if (!blob) { state.value = 'IDLE'; return }
    state.value = 'SCORING'
    try {
      result.value = await assessPronunciation(blob, referenceText.value)
    } catch (err) {
      showToast(err.message || '发音评测失败', 'error')
    } finally {
      state.value = 'IDLE'
    }
  }
}
</script>

<style scoped>
.pron-view { max-width: 720px; margin: 0 auto; }

.pron-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.5rem;
}
.pron-header h2 { color: #1f4e79; margin: 0; }
.back-btn {
  background: none;
  border: none;
  color: #1f4e79;
  cursor: pointer;
  font-size: 1rem;
}
.provider-badge {
  margin-left: auto;
  font-size: 0.75rem;
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  background: #e3f2fd;
  color: #1565c0;
}
.provider-badge.mock { background: #fff3e0; color: #ef6c00; }

.hint { color: #666; font-size: 0.9rem; margin-bottom: 1rem; }

.ref-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  cursor: pointer;
  transition: box-shadow 0.2s;
}
.ref-card:hover { box-shadow: 0 6px 18px rgba(31,78,121,0.15); }
.ref-text { font-size: 1.3rem; color: #1f4e79; line-height: 1.5; margin: 0 0 0.5rem; }
.change-hint { font-size: 0.75rem; color: #999; }

.controls { text-align: center; margin: 1.5rem 0; }
.record-btn {
  background: #1f4e79;
  color: white;
  border: none;
  border-radius: 999px;
  padding: 0.9rem 2rem;
  font-size: 1.05rem;
  cursor: pointer;
  transition: background 0.2s, transform 0.1s;
}
.record-btn:hover { background: #163d5f; }
.record-btn:active { transform: scale(0.97); }
.record-btn.recording { background: #c62828; animation: pulse 1.2s infinite; }
.record-btn.busy { background: #999; cursor: not-allowed; }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.65; } }

.result {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.scores { display: flex; flex-wrap: wrap; gap: 0.8rem; margin-bottom: 1.2rem; }
.score-pill {
  flex: 1;
  min-width: 80px;
  text-align: center;
  background: #f5f7fa;
  border-radius: 10px;
  padding: 0.6rem;
}
.score-pill span { display: block; font-size: 0.75rem; color: #888; }
.score-pill b { font-size: 1.5rem; color: #1f4e79; }

.words { line-height: 2; font-size: 1.2rem; }
.word { margin-right: 0.4rem; font-weight: 600; cursor: default; }
</style>


