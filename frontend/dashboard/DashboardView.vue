<template>
  <div class="dashboard">
    <Toast :message="toast.message" :type="toast.type" @close="toast.message = ''" />
    <h1>📊 {{ t('dashboard.title') }}</h1>

    <!-- Login prompt for guests -->
    <div v-if="!isAuthenticated" class="login-prompt">
      <span>💡 登录后可持久保存练习进度</span>
      <router-link to="/login" class="prompt-link">去登录 →</router-link>
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

    <!-- Score Trend Chart -->
    <div class="chart-section" v-if="hasScoreData">
      <h2>{{ t('dashboard.scoreTrends') }}</h2>
      <div class="chart-container">
        <Line :data="trendChartData" :options="trendChartOptions" />
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
import { ref, reactive, computed, onMounted } from 'vue'
import { isAuthenticated } from '../composables/useAuth'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { CONFIG } from '../../shared/config'
import { useI18n } from '../composables/useI18n'
import Toast from '../components/Toast.vue'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend)

const { t } = useI18n()
const API = CONFIG.API.BASE_URL
const progress = ref(null)
const sessions = ref([])
const selectedSummary = ref(null)
const toast = reactive({ message: '', type: 'info' })

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
</style>
