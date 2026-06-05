/**
 * useRecorder - 浏览器录音 composable
 * 使用 MediaRecorder API 录制音频，返回 Blob
 */
import { ref } from 'vue'

export function useRecorder() {
  const mediaRecorder = ref(null)
  const chunks = ref([])

  async function start() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    const recorder = new MediaRecorder(stream, {
      mimeType: MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
        ? 'audio/webm;codecs=opus'
        : 'audio/webm',
    })

    chunks.value = []

    recorder.ondataavailable = (e) => {
      if (e.data.size > 0) {
        chunks.value.push(e.data)
      }
    }

    recorder.start()
    mediaRecorder.value = recorder
  }

  function stop() {
    return new Promise((resolve) => {
      const recorder = mediaRecorder.value
      if (!recorder || recorder.state === 'inactive') {
        resolve(null)
        return
      }

      recorder.onstop = () => {
        const blob = new Blob(chunks.value, { type: recorder.mimeType })
        // 停止所有音轨释放麦克风
        recorder.stream.getTracks().forEach((t) => t.stop())
        resolve(blob)
      }

      recorder.stop()
    })
  }

  function getBlob() {
    if (chunks.value.length === 0) return null
    return new Blob(chunks.value, { type: 'audio/webm' })
  }

  return { start, stop, getBlob }
}
