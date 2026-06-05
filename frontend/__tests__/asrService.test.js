/**
 * ASR service 单元测试
 * 测试 sendAudioForChat、recognizeOnly、streamChat
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'

// Must mock import.meta.env before importing service
vi.stubGlobal('import', { meta: { env: { VITE_API_BASE: '' } } })

describe('ASR service', () => {
  let sendAudioForChat, recognizeOnly, streamChat

  beforeEach(async () => {
    // Mock fetch globally
    global.fetch = vi.fn()
    global.FormData = class {
      constructor() { this._data = {} }
      append(key, val) { this._data[key] = val }
    }
    global.Blob = class {
      constructor(parts, opts) { this.size = 100; this.type = opts?.type || '' }
    }
    global.AbortController = class {
      constructor() { this.signal = {}; this.abort = vi.fn() }
    }

    // Dynamic import to pick up mocks
    const mod = await import('../../voice/asr/service.js')
    sendAudioForChat = mod.sendAudioForChat
    recognizeOnly = mod.recognizeOnly
    streamChat = mod.streamChat
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('sendAudioForChat', () => {
    it('should send FormData with audio, scenario, history', async () => {
      const mockResponse = {
        ok: true,
        json: vi.fn().mockResolvedValue({ user_text: 'hello', reply_text: 'hi' }),
      }
      global.fetch.mockResolvedValue(mockResponse)

      const blob = new Blob(['audio'], { type: 'audio/webm' })
      const result = await sendAudioForChat(blob, 'interview', [])

      expect(global.fetch).toHaveBeenCalledWith(
        '/api/chat',
        expect.objectContaining({ method: 'POST' })
      )
      expect(result).toEqual({ user_text: 'hello', reply_text: 'hi' })
    })

    it('should throw on non-ok response', async () => {
      global.fetch.mockResolvedValue({
        ok: false,
        status: 500,
        json: vi.fn().mockResolvedValue({ detail: 'Server error' }),
      })

      const blob = new Blob(['audio'], { type: 'audio/webm' })
      await expect(sendAudioForChat(blob, 'interview', []))
        .rejects.toThrow('Server error')
    })
  })

  describe('recognizeOnly', () => {
    it('should return recognized text', async () => {
      global.fetch.mockResolvedValue({
        ok: true,
        json: vi.fn().mockResolvedValue({ text: 'recognized text' }),
      })

      const blob = new Blob(['audio'], { type: 'audio/webm' })
      const result = await recognizeOnly(blob)
      expect(result.text).toBe('recognized text')
    })

    it('should throw on failure', async () => {
      global.fetch.mockResolvedValue({ ok: false, status: 503 })

      const blob = new Blob(['audio'], { type: 'audio/webm' })
      await expect(recognizeOnly(blob)).rejects.toThrow('语音识别失败')
    })
  })

  describe('streamChat', () => {
    it('should return an AbortController', () => {
      global.fetch.mockResolvedValue({ ok: true, body: { getReader: vi.fn() } })

      const blob = new Blob(['audio'], { type: 'audio/webm' })
      const controller = streamChat(blob, 'interview', [], '', {})

      expect(controller).toBeDefined()
      expect(controller.abort).toBeDefined()
    })
  })
})
