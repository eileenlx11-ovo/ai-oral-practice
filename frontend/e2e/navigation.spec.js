/**
 * E2E: 首页导航 + 场景选择
 */
import { test, expect } from '@playwright/test'

test.describe('Home & Navigation', () => {
  test('should render the home page with scenario cards', async ({ page }) => {
    await page.goto('/')
    await expect(page.locator('h1, .app-title')).toBeVisible()
    // Should have scenario selection or call-to-action
    await expect(page.locator('.cta-btn, .scenario-card, .tool-btn')).toHaveCount(expect.any(Number))
  })

  test('should navigate to dashboard', async ({ page }) => {
    await page.goto('/')
    await page.click('text=学习进度')
    await expect(page).toHaveURL(/\/dashboard/)
    await expect(page.locator('h1')).toContainText('Progress Dashboard')
  })

  test('should navigate to pronunciation practice', async ({ page }) => {
    await page.goto('/')
    await page.click('text=发音评测')
    await expect(page).toHaveURL(/\/pronunciation/)
  })
})
