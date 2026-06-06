# AI English Oral Practice（AI 英语口语陪练）

> 七牛云 XEngineer 第三批 · 题目一

一款面向英语学习者的 AI 口语陪练应用，支持多场景对话、实时语音交互、发音评测、语法纠错和可量化的学习反馈。

**🌐 在线体验：https://speak.projfit.top**

**🎬 Demo 视频：** <!-- TODO: 补充 bilibili/云盘链接 -->

## 功能特性

| 模块 | 说明 |
|------|------|
| 🎭 场景选择 | 18 个真实场景（咖啡厅/医院/面试/会议等），分类/难度/角色人设 |
| 🎙️ 实时语音对话 | 录音 → ASR → LLM 生成回复 → TTS 语音播放，全链路 SSE 流式 |
| 📝 发音评测 | 逐词评分 + 诊断反馈（漏读/发音错误/多读）+ 改进建议 |
| ✏️ 语法纠错 | 对话中实时标注语法和表达问题 |
| 📊 进步看板 | 图表 + 历史记录 + 详情弹窗 |
| 📋 课后报告 | 3 轮对话后可结束，LLM 生成总结 |
| 💡 Hint 提示 | 10s 沉默触发 + 点击获取 |
| 🎯 水平评估 | 5 题测试 → CEFR 等级 |
| 🔗 外部集成 | talent-agent 一键发起自定义面试 |

## 技术架构

```
浏览器（Vue 3 + Web Audio API）
    ↕ SSE / REST
FastAPI 后端
    ├── ASR: SiliconFlow SenseVoiceSmall（language=en）
    ├── LLM: Deepseek Chat（对话 + 纠错 + 报告）
    ├── TTS: SiliconFlow CosyVoice → Azure Speech SDK → edge-tts
    ├── 发音评测: 腾讯 SOE 新版（WebSocket）→ Azure Speech → mock
    └── Session 存储: JSON 文件（MVP）
```

## 项目结构

```
ai-oral-practice/
├── assessment/          ← 后端（FastAPI）
│   ├── app.py           主路由
│   ├── scoring/         发音评测（多 provider 调度）
│   ├── feedback/        Session 存储 + 进度追踪
│   ├── scenarios/       18 个场景配置
│   ├── streaming.py     SSE 流式 + TTS 合成
│   ├── correction.py    语法纠错
│   ├── level_test.py    水平评估
│   ├── hints.py         Hint 提示
│   └── Dockerfile
├── frontend/            ← 前端（Vue 3 + Vite）
│   ├── chat/            对话界面 + 首页
│   ├── pronunciation/   发音评测页
│   ├── assessment/      水平评估页
│   ├── dashboard/       进步看板
│   ├── composables/     网络状态检测等
│   ├── e2e/             E2E 测试（Playwright）
│   └── Dockerfile
├── voice/               ← 音频采集 + ASR 服务层
├── shared/              ← 共用配置
├── mock-server/         ← Mock API（前端独立开发用）
├── deploy/              ← 部署配置（nginx + 脚本）
└── docker-compose.prod.yml
```

## 快速开始

### 环境要求

- Node.js >= 18
- Python >= 3.10
- ffmpeg（发音评测音频转换）

### 本地开发

```bash
# 1. 后端
cd assessment
cp ../.env.example ../.env  # 填入 API keys
pip install -r requirements.txt
uvicorn assessment.app:app --reload --port 8001

# 2. 前端
cd frontend
npm install
npm run dev
# 访问 http://localhost:3000（Vite 代理 /api → :8001）
```

### 生产部署（Docker）

```bash
cp .env.example .env  # 填入 API keys
docker compose -f docker-compose.prod.yml up -d --build
# 配合 nginx 反代 + certbot HTTPS
```

### 运行测试

```bash
# 后端
cd assessment && python -m pytest tests/

# 前端
cd frontend && npm test
```

## 环境变量

| 变量 | 用途 | 必须 |
|------|------|------|
| `LLM_API_KEY` | LLM 对话（Deepseek） | ✓ |
| `LLM_BASE_URL` | LLM API 地址 | ✓ |
| `LLM_MODEL` | 模型名 | ✓ |
| `SILICONFLOW_API_KEY` | ASR + TTS | ✓ |
| `AZURE_SPEECH_KEY` | Azure 发音评测 + TTS fallback | 可选 |
| `AZURE_SPEECH_REGION` | Azure 区域 | 可选 |
| `TENCENT_APP_ID` | 腾讯 SOE 新版 | 可选 |
| `TENCENT_SECRET_ID` | 腾讯云密钥 | 可选 |
| `TENCENT_SECRET_KEY` | 腾讯云密钥 | 可选 |
| `CORS_ORIGINS` | 允许的跨域来源（逗号分隔） | 生产必须 |

## 第三方依赖

| 依赖 | 用途 | 许可证 |
|------|------|--------|
| Vue 3 | 前端框架 | MIT |
| Vite | 构建工具 | MIT |
| FastAPI | 后端框架 | MIT |
| Azure Speech SDK | 发音评测 / TTS fallback | Microsoft |
| OpenAI SDK | LLM 对话 + ASR 调用 | MIT |
| tencentcloud-sdk-python | 腾讯 SOE | Apache 2.0 |
| websocket-client | SOE 新版 WebSocket | Apache 2.0 |
| edge-tts | TTS 备选 | MIT |
| Playwright | E2E 测试 | Apache 2.0 |

## 团队分工

| 成员 | GitHub | 负责模块 |
|------|--------|----------|
| 陈嘉豪 | @DNMCJH | 后端架构、发音评测、部署运维、安全加固 |
| 龚琳茜 | @eileenlx11-ovo | 前端交互、语音链路、场景系统、E2E 测试 |

## License

MIT
