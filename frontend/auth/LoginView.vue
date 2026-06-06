<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-header">
        <span class="auth-logo">🎙️</span>
        <h1>SpeakFlow</h1>
        <p class="auth-subtitle">AI 英语口语陪练</p>
      </div>

      <!-- Tab switch -->
      <div class="auth-tabs">
        <button
          class="tab" :class="{ active: mode === 'login' }"
          @click="mode = 'login'; error = ''"
        >登录</button>
        <button
          class="tab" :class="{ active: mode === 'register' }"
          @click="mode = 'register'; error = ''"
        >注册</button>
      </div>

      <form @submit.prevent="handleSubmit" class="auth-form">
        <div v-if="mode === 'register'" class="field">
          <label for="nickname">昵称</label>
          <input
            id="nickname" v-model="nickname" type="text"
            placeholder="你的名字" autocomplete="name"
          />
        </div>

        <div class="field">
          <label for="email">邮箱</label>
          <input
            id="email" v-model="email" type="email" required
            placeholder="your@email.com" autocomplete="email"
          />
        </div>

        <div class="field">
          <label for="password">密码</label>
          <input
            id="password" v-model="password" type="password" required
            :placeholder="mode === 'register' ? '至少 6 位' : '输入密码'"
            autocomplete="current-password"
          />
        </div>

        <p v-if="error" class="error-msg">{{ error }}</p>

        <button type="submit" class="submit-btn" :disabled="loading">
          {{ loading ? '请稍候...' : (mode === 'login' ? '登录' : '注册') }}
        </button>
      </form>

      <!-- Skip for demo -->
      <button class="skip-btn" @click="skipAuth">
        跳过，先体验 →
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { login, register } from '../composables/useAuth'

const router = useRouter()
const mode = ref('login')
const email = ref('')
const password = ref('')
const nickname = ref('')
const error = ref('')
const loading = ref(false)

async function handleSubmit() {
  error.value = ''
  loading.value = true
  try {
    if (mode.value === 'login') {
      await login(email.value, password.value)
    } else {
      if (password.value.length < 6) {
        error.value = '密码至少 6 位'
        return
      }
      await register(email.value, password.value, nickname.value)
    }
    router.push('/')
  } catch (e) {
    error.value = e.message || '操作失败，请重试'
  } finally {
    loading.value = false
  }
}

function skipAuth() {
  router.push('/')
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg);
  padding: var(--space-4);
}

.auth-card {
  width: 100%;
  max-width: 400px;
  background: var(--color-surface);
  border-radius: var(--radius-xl);
  padding: var(--space-8);
  box-shadow: var(--shadow-xl);
  animation: scale-in var(--transition-base) both;
}

.auth-header {
  text-align: center;
  margin-bottom: var(--space-6);
}

.auth-logo { font-size: 2.5rem; }

.auth-header h1 {
  font-size: var(--text-2xl);
  font-weight: 800;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-light));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-top: var(--space-2);
}

.auth-subtitle {
  color: var(--color-text-muted);
  font-size: var(--text-sm);
  margin-top: var(--space-1);
}

.auth-tabs {
  display: flex;
  background: var(--color-bg);
  border-radius: var(--radius-md);
  padding: 3px;
  margin-bottom: var(--space-6);
}

.tab {
  flex: 1;
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text-secondary);
  transition: all var(--transition-fast);
}

.tab.active {
  background: var(--color-surface);
  color: var(--color-primary);
  box-shadow: var(--shadow-sm);
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.field {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.field label {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text-secondary);
}

.field input {
  padding: var(--space-3) var(--space-4);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--text-base);
  font-family: inherit;
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
  outline: none;
}

.field input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(26, 86, 219, 0.1);
}

.field input::placeholder { color: var(--color-text-muted); }

.error-msg {
  color: var(--color-error);
  font-size: var(--text-sm);
  text-align: center;
}

.submit-btn {
  padding: var(--space-3) var(--space-4);
  background: var(--color-primary);
  color: white;
  border-radius: var(--radius-md);
  font-size: var(--text-base);
  font-weight: 600;
  transition: all var(--transition-fast);
  margin-top: var(--space-2);
}

.submit-btn:hover:not(:disabled) { background: var(--color-primary-dark); }
.submit-btn:disabled { opacity: 0.6; }

.skip-btn {
  display: block;
  width: 100%;
  margin-top: var(--space-4);
  padding: var(--space-2);
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  text-align: center;
  transition: color var(--transition-fast);
}

.skip-btn:hover { color: var(--color-primary); }
</style>
