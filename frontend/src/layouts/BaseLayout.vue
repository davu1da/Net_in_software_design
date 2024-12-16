<template>
  <el-container class="layout-container">
    <el-aside width="200px">
      <el-menu
        :router="true"
        :default-active="$route.path"
        class="el-menu-vertical">
        <el-menu-item index="/dashboard">
          <el-icon><Monitor /></el-icon>
          <span>仪表板</span>
        </el-menu-item>

        <el-sub-menu index="/data">
          <template #title>
            <el-icon><Document /></el-icon>
            <span>数据管理</span>
          </template>
          
          <el-menu-item index="/data-management">
            <el-icon><Folder /></el-icon>
            <span>数据集管理</span>
          </el-menu-item>
          
          <el-menu-item index="/data-preprocessing">
            <el-icon><Edit /></el-icon>
            <span>数据预处理</span>
          </el-menu-item>
          
          <el-menu-item index="/data-processing">
            <el-icon><Operation /></el-icon>
            <span>数据处理</span>
          </el-menu-item>
        </el-sub-menu>

        <el-menu-item index="/model">
          <el-icon><Connection /></el-icon>
          <span>模型编辑器</span>
        </el-menu-item>

        <el-menu-item index="/training">
          <el-icon><VideoPlay /></el-icon>
          <span>模型训练</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <el-container>
      <el-header>
        <div class="header-content">
          <h2>神经网络设计平台</h2>
          <el-dropdown @command="handleCommand">
            <el-avatar :size="32" icon="UserFilled" />
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="settings">个人设置</el-dropdown-item>
                <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <el-main>
        <router-view></router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { 
  Monitor, 
  Document, 
  Connection, 
  VideoPlay,
  Folder,
  Edit,
  Operation 
} from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { ElMessage } from 'element-plus'

const router = useRouter()
const store = useStore()

const handleCommand = async (command) => {
  if (command === 'logout') {
    try {
      await store.dispatch('logout')
      ElMessage.success('已退出登录')
      router.push('/login')
    } catch (error) {
      ElMessage.error('退出登录失败')
    }
  } else if (command === 'settings') {
    router.push('/settings')
  }
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.el-header {
  background-color: #fff;
  border-bottom: 1px solid #dcdfe6;
  padding: 0 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}

.el-menu-vertical {
  height: 100%;
  border-right: none;
}

.el-main {
  background-color: #f5f7fa;
  padding: 20px;
}
</style> 