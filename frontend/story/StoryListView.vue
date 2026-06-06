<template>
  <div class="story-list">
    <header class="story-hero">
      <div>
        <p class="eyebrow">{{ t('story.eyebrow') }}</p>
        <h1>{{ t('story.title') }}</h1>
        <p>{{ t('story.subtitle') }}</p>
      </div>
      <button class="back-btn" @click="$router.push('/')">{{ t('story.backHome') }}</button>
    </header>

    <div v-if="loading" class="state">{{ t('story.loading') }}</div>
    <div v-else-if="error" class="state error">{{ error }}</div>

    <section v-else class="story-grid">
      <button
        v-for="story in stories"
        :key="story.id"
        class="story-card"
        @click="$router.push(`/story/${story.id}`)"
      >
        <span class="cover">{{ story.cover_emoji }}</span>
        <div class="card-main">
          <div class="card-top">
            <h2>{{ locale === 'zh' ? story.title_zh : story.title }}</h2>
            <span class="difficulty" :class="story.difficulty">{{ story.difficulty }}</span>
          </div>
          <p>{{ locale === 'zh' ? story.synopsis_zh : story.synopsis }}</p>
          <span class="scene-count">{{ story.scene_count }} {{ t('story.scenes') }}</span>
        </div>
      </button>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useI18n } from '../composables/useI18n'

const { t, locale } = useI18n()
const stories = ref([])
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const res = await fetch('/api/stories')
    if (!res.ok) throw new Error(t('story.loadFailed'))
    stories.value = await res.json()
  } catch (e) {
    error.value = e.message || t('story.loadFailed')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.story-list {
  animation: fade-in var(--transition-base) both;
}

.story-hero {
  display: flex;
  justify-content: space-between;
  gap: var(--space-4);
  align-items: flex-end;
  margin-bottom: var(--space-8);
}

.eyebrow {
  color: var(--color-primary);
  font-size: var(--text-sm);
  font-weight: 700;
  margin-bottom: var(--space-2);
}

.story-hero h1 {
  color: var(--color-text);
  font-size: var(--text-3xl);
  margin-bottom: var(--space-2);
}

.story-hero p {
  color: var(--color-text-secondary);
}

.back-btn {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-full);
  color: var(--color-text-secondary);
  padding: var(--space-2) var(--space-4);
  white-space: nowrap;
}

.story-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: var(--space-4);
}

.story-card {
  display: flex;
  gap: var(--space-4);
  text-align: left;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  transition: transform var(--transition-base), box-shadow var(--transition-base), border-color var(--transition-base);
}

.story-card:hover {
  border-color: var(--color-primary-200);
  box-shadow: var(--shadow-lg);
  transform: translateY(-3px);
}

.cover {
  width: 52px;
  height: 52px;
  display: grid;
  place-items: center;
  border-radius: var(--radius-md);
  background: var(--color-primary-50);
  font-size: 1.8rem;
  flex-shrink: 0;
}

.card-main {
  min-width: 0;
}

.card-top {
  display: flex;
  gap: var(--space-2);
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--space-2);
}

.card-top h2 {
  color: var(--color-text);
  font-size: var(--text-lg);
}

.story-card p {
  color: var(--color-text-secondary);
  font-size: var(--text-sm);
  margin-bottom: var(--space-3);
}

.difficulty,
.scene-count {
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: 700;
  padding: 2px var(--space-2);
}

.difficulty.intermediate {
  background: var(--color-intermediate-bg);
  color: var(--color-intermediate);
}

.difficulty.advanced {
  background: var(--color-advanced-bg);
  color: var(--color-advanced);
}

.scene-count {
  background: var(--color-border-light);
  color: var(--color-text-muted);
}

.state {
  color: var(--color-text-secondary);
  padding: var(--space-8);
  text-align: center;
}

.state.error {
  color: var(--color-error);
}

@media (max-width: 768px) {
  .story-hero {
    align-items: flex-start;
    flex-direction: column;
  }

  .story-grid {
    grid-template-columns: 1fr;
  }
}
</style>
