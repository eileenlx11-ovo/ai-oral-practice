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
    STREAM: '/api/stream',
    ASSESS: '/api/assess',
    SCENARIOS: '/api/scenarios',
    CATEGORIES: '/api/categories',
    SESSIONS: '/api/sessions',
    HINT: '/api/hint',
    LEVEL_TEST: '/api/level-test',
    PROFILE: '/api/profile',
    INTEGRATIONS: '/api/integrations',
    ANALYTICS: '/api/analytics',
  },

  // Hint system
  HINT: {
    SILENCE_TRIGGER_MS: 10000, // Show hint prompt after 10s of silence
  },

  // 场景分类
  CATEGORIES: [
    { id: 'all', name: 'All', icon: '🌟' },
    { id: 'daily', name: 'Daily Life', icon: '🏠' },
    { id: 'work', name: 'Work', icon: '💼' },
    { id: 'travel', name: 'Travel', icon: '✈️' },
    { id: 'social', name: 'Social', icon: '💬' },
  ],

  // 场景列表 (used as fallback; primary source is /api/scenarios)
  SCENARIOS: [
    { id: 'coffee_shop', icon: '☕', name: 'Coffee Shop', category: 'daily', difficulty: 'beginner', description: '在咖啡店点饮品' },
    { id: 'grocery', icon: '🛒', name: 'Grocery Shopping', category: 'daily', difficulty: 'beginner', description: '超市购物找商品' },
    { id: 'doctor', icon: '🏥', name: "Doctor's Visit", category: 'daily', difficulty: 'intermediate', description: '描述症状和理解医嘱' },
    { id: 'restaurant', icon: '🍽️', name: 'Restaurant', category: 'daily', difficulty: 'beginner', description: '餐厅点餐全流程' },
    { id: 'delivery', icon: '🚴', name: 'Food Delivery', category: 'daily', difficulty: 'beginner', description: '和外卖员电话沟通' },
    { id: 'interview', icon: '💼', name: 'Job Interview', category: 'work', difficulty: 'advanced', description: '模拟英语面试' },
    { id: 'meeting', icon: '📋', name: 'Team Meeting', category: 'work', difficulty: 'intermediate', description: '团队会议讨论' },
    { id: 'coworker', icon: '👩‍💻', name: 'Office Chat', category: 'work', difficulty: 'intermediate', description: '同事间日常闲聊' },
    { id: 'phone_call', icon: '📞', name: 'Business Call', category: 'work', difficulty: 'advanced', description: '商务电话沟通' },
    { id: 'salary', icon: '💰', name: 'Salary Negotiation', category: 'work', difficulty: 'advanced', description: '薪资谈判' },
    { id: 'airport', icon: '✈️', name: 'Airport Check-in', category: 'travel', difficulty: 'intermediate', description: '机场值机和行李' },
    { id: 'hotel', icon: '🏨', name: 'Hotel Check-in', category: 'travel', difficulty: 'beginner', description: '酒店入住' },
    { id: 'directions', icon: '🗺️', name: 'Asking Directions', category: 'travel', difficulty: 'beginner', description: '问路和导航' },
    { id: 'travel', icon: '🚗', name: 'Car Rental', category: 'travel', difficulty: 'intermediate', description: '租车和条款' },
    { id: 'smalltalk', icon: '💬', name: 'Small Talk', category: 'social', difficulty: 'beginner', description: '日常社交闲聊' },
    { id: 'party', icon: '🎉', name: 'Party Chat', category: 'social', difficulty: 'intermediate', description: '派对认识新朋友' },
    { id: 'neighbor', icon: '🏠', name: 'Neighbor Chat', category: 'social', difficulty: 'beginner', description: '邻居日常寒暄' },
    { id: 'gym', icon: '💪', name: 'Gym Buddy', category: 'social', difficulty: 'intermediate', description: '健身房社交' },
  ],
}
