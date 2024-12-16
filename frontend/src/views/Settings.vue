<template>
  <div class="settings">
    <el-card>
      <template #header>
        <h3>个人设置</h3>
      </template>

      <el-form
        ref="settingsFormRef"
        :model="settingsForm"
        :rules="settingsRules"
        label-width="100px">
        
        <el-form-item label="用户名" prop="username">
          <el-input v-model="settingsForm.username" disabled />
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input v-model="settingsForm.email" />
        </el-form-item>

        <el-form-item label="旧密码" prop="oldPassword">
          <el-input
            v-model="settingsForm.oldPassword"
            type="password"
            show-password />
        </el-form-item>

        <el-form-item label="新密码" prop="newPassword">
          <el-input
            v-model="settingsForm.newPassword"
            type="password"
            show-password />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="settingsForm.confirmPassword"
            type="password"
            show-password />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="loading">
            保存修改
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import { useStore } from 'vuex'

const store = useStore()
const loading = ref(false)
const settingsFormRef = ref()

const settingsForm = ref({
  username: store.state.user?.username || '',
  email: store.state.user?.email || '',
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const validatePass = (rule, value, callback) => {
  if (value === '') {
    callback()
  } else if (value !== settingsForm.value.newPassword) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const settingsRules = {
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  oldPassword: [
    { required: false, message: '请输入旧密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能小于6位', trigger: 'blur' }
  ],
  newPassword: [
    { required: false, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能小于6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { validator: validatePass, trigger: 'blur' }
  ]
}

const handleSubmit = async () => {
  if (!settingsFormRef.value) return

  try {
    await settingsFormRef.value.validate()
    loading.value = true

    const response = await request.put('/api/auth/settings/', settingsForm.value)
    
    store.commit('setUser', response.data.user)
    ElMessage.success('设置更新成功')
    
    // 清空密码字段
    settingsForm.value.oldPassword = ''
    settingsForm.value.newPassword = ''
    settingsForm.value.confirmPassword = ''
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '设置更新失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.settings {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}

h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}
</style> 