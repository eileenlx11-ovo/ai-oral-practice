/**
 * Mock Server — 模拟后端 API，用于前端独立开发调试
 * 端口 8001，与 vite.config.js 的 proxy 配置对应
 *
 * 功能：
 * - /api/scenarios — 场景列表 & 详情
 * - /api/chat — 非流式对话
 * - /api/stream — SSE 流式对话
 * - /api/asr — 语音识别
 * - /api/assess — 发音评估
 * - /api/sessions — 会话管理
 * - /api/progress — 学习进度
 * - /audio/* — 静态音频文件
 */

import express from 'express'
import multer from 'multer'
import cors from 'cors'
import { randomUUID } from 'crypto'

const app = express()
const upload = multer({ storage: multer.memoryStorage() })
const PORT = 8001

app.use(cors())
app.use(express.json())

// ========== Mock Data ==========

const SCENARIOS = [
  { id: 'interview', icon: '💼', name: 'Job Interview', description: '模拟英语面试场景', greeting: "Hello! I'm your interviewer today. Could you please introduce yourself briefly?" },
  { id: 'restaurant', icon: '🍽️', name: 'Restaurant', description: '模拟餐厅点餐', greeting: "Welcome to our restaurant! I'll be your server today. Would you like to see the menu?" },
  { id: 'meeting', icon: '📋', name: 'Business Meeting', description: '模拟商务会议', greeting: "Good morning everyone. Let's start today's meeting. Would you like to share your update first?" },
  { id: 'travel', icon: '✈️', name: 'Travel', description: '模拟旅行场景', greeting: "Welcome to the information center! How can I help you today? Are you looking for directions?" },
  { id: 'smalltalk', icon: '💬', name: 'Small Talk', description: '日常闲聊', greeting: "Hey! Nice weather today, isn't it? What have you been up to lately?" },
]

// Mock AI replies per scenario (cycles through them)
const MOCK_REPLIES = {
  interview: [
    "That's a great introduction! Can you tell me about a challenging project you've worked on?",
    "Interesting! How did you handle the technical difficulties in that project?",
    "Good answer. What are your main strengths as a developer?",
    "I see. Where do you see yourself in five years?",
  ],
  restaurant: [
    "Our specials today are grilled salmon and mushroom risotto. Would you like to try either of those?",
    "Excellent choice! Would you like any appetizers or drinks to start?",
    "Sure thing! Would you prefer still or sparkling water?",
    "Your order will be ready in about 15 minutes. Is there anything else I can help you with?",
  ],
  meeting: [
    "Thank you for that update. Does anyone have questions about the timeline?",
    "Good point. Let's discuss the resource allocation for next sprint.",
    "I agree with your approach. Can you prepare a detailed proposal by Friday?",
    "Let's wrap up. I'll send out the meeting notes and action items later today.",
  ],
  travel: [
    "The city center is about 20 minutes by bus. You can take line 42 from the stop right outside.",
    "Yes, there are several good hotels nearby. What's your budget range?",
    "I'd recommend the old town area. It has great restaurants and historical sites.",
    "The museum is open from 9am to 6pm. Tickets are available at the entrance or online.",
  ],
  smalltalk: [
    "Oh that sounds fun! I've been meaning to try that too. Do you go often?",
    "Really? That's interesting! I actually had a similar experience last week.",
    "Ha, I know exactly what you mean! Have you tried the new place downtown?",
    "That's awesome! We should definitely hang out more often. What are you doing this weekend?",
  ],
}

// Mock grammar corrections
const MOCK_CORRECTIONS = [
  { original: 'I goed to', corrected: 'I went to', explanation: 'Irregular past tense: "go" → "went"' },
  { original: 'more better', corrected: 'much better', explanation: '"Better" is already comparative; use "much" for emphasis' },
  { original: 'He don\'t', corrected: 'He doesn\'t', explanation: 'Third person singular uses "doesn\'t"' },
]

// Track reply index per session scenario
const replyCounters = {}
let sessions = []

function getNextReply(scenario) {
  const key = scenario || 'smalltalk'
  const replies = MOCK_REPLIES[key] || MOCK_REPLIES.smalltalk
  if (!replyCounters[key]) replyCounters[key] = 0
  const reply = replies[replyCounters[key] % replies.length]
  replyCounters[key]++
  return reply
}

// ========== Routes ==========

// --- Scenarios ---
app.get('/api/scenarios', (req, res) => {
  res.json(SCENARIOS.map(({ id, icon, name, description }) => ({ id, icon, name, description })))
})

app.get('/api/scenarios/:id', (req, res) => {
  const s = SCENARIOS.find((x) => x.id === req.params.id)
  if (!s) return res.status(404).json({ detail: 'Scenario not found' })
  res.json(s)
})

// --- ASR (transcription only) ---
app.post('/api/asr', upload.single('audio'), (req, res) => {
  // Simulate delay
  setTimeout(() => {
    res.json({ text: "I think this is a really interesting question and I'd like to share my thoughts on it." })
  }, 500)
})

// --- Chat (non-streaming) ---
app.post('/api/chat', upload.single('audio'), (req, res) => {
  const scenario = req.body?.scenario || 'smalltalk'
  const replyText = getNextReply(scenario)

  setTimeout(() => {
    res.json({
      user_text: "I think this project is going very well so far.",
      reply_text: replyText,
      reply_audio_url: null,
      corrections: Math.random() > 0.5 ? [MOCK_CORRECTIONS[Math.floor(Math.random() * MOCK_CORRECTIONS.length)]] : [],
      pronunciation: { overall: 82, words: [] },
      session_id: randomUUID(),
    })
  }, 800)
})

// --- Stream (SSE) ---
app.post('/api/stream', upload.single('audio'), (req, res) => {
  const scenario = req.body?.scenario || 'smalltalk'
  const sid = req.body?.session_id || randomUUID()
  const replyText = getNextReply(scenario)

  // Set SSE headers
  res.setHeader('Content-Type', 'text/event-stream')
  res.setHeader('Cache-Control', 'no-cache')
  res.setHeader('Connection', 'keep-alive')
  res.flushHeaders()

  // Simulated user text
  const mockUserText = "I have been working on a project for the past few months and it has been a great learning experience."

  // 1. ASR event (after 300ms)
  setTimeout(() => {
    res.write(`event: asr\ndata: ${JSON.stringify({ text: mockUserText })}\n\n`)
  }, 300)

  // 2. Split reply into sentences and stream them
  const sentences = replyText.match(/[^.!?]+[.!?]+/g) || [replyText]
  sentences.forEach((sentence, i) => {
    setTimeout(() => {
      res.write(`event: sentence\ndata: ${JSON.stringify({ text: sentence.trim(), audio_url: null })}\n\n`)
    }, 600 + i * 400)
  })

  // 3. Corrections (randomly)
  setTimeout(() => {
    if (Math.random() > 0.4) {
      const correction = MOCK_CORRECTIONS[Math.floor(Math.random() * MOCK_CORRECTIONS.length)]
      res.write(`event: corrections\ndata: ${JSON.stringify([correction])}\n\n`)
    }
  }, 600 + sentences.length * 400 + 200)

  // 4. Done event
  setTimeout(() => {
    res.write(`event: done\ndata: ${JSON.stringify({ session_id: sid })}\n\n`)
    res.end()
  }, 600 + sentences.length * 400 + 400)
})

// --- Pronunciation Assessment ---
app.post('/api/assess', upload.single('audio'), (req, res) => {
  const referenceText = req.body?.reference_text || ''
  const words = referenceText.split(/\s+/).filter(Boolean)

  setTimeout(() => {
    res.json({
      overall: Math.floor(70 + Math.random() * 25),
      words: words.map((w) => ({
        word: w,
        accuracy: Math.floor(60 + Math.random() * 40),
        error_type: Math.random() > 0.8 ? 'mispronunciation' : 'none',
      })),
    })
  }, 600)
})

// --- Sessions ---
app.post('/api/sessions', upload.none(), (req, res) => {
  const session = {
    session_id: randomUUID(),
    scenario: req.body?.scenario || 'smalltalk',
    started_at: new Date().toISOString(),
    turns: [],
  }
  sessions.push(session)
  res.json({ session_id: session.session_id })
})

app.get('/api/sessions', (req, res) => {
  const limit = parseInt(req.query.limit) || 10
  const offset = parseInt(req.query.offset) || 0
  // Return mock sessions
  const mockSessions = [
    { session_id: 'mock-1', scenario: 'interview', started_at: '2026-06-05T10:00:00Z', turns: 8, avg_pronunciation: 78, avg_fluency: 72 },
    { session_id: 'mock-2', scenario: 'restaurant', started_at: '2026-06-04T14:30:00Z', turns: 5, avg_pronunciation: 82, avg_fluency: 80 },
    { session_id: 'mock-3', scenario: 'smalltalk', started_at: '2026-06-03T09:15:00Z', turns: 12, avg_pronunciation: 75, avg_fluency: 68 },
  ]
  res.json(mockSessions.slice(offset, offset + limit))
})

app.post('/api/sessions/:id/turns', upload.none(), (req, res) => {
  res.json({ ok: true })
})

app.post('/api/sessions/:id/end', (req, res) => {
  res.json({
    session_id: req.params.id,
    scenario: 'interview',
    total_turns: 6,
    avg_pronunciation: 79,
    avg_fluency: 74,
    avg_accuracy: 81,
    total_corrections: 3,
    common_errors: [
      { pattern: 'Subject-verb agreement', count: 2 },
      { pattern: 'Article usage', count: 1 },
    ],
  })
})

app.get('/api/sessions/:id/summary', (req, res) => {
  res.json({
    session_id: req.params.id,
    scenario: 'interview',
    total_turns: 6,
    avg_pronunciation: 79,
    avg_fluency: 74,
    avg_accuracy: 81,
    total_corrections: 3,
    common_errors: [
      { pattern: 'Subject-verb agreement', count: 2 },
      { pattern: 'Article usage', count: 1 },
    ],
  })
})

// --- Progress ---
app.get('/api/progress', (req, res) => {
  res.json({
    total_sessions: 15,
    total_turns: 87,
    total_corrections: 23,
    avg_pronunciation: 78,
    score_history: [
      { date: '2026-06-01', avg_pronunciation: 72, avg_fluency: 68, avg_accuracy: 74 },
      { date: '2026-06-02', avg_pronunciation: 74, avg_fluency: 70, avg_accuracy: 76 },
      { date: '2026-06-03', avg_pronunciation: 75, avg_fluency: 72, avg_accuracy: 78 },
      { date: '2026-06-04', avg_pronunciation: 78, avg_fluency: 74, avg_accuracy: 80 },
      { date: '2026-06-05', avg_pronunciation: 80, avg_fluency: 76, avg_accuracy: 82 },
      { date: '2026-06-06', avg_pronunciation: 82, avg_fluency: 78, avg_accuracy: 84 },
    ],
  })
})

// --- Static audio (placeholder) ---
app.use('/audio', express.static('audio_cache'))

// ========== Start ==========
app.listen(PORT, () => {
  console.log(`\n🎯 Mock Server running at http://localhost:${PORT}`)
  console.log(`   API endpoints ready:`)
  console.log(`   - GET  /api/scenarios`)
  console.log(`   - POST /api/chat`)
  console.log(`   - POST /api/stream (SSE)`)
  console.log(`   - POST /api/asr`)
  console.log(`   - POST /api/assess`)
  console.log(`   - GET  /api/sessions`)
  console.log(`   - GET  /api/progress`)
  console.log(`\n   Frontend should proxy to this port (vite.config.js → localhost:${PORT})`)
  console.log(`   Start frontend: cd frontend && npm run dev\n`)
})
