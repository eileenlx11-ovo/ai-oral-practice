<template>
  <Transition name="toast-slide">
    <div v-if="visible" class="toast" :class="type">
      <span class="toast-icon">{{ icon }}</span>
      <span class="toast-message">{{ message }}</span>
      <button class="toast-close" @click="close">×</button>
    </div>
  </Transition>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  message: { type: String, default: '' },
  type: { type: String, default: 'info' }, // info | success | warning | error
  duration: { type: Number, default: 4000 },
})

const emit = defineEmits(['close'])
const visible = ref(false)
let timer = null

const icon = computed(() => {
  switch (props.type) {
    case 'success': return '✅'
    case 'warning': return '⚠️'
    case 'error': return '❌'
    default: return 'ℹ️'
  }
})

watch(() => props.message, (val) => {
  if (val) {
    visible.value = true
    clearTimeout(timer)
    if (props.duration > 0) {
      timer = setTimeout(close, props.duration)
    }
  }
})

function close() {
  visible.value = false
  emit('close')
}
</script>

<style scoped>
.toast {
  position: fixed;
  top: 1rem;
  left: 50%;
  transform: translateX(-50%);
  padding: 0.75rem 1.25rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  z-index: 9999;
  font-size: 0.9rem;
  max-width: 90vw;
}
.toast.info { background: #e3f2fd; color: #1565c0; }
.toast.success { background: #e8f5e9; color: #2e7d32; }
.toast.warning { background: #fff3e0; color: #e65100; }
.toast.error { background: #fbe9e7; color: #c62828; }

.toast-close {
  background: none; border: none; font-size: 1.2rem;
  cursor: pointer; opacity: 0.6; margin-left: 0.5rem;
}
.toast-close:hover { opacity: 1; }

.toast-slide-enter-active { transition: all 0.3s ease; }
.toast-slide-leave-active { transition: all 0.2s ease; }
.toast-slide-enter-from { opacity: 0; transform: translateX(-50%) translateY(-1rem); }
.toast-slide-leave-to { opacity: 0; transform: translateX(-50%) translateY(-0.5rem); }
</style>
