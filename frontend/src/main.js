import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'

const routes = [
  { path: '/', name: 'Home', component: () => import('../chat/HomeView.vue') },
  { path: '/chat/:scenario', name: 'Chat', component: () => import('../chat/ChatView.vue') },
  { path: '/pronunciation', name: 'Pronunciation', component: () => import('../pronunciation/PronunciationView.vue') },
  { path: '/dashboard', name: 'Dashboard', component: () => import('../dashboard/DashboardView.vue') },
  { path: '/assessment', name: 'Assessment', component: () => import('../assessment/LevelTest.vue') },
  { path: '/topic', name: 'CustomTopic', component: () => import('../topic/CustomTopicView.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

createApp(App).use(router).mount('#app')
