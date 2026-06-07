# 交接任务：talent-agent → 口语助手「项目联动」补全

**Owner**: codex
**From**: claude（已核实口语侧现状，2026-06-07）
**Scope**: 跨项目 —— talent-agent（求职端）+ ai-oral-practice（口语端）

## 背景 / 真实现状（已核实，别从零设计）

用户问题原话：「我在 talent-agent 那边导入的项目能在口语这边用吗？」

核实结论：**口语侧的接收管道已经建好，缺的是 talent-agent 侧的"跳转出口"**。不要重做口语侧。

口语侧已有的东西（已部署、能用）：

1. **接口** `POST /api/integrations/talent-agent/oral-interview-session`
   （`assessment/app.py:1647`）已接受三个表单字段：
   - `jd_text`、`resume_text`、`project_context`、`language`
   - 三者至少填一个即可建面试 session；其中 `jd_text` 还会回调 talent-agent
     的 `/match` 拿 key_skills / focus_areas / difficulty 丰富面试 prompt。
   - 返回 `{session_id, redirect_url, greeting, ...}`，前端据此跳进 `/chat/interview`。

2. **前端面试准备页** `frontend/interview/InterviewPrepView.vue`：
   - 已有 JD / 简历 / 项目 三个文本框（手动粘贴可用）。
   - **已支持 URL query 预填**：`route.query.jd / resume / project / language`
     （见 `InterviewPrepView.vue:80-82`）。
   - 路由是 `/interview-prep`（HomeView 有入口按钮）。

   ⇒ 即：talent-agent 只要把用户已导入的项目数据，拼成
   `https://speak.projfit.top/interview-prep?project=<URL编码的项目文本>&jd=...&language=zh`
   跳过来，口语侧就会自动预填并能一键开始口语面试。**管道是通的。**

## 要做什么（talent-agent 侧）

在 talent-agent 的项目/简历详情页（用户导入项目的地方），加一个出口动作，例如
「用这个项目练口语面试」按钮：

1. 取用户当前选中的项目（和可选的 JD/简历）文本。
2. URL 编码后拼成上面的 `/interview-prep?...` 链接。
3. 跳转到 `https://speak.projfit.top/interview-prep?...`（生产域名）。

### 关键决策点（codex 自行判断或问用户）

- **传文本还是传 ID**：当前口语侧只吃**纯文本**（project_context 等）。最简单是
  talent-agent 直接把项目文本塞进 URL。若项目文本过长（URL 长度上限 ~2000 字符），
  改为：talent-agent 提供一个"导出项目文本"的接口，口语侧带 `project_id` 来拉取。
  **建议先用纯文本走通 MVP**，长文本问题后续再说。
- **语言**：talent-agent 跳转时带上 `language=zh|en`，对齐用户偏好。
- **鉴权**：`oral-interview-session` 用 `get_optional_user`（匿名可用），跨域跳转
  不需要透传 token；但若要把面试成绩回流（见下），需要登录态对齐。

## 已存在、无需重做的回流链路

口语侧已有 `POST /api/integrations/talent-agent/sync`（ChatView 里有「同步到
Talent Agent」按钮），把口语练习的发音/流利度成绩回传 talent-agent 的
`/integrations/oral-practice/result`。这条**反向**链路已通，本任务不用动。

## 验收

- 在 talent-agent 选一个导入的项目 → 点「练口语面试」→ 跳到口语
  `/interview-prep` 且项目框已预填 → 点开始 → 进入 `/chat/interview` 能就该项目
  展开面试问答。

## 注意

- 口语侧 `InterviewPrepView.vue` 的 query 预填已就绪，**除非要支持 project_id
  拉取，否则口语侧不用改**。
- 别动 `assessment/scoring/*`（claude 正在改发音音标，已 claim）。
