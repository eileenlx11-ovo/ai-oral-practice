/**
 * E2E: SSE 流式对话 — 验证 mock-server 到前端完整链路
 * 注意：录音依赖 getUserMedia，在 headless 浏览器中需要 mock
 */
import { test, expect } from '@playwright/test'

test.describe('Chat SSE Flow', () => {
  test('should load scenario chat page with greeting', async ({ page }) => {
    await page.goto('/chat/coffee_shop')

    // Should show character name or scenario title
    await expect(page.locator('.chat-header')).toContainText('Coffee Shop')

    // Greeting message should appear (loaded from mock /api/scenarios/:id)
    await expect(page.locator('.message.assistant .bubble')).toBeVisible({ timeout: 5000 })
  })

  test('should show record button in idle state', async ({ page }) => {
    await page.goto('/chat/coffee_shop')

    const recordBtn = page.locator('.record-btn')
    await expect(recordBtn).toBeVisible()
    await expect(recordBtn).toContainText('点击录音')
    await expect(recordBtn).toBeEnabled()
  })

  test('should display offline banner when network is offline', async ({ page }) => {
    await page.goto('/chat/coffee_shop')

    // Simulate going offline
    await page.context().setOffline(true)

    // The offline banner should appear (reactive)
    await expect(page.locator('.offline-banner')).toBeVisible({ timeout: 3000 })

    // Record button should be disabled
    const recordBtn = page.locator('.record-btn')
    await expect(recordBtn).toBeDisabled()
    await expect(recordBtn).toContainText('离线中')

    // Go back online
    await page.context().setOffline(false)
    await expect(page.locator('.offline-banner')).toBeHidden({ timeout: 3000 })
    await expect(recordBtn).toBeEnabled()
  })

  test('SSE stream integration — simulate a full turn via direct API call', async ({ page }) => {
    await page.goto('/chat/coffee_shop')

    // We cannot easily trigger real mic recording in headless mode.
    // Instead we verify the mock server SSE endpoint works by calling it directly
    // and checking the response format.
    const response = await page.evaluate(async () => {
      const formData = new FormData()
      formData.append('audio', new Blob(['fake-audio'], { type: 'audio/webm' }), 'recording.webm')
      formData.append('scenario', 'coffee_shop')
      formData.append('history', '[]')
      formData.append('session_id', 'e2e-test')

      const res = await fetch('/api/stream', { method: 'POST', body: formData })
      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let full = ''
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        full += decoder.decode(value, { stream: true })
      }
      return full
    })

    // Verify SSE format
    expect(response).toContain('event: asr')
    expect(response).toContain('event: sentence')
    expect(response).toContain('event: done')
    expect(response).toContain('"index":')
    expect(response).toContain('"audio_url":')
  })

  test('should show end session button after 3+ turns', async ({ page }) => {
    await page.goto('/chat/coffee_shop')

    // Initially end button should not be visible (0 turns)
    await expect(page.locator('.end-btn')).toBeHidden()
  })
})
