<template>
  <div class="home">
    <!-- Hero section -->
    <section class="hero">
      <h1 class="hero-title">
        <span class="hero-wave">👋</span> Ready to practice?
      </h1>
      <p class="hero-subtitle">{{ t('home.hero.subtitle') }}</p>
    </section>

    <!-- Quick actions -->
    <div class="quick-actions">
      <button class="action-card pronunciation" @click="$router.push('/pronunciation')">
        <span class="action-icon">🎯</span>
        <div class="action-info">
          <span class="action-title">{{ t('home.actions.pronunciation') }}</span>
          <span class="action-desc">{{ t('home.actions.pronunciationDesc') }}</span>
        </div>
        <span class="action-arrow">→</span>
      </button>
      <button v-if="!hasLevel" class="action-card assessment" @click="$router.push('/assessment')">
        <span class="action-icon">🎓</span>
        <div class="action-info">
          <span class="action-title">{{ t('home.actions.assessment') }}</span>
          <span class="action-desc">{{ t('home.actions.assessmentDesc') }}</span>
        </div>
        <span class="action-arrow">→</span>
      </button>
      <button v-else class="action-card assessment" @click="$router.push('/assessment')">
        <span class="action-icon">🎓</span>
        <div class="action-info">
          <span class="action-title">重新评估</span>
          <span class="action-desc">更新你的水平</span>
        </div>
        <span class="action-arrow">→</span>
      </button>
    </div>

    <!-- Filters -->
    <div class="filters">
      <div class="category-tabs">
        <button
          v-for="cat in categories"
          :key="cat.id"
          class="tab-btn"
          :class="{ active: activeCategory === cat.id }"
          @click="activeCategory = cat.id"
        >
          <span class="tab-icon">{{ cat.icon }}</span>
          <span class="tab-name">{{ cat.name }}</span>
        </button>
      </div>
      <div class="difficulty-pills">
        <button
          v-for="d in difficulties"
          :key="d.id"
          class="pill"
          :class="{ active: activeDifficulty === d.id, [d.id]: true }"
          @click="activeDifficulty = activeDifficulty === d.id ? 'all' : d.id"
        >
          {{ t(d.labelKey) }}
        </button>
      </div>
    </div>

    <!-- Scenario grid -->
    <div class="scenarios">
      <div
        v-for="(s, idx) in filteredScenarios"
        :key="s.id"
        class="scenario-card"
        :style="{ animationDelay: `${idx * 50}ms` }"
        @click="$router.push(`/chat/${s.id}`)"
      >
        <div class="card-icon-wrap">
          <span class="card-icon">{{ s.icon }}</span>
        </div>
        <div class="card-body">
          <div class="card-top">
            <h3>{{ s.name }}</h3>
            <span class="diff-tag" :class="s.difficulty">{{ diffLabel(s.difficulty) }}</span>
          </div>
          <p class="card-desc">{{ s.description }}</p>
          <div v-if="s.objective" class="card-objective">
            🎯 {{ s.objective }}
          </div>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-if="filteredScenarios.length === 0" class="empty-state">
      <p>😅 {{ t('home.empty') }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { CONFIG } from '../../shared/config'
import { useI18n } from '../composables/useI18n'

const { t } = useI18n()
const categories = CONFIG.CATEGORIES
const activeCategory = ref('all')
const activeDifficulty = ref('all')
const scenarios = ref(CONFIG.SCENARIOS)
const hasLevel = ref(false)

const difficulties = [
  { id: 'beginner', labelKey: 'home.difficulty.beginner' },
  { id: 'intermediate', labelKey: 'home.difficulty.intermediate' },
  { id: 'advanced', labelKey: 'home.difficulty.advanced' },
]

function diffLabel(d) {
  return t(`home.difficulty.${d}`, d)
}

const filteredScenarios = computed(() => {
  let list = scenarios.value
  if (activeCategory.value !== 'all') {
    list = list.filter((s) => s.category === activeCategory.value)
  }
  if (activeDifficulty.value !== 'all') {
    list = list.filter((s) => s.difficulty === activeDifficulty.value)
  }
  return list
})

onMounted(async () => {
  try {
    const res = await fetch('/api/scenarios')
    if (res.ok) scenarios.value = await res.json()
  } catch { /* fallback from config */ }

  try {
    const res = await fetch('/api/profile')
    if (res.ok) {
      const profile = await res.json()
      hasLevel.value = !!profile.level
    }
  } catch { /* no profile yet */ }
})
</script>

<style scoped>
.home {
  animation: fade-in var(--transition-base) both;
}

/* Hero */
.hero {
  text-align: center;
  margin-bottom: var(--space-8);
}

.hero-title {
  font-size: var(--text-3xl);
  font-weight: 800;
  color: var(--color-text);
  margin-bottom: var(--space-2);
}

.hero-wave {
  display: inline-block;
  animation: bounce-subtle 2s ease-in-out infinite;
}

.hero-subtitle {
  color: var(--color-text-secondary);
  font-size: var(--text-lg);
}

/* Quick actions */
.quick-actions {
  display: flex;
  gap: var(--space-4);
  margin-bottom: var(--space-8);
}

.action-card {
  flex: 1;
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-4) var(--space-5);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  transition: all var(--transition-base);
  text-align: left;
}

.action-card:hover {
  border-color: var(--color-primary-200);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.action-card.pronunciation { border-left: 3px solid var(--color-primary); }
.action-card.assessment { border-left: 3px solid var(--color-accent); }

.action-icon { font-size: 1.8rem; }
.action-info { flex: 1; }
.action-title { display: block; font-weight: 600; font-size: var(--text-base); color: var(--color-text); }
.action-desc { display: block; font-size: var(--text-sm); color: var(--color-text-muted); }
.action-arrow { font-size: var(--text-lg); color: var(--color-text-muted); transition: transform var(--transition-fast); }
.action-card:hover .action-arrow { transform: translateX(4px); color: var(--color-primary); }

/* Filters */
.filters {
  margin-bottom: var(--space-6);
}

.category-tabs {
  display: flex;
  gap: var(--space-2);
  margin-bottom: var(--space-3);
  overflow-x: auto;
  padding-bottom: var(--space-2);
  -ms-overflow-style: none;
  scrollbar-width: none;
}
.category-tabs::-webkit-scrollbar { display: none; }

.tab-btn {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-full);
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text-secondary);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  white-space: nowrap;
  transition: all var(--transition-fast);
}

.tab-btn:hover { border-color: var(--color-primary-200); color: var(--color-primary); }
.tab-btn.active {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.tab-icon { font-size: 1rem; }

.difficulty-pills {
  display: flex;
  gap: var(--space-2);
}

.pill {
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: 600;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  color: var(--color-text-secondary);
  transition: all var(--transition-fast);
}

.pill:hover { border-color: var(--color-text-muted); }
.pill.active.beginner { background: var(--color-beginner-bg); border-color: var(--color-beginner); color: var(--color-beginner); }
.pill.active.intermediate { background: var(--color-intermediate-bg); border-color: var(--color-intermediate); color: #b45309; }
.pill.active.advanced { background: var(--color-advanced-bg); border-color: var(--color-advanced); color: var(--color-advanced); }

/* Scenario grid */
.scenarios {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--space-4);
}

.scenario-card {
  display: flex;
  gap: var(--space-4);
  padding: var(--space-5);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-base);
  animation: fade-in var(--transition-base) both;
}

.scenario-card:hover {
  border-color: var(--color-primary-200);
  box-shadow: var(--shadow-lg);
  transform: translateY(-3px);
}

.card-icon-wrap {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  background: var(--color-primary-50);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.card-icon { font-size: 1.5rem; }

.card-body { flex: 1; min-width: 0; }

.card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-2);
  margin-bottom: var(--space-1);
}

.card-body h3 {
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--color-text);
}

.diff-tag {
  font-size: var(--text-xs);
  font-weight: 600;
  padding: 2px var(--space-2);
  border-radius: var(--radius-sm);
  text-transform: capitalize;
  white-space: nowrap;
}

.diff-tag.beginner { background: var(--color-beginner-bg); color: var(--color-beginner); }
.diff-tag.intermediate { background: var(--color-intermediate-bg); color: #b45309; }
.diff-tag.advanced { background: var(--color-advanced-bg); color: var(--color-advanced); }

.card-desc {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  margin-bottom: var(--space-2);
}

.card-objective {
  font-size: var(--text-xs);
  color: var(--color-primary);
  background: var(--color-primary-50);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
}

.empty-state {
  text-align: center;
  padding: var(--space-12);
  color: var(--color-text-muted);
}

/* Responsive */
@media (max-width: 768px) {
  .hero-title { font-size: var(--text-2xl); }

  .quick-actions { flex-direction: column; }

  .scenarios {
    grid-template-columns: 1fr;
  }
}
</style>
