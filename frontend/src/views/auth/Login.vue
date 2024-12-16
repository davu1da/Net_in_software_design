<template>
  <el-card class="login-card">
    <template #header>
      <h2>登录</h2>
    </template>

    <el-form
      ref="loginFormRef"
      :model="loginForm"
      :rules="loginRules"
      label-position="top">
      <el-form-item label="用户名" prop="username">
        <el-input 
          v-model="loginForm.username"
          prefix-icon="User" />
      </el-form-item>

      <el-form-item label="密码" prop="password">
        <el-input
          v-model="loginForm.password"
          type="password"
          prefix-icon="Lock"
          show-password />
      </el-form-item>

      <el-form-item>
        <div class="form-actions">
          <el-button
            type="primary"
            :loading="loading"
            @click="handleLogin">
            登录
          </el-button>
          <el-link
            type="primary"
            @click="$router.push('/register')">
            没有账号？立即注册
          </el-link>
        </div>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import request from '@/utils/request'
import { useStore } from 'vuex'

const router = useRouter()
const store = useStore()
const loading = ref(false)
const loginFormRef = ref()

const loginForm = ref({
  username: '',
  password: ''
})

const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能小于6位', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  try {
    await loginFormRef.value.validate()
    loading.value = true
    
    const response = await request.post('/api/auth/login/', loginForm.value)
    
    // 存储认证信息
    localStorage.setItem('isAuthenticated', 'true')
    store.commit('setUser', response.data.user)
    
    ElMessage.success('登录成功')
    router.push('/dashboard')
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

h2 {
  text-align: center;
  margin: 0;
  color: #303133;
}

.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style> 