/**
 * ASR 服务接入
 * 将录音 Blob 发送到后端 ASR 接口，返回识别文本
 */

const API_BASE = import.meta.env?.VITE_API_BASE || ''

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
 * Streaming chat — sends audio and receives SSE events as response generates.
 * @param {Blob} audioBlob - 录音 Blob
 * @param {string} scenario - 场景 ID
 * @param {Array} history - 对话历史
 * @param {string} sessionId - 会话 ID (optional)
 * @param {object} callbacks - { onASR, onSentence, onCorrections, onFeedback, onDone, onError }
 * @returns {AbortController} - call .abort() to cancel the stream
 */
export function streamChat(audioBlob, scenario, history = [], sessionId = '', callbacks = {}) {
  const controller = new AbortController()

  const formData = new FormData()
  formData.append('audio', audioBlob, 'recording.webm')
  formData.append('scenario', scenario)
  formData.append('history', JSON.stringify(history))
  formData.append('session_id', sessionId)

  fetch(`${API_BASE}/api/stream`, {
    method: 'POST',
    body: formData,
    signal: controller.signal,
  })
    .then(async (res) => {
      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        callbacks.onError?.(err.detail || `请求失败 (${res.status})`)
        return
      }

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })

        // Parse SSE events from buffer
        const events = buffer.split('\n\n')
        buffer = events.pop() // keep incomplete event in buffer

        for (const raw of events) {
          if (!raw.trim()) continue
          const eventMatch = raw.match(/^event:\s*(.+)$/m)
          const dataMatch = raw.match(/^data:\s*(.+)$/m)
          if (!eventMatch || !dataMatch) continue

          const eventType = eventMatch[1]
          let data
          try {
            data = JSON.parse(dataMatch[1])
          } catch {
            continue
          }

          switch (eventType) {
            case 'asr':
              callbacks.onASR?.(data.text)
              break
            case 'sentence':
              callbacks.onSentence?.(data)
              break
            case 'corrections':
              callbacks.onCorrections?.(data)
              break
            case 'feedback':
              callbacks.onFeedback?.(data)
              break
            case 'done':
              callbacks.onDone?.(data)
              break
            case 'error':
              callbacks.onError?.(data.message)
              break
          }
        }
      }
    })
    .catch((err) => {
      if (err.name !== 'AbortError') {
        callbacks.onError?.(err.message)
      }
    })

  return controller
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

/**
 * 发音评测：将录音与参考文本比对，返回单词级评分
 * @param {Blob} audioBlob
 * @param {string} referenceText 参考朗读文本
 * @returns {Promise<{accuracy_score, fluency_score, completeness_score, pronunciation_score, words, provider}>}
 */
export async function assessPronunciation(audioBlob, referenceText) {
  const formData = new FormData()
  formData.append('audio', audioBlob, 'recording.webm')
  formData.append('reference_text', referenceText)

  const res = await fetch(`${API_BASE}/api/assess`, {
    method: 'POST',
    body: formData,
  })

  if (res.status === 503) {
    throw new Error('发音评测服务未配置，请稍后再试')
  }
  if (!res.ok) {
    throw new Error('发音评测失败，请重试')
  }

  return res.json()
}

/**
 * 查询发音评测当前可用的 provider（azure / tencent / mock / null）
 * @returns {Promise<{available: boolean, provider: string|null, is_mock: boolean}>}
 */
export async function getAssessStatus() {
  const res = await fetch(`${API_BASE}/api/assess/status`)
  if (!res.ok) {
    return { available: false, provider: null, is_mock: false }
  }
  return res.json()
}
