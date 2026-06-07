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
            <input id="partnerName" v-model="partnerName" placeholder="John" maxlength="20" />
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
        partner_name: data.partner?.name || '',
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
.custom-topic { max-width: 640px; margin: 0 auto; padding: 2rem 1.5rem; }
h1 { margin-bottom: 0.25rem; }
.subtitle { color: #666; margin-bottom: 1.5rem; }

.trending-section { margin-bottom: 1.5rem; }
.trending-section h3 { font-size: 1rem; margin-bottom: 0.75rem; }
.trending-list { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.trending-chip {
  display: flex; flex-direction: column; gap: 0.2rem;
  padding: 0.5rem 0.75rem; background: #f8f9fa; border: 1px solid #e0e0e0;
  border-radius: 8px; cursor: pointer; transition: all 0.2s; max-width: 200px;
}
.trending-chip:hover { border-color: #4a90d9; background: #f0f7ff; }
.trending-chip strong { font-size: 0.85rem; color: #1f4e79; }
.trending-chip span { font-size: 0.75rem; color: #666; }

.topic-form { display: flex; flex-direction: column; gap: 1.25rem; }
.form-group { display: flex; flex-direction: column; gap: 0.4rem; position: relative; }
.form-group label { font-weight: 600; font-size: 0.9rem; }
.form-group.compact { flex: 1; }
.required { color: #e74c3c; }
.char-count { position: absolute; right: 8px; bottom: 8px; font-size: 0.7rem; color: #999; }

input[type="text"], textarea, select {
  padding: 0.65rem 0.85rem; border: 1.5px solid #e0e0e0; border-radius: 8px;
  font-size: 0.95rem; transition: border-color 0.2s;
}
input:focus, textarea:focus, select:focus { outline: none; border-color: #4a90d9; }

.partner-config {
  border: 1.5px solid #e8ecf0; border-radius: 12px; padding: 1rem 1.25rem;
  display: flex; flex-direction: column; gap: 1rem;
}
.partner-config legend { font-weight: 600; padding: 0 0.5rem; color: #1f4e79; }
.config-row { display: flex; gap: 1rem; }

.speed-options { display: flex; gap: 0.4rem; flex-wrap: wrap; }
.speed-btn {
  padding: 0.4rem 0.75rem; border: 1px solid #ddd; border-radius: 20px;
  background: white; cursor: pointer; font-size: 0.85rem; transition: all 0.2s;
}
.speed-btn.active { background: #1f4e79; color: white; border-color: #1f4e79; }
.speed-btn:hover:not(.active) { border-color: #4a90d9; }

.start-btn {
  padding: 0.85rem 2rem; background: #4a90d9; color: white; border: none;
  border-radius: 8px; font-size: 1.05rem; font-weight: 600; cursor: pointer;
  transition: background 0.2s;
}
.start-btn:hover:not(:disabled) { background: #357abd; }
.start-btn:disabled { background: #ccc; cursor: not-allowed; }
.spinner {
  display: inline-block; width: 18px; height: 18px;
  border: 2px solid #fff; border-top-color: transparent;
  border-radius: 50%; animation: spin 0.6s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>