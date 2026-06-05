/**
 * useTTS 单元测试
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { useTTS } from '../../voice/tts/useTTS'

// Mock vue's ref
vi.mock('vue', () => ({
  ref: (val) => ({ value: val }),
}))

// Mock Audio as a proper class
function createMockAudioClass() {
  const instances = []

  class MockAudio {
    constructor(url) {
      this.url = url
      this.onended = null
      this.onerror = null
      this.paused = false
      this.currentTime = 0
      this.play = vi.fn().mockResolvedValue(undefined)
      this.pause = vi.fn(() => { this.paused = true })
      instances.push(this)
    }
  }

  return { MockAudio, instances }
}

describe('useTTS', () => {
  let MockAudio, instances

  beforeEach(() => {
    const mock = createMockAudioClass()
    MockAudio = mock.MockAudio
    instances = mock.instances
    global.Audio = MockAudio
  })

  afterEach(() => {
    vi.restoreAllMocks()
    instances.length = 0
  })

  it('should initialize with isPlaying = false', () => {
    const { isPlaying } = useTTS()
    expect(isPlaying.value).toBe(false)
  })

  it('should set isPlaying to true when play() is called', async () => {
    const { play, isPlaying } = useTTS()

    const playPromise = play('http://example.com/audio.mp3')
    expect(isPlaying.value).toBe(true)

    // Simulate audio ended
    const audio = instances[instances.length - 1]
    audio.onended()
    await playPromise

    expect(isPlaying.value).toBe(false)
  })

  it('should create Audio with the given URL', () => {
    const { play } = useTTS()
    play('http://example.com/test.mp3')

    const audio = instances[instances.length - 1]
    expect(audio.url).toBe('http://example.com/test.mp3')
  })

  it('should reject on audio error', async () => {
    const { play } = useTTS()

    const playPromise = play('http://example.com/bad.mp3')
    const audio = instances[instances.length - 1]
    audio.onerror(new Error('failed'))

    await expect(playPromise).rejects.toThrow('音频播放失败')
  })

  it('should stop current audio on stopCurrent()', () => {
    const { play, stopCurrent, isPlaying } = useTTS()

    play('http://example.com/audio.mp3')
    expect(isPlaying.value).toBe(true)

    stopCurrent()
    const audio = instances[0]
    expect(audio.pause).toHaveBeenCalled()
    expect(isPlaying.value).toBe(false)
  })

  it('should stop previous audio when playing a new one', () => {
    const { play } = useTTS()

    play('http://example.com/first.mp3')
    const firstAudio = instances[0]

    play('http://example.com/second.mp3')
    expect(firstAudio.pause).toHaveBeenCalled()
  })
})
