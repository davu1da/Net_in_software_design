<template>
  <div class="auth-layout">
    <div class="auth-container">
      <div class="auth-header">
        <h1>神经网络设计平台</h1>
      </div>
      <router-view></router-view>
    </div>
  </div>
</template>

<style scoped>
.auth-layout {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
}

.auth-container {
  width: 100%;
  max-width: 400px;
  padding: 20px;
}

.auth-header {
  text-align: center;
  margin-bottom: 30px;
}

.auth-header h1 {
  color: #409EFF;
  font-size: 24px;
  margin: 0;
}
</style> 