<template>
  <div id="app">
    <nav class="navbar">
      <router-link to="/" class="brand">🎙️ AI Oral Practice</router-link>
      <router-link to="/dashboard">📊 进步看板</router-link>
    </nav>
    <main>
      <router-view />
    </main>
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: #f5f7fa;
  color: #333;
}

.navbar {
  display: flex;
  align-items: center;
  gap: 2rem;
  padding: 1rem 2rem;
  background: #1f4e79;
  color: white;
}

.navbar a {
  color: white;
  text-decoration: none;
  font-weight: 500;
}

.brand {
  font-size: 1.2rem;
  font-weight: 700;
}

main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}
</style>
