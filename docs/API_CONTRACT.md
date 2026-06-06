# API 接口契约文档

> 前后端联调参考，基于 `assessment/app.py` 实际实现整理

## Base URL

- 开发环境：`http://localhost:8001`（mock）或 `http://localhost:8000`（真实后端）
- Vite 代理：前端请求 `/api/*` 自动转发到后端

## 认证

多数学习接口支持游客模式；未带 token 时数据归入 `default_user`。登录后需要在请求头带：

```http
Authorization: Bearer <jwt>
```

`/api/settings` 必须登录。

---

## 1. 认证与设置

### POST /api/auth/register
邮箱注册。

**Request:** `multipart/form-data`
| Field | Type | Description |
|-------|------|-------------|
| email | string | 邮箱 |
| password | string | 密码，至少 6 位 |
| nickname | string | 可选昵称 |

**Response:**
```json
{ "token": "...", "user": { "id": "a@example.com", "email": "a@example.com", "nickname": "a" } }
```

### POST /api/auth/login
邮箱登录。字段：`email`, `password`。

### POST /api/auth/send-code
发送手机验证码。字段：`phone`。开发模式可能返回 `_dev_code` 方便演示。

### POST /api/auth/phone-login
手机号验证码登录/自动注册。字段：`phone`, `code`。

### GET /api/auth/me
返回当前登录用户，需要 `Authorization`。

### GET /api/settings / PUT /api/settings
读取/更新当前用户设置，需要 `Authorization`。

**PUT Request:** `multipart/form-data`
| Field | Type | Description |
|-------|------|-------------|
| nickname | string | 昵称 |
| voice | string | `VOICES` 中的 voice key |
| locale | string | `zh` 或 `en` |
| theme | string | `light` / `dark` / `system` |

---

## 2. 场景管理

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

### GET /api/categories
返回场景分类。

### GET /api/voices
返回可用口音/声音配置。

### GET /api/characters
返回可切换的角色列表。

**Response:**
```json
[
  {
    "id": "coffee_shop",
    "name": "Maya",
    "avatar": "👩‍🦱",
    "role": "Barista at a cozy coffee shop",
    "voice": "american_female"
  }
]
```

---

## 3. 语音对话

### POST /api/chat（非流式）
发送录音，返回完整对话结果。

**Request:** `multipart/form-data`
| Field | Type | Description |
|-------|------|-------------|
| audio | File | WebM/Opus 录音文件 |
| scenario | string | 场景 ID |
| history | string | JSON 序列化的对话历史 `[{role, content}]` |
| session_id | string | 可选；传入时必须属于当前用户/游客 |

**Response:**
```json
{
  "user_text": "用户语音识别结果",
  "reply_text": "AI 回复文本",
  "reply_audio_url": "/audio/xxx.mp3",
  "corrections": [{ "original": "...", "corrected": "...", "explanation": "..." }],
  "pronunciation": null,
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
data: {"phase": "asr", "code": "asr_failed", "message": "语音识别失败，请重试", "action": "retry"}
```

`error` 事件始终保留 `message` 字段，前端可继续按旧逻辑展示错误。新增字段用于诊断：

| Field | Description |
|-------|-------------|
| phase | 出错阶段，如 `asr` / `llm` |
| code | 稳定错误码，如 `asr_failed` / `no_speech` / `llm_failed` |
| action | 建议动作，如 `retry` |

TTS 单句合成失败不会终止 SSE；对应 `sentence.audio_url` 可能为 `null`，文本仍会继续返回。

### POST /api/asr（仅识别）
只做语音转文字，不触发 LLM 对话。

**Request:** `multipart/form-data` — `audio` (File)

**Response:**
```json
{ "text": "识别出的文本" }
```

### POST /api/tts
生成标准发音示范音频，返回 `audio/mpeg`。字段：`text`，最多 500 字符。

### GET /api/tts-preview
设置页试听接口。Query：`voice`, `text`。返回 `audio/mpeg`。

---

## 4. 发音评估

### POST /api/assess
对比参考文本评估发音质量。

**Request:** `multipart/form-data`
| Field | Type | Description |
|-------|------|-------------|
| audio | File | 录音文件 |
| reference_text | string | 参考文本 |
| advanced | string | 可选；`true` 时优先 Azure，包含韵律能力 |

**Response:**
```json
{
  "accuracy_score": 86.5,
  "fluency_score": 78.0,
  "completeness_score": 92.0,
  "pronunciation_score": 84.0,
  "prosody_score": 80.0,
  "provider": "azure",
  "words": [
    { "word": "hello", "accuracy_score": 95, "error_type": "None" },
    { "word": "world", "accuracy_score": 67, "error_type": "Mispronunciation" }
  ]
}
```

### GET /api/assess/status
返回当前发音评测 provider 状态。

```json
{
  "available": true,
  "provider": "tencent",
  "is_mock": false,
  "advanced_available": true,
  "advanced_provider": "azure",
  "providers": {
    "tencent_configured": true,
    "azure_configured": true,
    "mock_enabled": false
  },
  "ffmpeg_available": true
}
```

---

## 5. 会话管理

会话接口支持游客模式；登录后只返回/操作当前用户自己的 session。直接访问不属于自己的 `session_id` 返回 404。

### POST /api/sessions — 创建会话
**Request:** `scenario` (form field)
**Response:** `{ "session_id": "uuid" }`

### POST /api/sessions/custom — 创建自定义面试会话
**Request:** `jd_text`, `resume_text`, `project_context` 至少一个非空。

### GET /api/sessions — 列表
**Query:** `limit`, `offset`
**Response:**
```json
[
  {
    "session_id": "...",
    "user_id": "default_user",
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

### POST /api/sessions/:id/turns
手动记录一轮对话。字段：`user_text`, `reply_text`, `corrections`, `pronunciation`。

### POST /api/sessions/:id/character
切换当前会话角色/场景，下一轮对话将使用新角色 prompt 和 voice。该 session 必须属于当前用户/游客。

**Request:** `multipart/form-data`
| Field | Type | Description |
|-------|------|-------------|
| scenario | string | 新角色对应的 scenario id |
| voice | string | 可选，覆盖角色默认 voice |

**Response:**
```json
{
  "session_id": "abc123",
  "scenario": "coffee_shop",
  "character": {
    "name": "Maya",
    "avatar": "👩‍🦱",
    "role": "Barista at a cozy coffee shop",
    "personality": "...",
    "speaking_style": "...",
    "background": "...",
    "voice": "american_female"
  },
  "voice": "british_female",
  "voice_id": "en-GB-SoniaNeural"
}
```

---

## 6. 学习进度

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
  ],
  "streak": {
    "current": 3,
    "longest": 7,
    "active_dates": ["2026-06-04", "2026-06-05", "2026-06-06"],
    "daily_counts": { "2026-06-06": 2 }
  },
  "weakness": {
    "common_grammar_errors": [{ "pattern": "Wrong tense", "count": 4 }],
    "weak_scenarios": [{ "scenario": "interview", "avg_score": 62.5, "sessions": 2 }],
    "low_dimension": "pronunciation"
  },
  "scenario_distribution": { "interview": 3, "coffee_shop": 2 }
}
```

---

## 7. Hint / 水平评估 / 用户画像

### POST /api/hint
生成 2-3 个上下文提示。字段：`scenario`, `history`。

### GET /api/level-test/questions
获取水平评估问题。

### POST /api/level-test/assess
提交水平评估回答。字段：`responses`，JSON 字符串数组。

### GET /api/profile
获取当前用户/游客画像。

### GET /api/profile/memory/:scenario_id
获取角色记忆和亲密度等级。

---

## 8. Talent Agent 集成

### GET /api/integrations/talent-agent/status
检查 talent-agent 可达性。

### POST /api/integrations/talent-agent/interview-prep
字段：`jd_text`, `language`。

### POST /api/integrations/talent-agent/sync
字段：`session_id`，必须属于当前用户/游客。

---

## 9. 静态资源

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
| TENCENT_APP_ID / TENCENT_APPID | 腾讯 SOE 新版 AppID | 推荐 |
| TENCENT_SECRET_ID | 腾讯云 API SecretId | 推荐 |
| TENCENT_SECRET_KEY | 腾讯云 API SecretKey | 推荐 |
| AZURE_SPEECH_KEY | Azure 高级发音评估 | 可选 |
| AZURE_SPEECH_REGION | Azure 区域 | 否（默认 eastasia） |
| TENCENT_SMS_SECRET_ID | 腾讯云短信 SecretId | 可选 |
| TENCENT_SMS_SECRET_KEY | 腾讯云短信 SecretKey | 可选 |
| TENCENT_SMS_APP_ID | 腾讯云短信 AppId | 可选 |
| TENCENT_SMS_SIGN | 腾讯云短信签名 | 可选 |
| TENCENT_SMS_TEMPLATE_ID | 腾讯云短信模板 ID | 可选 |
| JWT_SECRET | JWT 签名密钥 | 生产必须 |
| CORS_ORIGINS | 允许跨域来源，逗号分隔 | 生产必须 |
| PRONUNCIATION_ALLOW_MOCK | 是否允许 mock 评分，生产设 `0` | 生产建议 |
