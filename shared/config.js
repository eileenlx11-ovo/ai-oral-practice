/**
 * 共用配置常量
 */

export const CONFIG = {
  // 音频采集
  AUDIO: {
    SAMPLE_RATE: 16000,
    CHANNELS: 1,
    MIME_TYPE: 'audio/webm;codecs=opus',
    VAD_SILENCE_MS: 1500, // 静音超过此时间自动截断
  },

  // API endpoints (proxied by Vite in dev, Nginx in prod)
  API: {
    BASE_URL: import.meta.env?.VITE_API_BASE || '',
    CHAT: '/api/chat',
    ASSESS: '/api/assess',
    SCENARIOS: '/api/scenarios',
    SESSIONS: '/api/sessions',
  },

  // 场景列表
  SCENARIOS: [
    { id: 'interview', icon: '💼', name: 'Job Interview', description: '模拟英语面试场景，练习自我介绍和回答面试问题' },
    { id: 'restaurant', icon: '🍽️', name: 'Restaurant', description: '模拟餐厅点餐，练习日常用餐对话' },
    { id: 'meeting', icon: '📋', name: 'Business Meeting', description: '模拟商务会议，练习表达观点和讨论' },
    { id: 'travel', icon: '✈️', name: 'Travel', description: '模拟旅行场景，练习问路、住酒店、买票等' },
    { id: 'smalltalk', icon: '💬', name: 'Small Talk', description: '日常闲聊，练习自然的社交英语' },
  ],
}
