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
const scenarios = [
  { id: 'interview', icon: '💼', name: 'Job Interview', description: '模拟英语面试场景，练习自我介绍和回答面试问题' },
  { id: 'restaurant', icon: '🍽️', name: 'Restaurant', description: '模拟餐厅点餐，练习日常用餐对话' },
  { id: 'meeting', icon: '📋', name: 'Business Meeting', description: '模拟商务会议，练习表达观点和讨论' },
  { id: 'travel', icon: '✈️', name: 'Travel', description: '模拟旅行场景，练习问路、住酒店、买票等' },
  { id: 'smalltalk', icon: '💬', name: 'Small Talk', description: '日常闲聊，练习自然的社交英语' },
]
</script>

<style scoped>
.home {
  text-align: center;
}

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

.icon {
  font-size: 2.5rem;
  display: block;
  margin-bottom: 0.8rem;
}

.scenario-card h3 {
  margin-bottom: 0.5rem;
  color: #1f4e79;
}

.scenario-card p {
  font-size: 0.9rem;
  color: #666;
}
</style>
