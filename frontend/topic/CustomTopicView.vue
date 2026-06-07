<template>
  <div class="custom-topic">
    <h1>🎯 自定义话题</h1>
    <p class="subtitle">输入话题，选择对话伙伴，开始自由练习</p>

    <!-- Trending Topics -->
    <div class="trending-section" v-if="trendingTopics.length">
      <h3>🔥 热门话题推荐</h3>
      <div class="trending-list">
        <div
          v-for="t in trendingTopics"
          :key="t.title"
          class="trending-chip"
          @click="topic = t.title"
        >
          <strong>{{ t.title }}</strong>
          <span>{{ t.description }}</span>
        </div>
      </div>
    </div>

    <form class="topic-form" @submit.prevent="startPractice">
      <!-- Topic Input -->
      <div class="form-group">
        <label for="topic">话题描述 <span class="required">*</span></label>
        <input
          id="topic"
          v-model="topic"
          type="text"
          placeholder="例如：讨论 AI 对教育的影响、如何在药店买药、租房看房..."
          maxlength="200"
          required
        />
        <span class="char-count">{{ topic.length }}/200</span>
      </div>

      <!-- Partner Configuration -->
      <fieldset class="partner-config">
        <legend>🧑‍🤝‍🧑 对话伙伴设置</legend>

        <div class="config-row">
          <div class="form-group compact">
            <label for="partnerName">名字</label>
            <input id="partnerName" type="text" v-model="partnerName" placeholder="John" maxlength="20" />
          </div>
          <div class="form-group compact">
            <label for="partnerCountry">来自</label>
            <select id="partnerCountry" v-model="partnerCountry">
              <option value="US">🇺🇸 美国</option>
              <option value="UK">🇬🇧 英国</option>
              <option value="Australia">🇦🇺 澳大利亚</option>
              <option value="India">🇮🇳 印度</option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label for="personality">性格特征</label>
          <input
            id="personality"
            type="text"
            v-model="partnerPersonality"
            placeholder="例如：绅士、开朗、友善、幽默、耐心..."
            maxlength="100"
          />
        </div>

        <div class="form-group">
          <label>语速</label>
          <div class="speed-options">
            <button
              v-for="s in speeds"
              :key="s.value"
              type="button"
              class="speed-btn"
              :class="{ active: speed === s.value }"
              @click="speed = s.value"
            >{{ s.label }}</button>
          </div>
        </div>
      </fieldset>

      <!-- Material -->
      <div class="form-group">
        <label for="material">补充材料（可选）</label>
        <textarea
          id="material"
          v-model="material"
          placeholder="粘贴文章、词汇表等参考材料..."
          rows="4"
          maxlength="3000"
        ></textarea>
      </div>

      <button type="submit" class="start-btn" :disabled="!topic.trim() || loading">
        <span v-if="loading" class="spinner"></span>
        <span v-if="loading">创建中...</span>
        <span v-else>开始练习 →</span>
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { CONFIG } from '../../shared/config'

const router = useRouter()
const topic = ref('')
const material = ref('')
const partnerName = ref('')
const partnerCountry = ref('US')
const partnerPersonality = ref('')
const speed = ref('normal')
const loading = ref(false)
const trendingTopics = ref([])

const speeds = [
  { value: 'slowest', label: '最慢' },
  { value: 'slow', label: '较慢' },
  { value: 'normal', label: '正常' },
  { value: 'fast', label: '较快' },
  { value: 'fastest', label: '最快' },
]

onMounted(async () => {
  try {
    const res = await fetch(`${CONFIG.API.BASE_URL}/api/topics/trending`)
    if (res.ok) {
      const data = await res.json()
      trendingTopics.value = data.topics || []
    }
  } catch { /* ignore */ }
})

async function startPractice() {
  if (!topic.value.trim()) return
  loading.value = true

  try {
    const form = new FormData()
    form.append('topic', topic.value.trim())
    if (material.value.trim()) form.append('material', material.value.trim())
    form.append('partner_name', partnerName.value.trim())
    form.append('partner_country', partnerCountry.value)
    form.append('partner_personality', partnerPersonality.value.trim())
    form.append('speed', speed.value)

    const res = await fetch(`${CONFIG.API.BASE_URL}/api/sessions/topic`, {
      method: 'POST',
      body: form,
    })

    if (!res.ok) throw new Error('Failed')
    const data = await res.json()

    router.push({
      path: '/chat/custom_topic',
      query: {
        session_id: data.session_id,
        greeting: data.greeting,
        topic: data.topic,
      },
    })
  } catch {
    alert('创建话题失败，请重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.custom-topic { max-width: 760px; margin: 0 auto; padding: var(--space-8) var(--space-6); }
h1 { margin-bottom: var(--space-1); color: var(--color-text); }
.subtitle { color: var(--color-text-secondary); margin-bottom: var(--space-6); }

.trending-section { margin-bottom: var(--space-6); }
.trending-section h3 { font-size: var(--text-base); margin-bottom: var(--space-3); color: var(--color-text); }
.trending-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: var(--space-3);
}
.trending-chip {
  display: flex; flex-direction: column; gap: var(--space-1);
  padding: var(--space-3) var(--space-4); background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md); cursor: pointer; transition: var(--transition-fast);
}
.trending-chip:hover { border-color: var(--color-primary); background: var(--color-primary-50); }
.trending-chip strong { font-size: var(--text-sm); color: var(--color-primary); }
.trending-chip span { font-size: var(--text-xs); color: var(--color-text-secondary); }

.topic-form { display: flex; flex-direction: column; gap: var(--space-5); }
.form-group { display: flex; flex-direction: column; gap: var(--space-2); position: relative; }
.form-group label { font-weight: 600; font-size: var(--text-sm); color: var(--color-text); }
.form-group.compact { flex: 1; }
.required { color: var(--color-error); }
.char-count { position: absolute; right: 10px; bottom: 10px; font-size: var(--text-xs); color: var(--color-text-muted); }

.topic-form input, .topic-form textarea, .topic-form select {
  padding: var(--space-3) var(--space-4);
  border: 1.5px solid var(--color-border); border-radius: var(--radius-md);
  font-size: var(--text-base); font-family: inherit;
  background: var(--color-surface); color: var(--color-text);
  transition: border-color var(--transition-fast);
}
.topic-form input::placeholder, .topic-form textarea::placeholder { color: var(--color-text-muted); }
.topic-form input:focus, .topic-form textarea:focus, .topic-form select:focus {
  outline: none; border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-100);
}

.partner-config {
  border: 1.5px solid var(--color-border); border-radius: var(--radius-lg);
  padding: var(--space-5) var(--space-6);
  display: flex; flex-direction: column; gap: var(--space-5);
  background: var(--color-bg);
}
.partner-config legend { font-weight: 600; padding: 0 var(--space-2); color: var(--color-primary); }
.config-row { display: flex; gap: var(--space-5); flex-wrap: wrap; }
.config-row .form-group.compact { min-width: 180px; }

.speed-options { display: flex; gap: var(--space-2); flex-wrap: wrap; }
.speed-btn {
  padding: var(--space-2) var(--space-4); border: 1px solid var(--color-border);
  border-radius: var(--radius-full);
  background: var(--color-surface); color: var(--color-text);
  cursor: pointer; font-size: var(--text-sm); transition: var(--transition-fast);
}
.speed-btn.active { background: var(--color-primary); color: #fff; border-color: var(--color-primary); }
.speed-btn:hover:not(.active) { border-color: var(--color-primary); }

.start-btn {
  padding: var(--space-4) var(--space-8); background: var(--color-primary); color: #fff; border: none;
  border-radius: var(--radius-md); font-size: var(--text-lg); font-weight: 600; cursor: pointer;
  transition: background var(--transition-fast);
}
.start-btn:hover:not(:disabled) { background: var(--color-primary-dark); }
.start-btn:disabled { background: var(--color-text-muted); cursor: not-allowed; }
.spinner {
  display: inline-block; width: 18px; height: 18px;
  border: 2px solid #fff; border-top-color: transparent;
  border-radius: 50%; animation: spin 0.6s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
