<template>
  <div class="guide-page">
    <header class="guide-header">
      <button class="back-btn" @click="$router.push('/')">← 返回</button>
      <h1 v-if="guide">{{ guide.title }} 学习指南</h1>
      <h1 v-else>加载中...</h1>
    </header>

    <div v-if="loading" class="loading">加载学习资料中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>

    <div v-else-if="guide" class="guide-content">
      <!-- Vocabulary Section -->
      <section class="section vocabulary-section">
        <h2>核心词汇</h2>
        <div class="vocab-grid">
          <div v-for="(item, i) in guide.vocabulary" :key="i" class="vocab-card">
            <div class="vocab-top">
              <span class="vocab-word">{{ item.word }}</span>
              <button class="speak-btn" @click="speak(item.word)" aria-label="播放发音">
                🔊
              </button>
            </div>
            <span class="vocab-phonetic">{{ item.phonetic }}</span>
            <span class="vocab-meaning">{{ item.meaning }}</span>
            <p class="vocab-example">{{ item.example }}</p>
          </div>
        </div>
      </section>

      <!-- Expressions Section -->
      <section class="section expressions-section">
        <h2>常用表达</h2>
        <div class="expr-list">
          <div v-for="(item, i) in guide.expressions" :key="i" class="expr-card">
            <div class="expr-top">
              <span class="expr-phrase">{{ item.phrase }}</span>
              <button class="speak-btn" @click="speak(item.phrase)" aria-label="播放发音">
                🔊
              </button>
            </div>
            <span class="expr-phonetic">{{ item.phonetic }}</span>
            <span class="expr-meaning">{{ item.meaning }}</span>
            <p class="expr-example">{{ item.example }}</p>
          </div>
        </div>
      </section>
      <!-- Tips Section -->
      <section class="section tips-section">
        <h2>实用技巧</h2>
        <div class="tips-list">
          <div v-for="(tip, i) in guide.tips" :key="i" class="tip-card">
            <h3>{{ tip.title }}</h3>
            <p class="tip-desc">{{ tip.description }}</p>
            <div class="tip-example">
              <span class="tip-example-label">Example:</span>
              <span class="tip-example-text">{{ tip.example }}</span>
              <button class="speak-btn small" @click="speak(tip.example)" aria-label="播放示例">
                🔊
              </button>
            </div>
            <p v-if="tip.note" class="tip-note">💡 {{ tip.note }}</p>
          </div>
        </div>
      </section>

      <!-- Dialogue Section -->
      <section class="section dialogue-section">
        <h2>示范对话</h2>
        <div class="dialogue-list">
          <div v-for="(line, i) in guide.dialogue" :key="i" class="dialogue-line" :class="'speaker-' + line.speaker.toLowerCase()">
            <div class="dialogue-top">
              <span class="speaker-badge">{{ line.speaker }}</span>
              <button class="speak-btn small" @click="speak(line.text)" aria-label="播放对话">
                🔊
              </button>
            </div>
            <p class="dialogue-text">{{ line.text }}</p>
            <p class="dialogue-translation">{{ line.translation }}</p>
            <div v-if="line.notes && line.notes.length" class="dialogue-notes">
              <span v-for="(note, j) in line.notes" :key="j" class="dialogue-note">
                <strong>{{ note.term }}</strong>: {{ note.explanation }}
              </span>
            </div>
          </div>
        </div>
      </section>

      <!-- Start Practice Button -->
      <div class="start-practice">
        <button class="practice-btn" @click="$router.push(`/chat/${scenarioId}`)">
          开始练习 →
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const scenarioId = route.params.scenario

const guide = ref(null)
const loading = ref(true)
const error = ref('')

function speak(text) {
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel()
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = 'en-US'
    utterance.rate = 0.85
    window.speechSynthesis.speak(utterance)
  }
}

onMounted(async () => {
  try {
    const res = await fetch(`/api/scenarios/${scenarioId}/guide`)
    if (res.ok) {
      guide.value = await res.json()
    } else {
      error.value = '无法加载学习指南'
    }
  } catch {
    error.value = '网络错误，请稍后重试'
  } finally {
    loading.value = false
  }
})
</script>
<style scoped>
.guide-page { max-width: 800px; margin: 0 auto; padding: 1.5rem; }

.guide-header {
  display: flex; align-items: center; gap: 1rem; margin-bottom: 2rem;
}
.guide-header h1 { font-size: 1.5rem; color: #1f4e79; margin: 0; }
.back-btn {
  background: none; border: 1px solid #d0d9e3; border-radius: 8px;
  padding: 0.4rem 0.8rem; cursor: pointer; color: #1f4e79; font-size: 0.9rem;
}
.back-btn:hover { background: #f0f5fa; }

.loading, .error { text-align: center; padding: 3rem; color: #666; }
.error { color: #c62828; }

.section { margin-bottom: 2.5rem; }
.section h2 {
  font-size: 1.2rem; color: #1f4e79; margin-bottom: 1rem;
  padding-bottom: 0.5rem; border-bottom: 2px solid #e3edf7;
}

/* Vocabulary */
.vocab-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 1rem; }
.vocab-card {
  background: white; border-radius: 10px; padding: 1rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06); display: flex; flex-direction: column; gap: 0.3rem;
}
.vocab-top { display: flex; justify-content: space-between; align-items: center; }
.vocab-word { font-weight: 700; font-size: 1.05rem; color: #1f4e79; }
.vocab-phonetic { font-size: 0.8rem; color: #888; font-style: italic; }
.vocab-meaning { font-size: 0.9rem; color: #333; }
.vocab-example { font-size: 0.82rem; color: #555; margin-top: 0.3rem; font-style: italic; }

/* Expressions */
.expr-list { display: flex; flex-direction: column; gap: 1rem; }
.expr-card {
  background: white; border-radius: 10px; padding: 1rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06); display: flex; flex-direction: column; gap: 0.3rem;
}
.expr-top { display: flex; justify-content: space-between; align-items: center; }
.expr-phrase { font-weight: 700; font-size: 1rem; color: #2e7d32; }
.expr-phonetic { font-size: 0.8rem; color: #888; font-style: italic; }
.expr-meaning { font-size: 0.9rem; color: #333; }
.expr-example { font-size: 0.82rem; color: #555; font-style: italic; margin-top: 0.3rem; }

/* Tips */
.tips-list { display: flex; flex-direction: column; gap: 1rem; }
.tip-card {
  background: #fffde7; border-radius: 10px; padding: 1.2rem;
  border-left: 4px solid #fbc02d;
}
.tip-card h3 { font-size: 1rem; color: #333; margin: 0 0 0.5rem 0; }
.tip-desc { font-size: 0.9rem; color: #555; margin-bottom: 0.6rem; }
.tip-example { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }
.tip-example-label { font-size: 0.8rem; color: #888; }
.tip-example-text { font-size: 0.9rem; color: #1f4e79; font-style: italic; }
.tip-note { font-size: 0.82rem; color: #666; margin-top: 0.5rem; }

/* Dialogue */
.dialogue-list { display: flex; flex-direction: column; gap: 0.8rem; }
.dialogue-line {
  background: white; border-radius: 10px; padding: 1rem;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.dialogue-line.speaker-a { border-left: 3px solid #1976d2; }
.dialogue-line.speaker-b { border-left: 3px solid #388e3c; }
.dialogue-top { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.4rem; }
.speaker-badge {
  display: inline-block; width: 24px; height: 24px; line-height: 24px;
  text-align: center; border-radius: 50%; font-size: 0.75rem; font-weight: 700; color: white;
}
.speaker-a .speaker-badge { background: #1976d2; }
.speaker-b .speaker-badge { background: #388e3c; }
.dialogue-text { font-size: 0.95rem; color: #222; margin: 0 0 0.3rem 0; }
.dialogue-translation { font-size: 0.85rem; color: #666; margin: 0 0 0.4rem 0; }
.dialogue-notes { display: flex; flex-direction: column; gap: 0.2rem; }
.dialogue-note { font-size: 0.8rem; color: #555; background: #f5f5f5; padding: 0.3rem 0.5rem; border-radius: 4px; }

/* Speak button */
.speak-btn {
  background: none; border: none; cursor: pointer; font-size: 1.1rem;
  padding: 0.2rem; border-radius: 4px; transition: background 0.15s;
}
.speak-btn:hover { background: #e3f2fd; }
.speak-btn.small { font-size: 0.9rem; }

/* Start practice */
.start-practice { text-align: center; padding: 2rem 0; }
.practice-btn {
  background: #1f4e79; color: white; border: none; border-radius: 12px;
  padding: 1rem 2.5rem; font-size: 1.1rem; cursor: pointer;
  transition: background 0.2s, transform 0.15s;
}
.practice-btn:hover { background: #2a6399; transform: translateY(-2px); }
</style>
