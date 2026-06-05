# AI English Oral Practice（AI 英语口语陪练）

> 七牛云 XEngineer 第三批 · 题目一

一款面向英语学习者的 AI 口语陪练应用，支持多场景对话、实时语音交互、发音评测、语法纠错和可量化的学习反馈。

## 功能特性

- 🎭 **场景选择**：面试、点餐、会议、旅行等多种真实场景
- 🎙️ **语音对话**：浏览器端录音 → ASR 识别 → LLM 对话 → TTS 语音回复
- 📝 **发音评测**：音素级打分、流利度/语调评估
- ✏️ **语法纠错**：实时语法和表达问题标注
- 📊 **进步看板**：历史评分趋势、课后总结报告

## 技术栈

### 前端
- Vue 3 + Vite
- Web Audio API / MediaRecorder（录音）
- Chart.js（进步看板可视化）

### 后端
- Python + FastAPI
- Azure Speech Services / 讯飞（ASR + TTS + 发音评测）
- OpenAI / 智谱 API（LLM 对话 + 纠错）

### 部署
- Docker + docker-compose
- Nginx（静态资源 + 反向代理）

## 项目结构

```
ai-oral-practice/
├── frontend/           # Vue 3 前端
│   ├── src/
│   │   ├── views/      # 页面
│   │   ├── components/ # 组件
│   │   ├── composables/# 可复用逻辑
│   │   └── assets/     # 静态资源
│   └── package.json
├── backend/            # Python FastAPI 后端
│   ├── app/
│   │   ├── routers/    # 路由
│   │   ├── services/   # 业务逻辑
│   │   └── models/     # 数据模型
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

## 快速开始

### 环境要求
- Node.js >= 18
- Python >= 3.10
- Docker & docker-compose（部署用）

### 本地开发

```bash
# 前端
cd frontend
npm install
npm run dev

# 后端
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Docker 一键启动

```bash
cp .env.example .env
# 编辑 .env 填入 API Key
docker-compose up --build
```

## 第三方依赖

| 依赖 | 用途 | 许可证 |
|------|------|--------|
| Vue 3 | 前端框架 | MIT |
| Vite | 构建工具 | MIT |
| Chart.js | 图表可视化 | MIT |
| FastAPI | 后端框架 | MIT |
| Azure Speech SDK | ASR/TTS/发音评测 | Microsoft |
| OpenAI SDK | LLM 对话 | MIT |
| Pydantic | 数据校验 | MIT |

## 团队分工

| 成员 | 角色 | 负责模块 |
|------|------|----------|
| 陈嘉豪 | 后端/算法 | LLM 对话、发音评测、语法纠错、场景管理、进步数据 |
| 龚琳茜 | 前端/语音交互 | 对话 UI、录音/播放、场景选择页面、评测展示、进步看板 |

## License

MIT
