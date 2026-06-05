/**
 * useRecorder 单元测试
 * Mock 了 MediaRecorder 和 AudioContext
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { useRecorder } from '../../voice/audio/useRecorder'

// Mock vue's ref to work outside component
vi.mock('vue', () => ({
  ref: (val) => ({ value: val }),
}))

// Mock browser APIs with proper class-based constructors
function setupBrowserMocks() {
  const mockStream = {
    getTracks: () => [{ stop: vi.fn() }],
  }

  const mockRecorderInstance = {
    state: 'inactive',
    stream: mockStream,
    mimeType: 'audio/webm;codecs=opus',
    ondataavailable: null,
    onstop: null,
    start: vi.fn(function () { this.state = 'recording' }),
    stop: vi.fn(function () {
      this.state = 'inactive'
      if (this.ondataavailable) {
        this.ondataavailable({ data: new Blob(['mock-audio'], { type: 'audio/webm' }) })
      }
      setTimeout(() => { if (this.onstop) this.onstop() }, 0)
    }),
  }

  global.navigator = {
    mediaDevices: {
      getUserMedia: vi.fn().mockResolvedValue(mockStream),
    },
  }

  // Use a class so `new MediaRecorder()` works
  global.MediaRecorder = class {
    constructor() {
      Object.assign(this, mockRecorderInstance)
    }
    static isTypeSupported() { return true }
  }

  const mockAnalyser = {
    fftSize: 512,
    getByteTimeDomainData: vi.fn((arr) => arr.fill(128)),
  }

  global.AudioContext = class {
    createMediaStreamSource() { return { connect: vi.fn() } }
    createAnalyser() { return mockAnalyser }
    close() {}
  }

  global.requestAnimationFrame = vi.fn((cb) => setTimeout(cb, 16))
  global.cancelAnimationFrame = vi.fn((id) => clearTimeout(id))

  return { mockRecorderInstance, mockAnalyser }
}

describe('useRecorder', () => {
  let mocks

  beforeEach(() => {
    mocks = setupBrowserMocks()
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
    vi.restoreAllMocks()
  })

  it('should initialize with isRecording = false', () => {
    const { isRecording } = useRecorder()
    expect(isRecording.value).toBe(false)
  })

  it('should set isRecording to true after start()', async () => {
    const { start, isRecording } = useRecorder()
    await start()
    expect(isRecording.value).toBe(true)
  })

  it('should request microphone permission on start()', async () => {
    const { start } = useRecorder()
    await start()
    expect(navigator.mediaDevices.getUserMedia).toHaveBeenCalledWith({ audio: true })
  })

  it('should return a Blob on stop()', async () => {
    const { start, stop } = useRecorder()
    await start()

    const blobPromise = stop()
    vi.runAllTimers()
    const blob = await blobPromise

    expect(blob).toBeInstanceOf(Blob)
  })

  it('should return null if stop() called without recording', async () => {
    const { stop } = useRecorder()
    const result = await stop()
    expect(result).toBeNull()
  })

  it('should call onSilence after silence timeout', async () => {
    const onSilence = vi.fn()
    const { start, duration } = useRecorder({ silenceMs: 1000, onSilence })

    await start()
    duration.value = 600

    // Advance timers to trigger requestAnimationFrame loop + silence check
    vi.advanceTimersByTime(1500)

    expect(onSilence).toHaveBeenCalled()
  })

  it('should track recording duration', async () => {
    const { start, duration } = useRecorder()
    await start()
    vi.advanceTimersByTime(500)
    expect(duration.value).toBeGreaterThanOrEqual(400)
  })
})
