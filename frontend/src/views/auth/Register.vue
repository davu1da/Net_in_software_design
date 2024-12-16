<template>
  <el-card class="register-card">
    <template #header>
      <h2>注册</h2>
    </template>

    <el-form
      ref="registerFormRef"
      :model="registerForm"
      :rules="registerRules"
      label-position="top">
      <el-form-item label="用户名" prop="username">
        <el-input 
          v-model="registerForm.username"
          prefix-icon="User" />
      </el-form-item>

      <el-form-item label="邮箱" prop="email">
        <el-input
          v-model="registerForm.email"
          prefix-icon="Message" />
      </el-form-item>

      <el-form-item label="密码" prop="password">
        <el-input
          v-model="registerForm.password"
          type="password"
          prefix-icon="Lock"
          show-password />
      </el-form-item>

      <el-form-item label="确认密码" prop="confirmPassword">
        <el-input
          v-model="registerForm.confirmPassword"
          type="password"
          prefix-icon="Lock"
          show-password />
      </el-form-item>

      <el-form-item>
        <div class="form-actions">
          <el-button
            type="primary"
            :loading="loading"
            @click="handleRegister">
            注册
          </el-button>
          <el-link
            type="primary"
            @click="$router.push('/login')">
            已有账号？立即登录
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
import { User, Lock, Message } from '@element-plus/icons-vue'
import request from '@/utils/request'

const router = useRouter()
const loading = ref(false)
const registerFormRef = ref()

const registerForm = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const validatePass = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== registerForm.value.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, message: '用户名长度不能小于3位', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能小于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, validator: validatePass, trigger: 'blur' }
  ]
}

const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  try {
    await registerFormRef.value.validate()
    loading.value = true
    
    const response = await request.post('/api/auth/register/', {
      username: registerForm.value.username,
      email: registerForm.value.email,
      password: registerForm.value.password
    })
    
    localStorage.setItem('access_token', response.data.tokens.access)
    localStorage.setItem('refresh_token', response.data.tokens.refresh)
    
    ElMessage.success('注册成功')
    router.push('/dashboard')
  } catch (error) {
    console.error('注册错误:', error)
    ElMessage.error(error.response?.data?.message || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-card {
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