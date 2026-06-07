<template>
  <div class="achievements-page">
    <h1>🏆 成就与打卡</h1>

    <!-- Streak -->
    <div class="streak-section">
      <div class="streak-card">
        <span class="streak-fire">🔥</span>
        <span class="streak-number">{{ streak }}</span>
        <span class="streak-label">天连续练习</span>
      </div>
    </div>

    <!-- Calendar Heatmap -->
    <div class="calendar-section">
      <h2>练习日历</h2>
      <div class="calendar-grid">
        <div
          v-for="day in calendar"
          :key="day.date"
          class="calendar-cell"
          :class="{ checked: day.checked, today: isToday(day.date) }"
          :title="day.date"
        ></div>
      </div>
      <div class="calendar-legend">
        <span>近 90 天</span>
        <span class="legend-item"><span class="dot unchecked"></span> 未练习</span>
        <span class="legend-item"><span class="dot checked"></span> 已练习</span>
      </div>
    </div>

    <!-- Badges -->
    <div class="badges-section">
      <h2>成就徽章</h2>
      <div class="badges-grid">
        <div v-for="a in achievements" :key="a.id" class="badge-card" :class="{ unlocked: a.unlocked, 'is-new': a.is_new }">
          <span class="badge-icon">{{ a.icon }}</span>
          <strong>{{ a.name }}</strong>
          <span class="badge-desc">{{ a.description }}</span>
          <div class="badge-progress" v-if="!a.unlocked">
            <div class="progress-bar"><div class="progress-fill" :style="{ width: (a.progress / a.threshold * 100) + '%' }"></div></div>
            <span class="progress-text">{{ a.progress }}/{{ a.threshold }}</span>
          </div>
          <span v-else class="badge-check">✓</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { CONFIG } from '../../shared/config'

const streak = ref(0)
const calendar = ref([])
const achievements = ref([])

function isToday(dateStr) { return dateStr === new Date().toISOString().slice(0, 10) }

onMounted(async () => {
  const base = CONFIG.API.BASE_URL
  try {
    const [sRes, aRes] = await Promise.all([
      fetch(`${base}/api/streak`),
      fetch(`${base}/api/achievements`),
    ])
    if (sRes.ok) { const d = await sRes.json(); streak.value = d.streak; calendar.value = d.calendar }
    if (aRes.ok) { const d = await aRes.json(); achievements.value = d.achievements }
  } catch (e) { console.error(e) }
})
</script>

<style scoped>
.achievements-page { max-width: 700px; margin: 0 auto; padding: 2rem 1.5rem; }
.streak-section { display: flex; justify-content: center; margin-bottom: 2rem; }
.streak-card { display: flex; align-items: center; gap: 0.5rem; padding: 1rem 2rem; background: linear-gradient(135deg, #fff3e0, #ffe0b2); border-radius: 16px; }
.streak-fire { font-size: 2rem; }
.streak-number { font-size: 2.5rem; font-weight: 700; color: #e65100; }
.streak-label { font-size: 1rem; color: #bf360c; }

.calendar-section { margin-bottom: 2rem; }
.calendar-section h2 { margin-bottom: 0.75rem; }
.calendar-grid { display: grid; grid-template-columns: repeat(13, 1fr); gap: 3px; }
.calendar-cell { aspect-ratio: 1; border-radius: 3px; background: #eee; }
.calendar-cell.checked { background: #4caf50; }
.calendar-cell.today { outline: 2px solid #ff9800; outline-offset: 1px; }
.calendar-legend { display: flex; align-items: center; gap: 1rem; margin-top: 0.5rem; font-size: 0.8rem; color: #666; }
.legend-item { display: flex; align-items: center; gap: 0.25rem; }
.dot { width: 10px; height: 10px; border-radius: 2px; display: inline-block; }
.dot.unchecked { background: #eee; }
.dot.checked { background: #4caf50; }

.badges-section h2 { margin-bottom: 1rem; }
.badges-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 1rem; }
.badge-card { display: flex; flex-direction: column; align-items: center; text-align: center; padding: 1.25rem 0.75rem; border-radius: 12px; border: 1.5px solid #e0e0e0; background: #f9f9f9; position: relative; opacity: 0.5; filter: grayscale(0.8); transition: all 0.3s; }
.badge-card.unlocked { opacity: 1; filter: none; background: #fff; border-color: #4caf50; box-shadow: 0 2px 8px rgba(76,175,80,0.15); }
.badge-card.is-new { animation: pulse 0.6s ease-in-out; border-color: #ff9800; }
@keyframes pulse { 0%,100%{transform:scale(1)} 50%{transform:scale(1.05)} }
.badge-icon { font-size: 2rem; margin-bottom: 0.4rem; }
.badge-desc { font-size: 0.75rem; color: #666; margin-top: 0.25rem; }
.badge-progress { width: 100%; margin-top: 0.5rem; }
.progress-bar { height: 4px; background: #e0e0e0; border-radius: 2px; overflow: hidden; }
.progress-fill { height: 100%; background: #4a90d9; border-radius: 2px; }
.progress-text { font-size: 0.7rem; color: #999; }
.badge-check { position: absolute; top: 8px; right: 10px; color: #4caf50; font-weight: bold; }
</style>
