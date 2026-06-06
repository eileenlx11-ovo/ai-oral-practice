import { computed, onMounted, onUnmounted, ref } from 'vue'

const STORAGE_KEY = 'oral_practice_theme'
const theme = ref(localStorage.getItem(STORAGE_KEY) || 'system')
const systemDark = ref(false)
let mediaQuery = null

const resolvedTheme = computed(() => {
  if (theme.value === 'system') return systemDark.value ? 'dark' : 'light'
  return theme.value
})

function applyTheme() {
  document.documentElement.setAttribute('data-theme', resolvedTheme.value)
}

export function setTheme(value) {
  theme.value = ['light', 'dark', 'system'].includes(value) ? value : 'system'
  localStorage.setItem(STORAGE_KEY, theme.value)
  applyTheme()
}

export function useTheme() {
  onMounted(() => {
    mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    systemDark.value = mediaQuery.matches
    applyTheme()

    const handleChange = (event) => {
      systemDark.value = event.matches
      applyTheme()
    }
    mediaQuery.addEventListener('change', handleChange)
    onUnmounted(() => mediaQuery?.removeEventListener('change', handleChange))
  })

  return { theme, resolvedTheme, setTheme }
}
