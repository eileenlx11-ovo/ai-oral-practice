/**
 * useNetwork — 网络状态检测 composable
 * 监听 online/offline 事件，提供响应式的 isOnline 状态
 */
import { ref, onMounted, onUnmounted } from 'vue'

export function useNetwork() {
  const isOnline = ref(navigator.onLine)

  function handleOnline() { isOnline.value = true }
  function handleOffline() { isOnline.value = false }

  onMounted(() => {
    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)
  })

  onUnmounted(() => {
    window.removeEventListener('online', handleOnline)
    window.removeEventListener('offline', handleOffline)
  })

  return { isOnline }
}
