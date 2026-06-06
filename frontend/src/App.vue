<template>
  <div id="app">
    <!-- Top navbar (desktop) -->
    <nav class="navbar">
      <router-link to="/" class="brand">
        <span class="brand-icon">🎙️</span>
        <span class="brand-text">SpeakFlow</span>
      </router-link>
      <div class="nav-links">
        <router-link to="/" class="nav-link" active-class="active" :exact="true">
          <span class="nav-icon">🏠</span>
          <span>{{ t('app.nav.home') }}</span>
        </router-link>
        <router-link to="/pronunciation" class="nav-link" active-class="active">
          <span class="nav-icon">🎯</span>
          <span>{{ t('app.nav.pronunciation') }}</span>
        </router-link>
        <router-link to="/dashboard" class="nav-link" active-class="active">
          <span class="nav-icon">📊</span>
          <span>{{ t('app.nav.progress') }}</span>
        </router-link>
      </div>
      <div class="nav-auth">
        <template v-if="isAuthenticated">
          <router-link to="/settings" class="nav-settings-btn" title="设置">⚙️</router-link>
          <span class="user-badge">{{ currentUser?.nickname || t('app.nav.user') }}</span>
          <button class="logout-btn" @click="handleLogout">{{ t('app.nav.logout') }}</button>
        </template>
        <template v-else>
          <router-link to="/settings" class="nav-settings-btn" title="设置">⚙️</router-link>
          <router-link to="/login" class="login-btn">{{ t('app.nav.login') }}</router-link>
        </template>
      </div>
    </nav>

    <!-- Main content -->
    <main>
      <router-view v-slot="{ Component }">
        <transition name="page" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <!-- Mobile bottom tab bar -->
    <nav class="tab-bar">
      <router-link to="/" class="tab-item" active-class="active" :exact="true">
        <span class="tab-icon">🏠</span>
        <span class="tab-label">{{ t('app.nav.practice') }}</span>
      </router-link>
      <router-link to="/pronunciation" class="tab-item" active-class="active">
        <span class="tab-icon">🎯</span>
        <span class="tab-label">{{ t('app.nav.pronunciation') }}</span>
      </router-link>
      <router-link to="/dashboard" class="tab-item" active-class="active">
        <span class="tab-icon">📊</span>
        <span class="tab-label">{{ t('app.nav.progress') }}</span>
      </router-link>
      <router-link to="/settings" class="tab-item" active-class="active">
        <span class="tab-icon">⚙️</span>
        <span class="tab-label">{{ t('app.nav.settings') }}</span>
      </router-link>
    </nav>
  </div>
</template>

<script setup>
import { isAuthenticated, currentUser, logout } from '../composables/useAuth'
import { useI18n } from '../composables/useI18n'
import { useTheme } from '../composables/useTheme'
import { useRouter } from 'vue-router'

const router = useRouter()
const { t } = useI18n()
useTheme()

function handleLogout() {
  logout()
  router.push('/login')
}
</script>

<style>
@import '../styles/variables.css';
@import '../styles/global.css';

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* --- Navbar --- */
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4) var(--space-8);
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  position: sticky;
  top: 0;
  z-index: var(--z-sticky);
  backdrop-filter: blur(8px);
  background: rgba(255, 255, 255, 0.92);
}

.brand {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.brand-icon {
  font-size: 1.5rem;
}

.brand-text {
  font-size: var(--text-xl);
  font-weight: 800;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-light));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav-links {
  display: flex;
  gap: var(--space-2);
}

.nav-link {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-full);
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text-secondary);
  transition: all var(--transition-fast);
}

.nav-link:hover {
  background: var(--color-primary-50);
  color: var(--color-primary);
}

.nav-link.active {
  background: var(--color-primary-100);
  color: var(--color-primary);
  font-weight: 600;
}

.nav-icon {
  font-size: 1.1rem;
}

/* --- Main content --- */
main {
  flex: 1;
  max-width: 1100px;
  width: 100%;
  margin: 0 auto;
  padding: var(--space-8);
  padding-bottom: calc(var(--space-8) + 80px); /* Room for tab bar on mobile */
}

/* Immersive routes (chat) go full-bleed: no padding, no max-width cap, no overflow */
main:has(.chat-view) {
  max-width: none;
  padding: 0;
  min-height: 0;
  overflow: hidden;
}

/* --- Page transition --- */
.page-enter-active,
.page-leave-active {
  transition: opacity 200ms ease, transform 200ms ease;
}

.page-enter-from {
  opacity: 0;
  transform: translateY(8px);
}

.page-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

/* --- Mobile tab bar --- */
.tab-bar {
  display: none;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: var(--color-surface);
  border-top: 1px solid var(--color-border);
  padding: var(--space-2) 0;
  padding-bottom: env(safe-area-inset-bottom, var(--space-2));
  z-index: var(--z-sticky);
}

.tab-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: var(--space-1) var(--space-3);
  color: var(--color-text-muted);
  font-size: var(--text-xs);
  transition: color var(--transition-fast);
}

.tab-item.active {
  color: var(--color-primary);
}

.tab-item.active .tab-icon {
  transform: scale(1.1);
}

.tab-icon {
  font-size: 1.3rem;
  transition: transform var(--transition-bounce);
}

.tab-label {
  font-weight: 500;
}

/* --- Auth nav --- */
.nav-auth {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.user-badge {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text-secondary);
  padding: var(--space-1) var(--space-3);
  background: var(--color-primary-50);
  border-radius: var(--radius-full);
}

.logout-btn {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  transition: color var(--transition-fast);
}
.logout-btn:hover { color: var(--color-error); }

.login-btn {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-primary);
  padding: var(--space-2) var(--space-4);
  border: 1px solid var(--color-primary);
  border-radius: var(--radius-full);
  transition: all var(--transition-fast);
}
.login-btn:hover { background: var(--color-primary); color: white; }

.nav-settings-btn {
  font-size: 1.2rem;
  padding: var(--space-1);
  opacity: 0.7;
  transition: opacity var(--transition-fast);
}
.nav-settings-btn:hover { opacity: 1; }

/* --- Responsive --- */
@media (max-width: 768px) {
  .navbar {
    padding: var(--space-3) var(--space-4);
  }

  .nav-links {
    display: none;
  }

  .tab-bar {
    display: flex;
    justify-content: space-around;
  }

  main {
    padding: var(--space-4);
    padding-bottom: 100px;
  }
}
</style>
