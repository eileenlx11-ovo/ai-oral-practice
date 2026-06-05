/**
 * ASR 服务接入
 * 将录音 Blob 发送到后端 ASR 接口，返回识别文本
 */

const API_BASE = import.meta.env?.VITE_API_BASE || 'http://localhost:8000'

/**
 * 发送音频到后端进行语音识别
 * @param {Blob} audioBlob - 录音 Blob
 * @param {string} scenario - 场景 ID
 * @param {Array} history - 对话历史
 * @returns {Promise<import('../../shared/types').ChatResponse>}
 */
export async function sendAudioForChat(audioBlob, scenario, history = []) {
  const formData = new FormData()
  formData.append('audio', audioBlob, 'recording.webm')
  formData.append('scenario', scenario)
  formData.append('history', JSON.stringify(history))

  const res = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    body: formData,
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || `ASR 请求失败 (${res.status})`)
  }

  return res.json()
}

/**
 * 仅做语音识别（不触发 LLM 对话）
 * @param {Blob} audioBlob
 * @returns {Promise<{text: string}>}
 */
export async function recognizeOnly(audioBlob) {
  const formData = new FormData()
  formData.append('audio', audioBlob, 'recording.webm')

  const res = await fetch(`${API_BASE}/api/asr`, {
    method: 'POST',
    body: formData,
  })

  if (!res.ok) {
    throw new Error('语音识别失败')
  }

  return res.json()
}
