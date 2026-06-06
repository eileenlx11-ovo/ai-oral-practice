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
          <span>首页</span>
        </router-link>
        <router-link to="/pronunciation" class="nav-link" active-class="active">
          <span class="nav-icon">🎯</span>
          <span>发音</span>
        </router-link>
        <router-link to="/dashboard" class="nav-link" active-class="active">
          <span class="nav-icon">📊</span>
          <span>进度</span>
        </router-link>
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
        <span class="tab-label">练习</span>
      </router-link>
      <router-link to="/pronunciation" class="tab-item" active-class="active">
        <span class="tab-icon">🎯</span>
        <span class="tab-label">发音</span>
      </router-link>
      <router-link to="/dashboard" class="tab-item" active-class="active">
        <span class="tab-icon">📊</span>
        <span class="tab-label">进度</span>
      </router-link>
    </nav>
  </div>
</template>

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
