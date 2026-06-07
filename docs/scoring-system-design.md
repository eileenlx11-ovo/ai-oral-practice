# 混合评分系统设计方案

> 给龚参考，她负责实现

## 设计思路

硬评估（Azure/SOE）解决**发音准确性**，LLM 软评估解决**语言能力**。两者加权合成最终得分，对标雅思口语四维标准。

## 评分维度

| 维度 | 来源 | 权重 | 对标 |
|------|------|------|------|
| Pronunciation（发音） | Azure/SOE 硬评估 | 25% | 雅思 Band Descriptor: Pronunciation |
| Fluency & Coherence（流利与连贯） | Azure fluency_score + LLM 分析 | 25% | 雅思 Band Descriptor: Fluency & Coherence |
| Lexical Resource（词汇丰富度） | LLM 分析对话文本 | 25% | 雅思 Band Descriptor: Lexical Resource |
| Grammatical Range & Accuracy（语法） | LLM 分析 + 纠错数据 | 25% | 雅思 Band Descriptor: Grammatical Range |

## 数据来源

### 硬评估数据（已有）
```python
# 每轮对话的 pronunciation 评测结果（如果用户开启了）
{
    "pronunciation_score": 73,
    "accuracy_score": 69,
    "fluency_score": 80,
    "completeness_score": 78,
    "words": [{"word": "hello", "accuracy_score": 95, "error_type": None}, ...]
}
```

### 软评估数据（从 session turns 提取）
```python
# 用户所有对话文本
user_texts = [turn["user_text"] for turn in session["turns"]]

# 可统计的指标
stats = {
    "total_words": ...,           # 总词数
    "unique_words": ...,          # 不重复词数
    "avg_sentence_length": ...,   # 平均句长
    "vocabulary_richness": ...,   # unique / total
    "total_corrections": ...,     # 语法纠错次数
    "correction_categories": ..., # 纠错类别分布
}
```

## LLM 评分 Prompt

```python
EVALUATION_PROMPT = """You are an IELTS speaking examiner. Evaluate this English practice session.

## User's conversation turns:
{user_texts}

## Grammar corrections made during session:
{corrections_summary}

## Statistical data:
- Total words spoken: {total_words}
- Unique vocabulary: {unique_words}
- Vocabulary richness: {vocabulary_richness:.2%}
- Average sentence length: {avg_sentence_length:.1f} words
- Grammar corrections: {total_corrections}

## Azure/SOE pronunciation scores (if available):
- Average pronunciation: {avg_pronunciation}
- Average fluency: {avg_fluency}
- Average accuracy: {avg_accuracy}

## Task
Score each dimension 0-9 (IELTS band scale) with specific evidence:

Output strictly as JSON:
{{
  "fluency_coherence": {{
    "band": 6.5,
    "evidence": "Generally fluent with occasional hesitation. Good use of connectors.",
    "suggestion": "Practice linking ideas with more varied discourse markers."
  }},
  "lexical_resource": {{
    "band": 6.0,
    "evidence": "Adequate vocabulary for topic but limited range of less common words.",
    "suggestion": "Expand vocabulary with topic-specific collocations."
  }},
  "grammatical_range": {{
    "band": 5.5,
    "evidence": "Mix of simple and complex structures. Frequent errors with articles.",
    "suggestion": "Focus on article usage (a/an/the) and subject-verb agreement."
  }},
  "pronunciation": {{
    "band": 6.0,
    "evidence": "Generally clear but some mispronunciations affect understanding.",
    "suggestion": "Practice word stress patterns, especially multi-syllable words."
  }},
  "overall_band": 6.0,
  "cefr_level": "B2",
  "strengths": ["Good willingness to communicate", "Clear topic development"],
  "priority_improvements": ["Article usage", "Vocabulary range", "Word stress"],
  "study_plan": "Focus on reading English articles to absorb natural phrasing. Practice shadowing podcasts for fluency."
}}
"""
```

## 实现位置

### 后端
- **新 endpoint**: `POST /api/sessions/{session_id}/evaluate`
  - 调用上面的 prompt，返回结构化评分
  - 和现有 `/api/sessions/{session_id}/end` 分开（end 是快速总结，evaluate 是深度评估）
  - 或者直接增强 `end_session()` 的返回，加一个 `evaluation` 字段

### 前端
- 结束对话后的报告 modal 里新增：
  - 四维雷达图（CSS/SVG 实现）或四个环形进度条
  - IELTS Band 分数展示
  - strengths / improvements 列表
  - study_plan 建议

### 数据流
```
用户点「结束练习」
  → POST /api/sessions/{sid}/end
  → 后端统计 session 数据
  → 调 LLM 生成结构化评分
  → 返回 {summary + evaluation}
  → 前端渲染报告
```

## 和现有代码的关系

- `assessment/feedback/__init__.py` 的 `get_summary()` 需要新增统计字段（unique_words, avg_sentence_length 等）
- `assessment/app.py` 的 `_generate_session_report()` 需要改为双模式：简单文本报告 + 结构化评分
- `frontend/chat/ChatView.vue` 的 report modal 需要扩展展示维度

## 关于 Azure 韵律评估

可选增强：在 `assessment/scoring/azure.py` 里开启 `EnableProsodyAssessment`：
```python
pron_config = speechsdk.PronunciationAssessmentConfig(
    reference_text=reference_text,
    grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
    granularity=speechsdk.PronunciationAssessmentGranularity.Word,
    enable_miscue=True,
)
pron_config.enable_prosody_assessment()  # 加这行
```

返回额外字段：`prosody_score`（包含语调、重音、节奏子分）。可以作为 fluency 维度的客观补充。

## 注意事项

1. LLM 评分有延迟（2-5s），前端要显示 loading 状态
2. 如果 session turns < 3 轮，数据太少评分不准，建议提示"至少练习 3 轮后才能获得详细评估"
3. 评分结果存入 session JSON，下次打开 dashboard 能看到历史
4. prompt 里的维度和建议要**中文输出**（面向中国用户）——在 prompt 末尾加 "Output evidence and suggestions in Chinese."
