<template>
  <div class="dashboard">
    <h1>📊 进步看板</h1>
    <p class="subtitle">追踪你的口语练习进步</p>

    <div class="stats-grid">
      <div class="stat-card">
        <span class="stat-value">0</span>
        <span class="stat-label">总练习次数</span>
      </div>
      <div class="stat-card">
        <span class="stat-value">--</span>
        <span class="stat-label">平均发音评分</span>
      </div>
      <div class="stat-card">
        <span class="stat-value">--</span>
        <span class="stat-label">平均流利度</span>
      </div>
      <div class="stat-card">
        <span class="stat-value">0</span>
        <span class="stat-label">本周练习天数</span>
      </div>
    </div>

    <div class="chart-placeholder">
      <p>📈 评分趋势图（连接后端后展示历史数据）</p>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  text-align: center;
}

h1 {
  color: #1f4e79;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #666;
  margin-bottom: 2rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.stat-value {
  display: block;
  font-size: 2rem;
  font-weight: 700;
  color: #1f4e79;
}

.stat-label {
  display: block;
  margin-top: 0.5rem;
  font-size: 0.9rem;
  color: #666;
}

.chart-placeholder {
  background: white;
  border-radius: 12px;
  padding: 3rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  color: #999;
}
</style>
