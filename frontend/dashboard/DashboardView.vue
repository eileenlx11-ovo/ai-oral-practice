<template>
  <div class="dashboard">
    <Toast :message="toast.message" :type="toast.type" @close="toast.message = ''" />
    <h1>📊 {{ t('dashboard.title') }}</h1>

    <!-- Login prompt for guests -->
    <div v-if="!isAuthenticated" class="login-prompt">
      <span>💡 登录后可持久保存练习进度</span>
      <router-link to="/login" class="prompt-link">去登录 →</router-link>
    </div>

    <!-- Daily plan: AI study coach -->
    <div v-if="progress?.daily_plan" class="daily-plan">
      <div class="plan-header">
        <span class="plan-icon">🧭</span>
        <h2>{{ t('dashboard.todayPlan', '今日计划') }}</h2>
        <span class="plan-target">
          {{ progress.daily_plan.target_turns }} {{ t('dashboard.turns') }} · {{ progress.daily_plan.target_minutes }} min
        </span>
      </div>
      <ul class="plan-tasks">
        <li v-for="(task, i) in progress.daily_plan.tasks" :key="i">
          <span class="plan-check">○</span> {{ task }}
        </li>
      </ul>
      <button
        v-if="progress.daily_plan.recommended_scenario"
        class="plan-start-btn"
        @click="$router.push(`/chat/${progress.daily_plan.recommended_scenario}`)"
      >
        {{ getScenarioIcon(progress.daily_plan.recommended_scenario) }}
        {{ t('dashboard.startRecommended', '开始推荐练习') }} →
      </button>
    </div>

    <!-- Summary Cards -->
    <div class="summary-cards" v-if="progress">
      <div class="card">
        <span class="card-value">{{ progress.total_sessions }}</span>
        <span class="card-label">{{ t('dashboard.sessions') }}</span>
      </div>
      <div class="card">
        <span class="card-value">{{ progress.total_turns }}</span>
        <span class="card-label">{{ t('dashboard.turnsSpoken') }}</span>
      </div>
      <div class="card">
        <span class="card-value">{{ progress.total_corrections }}</span>
        <span class="card-label">{{ t('dashboard.corrections') }}</span>
      </div>
      <div class="card highlight">
        <span class="card-value">{{ formatScore(progress.avg_pronunciation) }}</span>
        <span class="card-label">{{ t('dashboard.avgPronunciation') }}</span>
      </div>
    </div>

    <!-- Streak banner -->
    <div v-if="progress?.streak" class="streak-banner">
      <div class="streak-item">
        <span class="streak-flame">🔥</span>
        <span class="streak-num">{{ progress.streak.current }}</span>
        <span class="streak-label">{{ t('dashboard.streakCurrent', '当前连续天数') }}</span>
      </div>
      <div class="streak-divider"></div>
      <div class="streak-item">
        <span class="streak-flame">🏆</span>
        <span class="streak-num">{{ progress.streak.longest }}</span>
        <span class="streak-label">{{ t('dashboard.streakLongest', '最长连续天数') }}</span>
      </div>
    </div>

    <!-- Contribution heatmap -->
    <div v-if="progress?.streak?.daily_counts" class="chart-section">
      <h2>{{ t('dashboard.activity', '练习活跃度') }}</h2>
      <HeatMap :daily-counts="progress.streak.daily_counts" :weeks="12" />
    </div>

    <!-- Score Trend Chart -->
    <div class="chart-section" v-if="hasScoreData">
      <h2>{{ t('dashboard.scoreTrends') }}</h2>
      <div class="chart-container">
        <Line :data="trendChartData" :options="trendChartOptions" />
      </div>
    </div>

    <!-- Skill radar + scenario distribution side by side -->
    <div class="dual-charts" v-if="hasRadarData || hasDistribution">
      <div class="chart-section half" v-if="hasRadarData">
        <h2>{{ t('dashboard.skillRadar', '能力雷达') }}</h2>
        <div class="chart-container small">
          <Radar :data="radarChartData" :options="radarChartOptions" />
        </div>
      </div>
      <div class="chart-section half" v-if="hasDistribution">
        <h2>{{ t('dashboard.scenarioDist', '场景分布') }}</h2>
        <div class="chart-container small">
          <Doughnut :data="distChartData" :options="distChartOptions" />
        </div>
      </div>
    </div>

    <!-- Weakness analysis -->
    <div v-if="progress?.weakness" class="weakness-section">
      <h2>{{ t('dashboard.weakness', '弱项分析') }}</h2>
      <div class="weakness-grid">
        <div class="weakness-card" v-if="progress.weakness.low_dimension">
          <span class="wk-icon">🎯</span>
          <span class="wk-title">{{ t('dashboard.weakestDimension', '最需提升') }}</span>
          <span class="wk-value">{{ dimensionLabel(progress.weakness.low_dimension) }}</span>
        </div>
        <div class="weakness-card" v-if="progress.weakness.weak_scenarios?.length">
          <span class="wk-icon">📉</span>
          <span class="wk-title">{{ t('dashboard.weakScenarios', '薄弱场景') }}</span>
          <ul class="wk-list">
            <li v-for="s in progress.weakness.weak_scenarios" :key="s.scenario">
              {{ getScenarioIcon(s.scenario) }} {{ s.scenario }}
              <span class="wk-score">{{ s.avg_score?.toFixed(0) }}</span>
            </li>
          </ul>
        </div>
        <!-- Personalized grammar coaching (LLM analysis instead of a bare list) -->
        <div class="weakness-card wide grammar-card" v-if="progress.weakness.common_grammar_errors?.length">
          <div class="grammar-head">
            <span class="wk-icon">📝</span>
            <span class="wk-title">{{ t('dashboard.grammarCoach', '语法分析与建议') }}</span>
            <button
              v-if="!grammarAnalysis && !grammarLoading"
              class="grammar-btn"
              @click="loadGrammarAnalysis"
            >{{ t('dashboard.generateAnalysis', '生成针对性分析') }}</button>
          </div>

          <!-- Compact error tags (kept as supporting evidence) -->
          <div class="grammar-tags">
            <span class="grammar-tag" v-for="e in progress.weakness.common_grammar_errors.slice(0, 6)" :key="e.pattern">
              {{ e.pattern }}<i>×{{ e.count }}</i>
            </span>
          </div>

          <div v-if="grammarLoading" class="grammar-loading">
            <span class="mini-spinner"></span> {{ t('dashboard.analyzing', '正在分析你的高频错误…') }}
          </div>
          <template v-else-if="grammarAnalysis">
            <p class="grammar-analysis">{{ grammarAnalysis.analysis }}</p>
            <ul class="grammar-tips" v-if="grammarAnalysis.tips?.length">
              <li v-for="(tip, i) in grammarAnalysis.tips" :key="i">{{ tip }}</li>
            </ul>
          </template>
          <p v-else class="grammar-hint">{{ t('dashboard.grammarHint', '点击上方按钮，让 AI 教练分析这些错误背后的规律并给出改进建议') }}</p>
        </div>
      </div>
    </div>

    <!-- Learning Analytics -->
    <div class="analytics-section" v-if="analytics">
      <h2>{{ t('dashboard.learningAnalytics', '学习分析') }}</h2>

      <!-- Time Range Picker -->
      <div class="time-range-picker">
        <button
          v-for="range in timeRanges"
          :key="range.value"
          :class="['range-btn', { active: selectedRange === range.value }]"
          @click="selectedRange = range.value"
        >
          {{ range.label }}
        </button>
      </div>

      <!-- Vocabulary Trend Chart -->
      <div class="analytics-card" v-if="analytics.vocabulary_trend && analytics.vocabulary_trend.length">
        <h3>{{ t('dashboard.vocabularyGrowth', '词汇量增长') }}</h3>
        <div class="chart-container">
          <Line :data="vocabChartData" :options="vocabChartOptions" />
        </div>
      </div>

      <!-- Error Distribution (HTML/CSS bars) -->
      <div class="analytics-card" v-if="analytics.error_distribution && Object.keys(analytics.error_distribution).length">
        <h3>{{ t('dashboard.errorDistribution', '错误类型分布') }}</h3>
        <div class="bar-chart-horizontal">
          <div
            v-for="(count, category) in analytics.error_distribution"
            :key="category"
            class="bar-row"
          >
            <span class="bar-label">{{ formatCategory(category) }}</span>
            <div class="bar-track">
              <div
                class="bar-fill"
                :style="{ width: getBarWidth(count, analytics.error_distribution) }"
              ></div>
            </div>
            <span class="bar-value">{{ count }}</span>
          </div>
        </div>
      </div>

      <!-- Scenario Coverage (HTML/CSS bars) -->
      <div class="analytics-card" v-if="analytics.scenario_coverage && Object.keys(analytics.scenario_coverage).length">
        <h3>{{ t('dashboard.scenarioCoverage', '场景覆盖') }}</h3>
        <div class="bar-chart-horizontal">
          <div
            v-for="(count, scenario) in analytics.scenario_coverage"
            :key="scenario"
            class="bar-row"
          >
            <span class="bar-label">{{ scenario }}</span>
            <div class="bar-track">
              <div
                class="bar-fill scenario-bar"
                :style="{ width: getBarWidth(count, analytics.scenario_coverage) }"
              ></div>
            </div>
            <span class="bar-value">{{ count }}</span>
          </div>
        </div>
      </div>

      <!-- Summary Stats -->
      <div class="analytics-card summary-stats" v-if="analytics.summary">
        <div class="stat-item">
          <span class="stat-value">{{ analytics.summary.unique_words }}</span>
          <span class="stat-label">{{ t('dashboard.uniqueWords', '独立词汇数') }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ analytics.summary.total_words_spoken }}</span>
          <span class="stat-label">{{ t('dashboard.totalWordsSpoken', '累计开口词数') }}</span>
        </div>
      </div>
    </div>

    <!-- Session History -->
    <div class="history-section">
      <h2>{{ t('dashboard.practiceHistory') }}</h2>
      <div v-if="sessions.length === 0" class="empty-state">
        <p>{{ t('dashboard.empty') }}</p>
      </div>
      <div v-else class="session-list">
        <div
          v-for="s in sessions"
          :key="s.session_id"
          class="session-item"
          @click="viewSession(s.session_id)"
        >
          <div class="session-meta">
            <span class="scenario-tag">{{ getScenarioIcon(s.scenario) }} {{ s.scenario }}</span>
            <span class="session-date">{{ formatDate(s.started_at) }}</span>
          </div>
          <div class="session-stats">
            <span>{{ s.turns }} {{ t('dashboard.turns') }}</span>
            <span v-if="s.avg_pronunciation" class="score-badge">
              🎯 {{ s.avg_pronunciation.toFixed(0) }}
            </span>
            <span v-if="s.avg_fluency" class="score-badge">
              🗣️ {{ s.avg_fluency.toFixed(0) }}
            </span>
            <button class="playback-btn" @click.stop="$router.push('/playback/' + s.session_id)">{{ t('dashboard.playback', '回放') }}</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Session Detail Modal -->
    <div v-if="selectedSummary" class="modal-overlay" @click.self="selectedSummary = null">
      <div class="modal">
        <h3>{{ t('dashboard.sessionReport') }}</h3>
        <div class="report-grid">
          <div class="report-item">
            <label>{{ t('dashboard.scenario') }}</label>
            <span>{{ selectedSummary.scenario }}</span>
          </div>
          <div class="report-item">
            <label>{{ t('dashboard.duration') }}</label>
            <span>{{ selectedSummary.total_turns }} {{ t('dashboard.turns') }}</span>
          </div>
          <div class="report-item">
            <label>{{ t('dashboard.pronunciation') }}</label>
            <span>{{ formatScore(selectedSummary.avg_pronunciation) }}</span>
          </div>
          <div class="report-item">
            <label>{{ t('dashboard.fluency') }}</label>
            <span>{{ formatScore(selectedSummary.avg_fluency) }}</span>
          </div>
          <div class="report-item">
            <label>{{ t('dashboard.accuracy') }}</label>
            <span>{{ formatScore(selectedSummary.avg_accuracy) }}</span>
          </div>
          <div class="report-item">
            <label>{{ t('dashboard.corrections') }}</label>
            <span>{{ selectedSummary.total_corrections }}</span>
          </div>
        </div>

        <div v-if="selectedSummary.common_errors && selectedSummary.common_errors.length" class="common-errors">
          <h4>{{ t('dashboard.commonErrorPatterns') }}</h4>
          <ul>
            <li v-for="e in selectedSummary.common_errors" :key="e.pattern">
              {{ e.pattern }} <span class="error-count">(×{{ e.count }})</span>
            </li>
          </ul>
        </div>

        <button class="close-btn" @click="selectedSummary = null">{{ t('dashboard.close') }}</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { isAuthenticated } from '../composables/useAuth'
import { Line, Radar, Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  RadialLinearScale,
  ArcElement,
  Filler,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { CONFIG } from '../../shared/config'
import { useI18n } from '../composables/useI18n'
import { getScene } from '../styles/scenes'
import Toast from '../components/Toast.vue'
import HeatMap from '../components/HeatMap.vue'

ChartJS.register(
  CategoryScale, LinearScale, PointElement, LineElement,
  RadialLinearScale, ArcElement, Filler, Title, Tooltip, Legend
)

const { t } = useI18n()
const API = CONFIG.API.BASE_URL
const progress = ref(null)
const sessions = ref([])
const selectedSummary = ref(null)
const toast = reactive({ message: '', type: 'info' })
const analytics = ref(null)
const selectedRange = ref(30)

const timeRanges = [
  { label: '7天', value: 7 },
  { label: '30天', value: 30 },
  { label: '全部', value: 0 },
]

// Personalized grammar coaching (lazy — only fetched when the user asks)
const grammarAnalysis = ref(null)
const grammarLoading = ref(false)

async function loadGrammarAnalysis() {
  grammarLoading.value = true
  try {
    const res = await fetch(`${API}/api/progress/grammar-analysis`, { method: 'POST' })
    if (res.ok) {
      grammarAnalysis.value = await res.json()
    } else {
      showToast(t('dashboard.analysisFailed', '分析生成失败，请稍后再试'))
    }
  } catch {
    showToast(t('dashboard.networkFailed'))
  } finally {
    grammarLoading.value = false
  }
}

function showToast(message, type = 'error') {
  toast.message = message
  toast.type = type
}

const hasScoreData = computed(() => {
  return progress.value?.score_history?.some((s) => s.avg_pronunciation !== null)
})

const trendChartData = computed(() => {
  if (!progress.value?.score_history) return { labels: [], datasets: [] }

  const history = progress.value.score_history.filter((s) => s.avg_pronunciation !== null)
  const labels = history.map((s) => s.date)

  return {
    labels,
    datasets: [
      {
        label: 'Pronunciation',
        data: history.map((s) => s.avg_pronunciation),
        borderColor: '#1f4e79',
        backgroundColor: 'rgba(31, 78, 121, 0.1)',
        tension: 0.3,
      },
      {
        label: 'Fluency',
        data: history.map((s) => s.avg_fluency),
        borderColor: '#2ecc71',
        backgroundColor: 'rgba(46, 204, 113, 0.1)',
        tension: 0.3,
      },
      {
        label: 'Accuracy',
        data: history.map((s) => s.avg_accuracy),
        borderColor: '#e67e22',
        backgroundColor: 'rgba(230, 126, 34, 0.1)',
        tension: 0.3,
      },
    ],
  }
})

const trendChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    y: { min: 0, max: 100, title: { display: true, text: 'Score' } },
    x: { title: { display: true, text: 'Session Date' } },
  },
  plugins: {
    legend: { position: 'top' },
  },
}

// --- Skill radar (3 dimensions overall) ---
const hasRadarData = computed(() =>
  progress.value?.avg_pronunciation != null ||
  progress.value?.avg_fluency != null ||
  progress.value?.avg_accuracy != null
)

const radarChartData = computed(() => ({
  labels: [
    t('dashboard.pronunciation', 'Pronunciation'),
    t('dashboard.fluency', 'Fluency'),
    t('dashboard.accuracy', 'Accuracy'),
  ],
  datasets: [{
    label: t('dashboard.avgScore', '平均分'),
    data: [
      progress.value?.avg_pronunciation || 0,
      progress.value?.avg_fluency || 0,
      progress.value?.avg_accuracy || 0,
    ],
    borderColor: '#2563eb',
    backgroundColor: 'rgba(37, 99, 235, 0.15)',
    pointBackgroundColor: '#2563eb',
  }],
}))

const radarChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: { r: { min: 0, max: 100, ticks: { stepSize: 25 } } },
  plugins: { legend: { display: false } },
}

// --- Scenario distribution (doughnut) ---
const hasDistribution = computed(() =>
  progress.value?.scenario_distribution &&
  Object.keys(progress.value.scenario_distribution).length > 0
)

const distChartData = computed(() => {
  const dist = progress.value?.scenario_distribution || {}
  const entries = Object.entries(dist).sort((a, b) => b[1] - a[1])
  return {
    labels: entries.map(([k]) => k),
    datasets: [{
      data: entries.map(([, v]) => v),
      backgroundColor: entries.map(([k]) => getScene(k).accent),
      borderWidth: 1,
    }],
  }
})

const distChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { position: 'right', labels: { boxWidth: 12, font: { size: 11 } } } },
}

function dimensionLabel(dim) {
  const map = {
    pronunciation: t('dashboard.pronunciation', '发音'),
    fluency: t('dashboard.fluency', '流利度'),
    accuracy: t('dashboard.accuracy', '准确度'),
  }
  return map[dim] || dim
}

const vocabChartData = computed(() => {
  if (!analytics.value?.vocabulary_trend?.length) return { labels: [], datasets: [] }
  const trend = analytics.value.vocabulary_trend
  return {
    labels: trend.map((t) => t.week),
    datasets: [
      {
        label: 'Cumulative Unique Words',
        data: trend.map((t) => t.unique_words),
        borderColor: '#8e44ad',
        backgroundColor: 'rgba(142, 68, 173, 0.1)',
        tension: 0.3,
        fill: true,
      },
    ],
  }
})

const vocabChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    y: { min: 0, title: { display: true, text: 'Words' } },
    x: { title: { display: true, text: 'Week' } },
  },
  plugins: {
    legend: { position: 'top' },
  },
}

function getBarWidth(count, distribution) {
  const max = Math.max(...Object.values(distribution), 1)
  return `${Math.round((count / max) * 100)}%`
}

function formatCategory(category) {
  const labels = {
    grammar_tense: t('dashboard.catTense', '时态'),
    grammar_articles: t('dashboard.catArticles', '冠词'),
    grammar_prepositions: t('dashboard.catPrepositions', '介词'),
    vocabulary: t('dashboard.catVocabulary', '词汇'),
    pronunciation: t('dashboard.catPronunciation', '发音'),
    other: t('dashboard.catOther', '其他'),
  }
  return labels[category] || category
}

async function loadAnalytics(days) {
  try {
    const res = await fetch(`${API}${CONFIG.API.ANALYTICS}?days=${days}`)
    if (res.ok) {
      analytics.value = await res.json()
    }
  } catch {
    // Analytics load failure is non-critical
  }
}

// Watch selectedRange changes
watch(selectedRange, (newVal) => {
  loadAnalytics(newVal)
})

function formatScore(val) {
  return val != null ? val.toFixed(1) : '—'
}

function formatDate(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function getScenarioIcon(id) {
  const icons = { interview: '💼', restaurant: '🍽️', meeting: '📋', travel: '✈️', smalltalk: '💬' }
  return icons[id] || '🎙️'
}

async function viewSession(sessionId) {
  try {
    const res = await fetch(`${API}/api/sessions/${sessionId}/summary`)
    if (!res.ok) {
      showToast(`${t('dashboard.loadSessionFailed')} (${res.status})`)
      return
    }
    selectedSummary.value = await res.json()
  } catch {
    showToast(t('dashboard.networkFailed'))
  }
}

onMounted(async () => {
  try {
    const [progRes, sessRes] = await Promise.all([
      fetch(`${API}/api/progress`),
      fetch(`${API}/api/sessions`),
    ])
    if (!progRes.ok || !sessRes.ok) {
      showToast(t('dashboard.loadDataFailed'))
      return
    }
    progress.value = await progRes.json()
    sessions.value = await sessRes.json()
  } catch {
    showToast(t('dashboard.serverFailed'))
  }

  // Load analytics with default range
  loadAnalytics(selectedRange.value)
})
</script>

<style scoped>
.dashboard {
  max-width: 900px;
  margin: 0 auto;
  animation: fade-in var(--transition-base) both;
}

.login-prompt {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-3) var(--space-4);
  background: var(--color-primary-50);
  border: 1px solid var(--color-primary-100);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-4);
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
}

.prompt-link {
  font-weight: 600;
  color: var(--color-primary);
  white-space: nowrap;
}

h1 {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: var(--space-6);
}

h2 {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--color-text);
  margin-bottom: var(--space-4);
}

/* Summary cards */
.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: var(--space-4);
  margin-bottom: var(--space-8);
}

.card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  text-align: center;
  border: 1px solid var(--color-border);
  transition: all var(--transition-fast);
  animation: slide-up 400ms ease both;
}
.summary-cards .card:nth-child(1) { animation-delay: 0ms; }
.summary-cards .card:nth-child(2) { animation-delay: 60ms; }
.summary-cards .card:nth-child(3) { animation-delay: 120ms; }
.summary-cards .card:nth-child(4) { animation-delay: 180ms; }

@media (prefers-reduced-motion: reduce) {
  .card { animation: none; }
}

.card:hover { box-shadow: var(--shadow-md); transform: translateY(-2px); }

.card.highlight {
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  color: white;
  border-color: transparent;
}

.card-value {
  display: block;
  font-size: var(--text-3xl);
  font-weight: 800;
  margin-bottom: var(--space-1);
}

.card-label {
  font-size: var(--text-sm);
  opacity: 0.75;
  font-weight: 500;
}

/* Chart */
.chart-section {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  margin-bottom: var(--space-8);
  border: 1px solid var(--color-border);
}

.chart-container { height: 280px; }
.chart-container.small { height: 240px; }

/* Daily plan card */
.daily-plan {
  padding: var(--space-5) var(--space-6);
  margin-bottom: var(--space-6);
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  color: white;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  animation: slide-up 400ms ease both;
}
.plan-header { display: flex; align-items: center; gap: var(--space-2); margin-bottom: var(--space-3); }
.plan-header h2 { font-size: var(--text-lg); font-weight: 700; color: white; }
.plan-icon { font-size: 1.4rem; }
.plan-target {
  margin-left: auto;
  font-size: var(--text-xs);
  font-weight: 600;
  background: rgba(255, 255, 255, 0.2);
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
}
.plan-tasks { list-style: none; display: flex; flex-direction: column; gap: var(--space-2); margin-bottom: var(--space-4); }
.plan-tasks li { display: flex; gap: var(--space-2); font-size: var(--text-sm); line-height: 1.5; }
.plan-check { opacity: 0.8; }
.plan-start-btn {
  background: white;
  color: var(--color-primary);
  font-weight: 600;
  font-size: var(--text-sm);
  padding: var(--space-2) var(--space-5);
  border-radius: var(--radius-full);
  transition: transform var(--transition-fast);
}
.plan-start-btn:hover { transform: translateY(-2px); }

@media (prefers-reduced-motion: reduce) {
  .daily-plan { animation: none; }
}

/* Streak banner */
.streak-banner {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-8);
  padding: var(--space-5);
  margin-bottom: var(--space-8);
  background: linear-gradient(135deg, #fff7ed, #ffedd5);
  border: 1px solid #fed7aa;
  border-radius: var(--radius-lg);
}
[data-theme="dark"] .streak-banner {
  background: linear-gradient(135deg, rgba(251, 146, 60, 0.1), rgba(234, 88, 12, 0.08));
  border-color: rgba(251, 146, 60, 0.25);
}
.streak-item { display: flex; flex-direction: column; align-items: center; gap: 2px; }
.streak-flame { font-size: 1.8rem; }
.streak-num { font-size: var(--text-3xl); font-weight: 800; color: #c2410c; line-height: 1; }
[data-theme="dark"] .streak-num { color: #fb923c; }
.streak-label { font-size: var(--text-xs); color: var(--color-text-muted); }
.streak-divider { width: 1px; height: 48px; background: var(--color-border); }

/* Dual charts row — auto-fit so a lone chart fills the width instead of
   leaving an awkward empty half */
.dual-charts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--space-6);
  margin-bottom: var(--space-8);
}
.chart-section.half { margin-bottom: 0; }

/* Weakness analysis */
.weakness-section { margin-bottom: var(--space-8); }
.weakness-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: var(--space-4);
}
.weakness-card {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  padding: var(--space-4) var(--space-5);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  border-left: 3px solid var(--color-warning);
}
.weakness-card.wide { grid-column: 1 / -1; }
.wk-icon { font-size: 1.4rem; }
.wk-title { font-size: var(--text-sm); font-weight: 600; color: var(--color-text-secondary); }
.wk-value { font-size: var(--text-lg); font-weight: 700; color: var(--color-text); }
.wk-list { list-style: none; display: flex; flex-direction: column; gap: var(--space-1); }
.wk-list li {
  display: flex;
  justify-content: space-between;
  font-size: var(--text-sm);
  color: var(--color-text);
  padding: var(--space-1) 0;
}
.wk-score { font-weight: 600; color: var(--color-text-muted); }

/* Grammar coaching card */
.grammar-card { gap: var(--space-3); }
.grammar-head { display: flex; align-items: center; gap: var(--space-2); flex-wrap: wrap; }
.grammar-head .wk-title { margin-right: auto; }
.grammar-btn {
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  background: var(--color-primary);
  color: white;
  font-size: var(--text-xs);
  font-weight: 600;
  transition: background var(--transition-fast);
}
.grammar-btn:hover { background: var(--color-primary-dark); }
.grammar-tags { display: flex; flex-wrap: wrap; gap: var(--space-2); }
.grammar-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px var(--space-2);
  border-radius: var(--radius-sm);
  background: var(--color-bg);
  border: 1px solid var(--color-border-light);
  font-size: var(--text-xs);
  color: var(--color-text-secondary);
}
.grammar-tag i { font-style: normal; font-weight: 700; color: var(--color-text-muted); }
.grammar-loading {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
}
.grammar-analysis {
  font-size: var(--text-sm);
  line-height: 1.7;
  color: var(--color-text);
  background: var(--color-primary-50);
  border-radius: var(--radius-md);
  padding: var(--space-3) var(--space-4);
}
.grammar-tips {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
.grammar-tips li {
  position: relative;
  padding-left: var(--space-5);
  font-size: var(--text-sm);
  line-height: 1.6;
  color: var(--color-text-secondary);
}
.grammar-tips li::before {
  content: '✓';
  position: absolute;
  left: 0;
  color: var(--color-success);
  font-weight: 700;
}
.grammar-hint { font-size: var(--text-sm); color: var(--color-text-muted); line-height: 1.6; }
.mini-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: dash-spin 0.7s linear infinite;
  display: inline-block;
}
@keyframes dash-spin { to { transform: rotate(360deg); } }

@media (max-width: 768px) {
  .dual-charts { grid-template-columns: 1fr; }
  .chart-section.half { margin-bottom: var(--space-6); }
}

/* History */
.history-section { margin-bottom: var(--space-8); }

.empty-state {
  text-align: center;
  color: var(--color-text-muted);
  padding: var(--space-12);
  font-size: var(--text-base);
}

.session-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.session-item {
  background: var(--color-surface);
  border-radius: var(--radius-md);
  padding: var(--space-4) var(--space-5);
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  border: 1px solid var(--color-border);
  transition: all var(--transition-fast);
}

.session-item:hover {
  border-color: var(--color-primary-200);
  box-shadow: var(--shadow-md);
  transform: translateX(4px);
}

.session-meta {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.scenario-tag {
  font-weight: 600;
  text-transform: capitalize;
  font-size: var(--text-base);
}

.session-date {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

.session-stats {
  display: flex;
  gap: var(--space-3);
  align-items: center;
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
}

.score-badge {
  background: var(--color-primary-50);
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: 600;
  color: var(--color-primary);
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-modal);
  animation: fade-in 200ms both;
}

.modal {
  background: var(--color-surface);
  border-radius: var(--radius-xl);
  padding: var(--space-8);
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  animation: scale-in var(--transition-base) both;
  box-shadow: var(--shadow-xl);
}

.modal h3 { color: var(--color-primary); margin-bottom: var(--space-5); font-size: var(--text-xl); }

.report-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.report-item label {
  display: block;
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  margin-bottom: 2px;
  font-weight: 500;
}

.report-item span { font-size: var(--text-lg); font-weight: 700; }

.common-errors h4 { margin-bottom: var(--space-2); color: var(--color-warning); font-size: var(--text-sm); }
.common-errors ul { list-style: none; padding: 0; }
.common-errors li {
  padding: var(--space-2) 0;
  border-bottom: 1px solid var(--color-border-light);
  font-size: var(--text-sm);
}
.error-count { color: var(--color-text-muted); font-size: var(--text-xs); }

.close-btn {
  margin-top: var(--space-4);
  padding: var(--space-3) var(--space-6);
  background: var(--color-primary);
  color: white;
  border-radius: var(--radius-md);
  font-size: var(--text-base);
  font-weight: 600;
  transition: background var(--transition-fast);
}
.close-btn:hover { background: var(--color-primary-dark); }

/* Responsive */
@media (max-width: 768px) {
  .summary-cards { grid-template-columns: repeat(2, 1fr); }
  .session-item { flex-direction: column; align-items: flex-start; gap: var(--space-2); }
  .report-grid { grid-template-columns: 1fr; }
}

.playback-btn {
  font-size: 0.75rem;
  padding: 0.2rem 0.5rem;
  border: 1px solid var(--color-primary);
  border-radius: var(--radius-sm);
  background: var(--color-surface);
  color: var(--color-primary);
  cursor: pointer;
  font-weight: 600;
  transition: all var(--transition-fast);
}

.playback-btn:hover {
  background: var(--color-primary);
  color: white;
}

/* Analytics Section */
.analytics-section {
  margin-bottom: 2rem;
}

.time-range-picker {
  display: flex;
  gap: var(--space-2);
  margin-bottom: 1.2rem;
}

.range-btn {
  padding: 0.4rem 1rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-full);
  background: var(--color-surface);
  color: var(--color-text-secondary);
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 600;
  transition: all var(--transition-fast);
}

.range-btn.active {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.range-btn:hover:not(.active) {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.analytics-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  margin-bottom: 1rem;
  box-shadow: var(--shadow-sm);
}

.analytics-card h3 {
  color: var(--color-text);
  margin-bottom: 1rem;
  font-size: 1.1rem;
}

.bar-chart-horizontal {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.bar-row {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}

.bar-label {
  min-width: 100px;
  font-size: 0.85rem;
  color: var(--color-text-secondary);
  text-transform: capitalize;
}

.bar-track {
  flex: 1;
  height: 20px;
  background: var(--color-border-light);
  border-radius: 10px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-accent), var(--color-warning));
  border-radius: 10px;
  transition: width 0.4s ease;
}

.bar-fill.scenario-bar {
  background: linear-gradient(90deg, var(--color-primary-dark), var(--color-primary));
}

.bar-value {
  min-width: 30px;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-text);
  text-align: right;
}

.summary-stats {
  display: flex;
  gap: 2rem;
  justify-content: center;
}

.stat-item {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 2rem;
  font-weight: 700;
  color: var(--color-primary);
}

.stat-label {
  font-size: 0.85rem;
  color: var(--color-text-muted);
}
</style>
