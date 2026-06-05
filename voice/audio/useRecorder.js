/**
 * useRecorder - 浏览器录音 composable
 * 支持 MediaRecorder 录音 + VAD 静音检测
 */
import { ref } from 'vue'

const DEFAULT_SILENCE_MS = 1500

export function useRecorder(options = {}) {
  const { silenceMs = DEFAULT_SILENCE_MS, onSilence } = options

  const mediaRecorder = ref(null)
  const chunks = ref([])
  const isRecording = ref(false)
  const duration = ref(0)

  let analyser = null
  let silenceTimer = null
  let durationTimer = null
  let audioContext = null

  async function start() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })

    // 设置音频分析器（用于 VAD）
    audioContext = new AudioContext()
    const source = audioContext.createMediaStreamSource(stream)
    analyser = audioContext.createAnalyser()
    analyser.fftSize = 512
    source.connect(analyser)

    // 录音
    const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
      ? 'audio/webm;codecs=opus'
      : 'audio/webm'

    const recorder = new MediaRecorder(stream, { mimeType })
    chunks.value = []

    recorder.ondataavailable = (e) => {
      if (e.data.size > 0) {
        chunks.value.push(e.data)
      }
    }

    recorder.start(100) // 每 100ms 生成一个 chunk，便于流式传输
    mediaRecorder.value = recorder
    isRecording.value = true
    duration.value = 0

    // 录音时长计时
    durationTimer = setInterval(() => {
      duration.value += 100
    }, 100)

    // VAD 静音检测
    _startVAD()
  }

  function stop() {
    return new Promise((resolve) => {
      _cleanup()

      const recorder = mediaRecorder.value
      if (!recorder || recorder.state === 'inactive') {
        resolve(null)
        return
      }

      recorder.onstop = () => {
        const blob = new Blob(chunks.value, { type: recorder.mimeType })
        recorder.stream.getTracks().forEach((t) => t.stop())
        resolve(blob)
      }

      recorder.stop()
      isRecording.value = false
    })
  }

  function _startVAD() {
    if (!analyser) return

    const dataArray = new Uint8Array(analyser.fftSize)
    let lastSoundTime = Date.now()

    function check() {
      if (!isRecording.value) return

      analyser.getByteTimeDomainData(dataArray)

      // 计算音量 RMS
      let sum = 0
      for (let i = 0; i < dataArray.length; i++) {
        const v = (dataArray[i] - 128) / 128
        sum += v * v
      }
      const rms = Math.sqrt(sum / dataArray.length)

      if (rms > 0.01) {
        lastSoundTime = Date.now()
      } else if (Date.now() - lastSoundTime > silenceMs && duration.value > 500) {
        // 超过 silenceMs 的静音，自动停止
        if (onSilence) {
          onSilence()
        }
        return
      }

      silenceTimer = requestAnimationFrame(check)
    }

    silenceTimer = requestAnimationFrame(check)
  }

  function _cleanup() {
    if (silenceTimer) {
      cancelAnimationFrame(silenceTimer)
      silenceTimer = null
    }
    if (durationTimer) {
      clearInterval(durationTimer)
      durationTimer = null
    }
    if (audioContext) {
      audioContext.close()
      audioContext = null
    }
    analyser = null
  }

  return { start, stop, isRecording, duration }
}
