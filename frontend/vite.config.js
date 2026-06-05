import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@voice': path.resolve(__dirname, '../voice'),
      '@shared': path.resolve(__dirname, '../shared'),
      '@chat': path.resolve(__dirname, 'chat'),
      '@dashboard': path.resolve(__dirname, 'dashboard'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
