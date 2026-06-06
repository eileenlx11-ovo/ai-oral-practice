/**
 * E2E: Dashboard 页面 — 数据加载 + 错误处理
 */
import { test, expect } from '@playwright/test'

test.describe('Dashboard', () => {
  test('should display progress summary cards', async ({ page }) => {
    await page.goto('/dashboard')

    // Wait for data to load from mock server
    await expect(page.locator('.card-value').first()).toBeVisible({ timeout: 5000 })

    // Should show 4 summary cards
    const cards = page.locator('.summary-cards .card')
    await expect(cards).toHaveCount(4)

    // Verify mock data: total_sessions = 15
    await expect(page.locator('.card-value').first()).toHaveText('15')
  })

  test('should display score trend chart', async ({ page }) => {
    await page.goto('/dashboard')
    await expect(page.locator('.chart-section')).toBeVisible({ timeout: 5000 })
    await expect(page.locator('canvas')).toBeVisible()
  })

  test('should show session history list', async ({ page }) => {
    await page.goto('/dashboard')

    // Mock server returns 3 sessions
    const items = page.locator('.session-item')
    await expect(items).toHaveCount(3, { timeout: 5000 })
  })

  test('should open session detail modal on click', async ({ page }) => {
    await page.goto('/dashboard')

    const firstSession = page.locator('.session-item').first()
    await firstSession.waitFor({ state: 'visible', timeout: 5000 })
    await firstSession.click()

    // Modal should appear
    await expect(page.locator('.modal')).toBeVisible()
    await expect(page.locator('.modal h3')).toContainText('Session Report')
  })
})
