/**
 * 共用类型定义 - 前后端/模块间接口约定
 */

/** 对话消息 */
export interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp?: string
}

/** 语音识别结果 */
export interface ASRResult {
  text: string
  confidence: number
  duration_ms: number
}

/** TTS 请求 */
export interface TTSRequest {
  text: string
  voice?: string
  speed?: number
}

/** 发音评测结果 */
export interface PronunciationScore {
  accuracy_score: number
  fluency_score: number
  completeness_score: number
  pronunciation_score: number
  words: WordScore[]
}

export interface WordScore {
  word: string
  accuracy_score: number
  error_type: 'None' | 'Omission' | 'Insertion' | 'Mispronunciation'
}

/** 语法纠错 */
export interface GrammarCorrection {
  original: string
  corrected: string
  explanation: string
}

/** 对话接口响应 */
export interface ChatResponse {
  user_text: string
  reply_text: string
  reply_audio_url: string | null
  corrections: GrammarCorrection[]
  pronunciation?: PronunciationScore
}

/** 会话摘要 */
export interface SessionSummary {
  session_id: string
  scenario: string
  timestamp: string
  turns: number
  avg_pronunciation: number | null
  avg_fluency: number | null
}

/** 场景定义 */
export interface Scenario {
  id: string
  name: string
  icon: string
  greeting?: string
}
