<template>
  <div class="interview-prep">
    <header class="page-header">
      <button class="back-btn" @click="$router.push('/')">← {{ t('chat.back') }}</button>
      <div>
        <h1>💼 {{ t('interview.title') }}</h1>
        <p>{{ t('interview.subtitle') }}</p>
      </div>
    </header>

    <div class="prep-layout">
      <section class="prep-form">
        <div class="language-row">
          <span>{{ t('interview.language') }}</span>
          <div class="segmented">
            <button :class="{ active: language === 'en' }" @click="language = 'en'">
              {{ t('interview.english') }}
            </button>
            <button :class="{ active: language === 'zh' }" @click="language = 'zh'">
              {{ t('interview.chinese') }}
            </button>
          </div>
        </div>

        <label>
          <span>{{ t('interview.jd') }}</span>
          <textarea v-model="jdText" :placeholder="t('interview.jdPlaceholder')" rows="7"></textarea>
        </label>
        <label>
          <span>{{ t('interview.resume') }}</span>
          <textarea v-model="resumeText" :placeholder="t('interview.resumePlaceholder')" rows="5"></textarea>
        </label>
        <label>
          <span>{{ t('interview.project') }}</span>
          <textarea v-model="projectContext" :placeholder="t('interview.projectPlaceholder')" rows="5"></textarea>
        </label>

        <p v-if="error" class="error-line">{{ error }}</p>
        <button class="start-btn" :disabled="loading" @click="startInterview">
          {{ loading ? t('interview.starting') : t('interview.start') }}
        </button>
      </section>

      <aside class="prep-panel">
        <h2>{{ t('interview.prepTitle') }}</h2>
        <p v-if="!analysis" class="empty">{{ t('interview.prepEmpty') }}</p>
        <div v-else class="analysis">
          <div class="metric">
            <span>{{ t('interview.difficulty') }}</span>
            <strong>{{ analysis.difficulty_level || '-' }}</strong>
          </div>
          <div v-if="analysis.key_skills?.length" class="tag-block">
            <span>{{ t('interview.skills') }}</span>
            <div class="tags">
              <span v-for="skill in analysis.key_skills" :key="skill">{{ skill }}</span>
            </div>
          </div>
          <div v-if="analysis.focus_areas?.length" class="tag-block">
            <span>{{ t('interview.focus') }}</span>
            <div class="tags focus">
              <span v-for="area in analysis.focus_areas" :key="area">{{ area }}</span>
            </div>
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from '../composables/useI18n'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()

const language = ref(route.query.language === 'zh' ? 'zh' : 'en')
const jdText = ref(route.query.jd || '')
const resumeText = ref(route.query.resume || '')
const projectContext = ref(route.query.project || '')
const loading = ref(false)
const error = ref('')
const analysis = ref(null)

async function startInterview() {
  error.value = ''
  if (!jdText.value.trim() && !resumeText.value.trim() && !projectContext.value.trim()) {
    error.value = t('interview.required')
    return
  }

  loading.value = true
  const formData = new FormData()
  formData.append('jd_text', jdText.value)
  formData.append('resume_text', resumeText.value)
  formData.append('project_context', projectContext.value)
  formData.append('language', language.value)

  try {
    const res = await fetch('/api/integrations/talent-agent/oral-interview-session', {
      method: 'POST',
      body: formData,
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    analysis.value = data.talent_agent && !data.talent_agent.error ? data.talent_agent : null
    router.push(data.redirect_url || `/chat/interview?session_id=${data.session_id}`)
  } catch {
    error.value = t('interview.failed')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.interview-prep {
  animation: fade-in var(--transition-base) both;
}

.page-header {
  display: flex;
  align-items: flex-start;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.back-btn {
  color: var(--color-primary);
  font-weight: 600;
  padding: var(--space-2);
  border-radius: var(--radius-sm);
}
.back-btn:hover { background: var(--color-primary-50); }

.page-header h1 {
  font-size: var(--text-2xl);
  color: var(--color-text);
}

.page-header p {
  color: var(--color-text-secondary);
  max-width: 760px;
}

.prep-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.7fr) minmax(280px, 0.9fr);
  gap: var(--space-5);
  align-items: start;
}

.prep-form,
.prep-panel {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
}

.prep-form {
  padding: var(--space-5);
}

.language-row {
  display: flex;
  justify-content: space-between;
  gap: var(--space-4);
  align-items: center;
  margin-bottom: var(--space-4);
  font-weight: 600;
}

.segmented {
  display: inline-flex;
  padding: 3px;
  background: var(--color-border-light);
  border-radius: var(--radius-full);
}

.segmented button {
  padding: var(--space-1) var(--space-4);
  border-radius: var(--radius-full);
  color: var(--color-text-secondary);
  font-size: var(--text-sm);
  font-weight: 600;
}

.segmented button.active {
  color: white;
  background: var(--color-primary);
}

label {
  display: block;
  margin-bottom: var(--space-4);
}

label span {
  display: block;
  margin-bottom: var(--space-2);
  font-size: var(--text-sm);
  font-weight: 700;
  color: var(--color-text);
}

textarea {
  width: 100%;
  resize: vertical;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-bg);
  color: var(--color-text);
  padding: var(--space-3);
  font: inherit;
  line-height: 1.5;
  min-height: 108px;
}

textarea:focus {
  border-color: var(--color-primary);
  outline: none;
  box-shadow: 0 0 0 3px var(--color-primary-100);
}

.start-btn {
  width: 100%;
  padding: var(--space-3) var(--space-5);
  background: var(--color-primary);
  color: white;
  border-radius: var(--radius-full);
  font-weight: 700;
  transition: background var(--transition-fast), transform var(--transition-fast);
}

.start-btn:hover:not(:disabled) {
  background: var(--color-primary-dark);
  transform: translateY(-1px);
}

.error-line {
  color: var(--color-error);
  background: var(--color-error-light);
  border-radius: var(--radius-md);
  padding: var(--space-2) var(--space-3);
  margin-bottom: var(--space-3);
  font-size: var(--text-sm);
}

.prep-panel {
  padding: var(--space-5);
  position: sticky;
  top: 92px;
}

.prep-panel h2 {
  font-size: var(--text-lg);
  margin-bottom: var(--space-3);
}

.empty {
  color: var(--color-text-muted);
  font-size: var(--text-sm);
}

.metric {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-3);
  background: var(--color-primary-50);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-4);
}

.metric span,
.tag-block > span {
  color: var(--color-text-secondary);
  font-size: var(--text-sm);
  font-weight: 600;
}

.metric strong {
  color: var(--color-primary);
  text-transform: capitalize;
}

.tag-block {
  margin-bottom: var(--space-4);
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  margin-top: var(--space-2);
}

.tags span {
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  background: var(--color-primary-50);
  color: var(--color-primary);
  font-size: var(--text-xs);
  font-weight: 700;
}

.tags.focus span {
  background: var(--color-warning-light);
  color: #92400e;
}

@media (max-width: 860px) {
  .prep-layout { grid-template-columns: 1fr; }
  .prep-panel { position: static; }
}

@media (max-width: 640px) {
  .page-header {
    flex-direction: column;
    gap: var(--space-2);
  }

  .language-row {
    flex-direction: column;
    align-items: stretch;
  }

  .segmented { width: 100%; }
  .segmented button { flex: 1; }
}
</style>
