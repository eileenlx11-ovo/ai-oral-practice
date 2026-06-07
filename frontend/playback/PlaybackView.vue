<template>
  <div class="playback">
    <h1>Session Playback</h1>

    <div v-if="loading" class="loading">Loading session...</div>
    <div v-else-if="error" class="error">{{ error }}</div>

    <div v-else class="conversation">
      <div v-for="(turn, idx) in turns" :key="idx" class="turn">
        <!-- User bubble -->
        <div class="bubble user-bubble">
          <div class="bubble-header">
            <span class="role-label">You</span>
            <button class="play-btn" @click="playRecording(idx)" :disabled="playingIndex === idx">
              {{ playingIndex === idx ? '...' : 'Play Recording' }}
            </button>
          </div>
          <p class="bubble-text">{{ turn.user_text }}</p>

          <!-- Corrections below user bubble -->
          <div v-if="turn.corrections && turn.corrections.length" class="corrections">
            <div v-for="(c, ci) in turn.corrections" :key="ci" class="correction-item">
              <span class="original">{{ c.original }}</span>
              <span class="arrow">→</span>
              <span class="corrected">{{ c.corrected }}</span>
              <span v-if="c.explanation" class="explanation">{{ c.explanation }}</span>
            </div>
          </div>
        </div>

        <!-- AI bubble -->
        <div class="bubble ai-bubble">
          <div class="bubble-header">
            <span class="role-label">AI</span>
          </div>
          <p class="bubble-text">{{ turn.reply_text }}</p>
        </div>
      </div>
    </div>

    <!-- AI Review Section -->
    <div v-if="turns.length > 0" class="review-section">
      <h2>AI Review</h2>
      <div v-if="review" class="review-content">{{ review }}</div>
      <button v-else class="review-btn" @click="generateReview" :disabled="reviewLoading">
        {{ reviewLoading ? 'Generating...' : 'Generate Review' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { CONFIG } from '../../shared/config'
import { getAuthHeaders } from '../composables/useAuth'

const route = useRoute()
const sessionId = route.params.sessionId

const API = CONFIG.API.BASE_URL
const turns = ref([])
const loading = ref(true)
const error = ref('')
const playingIndex = ref(null)
const review = ref('')
const reviewLoading = ref(false)

onMounted(async () => {
  try {
    const res = await fetch(`${API}/api/sessions/${sessionId}/turns-full`, {
      headers: getAuthHeaders(),
    })
    if (!res.ok) {
      error.value = `Failed to load session (${res.status})`
      return
    }
    const data = await res.json()
    turns.value = data.turns || []
  } catch (e) {
    error.value = 'Network error loading session'
  } finally {
    loading.value = false
  }
})

async function playRecording(turnIndex) {
  playingIndex.value = turnIndex
  try {
    // Fetch with auth (owner-only route) then play the blob — `new Audio(url)`
    // can't carry Authorization headers.
    const res = await fetch(`${API}/api/sessions/${sessionId}/recording/${turnIndex}`, {
      headers: getAuthHeaders(),
    })
    if (!res.ok) { playingIndex.value = null; return }
    const blob = await res.blob()
    const objectUrl = URL.createObjectURL(blob)
    const audio = new Audio(objectUrl)
    const cleanup = () => { playingIndex.value = null; URL.revokeObjectURL(objectUrl) }
    audio.onended = cleanup
    audio.onerror = cleanup
    await audio.play()
  } catch {
    playingIndex.value = null
  }
}

async function generateReview() {
  reviewLoading.value = true
  try {
    const res = await fetch(`${API}/api/sessions/${sessionId}/review`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    })
    if (res.ok) {
      const data = await res.json()
      review.value = data.review || ''
    }
  } catch {
    // silent
  } finally {
    reviewLoading.value = false
  }
}
</script>

<style scoped>
.playback {
  max-width: 800px;
  margin: 0 auto;
  padding: 1rem;
}

h1 {
  color: #1f4e79;
  margin-bottom: 1.5rem;
}

.loading, .error {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.error {
  color: #e74c3c;
}

.conversation {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.turn {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.bubble {
  border-radius: 12px;
  padding: 1rem 1.2rem;
  max-width: 85%;
}

.user-bubble {
  background: #e8f4fd;
  align-self: flex-end;
}

.ai-bubble {
  background: #f5f5f5;
  align-self: flex-start;
}

.bubble-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.4rem;
}

.role-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #999;
  text-transform: uppercase;
}

.bubble-text {
  margin: 0;
  line-height: 1.5;
}

.play-btn {
  font-size: 0.75rem;
  padding: 0.2rem 0.6rem;
  border: 1px solid #1f4e79;
  border-radius: 4px;
  background: white;
  color: #1f4e79;
  cursor: pointer;
}

.play-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.corrections {
  margin-top: 0.6rem;
  padding-top: 0.6rem;
  border-top: 1px dashed #ccc;
}

.correction-item {
  font-size: 0.85rem;
  margin-bottom: 0.3rem;
}

.original {
  color: #e74c3c;
  text-decoration: line-through;
}

.arrow {
  margin: 0 0.4rem;
  color: #999;
}

.corrected {
  color: #27ae60;
  font-weight: 600;
}

.explanation {
  display: block;
  color: #666;
  font-size: 0.8rem;
  margin-top: 0.1rem;
}

.review-section {
  margin-top: 2rem;
  padding: 1.5rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.review-section h2 {
  color: #1f4e79;
  margin-bottom: 1rem;
}

.review-content {
  white-space: pre-wrap;
  line-height: 1.6;
  color: #333;
}

.review-btn {
  padding: 0.6rem 1.5rem;
  background: #1f4e79;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.95rem;
}

.review-btn:hover {
  background: #163a5c;
}

.review-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
