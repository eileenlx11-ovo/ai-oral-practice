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
  { id: 'coffee_shop', icon: '☕', name: 'Coffee Shop', category: 'daily', difficulty: 'beginner', description: '在咖啡店点饮品', objective: 'Successfully order a customized coffee drink', greeting: "Hey there! Welcome to Bean & Brew. What can I get started for you today?", character: { name: 'Maya', avatar: '👩‍🦱' } },
  { id: 'grocery', icon: '🛒', name: 'Grocery Shopping', category: 'daily', difficulty: 'beginner', description: '超市购物找商品', objective: 'Ask for help finding items and check out', greeting: "Hi! Can I help you find something today?", character: { name: 'Tom', avatar: '👨' } },
  { id: 'doctor', icon: '🏥', name: "Doctor's Visit", category: 'daily', difficulty: 'intermediate', description: '描述症状和理解医嘱', objective: 'Explain your symptoms and understand the treatment plan', greeting: "Good morning! I'm Dr. Chen. What brings you in today?", character: { name: 'Dr. Chen', avatar: '👩‍⚕️' } },
  { id: 'restaurant', icon: '🍽️', name: 'Restaurant', category: 'daily', difficulty: 'beginner', description: '餐厅点餐全流程', objective: 'Order a complete meal including drinks and dessert', greeting: "Good evening! Welcome to The Garden Bistro. Can I start you with a drink?", character: { name: 'James', avatar: '🧑‍🍳' } },
  { id: 'delivery', icon: '🚴', name: 'Food Delivery', category: 'daily', difficulty: 'beginner', description: '和外卖员电话沟通', objective: 'Give clear directions and resolve a delivery issue', greeting: "Hey, this is Alex with your delivery. I can't find the entrance. Can you help?", character: { name: 'Alex', avatar: '🚴' } },
  { id: 'interview', icon: '💼', name: 'Job Interview', category: 'work', difficulty: 'advanced', description: '模拟英语面试', objective: 'Present yourself professionally', greeting: "Hello! I'm Sarah. Let's start — could you walk me through your background?", character: { name: 'Sarah', avatar: '👩‍💼' } },
  { id: 'meeting', icon: '📋', name: 'Team Meeting', category: 'work', difficulty: 'intermediate', description: '团队会议讨论', objective: 'Present your status update and respond to questions', greeting: "Alright, let's get started. Would you like to kick us off with your update?", character: { name: 'David', avatar: '👨‍💼' } },
  { id: 'coworker', icon: '👩‍💻', name: 'Office Chat', category: 'work', difficulty: 'intermediate', description: '同事间日常闲聊', objective: 'Build rapport naturally', greeting: "Hey! Finally grabbed lunch? Mind if I join?", character: { name: 'Lisa', avatar: '👩‍💻' } },
  { id: 'phone_call', icon: '📞', name: 'Business Call', category: 'work', difficulty: 'advanced', description: '商务电话沟通', objective: 'Communicate clearly and confirm action items', greeting: "Hi, this is Michael from Apex Solutions. I wanted to follow up on the proposal.", character: { name: 'Michael', avatar: '📞' } },
  { id: 'salary', icon: '💰', name: 'Salary Negotiation', category: 'work', difficulty: 'advanced', description: '薪资谈判', objective: 'Express expectations and reach agreement', greeting: "Great news — we'd like to extend an offer! The base is $85,000.", character: { name: 'Rachel', avatar: '💰' } },
  { id: 'airport', icon: '✈️', name: 'Airport Check-in', category: 'travel', difficulty: 'intermediate', description: '机场值机和行李', objective: 'Complete check-in and resolve an issue', greeting: "Good morning! Passport and booking reference, please.", character: { name: 'Emily', avatar: '✈️' } },
  { id: 'hotel', icon: '🏨', name: 'Hotel Check-in', category: 'travel', difficulty: 'beginner', description: '酒店入住', objective: 'Complete check-in and get recommendations', greeting: "Welcome to The Grand! Do you have a reservation?", character: { name: 'Carlos', avatar: '🏨' } },
  { id: 'directions', icon: '🗺️', name: 'Asking Directions', category: 'travel', difficulty: 'beginner', description: '问路和导航', objective: 'Get clear directions and confirm understanding', greeting: "Oh, you look a bit lost! Can I help you find somewhere?", character: { name: 'Sophie', avatar: '🗺️' } },
  { id: 'travel', icon: '🚗', name: 'Car Rental', category: 'travel', difficulty: 'intermediate', description: '租车和条款', objective: 'Choose the right car and understand options', greeting: "Welcome to QuickDrive Rentals! What name is your reservation under?", character: { name: 'Mark', avatar: '🚗' } },
  { id: 'smalltalk', icon: '💬', name: 'Small Talk', category: 'social', difficulty: 'beginner', description: '日常社交闲聊', objective: 'Keep a natural conversation going', greeting: "Hey! Nice to see you around. How's your week been?", character: { name: 'Jake', avatar: '💬' } },
  { id: 'party', icon: '🎉', name: 'Party Chat', category: 'social', difficulty: 'intermediate', description: '派对认识新朋友', objective: 'Introduce yourself and find common interests', greeting: "Hi! I don't think we've met — I'm Olivia. How do you know the host?", character: { name: 'Olivia', avatar: '🎉' } },
  { id: 'neighbor', icon: '🏠', name: 'Neighbor Chat', category: 'social', difficulty: 'beginner', description: '邻居日常寒暄', objective: 'Have a friendly exchange', greeting: "Oh hello! I noticed you moved in recently. How are you settling in?", character: { name: 'Robert', avatar: '🏠' } },
  { id: 'gym', icon: '💪', name: 'Gym Buddy', category: 'social', difficulty: 'intermediate', description: '健身房社交', objective: 'Discuss fitness and share tips', greeting: "Hey! I've seen you here a few times. How long have you been working out?", character: { name: 'Kevin', avatar: '💪' } },
]

// Mock AI replies per scenario (cycles through them)
const MOCK_REPLIES = {
  coffee_shop: [
    "Sure thing! What size would you like — small, medium, or large?",
    "Would you like that with oat milk, almond milk, or regular?",
    "Great choice! Anything else I can get you? Maybe a pastry to go with it?",
    "That'll be $5.50. For here or to go?",
  ],
  grocery: [
    "The pasta sauce is in aisle 3, right next to the canned tomatoes.",
    "I'm sorry, we're out of that brand. But we have a similar one — would you like to try it?",
    "The deli counter is at the back of the store. They can slice it fresh for you!",
    "Paper or plastic? Would you like help carrying those to your car?",
  ],
  doctor: [
    "I see. How long have you been experiencing these symptoms?",
    "On a scale of 1 to 10, how would you rate the discomfort?",
    "Based on what you've described, I'd like to run a few tests. Nothing to worry about.",
    "I'm prescribing a short course of medication. Take it twice daily with food.",
  ],
  restaurant: [
    "Our specials today are grilled salmon and mushroom risotto. Would you like to try either of those?",
    "Excellent choice! Would you like any appetizers or drinks to start?",
    "Sure thing! Would you prefer still or sparkling water?",
    "Your order will be ready in about 15 minutes. Is there anything else?",
  ],
  delivery: [
    "Okay, so I go left after the main gate? Is there a door code?",
    "Got it! I see the building now. Which floor are you on?",
    "I'm at your door! Sorry for the wait — the elevator was busy.",
    "You're all set! Enjoy your meal. Have a great evening!",
  ],
  interview: [
    "That's a great introduction! Can you tell me about a challenging project you've worked on?",
    "Interesting! How did you handle the technical difficulties in that project?",
    "Good answer. What are your main strengths as a developer?",
    "I see. Where do you see yourself in five years?",
  ],
  meeting: [
    "Thank you for that update. Does anyone have questions about the timeline?",
    "Good point. Let's discuss the resource allocation for next sprint.",
    "I agree with your approach. Can you prepare a detailed proposal by Friday?",
    "Let's wrap up. I'll send out the meeting notes and action items later today.",
  ],
  coworker: [
    "Oh man, those back-to-back meetings are brutal. What project are you on?",
    "Ha! Same here. Have you tried the new coffee place downstairs?",
    "Nice! Are you going to the team dinner on Friday?",
    "That sounds fun! We should grab lunch more often.",
  ],
  phone_call: [
    "Great, thanks for reviewing it. Do you have any questions about the pricing section?",
    "I understand your concern. We can definitely adjust the timeline on that.",
    "Perfect. Let me summarize the action items from our call today.",
    "Thanks for your time. I'll send a follow-up email with everything we discussed.",
  ],
  salary: [
    "I appreciate you sharing that. Can you walk me through your reasoning?",
    "That's within range. Let me also tell you about our equity package.",
    "We do have some flexibility there. What about the benefits side?",
    "I think we can make this work. Let me get the updated offer letter prepared.",
  ],
  airport: [
    "I see your booking. Would you prefer a window or aisle seat?",
    "Your luggage is 3kg over the limit. Would you like to pay the excess fee or repack?",
    "Your gate is B22. Boarding starts at 10:45. Enjoy your flight!",
    "There's a slight delay on your flight. The new departure time is 11:30.",
  ],
  hotel: [
    "Yes! I have your reservation right here. A deluxe room for 3 nights.",
    "Breakfast is served from 7 to 10am on the ground floor. WiFi password is on your key card.",
    "I'd recommend the old town for dinner — it's about a 10-minute walk from here.",
    "Is there anything else I can help you with? Enjoy your stay!",
  ],
  directions: [
    "The museum? Sure! Go straight for two blocks, then turn left at the big fountain.",
    "You'll see a red building on the corner — that's the post office. The museum is right next to it.",
    "It's about a 10-minute walk from here. Would you like me to show you on the map?",
    "Alternatively, you can take bus number 7. The stop is just around the corner.",
  ],
  travel: [
    "We have compact, sedan, and SUV available. The sedan is popular for road trips.",
    "The full coverage insurance is $15 per day. It covers everything including tires and glass.",
    "You'll need to return the car with a full tank. The nearest gas station is 2 miles from here.",
    "Here are your keys! The car is in spot B-12 in the parking garage.",
  ],
  smalltalk: [
    "Oh that sounds fun! I've been meaning to try that too. Do you go often?",
    "Really? That's interesting! I actually had a similar experience last week.",
    "Ha, I know exactly what you mean! Have you tried the new place downtown?",
    "That's awesome! What are you doing this weekend?",
  ],
  party: [
    "Oh cool! I'm actually a friend of a friend — we met at a conference last year.",
    "No way, you're into hiking too? Have you done any trails around here?",
    "That's so interesting! I've always wanted to learn more about that.",
    "We should totally exchange numbers! Let me know next time you're going.",
  ],
  neighbor: [
    "Welcome to the neighborhood! You'll love it here — very quiet and friendly.",
    "Oh, the recycling goes out on Tuesdays. The bins are the blue ones.",
    "There's a great farmers market on Saturdays, just two streets over.",
    "If you ever need anything, don't hesitate to knock. That's what neighbors are for!",
  ],
  gym: [
    "Nice! Consistency is key. Are you following any specific program?",
    "Have you tried progressive overload? It really helped me break through a plateau.",
    "I usually do a push-pull-legs split. Works great for recovery.",
    "Protein timing matters less than total daily intake. Just hit your macros!",
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

// --- Categories ---
app.get('/api/categories', (req, res) => {
  res.json([
    { id: 'all', name: 'All', icon: '🌟' },
    { id: 'daily', name: 'Daily Life', icon: '🏠' },
    { id: 'work', name: 'Work', icon: '💼' },
    { id: 'travel', name: 'Travel', icon: '✈️' },
    { id: 'social', name: 'Social', icon: '💬' },
  ])
})

// --- Scenarios ---
app.get('/api/scenarios', (req, res) => {
  const category = req.query.category
  let list = SCENARIOS
  if (category && category !== 'all') {
    list = list.filter((s) => s.category === category)
  }
  res.json(list)
})

app.get('/api/scenarios/:id', (req, res) => {
  const s = SCENARIOS.find((x) => x.id === req.params.id)
  if (!s) return res.status(404).json({ detail: 'Scenario not found' })
  res.json(s)
})

app.get('/api/scenarios/:id/sentences', (req, res) => {
  const mockSentences = {
    coffee_shop: ["I'd like a medium latte with oat milk, please.", "Could I also get a blueberry muffin to go?", "Do you have any seasonal specials today?"],
    interview: ["I have three years of experience in software development.", "My biggest strength is my ability to learn quickly.", "I led a team of five engineers on that project."],
    default: ["I would like to practice my English pronunciation.", "Could you help me with this, please?", "Thank you for your time today."],
  }
  const sentences = mockSentences[req.params.id] || mockSentences.default
  res.json({ scenario_id: req.params.id, sentences })
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
  res.setHeader('X-Accel-Buffering', 'no')
  res.flushHeaders()

  // Simulated user text
  const mockUserText = "I have been working on a project for the past few months and it has been a great learning experience."

  // Simulate error scenario if audio is missing
  if (!req.file) {
    setTimeout(() => {
      res.write(`event: error\ndata: ${JSON.stringify({ message: "No audio file provided" })}\n\n`)
      res.end()
    }, 200)
    return
  }

  // 1. ASR event (after 300ms)
  setTimeout(() => {
    res.write(`event: asr\ndata: ${JSON.stringify({ text: mockUserText })}\n\n`)
  }, 300)

  // 2. Split reply into sentences and stream them with index
  const sentences = replyText.match(/[^.!?]+[.!?]+/g) || [replyText]
  sentences.forEach((sentence, i) => {
    setTimeout(() => {
      res.write(`event: sentence\ndata: ${JSON.stringify({
        index: i,
        text: sentence.trim(),
        audio_url: `/audio/mock_${sid}_${i}.mp3`,
      })}\n\n`)
    }, 600 + i * 400)
  })

  // 3. Corrections (randomly) + Feedback
  setTimeout(() => {
    if (Math.random() > 0.4) {
      const correction = MOCK_CORRECTIONS[Math.floor(Math.random() * MOCK_CORRECTIONS.length)]
      res.write(`event: corrections\ndata: ${JSON.stringify([correction])}\n\n`)
    }
    // Always send feedback
    const feedbacks = [
      '🎯 Great sentence structure!',
      '💡 Try using more specific vocabulary next time.',
      '✨ Nice use of connectors!',
      '🎯 Good job expressing your opinion clearly!',
    ]
    res.write(`event: feedback\ndata: ${JSON.stringify({ text: feedbacks[Math.floor(Math.random() * feedbacks.length)] })}\n\n`)
  }, 600 + sentences.length * 400 + 200)

  // 4. Done event with full_reply
  setTimeout(() => {
    res.write(`event: done\ndata: ${JSON.stringify({
      session_id: sid,
      full_reply: replyText,
      turn_count: 1,
    })}\n\n`)
    res.end()
  }, 600 + sentences.length * 400 + 400)
})

// Serve mock audio — generate a tiny silence mp3 on-the-fly for /audio/mock_*
app.get('/audio/mock_:rest', (req, res) => {
  // Minimal valid MP3 frame (MPEG1 Layer3, 128kbps, 44100Hz, silence, ~26ms)
  const silentMp3 = Buffer.from(
    'SUQzBAAAAAAAI1RTU0UAAAAPAAADTGF2ZjU4Ljc2LjEwMAAAAAAAAAAAAAAA//tQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAWGluZwAAAA8AAAACAAABhgC7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7//////////////////////////////////////////////////////////////////8AAAAATGF2YzU4LjEzAAAAAAAAAAAAAAAAJAAAAAAAAAAAAYYoRwmHAAAAAAD/+1DEAAAHAAGf9AAAIgAAM/8AAABM',
    'base64'
  )
  res.setHeader('Content-Type', 'audio/mpeg')
  res.setHeader('Content-Length', silentMp3.length)
  res.end(silentMp3)
})

// --- Pronunciation Assessment ---
app.post('/api/assess', upload.single('audio'), (req, res) => {
  const referenceText = req.body?.reference_text || ''
  const words = referenceText.split(/\s+/).filter(Boolean)

  setTimeout(() => {
    res.json({
      pronunciation_score: Math.floor(70 + Math.random() * 25),
      accuracy_score: Math.floor(65 + Math.random() * 30),
      fluency_score: Math.floor(60 + Math.random() * 35),
      completeness_score: Math.floor(75 + Math.random() * 25),
      words: words.map((w) => ({
        word: w,
        accuracy_score: Math.floor(55 + Math.random() * 45),
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
    report: '本次面试练习表现不错，共完成6轮对话。主要问题集中在主谓一致和冠词使用上，建议多关注第三人称单数的动词变化。整体流利度良好，继续保持每天练习的节奏！',
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

// --- Hint System ---
app.post('/api/hint', upload.none(), (req, res) => {
  setTimeout(() => {
    res.json({
      hints: [
        { text: "Could you tell me more about that?", hint: "能多说一些吗？", difficulty: "easy" },
        { text: "That's interesting! I've actually had a similar experience.", hint: "有意思，我也有类似的经历", difficulty: "medium" },
        { text: "I'd love to hear your perspective on this matter.", hint: "我想听听你对这件事的看法", difficulty: "hard" },
      ],
    })
  }, 300)
})

// --- Level Test ---
app.get('/api/level-test/questions', (req, res) => {
  res.json([
    { index: 0, difficulty: 'A1', prompt: "Can you introduce yourself? Tell me your name, where you're from, and what you do." },
    { index: 1, difficulty: 'A2', prompt: "What did you do last weekend? Tell me about it in a few sentences." },
    { index: 2, difficulty: 'B1', prompt: "If you could live anywhere in the world, where would you choose and why?" },
    { index: 3, difficulty: 'B2', prompt: "Some people say AI will replace most jobs. What's your opinion?" },
    { index: 4, difficulty: 'C1', prompt: "Describe a significant challenge you overcame and what it taught you." },
  ])
})

app.post('/api/level-test/assess', upload.none(), (req, res) => {
  setTimeout(() => {
    res.json({
      assessment: {
        level: 'B1',
        scores: { grammar: 6, vocabulary: 7, fluency: 5, task_completion: 7 },
        strengths: ['vocabulary range', 'task completion'],
        weaknesses: ['grammar accuracy', 'fluency'],
        summary: '你的词汇量不错，能完成大部分交际任务，但语法准确度和流利度还有提升空间。',
        recommendations: ['Practice speaking in longer sentences', 'Focus on verb tenses in daily conversation'],
      },
      profile: { id: 'default_user', level: 'B1' },
    })
  }, 1000)
})

// --- User Profile ---
app.get('/api/profile', (req, res) => {
  res.json({
    id: 'default_user',
    level: null,
    strengths: [],
    weaknesses: [],
    character_affinity: {},
    total_sessions: 0,
    total_turns: 0,
  })
})

app.get('/api/profile/memory/:scenarioId', (req, res) => {
  res.json({ memories: [], affinity_level: 1 })
})

// --- Talent Agent Integration ---
app.get('/api/integrations/talent-agent/status', (req, res) => {
  res.json({ status: 'unavailable', error: 'Talent Agent not configured (mock mode)' })
})

app.post('/api/integrations/talent-agent/interview-prep', upload.none(), (req, res) => {
  res.json({
    key_skills: ['React', 'TypeScript', 'Node.js'],
    focus_areas: ['System Design', 'Performance Optimization'],
    difficulty_level: 'intermediate',
  })
})

app.post('/api/integrations/talent-agent/sync', upload.none(), (req, res) => {
  res.json({ synced: false, error: 'Talent Agent not configured (mock mode)' })
})

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
