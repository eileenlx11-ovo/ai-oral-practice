import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import { isAuthenticated } from '../composables/useAuth'

const routes = [
  { path: '/login', name: 'Login', component: () => import('../auth/LoginView.vue'), meta: { guest: true } },
  { path: '/', name: 'Home', component: () => import('../chat/HomeView.vue') },
  { path: '/chat/:scenario', name: 'Chat', component: () => import('../chat/ChatView.vue') },
  { path: '/interview-prep', name: 'InterviewPrep', component: () => import('../interview/InterviewPrepView.vue') },
  { path: '/pronunciation', name: 'Pronunciation', component: () => import('../pronunciation/PronunciationView.vue') },
  { path: '/dashboard', name: 'Dashboard', component: () => import('../dashboard/DashboardView.vue') },
  { path: '/assessment', name: 'Assessment', component: () => import('../assessment/LevelTest.vue') },
  { path: '/settings', name: 'Settings', component: () => import('../settings/SettingsView.vue'), meta: { requiresAuth: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Auth guard — redirect to login if not authenticated (skip for guest routes)
router.beforeEach((to) => {
  if (to.meta.guest) return true
  if (to.meta.requiresAuth && !isAuthenticated.value) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
  return true
})

createApp(App).use(router).mount('#app')
