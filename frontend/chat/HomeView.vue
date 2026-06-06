<template>
  <div class="home">
    <h1>选择练习场景</h1>
    <p class="subtitle">选择一个场景，开始与 AI 进行英语口语对话练习</p>

    <!-- Category tabs -->
    <div class="category-tabs">
      <button
        v-for="cat in categories"
        :key="cat.id"
        class="tab-btn"
        :class="{ active: activeCategory === cat.id }"
        @click="activeCategory = cat.id"
      >
        {{ cat.icon }} {{ cat.name }}
      </button>
    </div>

    <!-- Difficulty filter -->
    <div class="difficulty-filter">
      <span class="filter-label">难度：</span>
      <button
        v-for="d in difficulties"
        :key="d.id"
        class="diff-btn"
        :class="{ active: activeDifficulty === d.id, [d.id]: true }"
        @click="activeDifficulty = activeDifficulty === d.id ? 'all' : d.id"
      >
        {{ d.label }}
      </button>
    </div>

    <!-- Scenario grid -->
    <div class="scenarios">
      <div
        v-for="s in filteredScenarios"
        :key="s.id"
        class="scenario-card"
        @click="$router.push(`/chat/${s.id}`)"
      >
        <div class="card-header">
          <span class="icon">{{ s.icon }}</span>
          <span class="diff-badge" :class="s.difficulty">{{ s.difficulty }}</span>
        </div>
        <h3>{{ s.name }}</h3>
        <p>{{ s.description }}</p>
        <div v-if="s.objective" class="objective">
          🎯 {{ s.objective }}
        </div>
      </div>
    </div>

    <!-- Level test CTA (if not assessed) -->
    <div v-if="!hasLevel" class="level-cta">
      <p>🎓 还不知道你的英语水平？</p>
      <button @click="$router.push('/assessment')" class="cta-btn">
        做个快速评估（3分钟）
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { CONFIG } from '../../shared/config'

const categories = CONFIG.CATEGORIES
const activeCategory = ref('all')
const activeDifficulty = ref('all')
const scenarios = ref(CONFIG.SCENARIOS)
const hasLevel = ref(false)

const difficulties = [
  { id: 'beginner', label: '⭐ 入门' },
  { id: 'intermediate', label: '⭐⭐ 中级' },
  { id: 'advanced', label: '⭐⭐⭐ 高级' },
]

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
  // Try loading scenarios from API
  try {
    const res = await fetch('/api/scenarios')
    if (res.ok) {
      scenarios.value = await res.json()
    }
  } catch { /* use fallback from config */ }

  // Check if user has been assessed
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
.home { text-align: center; }

h1 {
  font-size: 2rem;
  color: #1f4e79;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #666;
  margin-bottom: 1.5rem;
}

.category-tabs {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.tab-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #e0e0e0;
  border-radius: 20px;
  background: white;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}
.tab-btn.active {
  background: #1f4e79;
  color: white;
  border-color: #1f4e79;
}
.tab-btn:hover:not(.active) {
  border-color: #1f4e79;
  color: #1f4e79;
}

.difficulty-filter {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}
.filter-label { color: #666; font-size: 0.85rem; }
.diff-btn {
  padding: 0.3rem 0.8rem;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  background: white;
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.2s;
}
.diff-btn.active.beginner { background: #e8f5e9; border-color: #4caf50; color: #2e7d32; }
.diff-btn.active.intermediate { background: #fff3e0; border-color: #ff9800; color: #e65100; }
.diff-btn.active.advanced { background: #fce4ec; border-color: #e91e63; color: #880e4f; }

.scenarios {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 1.5rem;
  text-align: left;
}

.scenario-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.scenario-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(31,78,121,0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.8rem;
}

.icon { font-size: 2rem; }

.diff-badge {
  font-size: 0.7rem;
  padding: 0.2rem 0.6rem;
  border-radius: 8px;
  text-transform: uppercase;
  font-weight: 600;
}
.diff-badge.beginner { background: #e8f5e9; color: #2e7d32; }
.diff-badge.intermediate { background: #fff3e0; color: #e65100; }
.diff-badge.advanced { background: #fce4ec; color: #880e4f; }

.scenario-card h3 { margin-bottom: 0.4rem; color: #1f4e79; }
.scenario-card p { font-size: 0.9rem; color: #666; margin-bottom: 0.5rem; }

.objective {
  font-size: 0.8rem;
  color: #1f4e79;
  padding: 0.4rem 0.6rem;
  background: #f0f7ff;
  border-radius: 6px;
  margin-top: 0.5rem;
}

.level-cta {
  margin-top: 2rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, #f0f7ff, #e8f5e9);
  border-radius: 12px;
}
.level-cta p { margin-bottom: 0.8rem; color: #333; }
.cta-btn {
  padding: 0.7rem 1.5rem;
  background: #1f4e79;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.95rem;
  transition: background 0.2s;
}
.cta-btn:hover { background: #2a6399; }
</style>
