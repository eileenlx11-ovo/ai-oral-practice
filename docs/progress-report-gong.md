# AI Oral Practice 进度同步

> 给龚 — 2026-06-06

## 目前是什么

一个独立的英语口语练习网页应用，核心玩法：

1. **场景对话** — 选一个场景（面试/餐厅/会议/旅行/闲聊），跟 AI 语音对话，AI 会实时纠语法
2. **发音评测** — 给一句话，录音后逐词打分（综合 / 准确度 / 流利度 / 完整度）
3. **模拟面试联动** — 从 talent-agent 的面试准备页一键发起，自动带入 JD + 简历 + 项目上下文

技术栈：Vue 3 前端 + FastAPI 后端 + 腾讯 SOE 发音评测 + Azure Speech 高级诊断

## 当前状态

| 模块 | 状态 | 备注 |
|------|------|------|
| 后端 API | ✅ 完成 | 对话/评测/流式/session 全通 |
| 发音评测 | ✅ 双 provider 跑通 | SOE 日常，Azure 高级 |
| 前端页面 | ✅ 可用 | 首页/对话/评测/看板 |
| talent-agent 联动 | ✅ 接口通 | 尚未完整联调 |
| 部署上线 | ❌ 未部署 | DNS 已配，Caddy + Docker 待写 |
| 测试 | ⚠️ 后端 24/24 pass | 前端无自动化测试 |

**网页还没上线**，目前只能本地 `npm run dev` + `uvicorn` 看效果。

## 架构一览

```
浏览器
  ├── / 首页（选场景）
  ├── /chat/:scenario 语音对话
  ├── /chat/interview?session_id=xxx 外部面试（talent-agent 跳转过来）
  ├── /pronunciation 发音评测
  └── /dashboard 学习进度

FastAPI 后端 (:8000)
  ├── /api/chat — 非流式对话（ASR → LLM → TTS）
  ├── /api/stream — 流式对话（SSE，逐句返回）
  ├── /api/assess — 发音评测
  ├── /api/assess/status — 查当前可用 provider
  └── /api/sessions/custom — 外部创建自定义面试 session
```

发音评测分层：
- **日常**（默认）：腾讯 SOE → mock fallback
- **高级诊断**（`advanced=true`）：Azure Speech → SOE → mock

## 你本地跑起来需要什么

1. `git clone` 然后切分支 `feat/custom-interview-session`
2. Python 3.10+，在 `assessment/` 下 `pip install -r requirements.txt`
3. 装 **ffmpeg**（Azure 需要把 webm 转 WAV，后端自动调）
4. `.env` 我私发你，放项目根目录（**别提交**）
5. 前端：`cd frontend && npm install && npm run dev`
6. 后端：`cd assessment && uvicorn app:app --reload --port 8000`

## 关于 Azure 和 SOE 的使用

**你开发/测试可以直接用**，共享一套 key：

- **SOE**：腾讯子账号，额度充足，随便调，日常开发用这个就行
- **Azure Speech**：Korea Central 区域 F0 免费层，**每月 5 小时**。测试够用，但别拿它跑批量音频

两个都配在 `.env` 里，代码自动识别可用性并 fallback。

## 可能需要你帮忙的

我白天在上实验课，能回消息但不方便长时间写代码。下面这些如果你有空可以推进：

### 优先级高
- [ ] **双服务联调**：同时起 oral-practice(:3001) + talent-agent(:3000)，从面试页点「语音模拟面试」按钮，确认整个流程走通
- [ ] **前端细节打磨**：对话页面的 loading 状态、错误提示、断网处理

### 可以做
- [ ] **「详细诊断」按钮**：发音评测页加个切换，后端已支持 `advanced=true` 参数
- [ ] **写几个前端单测**：`frontend/__tests__/` 下面目前是空的

### 我来做
- [ ] 部署上线（Caddy 反代 + Docker + HTTPS）
- [ ] PR review 和 merge
- [ ] 后端新功能/评测逻辑

## 规矩

1. **`.env` 不能提交** — .gitignore 已排除，但小心 `git add .`
2. **commit 格式** — 英文 conventional commits：`feat:`, `fix:`, `docs:`
3. **改了后端跑测试** — `cd assessment && pytest`，确认全绿再 push
4. **分支** — 在 `feat/custom-interview-session` 上开发，别动 main

## 依赖清单

| 工具 | 用途 | 必须装 |
|------|------|--------|
| Python 3.10+ | 后端 | ✓ |
| Node 18+ | 前端 | ✓ |
| ffmpeg | 音频转码 | ✓（Azure 必须） |
| azure-cognitiveservices-speech | 发音评测 | 在 requirements.txt |
| tencentcloud-sdk-python | SOE 评测 | 在 requirements.txt |

## 接下来的路线

1. 联调通过 → 部署 `speak.projfit.top`
2. 加学习数据统计（每日练习时长、分数趋势）
3. 接入更多场景 / 支持自定义场景
4. 考虑做成小程序或套壳 App

有问题随时问我，实验课间隙能回。
