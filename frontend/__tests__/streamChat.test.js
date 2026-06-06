/**
 * streamChat SSE 解析逻辑 完整单元测试
 * 覆盖：事件解析、回调调度、错误处理、中断、chunked 分包
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'

// --- Helpers ---

/** 构造一个模拟的 ReadableStream，按 chunks 逐步输出 */
function createMockStream(chunks) {
  let index = 0
  const encoder = new TextEncoder()
  return {
    getReader() {
      return {
        read() {
          if (index < chunks.length) {
            const value = encoder.encode(chunks[index++])
            return Promise.resolve({ done: false, value })
          }
          return Promise.resolve({ done: true, value: undefined })
        },
      }
    },
  }
}

/** 构造完整的 SSE 事件字符串 */
function sseEvent(event, data) {
  return `event: ${event}\ndata: ${JSON.stringify(data)}\n\n`
}

describe('streamChat SSE parsing', () => {
  let streamChat

  beforeEach(async () => {
    global.fetch = vi.fn()
    global.FormData = class {
      constructor() { this._data = {} }
      append(key, val) { this._data[key] = val }
    }
    global.Blob = class {
      constructor() { this.size = 100; this.type = 'audio/webm' }
    }
    global.AbortController = class {
      constructor() { this.signal = { aborted: false }; this.abort = vi.fn() }
    }
    global.TextDecoder = class {
      decode(value, opts) { return new TextDecoder().decode(value) }
    }
    // Use real TextDecoder from Node
    const { TextDecoder: RealDecoder } = await import('util')
    global.TextDecoder = RealDecoder

    const mod = await import('../../voice/asr/service.js')
    streamChat = mod.streamChat
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('should parse a complete SSE flow: asr → sentence → corrections → feedback → done', async () => {
    const callbacks = {
      onASR: vi.fn(),
      onSentence: vi.fn(),
      onCorrections: vi.fn(),
      onFeedback: vi.fn(),
      onDone: vi.fn(),
      onError: vi.fn(),
    }

    const ssePayload = [
      sseEvent('asr', { text: 'Hello world' }),
      sseEvent('sentence', { index: 0, text: 'Hi there!', audio_url: '/audio/0.mp3' }),
      sseEvent('sentence', { index: 1, text: 'How are you?', audio_url: '/audio/1.mp3' }),
      sseEvent('corrections', [{ original: 'goed', corrected: 'went', explanation: 'Irregular' }]),
      sseEvent('feedback', { text: 'Great job!' }),
      sseEvent('done', { session_id: 'abc123', full_reply: 'Hi there! How are you?' }),
    ].join('')

    const body = createMockStream([ssePayload])
    global.fetch.mockResolvedValue({ ok: true, body })

    const blob = new Blob()
    streamChat(blob, 'coffee_shop', [], 'sess1', callbacks)

    // Wait for async processing
    await new Promise((r) => setTimeout(r, 50))

    expect(callbacks.onASR).toHaveBeenCalledWith('Hello world')
    expect(callbacks.onSentence).toHaveBeenCalledTimes(2)
    expect(callbacks.onSentence).toHaveBeenCalledWith({ index: 0, text: 'Hi there!', audio_url: '/audio/0.mp3' })
    expect(callbacks.onSentence).toHaveBeenCalledWith({ index: 1, text: 'How are you?', audio_url: '/audio/1.mp3' })
    expect(callbacks.onCorrections).toHaveBeenCalledWith([{ original: 'goed', corrected: 'went', explanation: 'Irregular' }])
    expect(callbacks.onFeedback).toHaveBeenCalledWith({ text: 'Great job!' })
    expect(callbacks.onDone).toHaveBeenCalledWith({ session_id: 'abc123', full_reply: 'Hi there! How are you?' })
    expect(callbacks.onError).not.toHaveBeenCalled()
  })

  it('should handle chunked delivery (split across multiple reads)', async () => {
    const callbacks = { onASR: vi.fn(), onSentence: vi.fn(), onDone: vi.fn() }

    // Split in the middle of an event
    const event1 = sseEvent('asr', { text: 'Test' })
    const event2 = sseEvent('done', { session_id: 'x' })
    const full = event1 + event2
    const splitAt = Math.floor(full.length / 2)

    const body = createMockStream([full.slice(0, splitAt), full.slice(splitAt)])
    global.fetch.mockResolvedValue({ ok: true, body })

    streamChat(new Blob(), 'interview', [], '', callbacks)
    await new Promise((r) => setTimeout(r, 50))

    expect(callbacks.onASR).toHaveBeenCalledWith('Test')
    expect(callbacks.onDone).toHaveBeenCalledWith({ session_id: 'x' })
  })

  it('should dispatch onError for event: error', async () => {
    const callbacks = { onError: vi.fn() }

    const body = createMockStream([sseEvent('error', { message: 'No speech detected' })])
    global.fetch.mockResolvedValue({ ok: true, body })

    streamChat(new Blob(), 'coffee_shop', [], '', callbacks)
    await new Promise((r) => setTimeout(r, 50))

    expect(callbacks.onError).toHaveBeenCalledWith('No speech detected')
  })

  it('should call onError on non-ok HTTP response', async () => {
    const callbacks = { onError: vi.fn() }

    global.fetch.mockResolvedValue({
      ok: false,
      status: 500,
      json: vi.fn().mockResolvedValue({ detail: 'Internal error' }),
    })

    streamChat(new Blob(), 'coffee_shop', [], '', callbacks)
    await new Promise((r) => setTimeout(r, 50))

    expect(callbacks.onError).toHaveBeenCalledWith('Internal error')
  })

  it('should call onError on network failure', async () => {
    const callbacks = { onError: vi.fn() }

    global.fetch.mockRejectedValue(new Error('Network offline'))

    streamChat(new Blob(), 'coffee_shop', [], '', callbacks)
    await new Promise((r) => setTimeout(r, 50))

    expect(callbacks.onError).toHaveBeenCalledWith('Network offline')
  })

  it('should NOT call onError when aborted', async () => {
    const callbacks = { onError: vi.fn() }

    const abortErr = new Error('Aborted')
    abortErr.name = 'AbortError'
    global.fetch.mockRejectedValue(abortErr)

    streamChat(new Blob(), 'coffee_shop', [], '', callbacks)
    await new Promise((r) => setTimeout(r, 50))

    expect(callbacks.onError).not.toHaveBeenCalled()
  })

  it('should skip malformed events (missing event: or data: lines)', async () => {
    const callbacks = { onASR: vi.fn(), onDone: vi.fn() }

    const payload = [
      'data: {"text":"no event line"}\n\n',          // no event: prefix → skipped
      'event: asr\n\n',                               // no data: line → skipped
      sseEvent('asr', { text: 'valid' }),             // valid
      'event: done\ndata: not-json\n\n',              // invalid JSON → skipped
      sseEvent('done', { session_id: 'ok' }),         // valid
    ].join('')

    const body = createMockStream([payload])
    global.fetch.mockResolvedValue({ ok: true, body })

    streamChat(new Blob(), 'coffee_shop', [], '', callbacks)
    await new Promise((r) => setTimeout(r, 50))

    expect(callbacks.onASR).toHaveBeenCalledTimes(1)
    expect(callbacks.onASR).toHaveBeenCalledWith('valid')
    expect(callbacks.onDone).toHaveBeenCalledWith({ session_id: 'ok' })
  })

  it('should handle pronunciation event callback', async () => {
    const callbacks = { onPronunciation: vi.fn() }

    const body = createMockStream([sseEvent('pronunciation', { overall: 85, words: [] })])
    global.fetch.mockResolvedValue({ ok: true, body })

    streamChat(new Blob(), 'coffee_shop', [], '', callbacks)
    await new Promise((r) => setTimeout(r, 50))

    expect(callbacks.onPronunciation).toHaveBeenCalledWith({ overall: 85, words: [] })
  })
})
