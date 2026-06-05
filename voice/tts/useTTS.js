/**
 * TTS 语音合成与播放
 * 负责播放后端返回的 AI 回复语音
 */
import { ref } from 'vue'

export function useTTS() {
  const isPlaying = ref(false)
  let currentAudio = null

  /**
   * 播放指定 URL 的音频
   * @param {string} url - 音频文件 URL
   * @returns {Promise<void>}
   */
  function play(url) {
    return new Promise((resolve, reject) => {
      stopCurrent()

      currentAudio = new Audio(url)
      isPlaying.value = true

      currentAudio.onended = () => {
        isPlaying.value = false
        currentAudio = null
        resolve()
      }

      currentAudio.onerror = (e) => {
        isPlaying.value = false
        currentAudio = null
        reject(new Error('音频播放失败'))
      }

      currentAudio.play().catch(reject)
    })
  }

  /**
   * 停止当前播放
   */
  function stopCurrent() {
    if (currentAudio) {
      currentAudio.pause()
      currentAudio.currentTime = 0
      currentAudio = null
      isPlaying.value = false
    }
  }

  return { play, stopCurrent, isPlaying }
}
