<template>
  <div class="settings-page">
    <header class="settings-header">
      <button @click="$router.back()" class="back-btn">← {{ t('settings.back') }}</button>
      <h1>{{ t('settings.title') }}</h1>
    </header>

    <div class="settings-sections">
      <!-- Profile section -->
      <section class="settings-section">
        <h2 class="section-title">👤 {{ t('settings.profile') }}</h2>
        <div class="setting-item">
          <label>{{ t('settings.nickname') }}</label>
          <div class="input-row">
            <input v-model="nickname" type="text" :placeholder="t('settings.nicknamePlaceholder')" />
            <button class="save-btn" :disabled="saving" @click="saveSettings">{{ t('settings.save') }}</button>
          </div>
        </div>
        <div class="setting-item" v-if="userInfo">
          <label>{{ t('settings.account') }}</label>
          <span class="setting-value">{{ userInfo.email || userInfo.phone || t('settings.guest') }}</span>
        </div>
      </section>

      <!-- Voice preference -->
      <section class="settings-section">
        <h2 class="section-title">🎙️ {{ t('settings.voicePreference') }}</h2>
        <p class="section-desc">{{ t('settings.voiceDesc') }}</p>
        <div class="voice-grid">
          <button
            v-for="v in voices" :key="v.key"
            class="voice-card" :class="{ active: selectedVoice === v.key }"
            @click="selectedVoice = v.key"
          >
            <span class="voice-flag">{{ v.flag }}</span>
            <span class="voice-label">{{ t(v.labelKey) }}</span>
            <button class="voice-preview" @click.stop="previewVoice(v.key)" :title="t('settings.preview')">
              🔊
            </button>
          </button>
        </div>
      </section>

      <!-- Theme -->
      <section class="settings-section">
        <h2 class="section-title">🎨 {{ t('settings.theme') }}</h2>
        <div class="theme-options">
          <button
            v-for="themeOption in themes" :key="themeOption.value"
            class="theme-btn" :class="{ active: selectedTheme === themeOption.value }"
            @click="selectedTheme = themeOption.value"
          >
            <span class="theme-icon">{{ themeOption.icon }}</span>
            <span>{{ t(themeOption.labelKey) }}</span>
          </button>
        </div>
      </section>

      <!-- Language -->
      <section class="settings-section">
        <h2 class="section-title">🌐 {{ t('settings.language') }}</h2>
        <div class="lang-options">
          <button
            class="lang-btn" :class="{ active: selectedLocale === 'zh' }"
            @click="selectedLocale = 'zh'"
          >中文</button>
          <button
            class="lang-btn" :class="{ active: selectedLocale === 'en' }"
            @click="selectedLocale = 'en'"
          >English</button>
        </div>
        <p class="section-tip">💡 {{ t('settings.languageTip') }}</p>
      </section>

      <!-- Account actions -->
      <section class="settings-section">
        <h2 class="section-title">⚙️ {{ t('settings.account') }}</h2>
        <button class="action-btn danger" @click="handleLogout">{{ t('settings.logout') }}</button>
      </section>
    </div>

    <!-- Save floating button -->
    <div v-if="hasChanges" class="save-bar">
      <button class="save-all-btn" :disabled="saving" @click="saveSettings">
        {{ saving ? t('settings.saving') : t('settings.saveSettings') }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { currentUser, getAuthHeaders, logout, isAuthenticated } from '../composables/useAuth'
import { useI18n } from '../composables/useI18n'
import { setTheme } from '../composables/useTheme'

const router = useRouter()
const { t, setLocale } = useI18n()

const voices = [
  { key: 'american_female', labelKey: 'settings.voices.americanFemale', flag: '🇺🇸' },
  { key: 'american_male', labelKey: 'settings.voices.americanMale', flag: '🇺🇸' },
  { key: 'british_female', labelKey: 'settings.voices.britishFemale', flag: '🇬🇧' },
  { key: 'british_male', labelKey: 'settings.voices.britishMale', flag: '🇬🇧' },
  { key: 'indian_female', labelKey: 'settings.voices.indianFemale', flag: '🇮🇳' },
  { key: 'indian_male', labelKey: 'settings.voices.indianMale', flag: '🇮🇳' },
  { key: 'australian_female', labelKey: 'settings.voices.australianFemale', flag: '🇦🇺' },
]

const themes = [
  { value: 'light', labelKey: 'settings.themes.light', icon: '☀️' },
  { value: 'dark', labelKey: 'settings.themes.dark', icon: '🌙' },
  { value: 'system', labelKey: 'settings.themes.system', icon: '💻' },
]

const nickname = ref('')
const selectedVoice = ref('american_female')
const selectedTheme = ref('system')
const selectedLocale = ref('zh')
const saving = ref(false)
const userInfo = ref(null)

// Track original values for change detection
let original = {}

const hasChanges = computed(() => {
  return nickname.value !== original.nickname ||
    selectedVoice.value !== original.voice ||
    selectedTheme.value !== original.theme ||
    selectedLocale.value !== original.locale
})

onMounted(async () => {
  userInfo.value = currentUser.value
  if (!isAuthenticated.value) {
    // Load from localStorage for guests
    selectedVoice.value = localStorage.getItem('oral_practice_voice') || 'american_female'
    selectedTheme.value = localStorage.getItem('oral_practice_theme') || 'system'
    selectedLocale.value = localStorage.getItem('oral_practice_locale') || 'zh'
    nickname.value = t('settings.guest')
    original = { nickname: nickname.value, voice: selectedVoice.value, theme: selectedTheme.value, locale: selectedLocale.value }
    return
  }
  try {
    const res = await fetch('/api/settings', { headers: getAuthHeaders() })
    if (res.ok) {
      const data = await res.json()
      nickname.value = data.nickname || ''
      selectedVoice.value = data.voice || 'american_female'
      selectedTheme.value = data.theme || 'system'
      selectedLocale.value = data.locale || 'zh'
    }
  } catch { /* use defaults */ }
  original = { nickname: nickname.value, voice: selectedVoice.value, theme: selectedTheme.value, locale: selectedLocale.value }
})

async function saveSettings() {
  saving.value = true
  // Apply theme immediately
  setTheme(selectedTheme.value)
  setLocale(selectedLocale.value)
  localStorage.setItem('oral_practice_voice', selectedVoice.value)
  localStorage.setItem('oral_practice_theme', selectedTheme.value)
  localStorage.setItem('oral_practice_locale', selectedLocale.value)

  if (isAuthenticated.value) {
    try {
      const formData = new FormData()
      formData.append('nickname', nickname.value)
      formData.append('voice', selectedVoice.value)
      formData.append('locale', selectedLocale.value)
      formData.append('theme', selectedTheme.value)
      await fetch('/api/settings', { method: 'PUT', headers: getAuthHeaders(), body: formData })
    } catch { /* localStorage fallback already saved */ }
  }
  original = { nickname: nickname.value, voice: selectedVoice.value, theme: selectedTheme.value, locale: selectedLocale.value }
  saving.value = false
}

function previewVoice(voiceKey) {
  // Play a short sample sentence using the backend TTS
  const text = 'Hello! This is how I sound.'
  const audio = new Audio(`/api/tts-preview?voice=${voiceKey}&text=${encodeURIComponent(text)}`)
  audio.play().catch(() => {})
}

function handleLogout() {
  logout()
  router.push('/login')
}
</script>

<style scoped>
.settings-page {
  max-width: 640px;
  margin: 0 auto;
  padding: var(--space-6) var(--space-4);
  padding-bottom: 100px;
}

.settings-header {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.settings-header h1 {
  font-size: var(--text-xl);
  font-weight: 700;
}

.back-btn {
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  transition: all var(--transition-fast);
}
.back-btn:hover { background: var(--color-bg); }

.settings-sections {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

.settings-section {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  box-shadow: var(--shadow-sm);
}

.section-title {
  font-size: var(--text-base);
  font-weight: 600;
  margin-bottom: var(--space-3);
}

.section-desc {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  margin-bottom: var(--space-4);
}

.section-tip {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  margin-top: var(--space-3);
}

.setting-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-3) 0;
  border-bottom: 1px solid var(--color-border);
}
.setting-item:last-child { border-bottom: none; }

.setting-item label {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text-secondary);
}

.setting-value {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
}

.input-row {
  display: flex;
  gap: var(--space-2);
  align-items: center;
}

.input-row input {
  padding: var(--space-2) var(--space-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  width: 150px;
  outline: none;
  transition: border-color var(--transition-fast);
}
.input-row input:focus { border-color: var(--color-primary); }

.save-btn {
  padding: var(--space-2) var(--space-3);
  background: var(--color-primary);
  color: white;
  border-radius: var(--radius-md);
  font-size: var(--text-xs);
  font-weight: 600;
}

/* Voice grid */
.voice-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: var(--space-3);
}

.voice-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-1);
  padding: var(--space-3);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
  position: relative;
}
.voice-card:hover { border-color: var(--color-primary-light); }
.voice-card.active {
  border-color: var(--color-primary);
  background: var(--color-primary-50);
}

.voice-flag { font-size: 1.5rem; }
.voice-label { font-size: var(--text-xs); font-weight: 500; }
.voice-preview {
  position: absolute;
  top: 4px;
  right: 4px;
  font-size: 0.8rem;
  opacity: 0.6;
}
.voice-preview:hover { opacity: 1; }

/* Theme options */
.theme-options {
  display: flex;
  gap: var(--space-3);
}

.theme-btn {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-4);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  transition: all var(--transition-fast);
}
.theme-btn:hover { border-color: var(--color-primary-light); }
.theme-btn.active {
  border-color: var(--color-primary);
  background: var(--color-primary-50);
}
.theme-icon { font-size: 1.5rem; }

/* Language options */
.lang-options {
  display: flex;
  gap: var(--space-3);
}

.lang-btn {
  flex: 1;
  padding: var(--space-3);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: 600;
  text-align: center;
  transition: all var(--transition-fast);
}
.lang-btn:hover { border-color: var(--color-primary-light); }
.lang-btn.active {
  border-color: var(--color-primary);
  background: var(--color-primary-50);
  color: var(--color-primary);
}

/* Action buttons */
.action-btn {
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: 500;
  transition: all var(--transition-fast);
}
.action-btn.danger {
  color: var(--color-error);
  border: 1px solid var(--color-error);
}
.action-btn.danger:hover {
  background: var(--color-error);
  color: white;
}

/* Floating save bar */
.save-bar {
  position: fixed;
  bottom: 80px;
  left: 50%;
  transform: translateX(-50%);
  z-index: var(--z-dropdown);
}

.save-all-btn {
  padding: var(--space-3) var(--space-8);
  background: var(--color-primary);
  color: white;
  border-radius: var(--radius-full);
  font-size: var(--text-sm);
  font-weight: 600;
  box-shadow: var(--shadow-lg);
  transition: all var(--transition-fast);
}
.save-all-btn:hover { transform: scale(1.02); }
.save-all-btn:disabled { opacity: 0.6; }

@media (max-width: 768px) {
  .settings-page { padding: var(--space-4) var(--space-3); }
  .voice-grid { grid-template-columns: repeat(2, 1fr); }
  .theme-options { flex-direction: column; }
  .input-row input { width: 120px; }
}
</style>
