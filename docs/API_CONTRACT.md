# API 接口契约文档

> 前后端联调参考，基于 `assessment/app.py` 实际实现整理

## Base URL

- 开发环境：`http://localhost:8001`（mock）或 `http://localhost:8000`（真实后端）
- Vite 代理：前端请求 `/api/*` 自动转发到后端

---

## 1. 场景管理

### GET /api/scenarios
返回所有可用场景列表。

**Response:**
```json
[
  { "id": "interview", "icon": "💼", "name": "Job Interview", "description": "..." },
  { "id": "restaurant", "icon": "🍽️", "name": "Restaurant", "description": "..." }
]
```

### GET /api/scenarios/:id
返回单个场景详情，包含 greeting。

**Response:**
```json
{
  "id": "interview",
  "icon": "💼",
  "name": "Job Interview",
  "description": "模拟英语面试场景",
  "greeting": "Hello! I'm your interviewer today..."
}
```

---

## 2. 语音对话

### POST /api/chat（非流式）
发送录音，返回完整对话结果。

**Request:** `multipart/form-data`
| Field | Type | Description |
|-------|------|-------------|
| audio | File | WebM/Opus 录音文件 |
| scenario | string | 场景 ID |
| history | string | JSON 序列化的对话历史 `[{role, content}]` |

**Response:**
```json
{
  "user_text": "用户语音识别结果",
  "reply_text": "AI 回复文本",
  "reply_audio_url": "/audio/xxx.mp3",
  "corrections": [{ "original": "...", "corrected": "...", "explanation": "..." }],
  "pronunciation": { "overall": 82, "words": [] },
  "session_id": "uuid"
}
```

### POST /api/stream（SSE 流式）
发送录音，通过 Server-Sent Events 逐步返回结果。

**Request:** 同 `/api/chat`，额外字段 `session_id`

**Response:** `text/event-stream`
```
event: asr
data: {"text": "用户说的话"}

event: sentence
data: {"text": "AI 回复的一句话", "audio_url": "/audio/xxx.mp3"}

event: corrections
data: [{"original": "...", "corrected": "...", "explanation": "..."}]

event: done
data: {"session_id": "uuid"}

event: error
data: {"message": "错误描述"}
```

### POST /api/asr（仅识别）
只做语音转文字，不触发 LLM 对话。

**Request:** `multipart/form-data` — `audio` (File)

**Response:**
```json
{ "text": "识别出的文本" }
```

---

## 3. 发音评估

### POST /api/assess
对比参考文本评估发音质量。

**Request:** `multipart/form-data`
| Field | Type | Description |
|-------|------|-------------|
| audio | File | 录音文件 |
| reference_text | string | 参考文本 |

**Response:**
```json
{
  "overall": 82,
  "words": [
    { "word": "hello", "accuracy": 95, "error_type": "none" },
    { "word": "world", "accuracy": 67, "error_type": "mispronunciation" }
  ]
}
```

---

## 4. 会话管理

### POST /api/sessions — 创建会话
**Request:** `scenario` (form field)
**Response:** `{ "session_id": "uuid" }`

### GET /api/sessions — 列表
**Query:** `limit`, `offset`
**Response:**
```json
[
  {
    "session_id": "...",
    "scenario": "interview",
    "started_at": "2026-06-05T10:00:00Z",
    "turns": 8,
    "avg_pronunciation": 78,
    "avg_fluency": 72
  }
]
```

### GET /api/sessions/:id/summary
**Response:**
```json
{
  "scenario": "interview",
  "total_turns": 6,
  "avg_pronunciation": 79,
  "avg_fluency": 74,
  "avg_accuracy": 81,
  "total_corrections": 3,
  "common_errors": [{ "pattern": "Subject-verb agreement", "count": 2 }]
}
```

### POST /api/sessions/:id/end — 结束会话
**Response:** 同 summary 格式

---

## 5. 学习进度

### GET /api/progress
**Response:**
```json
{
  "total_sessions": 15,
  "total_turns": 87,
  "total_corrections": 23,
  "avg_pronunciation": 78,
  "score_history": [
    { "date": "2026-06-01", "avg_pronunciation": 72, "avg_fluency": 68, "avg_accuracy": 74 }
  ]
}
```

---

## 6. 静态资源

### GET /audio/:filename
TTS 生成的 MP3 文件。

---

## 环境变量

| 变量 | 用途 | 必填 |
|------|------|------|
| LLM_API_KEY | LLM 对话 | ✅ |
| LLM_BASE_URL | LLM 端点 | ✅ |
| LLM_MODEL | 模型名 | 否（默认 deepseek-chat） |
| SILICONFLOW_API_KEY | ASR 语音识别 | ✅ |
| AZURE_SPEECH_KEY | 发音评估 | 否（无则 /api/assess 返回 503） |
| AZURE_SPEECH_REGION | Azure 区域 | 否（默认 eastasia） |
