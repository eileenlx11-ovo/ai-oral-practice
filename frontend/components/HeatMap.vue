<template>
  <div class="heatmap">
    <div class="heatmap-scroll">
      <div class="heatmap-grid">
        <div
          v-for="(day, i) in days"
          :key="i"
          class="heatmap-cell"
          :class="`level-${day.level}`"
          :style="{ animationDelay: `${i * 3}ms` }"
          :title="day.date ? `${day.date}: ${day.count} ${t('dashboard.timesPracticed', '次练习')}` : ''"
        ></div>
      </div>
    </div>
    <div class="heatmap-footer">
      <span class="heatmap-caption">{{ t('dashboard.heatmapCaption', '每格代表一天，颜色越深当天练习越多') }}</span>
      <div class="heatmap-legend">
        <span>{{ t('dashboard.less', '少') }}</span>
        <span class="heatmap-cell level-0"></span>
        <span class="heatmap-cell level-1"></span>
        <span class="heatmap-cell level-2"></span>
        <span class="heatmap-cell level-3"></span>
        <span class="heatmap-cell level-4"></span>
        <span>{{ t('dashboard.more', '多') }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from '../composables/useI18n'

const { t } = useI18n()

const props = defineProps({
  // { "YYYY-MM-DD": count }
  dailyCounts: { type: Object, default: () => ({}) },
  weeks: { type: Number, default: 12 },
})

// Build a grid covering the last N weeks ending today, one cell per day.
const days = computed(() => {
  const total = props.weeks * 7
  const today = new Date()
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

// Level thresholds (count → intensity). Documented in the caption + tooltip.
function levelFor(count) {
  if (count <= 0) return 0
  if (count === 1) return 1
  if (count === 2) return 2
  if (count <= 4) return 3
  return 4
}
</script>

<style scoped>
/* Horizontal scroll guard for narrow screens; grid keeps fixed cell size so
   the heatmap never stretches to fill (and dominate) the card width. */
.heatmap-scroll {
  overflow-x: auto;
  overscroll-behavior-x: contain;
  padding-bottom: var(--space-1);
}

.heatmap-grid {
  display: grid;
  grid-template-rows: repeat(7, 13px);
  grid-auto-flow: column;
  grid-auto-columns: 13px;
  gap: 3px;
  justify-content: start;
  width: max-content;
  margin-bottom: var(--space-3);
}

.heatmap-cell {
  width: 13px;
  height: 13px;
  border-radius: 3px;
  background: var(--hm-level-0);
}
.heatmap-scroll .heatmap-cell {
  animation: fade-in 300ms ease both;
}

/* Soft emerald scale — calmer and more "premium" than the old hard blue ramp */
.heatmap {
  --hm-level-0: var(--color-border-light);
  --hm-level-1: #c7ecd5;
  --hm-level-2: #86d3a6;
  --hm-level-3: #46b377;
  --hm-level-4: #2f8d5b;
}
[data-theme="dark"] .heatmap {
  --hm-level-0: rgba(148, 163, 184, 0.12);
  --hm-level-1: rgba(52, 211, 153, 0.28);
  --hm-level-2: rgba(52, 211, 153, 0.5);
  --hm-level-3: rgba(52, 211, 153, 0.72);
  --hm-level-4: #34d399;
}

.heatmap-cell.level-0 { background: var(--hm-level-0); }
.heatmap-cell.level-1 { background: var(--hm-level-1); }
.heatmap-cell.level-2 { background: var(--hm-level-2); }
.heatmap-cell.level-3 { background: var(--hm-level-3); }
.heatmap-cell.level-4 { background: var(--hm-level-4); }

.heatmap-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  flex-wrap: wrap;
}
.heatmap-caption {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

.heatmap-legend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}
.heatmap-legend .heatmap-cell {
  width: 11px;
  height: 11px;
  animation: none;
}

@media (prefers-reduced-motion: reduce) {
  .heatmap-scroll .heatmap-cell { animation: none; }
}
</style>
