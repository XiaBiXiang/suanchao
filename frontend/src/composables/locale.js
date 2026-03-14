import { computed, ref } from 'vue'

const LOCALE_STORAGE_KEY = 'suanchao_locale'

const normalizeLocale = (value) => (value === 'en' ? 'en' : 'zh')

const detectInitialLocale = () => {
  if (typeof window === 'undefined') return 'zh'
  const saved = localStorage.getItem(LOCALE_STORAGE_KEY)
  return normalizeLocale(saved)
}

export const locale = ref(detectInitialLocale())

const syncDocumentLang = (lang) => {
  if (typeof document === 'undefined') return
  document.documentElement.lang = lang === 'en' ? 'en' : 'zh-CN'
}

export const setLocale = (nextLocale) => {
  const normalized = normalizeLocale(nextLocale)
  locale.value = normalized
  if (typeof window !== 'undefined') {
    localStorage.setItem(LOCALE_STORAGE_KEY, normalized)
  }
  syncDocumentLang(normalized)
}

export const toggleLocale = () => {
  setLocale(locale.value === 'zh' ? 'en' : 'zh')
}

export const t = (zhText, enText) => (locale.value === 'en' ? (enText || zhText) : zhText)

export const useLocale = () => ({
  locale,
  isEnglish: computed(() => locale.value === 'en'),
  setLocale,
  toggleLocale,
  t
})

syncDocumentLang(locale.value)
