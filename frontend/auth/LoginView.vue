<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-header">
        <span class="auth-logo">🎙️</span>
        <h1>SpeakFlow</h1>
        <p class="auth-subtitle">{{ t('auth.subtitle') }}</p>
      </div>

      <!-- Tab switch: phone / login / register -->
      <div class="auth-tabs">
        <button class="tab" :class="{ active: mode === 'phone' }" @click="switchMode('phone')">{{ t('auth.phone') }}</button>
        <button class="tab" :class="{ active: mode === 'login' }" @click="switchMode('login')">{{ t('auth.emailLogin') }}</button>
        <button class="tab" :class="{ active: mode === 'register' }" @click="switchMode('register')">{{ t('auth.register') }}</button>
      </div>

      <!-- Phone SMS login -->
      <form v-if="mode === 'phone'" @submit.prevent="handlePhoneLogin" class="auth-form">
        <div class="field">
          <label for="phone">{{ t('auth.phone') }}</label>
          <input
            id="phone" v-model="phone" type="tel" required
            :placeholder="t('auth.phonePlaceholder')" autocomplete="tel"
            maxlength="11"
          />
        </div>

        <div class="field">
          <label for="sms-code">{{ t('auth.code') }}</label>
          <div class="code-row">
            <input
              id="sms-code" v-model="smsCode" type="text" required
              :placeholder="t('auth.codePlaceholder')" autocomplete="one-time-code"
              maxlength="6" inputmode="numeric"
            />
            <button
              type="button" class="send-code-btn"
              :disabled="codeCooldown > 0 || sendingCode"
              @click="handleSendCode"
            >
              {{ sendingCode ? t('auth.sending') : codeCooldown > 0 ? `${codeCooldown}s` : t('auth.sendCode') }}
            </button>
          </div>
        </div>

        <!-- Demo mode: show verification code -->
        <div v-if="devCode" class="demo-code-banner">
          <span class="demo-badge">演示模式</span>
          <span class="demo-code">验证码：<strong>{{ devCode }}</strong></span>
        </div>

        <p v-if="error" class="error-msg">{{ error }}</p>

        <button type="submit" class="submit-btn" :disabled="loading">
          {{ loading ? t('auth.waiting') : t('auth.loginOrRegister') }}
        </button>
      </form>

      <!-- Email login -->
      <form v-if="mode === 'login'" @submit.prevent="handleEmailLogin" class="auth-form">
        <div class="field">
          <label for="email">{{ t('auth.email') }}</label>
          <input id="email" v-model="email" type="email" required placeholder="your@email.com" autocomplete="email" />
        </div>
        <div class="field">
          <label for="password">{{ t('auth.password') }}</label>
          <input id="password" v-model="password" type="password" required :placeholder="t('auth.passwordPlaceholder')" autocomplete="current-password" />
        </div>
        <p v-if="error" class="error-msg">{{ error }}</p>
        <button type="submit" class="submit-btn" :disabled="loading">
          {{ loading ? t('auth.waiting') : t('app.nav.login') }}
        </button>
      </form>

      <!-- Email register -->
      <form v-if="mode === 'register'" @submit.prevent="handleRegister" class="auth-form">
        <div class="field">
          <label for="reg-nickname">{{ t('auth.nickname') }}</label>
          <input id="reg-nickname" v-model="nickname" type="text" :placeholder="t('auth.nicknamePlaceholder')" autocomplete="name" />
        </div>
        <div class="field">
          <label for="reg-email">{{ t('auth.email') }}</label>
          <input id="reg-email" v-model="email" type="email" required placeholder="your@email.com" autocomplete="email" />
        </div>
        <div class="field">
          <label for="reg-password">{{ t('auth.password') }}</label>
          <input id="reg-password" v-model="password" type="password" required :placeholder="t('auth.newPasswordPlaceholder')" autocomplete="new-password" />
        </div>
        <p v-if="error" class="error-msg">{{ error }}</p>
        <button type="submit" class="submit-btn" :disabled="loading">
          {{ loading ? t('auth.waiting') : t('auth.register') }}
        </button>
      </form>

      <!-- Skip for demo -->
      <button class="skip-btn" @click="skipAuth">
        {{ t('auth.skip') }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { login, register, phoneLogin, sendCode } from '../composables/useAuth'
import { useI18n } from '../composables/useI18n'

const router = useRouter()
const { t } = useI18n()
const redirectTo = () => router.currentRoute.value.query.redirect || '/'
const mode = ref('phone')
const email = ref('')
const password = ref('')
const nickname = ref('')
const phone = ref('')
const smsCode = ref('')
const error = ref('')
const loading = ref(false)
const sendingCode = ref(false)
const codeCooldown = ref(0)
const devCode = ref('')  // Show code in demo mode
let cooldownTimer = null

function switchMode(m) {
  mode.value = m
  error.value = ''
}

// --- Phone SMS flow ---
async function handleSendCode() {
  if (!phone.value || phone.value.length !== 11) {
    error.value = t('auth.invalidPhone')
    return
  }
  error.value = ''
  sendingCode.value = true
  try {
    const result = await sendCode(phone.value)
    // Dev/demo mode: show code on screen
    if (result._dev_code) {
      devCode.value = result._dev_code
    }
    startCooldown()
  } catch (e) {
    error.value = e.message || t('auth.sendFailed')
  } finally {
    sendingCode.value = false
  }
}

function startCooldown() {
  codeCooldown.value = 60
  cooldownTimer = setInterval(() => {
    codeCooldown.value--
    if (codeCooldown.value <= 0) clearInterval(cooldownTimer)
  }, 1000)
}

async function handlePhoneLogin() {
  if (!phone.value || phone.value.length !== 11) { error.value = t('auth.invalidPhone'); return }
  if (!smsCode.value || smsCode.value.length !== 6) { error.value = t('auth.invalidCode'); return }
  error.value = ''
  loading.value = true
  try {
    await phoneLogin(phone.value, smsCode.value)
    router.push(redirectTo())
  } catch (e) {
    error.value = e.message || t('auth.verifyFailed')
  } finally {
    loading.value = false
  }
}

// --- Email flows ---
async function handleEmailLogin() {
  error.value = ''
  loading.value = true
  try {
    await login(email.value, password.value)
    router.push(redirectTo())
  } catch (e) {
    error.value = e.message || t('auth.loginFailed')
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  if (password.value.length < 6) { error.value = t('auth.passwordTooShort'); loading.value = false; return }
  error.value = ''
  loading.value = true
  try {
    await register(email.value, password.value, nickname.value)
    router.push(redirectTo())
  } catch (e) {
    error.value = e.message || t('auth.registerFailed')
  } finally {
    loading.value = false
  }
}

function skipAuth() { router.push('/') }

onUnmounted(() => { if (cooldownTimer) clearInterval(cooldownTimer) })
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
  max-width: 420px;
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
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text-secondary);
  transition: all var(--transition-fast);
  white-space: nowrap;
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
  width: 100%;
}

.field input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(26, 86, 219, 0.1);
}

.field input::placeholder { color: var(--color-text-muted); }

.code-row {
  display: flex;
  gap: var(--space-2);
}

.code-row input {
  flex: 1;
}

.send-code-btn {
  padding: var(--space-3) var(--space-4);
  background: var(--color-primary-50);
  color: var(--color-primary);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: 600;
  white-space: nowrap;
  transition: all var(--transition-fast);
  min-width: 100px;
}

.send-code-btn:hover:not(:disabled) { background: var(--color-primary-100); }
.send-code-btn:disabled { opacity: 0.5; cursor: not-allowed; }

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

.demo-code-banner {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  background: var(--color-success-light);
  border: 1px solid var(--color-success);
  border-radius: var(--radius-md);
  animation: scale-in var(--transition-base) both;
}

.demo-badge {
  font-size: var(--text-xs);
  font-weight: 700;
  color: white;
  background: var(--color-success);
  padding: 2px 8px;
  border-radius: var(--radius-full);
}

.demo-code {
  font-size: var(--text-sm);
  color: var(--color-text);
}

.demo-code strong {
  font-size: var(--text-lg);
  letter-spacing: 2px;
  color: var(--color-success);
}

@media (max-width: 768px) {
  .auth-card {
    max-width: none;
    border-radius: var(--radius-lg);
    padding: var(--space-6);
  }

  .tab { font-size: var(--text-xs); padding: var(--space-2); }
}
</style>
