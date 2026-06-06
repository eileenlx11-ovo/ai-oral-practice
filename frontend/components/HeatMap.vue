<template>
  <div class="heatmap">
    <div class="heatmap-grid">
      <div
        v-for="(day, i) in days"
        :key="i"
        class="heatmap-cell"
        :class="`level-${day.level}`"
        :style="{ animationDelay: `${i * 4}ms` }"
        :title="day.date ? `${day.date}: ${day.count} 次练习` : ''"
      ></div>
    </div>
    <div class="heatmap-legend">
      <span>少</span>
      <span class="heatmap-cell level-0"></span>
      <span class="heatmap-cell level-1"></span>
      <span class="heatmap-cell level-2"></span>
      <span class="heatmap-cell level-3"></span>
      <span class="heatmap-cell level-4"></span>
      <span>多</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  // { "YYYY-MM-DD": count }
  dailyCounts: { type: Object, default: () => ({}) },
  weeks: { type: Number, default: 12 },
})

// Build a grid covering the last N weeks ending today, one cell per day.
const days = computed(() => {
  const total = props.weeks * 7
  const today = new Date()
  // Align end to the most recent Saturday so weeks render as clean columns
  const out = []
  for (let i = total - 1; i >= 0; i--) {
    const d = new Date(today)
    d.setDate(today.getDate() - i)
    const key = d.toISOString().slice(0, 10)
    const count = props.dailyCounts[key] || 0
    out.push({ date: key, count, level: levelFor(count) })
  }
  return out
})

function levelFor(count) {
  if (count <= 0) return 0
  if (count === 1) return 1
  if (count === 2) return 2
  if (count <= 4) return 3
  return 4
}
</script>

<style scoped>
.heatmap-grid {
  display: grid;
  grid-template-rows: repeat(7, 1fr);
  grid-auto-flow: column;
  grid-auto-columns: 1fr;
  gap: 3px;
  margin-bottom: var(--space-3);
}

.heatmap-cell {
  width: 100%;
  aspect-ratio: 1;
  min-width: 10px;
  border-radius: 2px;
  background: var(--color-border-light);
  animation: fade-in 300ms ease both;
}

.heatmap-cell.level-0 { background: var(--color-border-light); }
.heatmap-cell.level-1 { background: var(--color-primary-100); }
.heatmap-cell.level-2 { background: var(--color-primary-200); }
.heatmap-cell.level-3 { background: var(--color-primary); }
.heatmap-cell.level-4 { background: var(--color-primary-dark); }

.heatmap-legend {
  display: flex;
  align-items: center;
  gap: 4px;
  justify-content: flex-end;
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}
.heatmap-legend .heatmap-cell {
  width: 12px;
  height: 12px;
  aspect-ratio: unset;
  animation: none;
}

@media (prefers-reduced-motion: reduce) {
  .heatmap-cell { animation: none; }
}
</style>
