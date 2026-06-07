<template>
  <div class="dashboard">
    <Toast :message="toast.message" :type="toast.type" @close="toast.message = ''" />
    <h1>📊 Progress Dashboard</h1>

    <!-- Summary Cards -->
    <div class="summary-cards" v-if="progress">
      <div class="card">
        <span class="card-value">{{ progress.total_sessions }}</span>
        <span class="card-label">Sessions</span>
      </div>
      <div class="card">
        <span class="card-value">{{ progress.total_turns }}</span>
        <span class="card-label">Turns Spoken</span>
      </div>
      <div class="card">
        <span class="card-value">{{ progress.total_corrections }}</span>
        <span class="card-label">Corrections</span>
      </div>
      <div class="card highlight">
        <span class="card-value">{{ formatScore(progress.avg_pronunciation) }}</span>
        <span class="card-label">Avg Pronunciation</span>
      </div>
    </div>

    <!-- Score Trend Chart -->
    <div class="chart-section" v-if="hasScoreData">
      <h2>Score Trends</h2>
      <div class="chart-container">
        <Line :data="trendChartData" :options="trendChartOptions" />
      </div>
    </div>

    <!-- Session History -->
    <div class="history-section">
      <h2>Practice History</h2>
      <div v-if="sessions.length === 0" class="empty-state">
        <p>No practice sessions yet. Start a conversation to see your progress!</p>
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
            <span>{{ s.turns }} turns</span>
            <span v-if="s.avg_pronunciation" class="score-badge">
              🎯 {{ s.avg_pronunciation.toFixed(0) }}
            </span>
            <span v-if="s.avg_fluency" class="score-badge">
              🗣️ {{ s.avg_fluency.toFixed(0) }}
            </span>
            <button class="playback-btn" @click.stop="$router.push('/playback/' + s.session_id)">回放</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Session Detail Modal -->
    <div v-if="selectedSummary" class="modal-overlay" @click.self="selectedSummary = null">
      <div class="modal">
        <h3>Session Report</h3>
        <div class="report-grid">
          <div class="report-item">
            <label>Scenario</label>
            <span>{{ selectedSummary.scenario }}</span>
          </div>
          <div class="report-item">
            <label>Duration</label>
            <span>{{ selectedSummary.total_turns }} turns</span>
          </div>
          <div class="report-item">
            <label>Pronunciation</label>
            <span>{{ formatScore(selectedSummary.avg_pronunciation) }}</span>
          </div>
          <div class="report-item">
            <label>Fluency</label>
            <span>{{ formatScore(selectedSummary.avg_fluency) }}</span>
          </div>
          <div class="report-item">
            <label>Accuracy</label>
            <span>{{ formatScore(selectedSummary.avg_accuracy) }}</span>
          </div>
          <div class="report-item">
            <label>Corrections</label>
            <span>{{ selectedSummary.total_corrections }}</span>
          </div>
        </div>

        <div v-if="selectedSummary.common_errors && selectedSummary.common_errors.length" class="common-errors">
          <h4>Common Error Patterns</h4>
          <ul>
            <li v-for="e in selectedSummary.common_errors" :key="e.pattern">
              {{ e.pattern }} <span class="error-count">(×{{ e.count }})</span>
            </li>
          </ul>
        </div>

        <button class="close-btn" @click="selectedSummary = null">Close</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
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
import Toast from '../components/Toast.vue'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend)

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
      showToast(`加载会话详情失败 (${res.status})`)
      return
    }
    selectedSummary.value = await res.json()
  } catch {
    showToast('网络错误，无法加载会话详情')
  }
}

onMounted(async () => {
  try {
    const [progRes, sessRes] = await Promise.all([
      fetch(`${API}/api/progress`),
      fetch(`${API}/api/sessions`),
    ])
    if (!progRes.ok || !sessRes.ok) {
      showToast('加载数据失败，请稍后刷新重试')
      return
    }
    progress.value = await progRes.json()
    sessions.value = await sessRes.json()
  } catch {
    showToast('网络错误，无法连接服务器')
  }
})
</script>

<style scoped>
.dashboard {
  max-width: 900px;
  margin: 0 auto;
}

h1 {
  color: #1f4e79;
  margin-bottom: 1.5rem;
}

h2 {
  color: #333;
  margin-bottom: 1rem;
  font-size: 1.3rem;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.card {
  background: white;
  border-radius: 12px;
  padding: 1.2rem;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.card.highlight {
  background: #1f4e79;
  color: white;
}

.card-value {
  display: block;
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.3rem;
}

.card-label {
  font-size: 0.85rem;
  opacity: 0.8;
}

.chart-section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.chart-container {
  height: 300px;
}

.history-section {
  margin-bottom: 2rem;
}

.empty-state {
  text-align: center;
  color: #999;
  padding: 3rem;
}

.session-list {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.session-item {
  background: white;
  border-radius: 10px;
  padding: 1rem 1.2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

.session-item:hover {
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(31, 78, 121, 0.12);
}

.session-meta {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.scenario-tag {
  font-weight: 600;
  text-transform: capitalize;
}

.session-date {
  font-size: 0.8rem;
  color: #999;
}

.session-stats {
  display: flex;
  gap: 0.8rem;
  align-items: center;
  font-size: 0.9rem;
  color: #666;
}

.score-badge {
  background: #f0f7ff;
  padding: 0.2rem 0.6rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  color: #1f4e79;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal h3 {
  color: #1f4e79;
  margin-bottom: 1.2rem;
}

.report-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.report-item label {
  display: block;
  font-size: 0.8rem;
  color: #999;
  margin-bottom: 0.2rem;
}

.report-item span {
  font-size: 1.1rem;
  font-weight: 600;
}

.common-errors h4 {
  margin-bottom: 0.5rem;
  color: #e67e22;
}

.common-errors ul {
  list-style: none;
  padding: 0;
}

.common-errors li {
  padding: 0.4rem 0;
  border-bottom: 1px solid #f0f0f0;
}

.error-count {
  color: #999;
  font-size: 0.85rem;
}

.close-btn {
  margin-top: 1rem;
  padding: 0.6rem 1.5rem;
  background: #1f4e79;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.95rem;
}

.close-btn:hover {
  background: #163a5c;
}

.playback-btn {
  font-size: 0.75rem;
  padding: 0.2rem 0.5rem;
  border: 1px solid #1f4e79;
  border-radius: 4px;
  background: white;
  color: #1f4e79;
  cursor: pointer;
  font-weight: 600;
}

.playback-btn:hover {
  background: #1f4e79;
  color: white;
}
</style>
