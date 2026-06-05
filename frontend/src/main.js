import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'

const routes = [
  { path: '/', name: 'Home', component: () => import('./views/HomeView.vue') },
  { path: '/chat/:scenario', name: 'Chat', component: () => import('./views/ChatView.vue') },
  { path: '/dashboard', name: 'Dashboard', component: () => import('./views/DashboardView.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

createApp(App).use(router).mount('#app')
