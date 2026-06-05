# AI English Oral Practice（AI 英语口语陪练）

> 七牛云 XEngineer 第三批 · 题目一

一款面向英语学习者的 AI 口语陪练应用，支持多场景对话、实时语音交互、发音评测、语法纠错和可量化的学习反馈。

## 功能特性

- 🎭 **场景选择**：面试、点餐、会议、旅行等多种真实场景
- 🎙️ **语音对话**：浏览器端录音 → ASR 识别 → LLM 对话 → TTS 语音回复
- 📝 **发音评测**：音素级打分、流利度/语调评估
- ✏️ **语法纠错**：实时语法和表达问题标注
- 📊 **进步看板**：历史评分趋势、课后总结报告

## 项目结构

```
ai-oral-practice/
├── /voice              ← 龚琳茜负责
│   ├── audio/          音频采集、VAD 静音检测
│   ├── asr/            ASR 语音识别接入
│   └── tts/            TTS 语音合成与播放
├── /assessment         ← 陈嘉豪负责
│   ├── scoring/        发音评测、语法纠错
│   ├── feedback/       课后总结、进步追踪
│   └── scenarios/      场景管理、面试题库
├── /frontend           ← 各自建各自的页面
│   ├── chat/           龚琳茜：对话界面、场景选择
│   ├── dashboard/      陈嘉豪：进步看板
│   └── src/            Vue 入口 & 全局样式
├── /shared             ← 共用类型定义、配置
├── docker-compose.yml
└── README.md
```

## 技术栈

### 前端 + 语音交互（龚琳茜）
- Vue 3 + Vite
- Web Audio API / MediaRecorder（录音 + VAD）
- Azure Speech Services / 讯飞（ASR + TTS）

### 后端 + 评测（陈嘉豪）
- Python + FastAPI
- Azure Speech 发音评测
- OpenAI / 智谱 API（LLM 对话 + 纠错）
- Chart.js（进步看板可视化）

### 部署
- Docker + docker-compose
- Nginx（静态资源 + 反向代理）

## 快速开始

### 环境要求
- Node.js >= 18
- Python >= 3.10（后端）

### 前端本地开发

```bash
cd frontend
npm install
npm run dev
# 访问 http://localhost:3000
```

### Docker 启动

```bash
cp .env.example .env
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

## 团队分工

| 成员 | 角色 | 负责模块 |
|------|------|----------|
| 陈嘉豪 | 后端/算法 | assessment（LLM 对话、发音评测、语法纠错、场景管理）、dashboard 页面 |
| 龚琳茜 | 前端/语音交互 | voice（录音、ASR、TTS）、chat 对话界面、场景选择页面 |

## License

MIT
