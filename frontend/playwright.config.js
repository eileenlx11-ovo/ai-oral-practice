import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  timeout: 30000,
  retries: 1,
  use: {
    baseURL: 'http://localhost:3000',
    headless: true,
    screenshot: 'only-on-failure',
  },
  webServer: [
    {
      command: 'node ../mock-server/server.js',
      port: 8001,
      reuseExistingServer: true,
    },
    {
      command: 'npm run dev -- --port 3000',
      port: 3000,
      reuseExistingServer: true,
    },
  ],
})
