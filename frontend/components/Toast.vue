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
  top: var(--space-4);
  left: 50%;
  transform: translateX(-50%);
  padding: var(--space-3) var(--space-5);
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  gap: var(--space-3);
  box-shadow: var(--shadow-lg);
  z-index: var(--z-toast);
  font-size: var(--text-sm);
  font-weight: 500;
  max-width: 90vw;
  backdrop-filter: blur(8px);
}

.toast.info { background: rgba(219, 234, 254, 0.95); color: #1e40af; border: 1px solid var(--color-primary-200); }
.toast.success { background: rgba(209, 250, 229, 0.95); color: #065f46; border: 1px solid #a7f3d0; }
.toast.warning { background: rgba(254, 243, 199, 0.95); color: #92400e; border: 1px solid #fde68a; }
.toast.error { background: rgba(254, 226, 226, 0.95); color: #991b1b; border: 1px solid #fecaca; }

.toast-close {
  font-size: 1.1rem;
  opacity: 0.5;
  margin-left: var(--space-2);
  padding: var(--space-1);
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
  color: inherit;
}
.toast-close:hover { opacity: 1; background: rgba(0, 0, 0, 0.05); }

.toast-slide-enter-active { transition: all 300ms cubic-bezier(0.34, 1.56, 0.64, 1); }
.toast-slide-leave-active { transition: all 200ms ease; }
.toast-slide-enter-from { opacity: 0; transform: translateX(-50%) translateY(-1rem) scale(0.95); }
.toast-slide-leave-to { opacity: 0; transform: translateX(-50%) translateY(-0.5rem); }
</style>
