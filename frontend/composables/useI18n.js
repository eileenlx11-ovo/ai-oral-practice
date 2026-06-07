import { computed, ref } from 'vue'
import zh from '../i18n/zh'
import en from '../i18n/en'

const STORAGE_KEY = 'oral_practice_locale'
const messages = { zh, en }
const locale = ref(localStorage.getItem(STORAGE_KEY) || 'zh')

function readPath(source, key) {
  return key.split('.').reduce((acc, part) => acc?.[part], source)
}

export const currentLocale = computed(() => locale.value)

export function setLocale(lang) {
  locale.value = messages[lang] ? lang : 'zh'
  localStorage.setItem(STORAGE_KEY, locale.value)
}

export function t(key, fallback = '') {
  const value = readPath(messages[locale.value], key) ?? readPath(messages.zh, key)
  return value ?? fallback ?? key
}

export function useI18n() {
  return { locale: currentLocale, setLocale, t }
}
