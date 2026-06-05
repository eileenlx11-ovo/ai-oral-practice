<template>
  <div class="home">
    <h1>选择练习场景</h1>
    <p class="subtitle">选择一个场景，开始与 AI 进行英语口语对话练习</p>

    <div class="scenarios">
      <div
        v-for="s in scenarios"
        :key="s.id"
        class="scenario-card"
        @click="$router.push(`/chat/${s.id}`)"
      >
        <span class="icon">{{ s.icon }}</span>
        <h3>{{ s.name }}</h3>
        <p>{{ s.description }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { CONFIG } from '../../shared/config'

const scenarios = CONFIG.SCENARIOS
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
  margin-bottom: 2rem;
}

.scenarios {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1.5rem;
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

.icon { font-size: 2.5rem; display: block; margin-bottom: 0.8rem; }
.scenario-card h3 { margin-bottom: 0.5rem; color: #1f4e79; }
.scenario-card p { font-size: 0.9rem; color: #666; }
</style>
