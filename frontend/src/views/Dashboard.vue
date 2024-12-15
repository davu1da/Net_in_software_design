<template>
  <div class="dashboard">
    <!-- 顶部统计卡片 -->
    <el-row :gutter="20" class="statistics">
      <el-col :span="6">
        <el-card shadow="hover" class="statistic-card">
          <template #header>
            <div class="card-header">
              <span>数据集</span>
              <el-icon><DataLine /></el-icon>
            </div>
          </template>
          <div class="statistic-value">{{ statistics.datasetsCount }}</div>
          <div class="statistic-label">总数据集数量</div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover" class="statistic-card">
          <template #header>
            <div class="card-header">
              <span>模型</span>
              <el-icon><Connection /></el-icon>
            </div>
          </template>
          <div class="statistic-value">{{ statistics.modelsCount }}</div>
          <div class="statistic-label">已创建模型数量</div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover" class="statistic-card">
          <template #header>
            <div class="card-header">
              <span>训练</span>
              <el-icon><VideoPlay /></el-icon>
            </div>
          </template>
          <div class="statistic-value">{{ statistics.activeTrainings }}</div>
          <div class="statistic-label">正在训练的模型</div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover" class="statistic-card">
          <template #header>
            <div class="card-header">
              <span>部署</span>
              <el-icon><Cpu /></el-icon>
            </div>
          </template>
          <div class="statistic-value">{{ statistics.deployedModels }}</div>
          <div class="statistic-label">已部署模型数量</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 主要内容区域 -->
    <el-row :gutter="20" class="main-content">
      <!-- 左侧：最近训练记录 -->
      <el-col :span="16">
        <el-card class="recent-trainings">
          <template #header>
            <div class="card-header">
              <span>最近训练记录</span>
              <el-button type="primary" link @click="$router.push('/training')">
                查看全部
              </el-button>
            </div>
          </template>

          <el-table :data="recentTrainings" style="width: 100%">
            <el-table-column prop="name" label="模型名称" />
            <el-table-column prop="dataset" label="数据集" />
            <el-table-column prop="status" label="状态">
              <template #default="scope">
                <el-tag :type="getStatusType(scope.row.status)">
                  {{ scope.row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="accuracy" label="准确率">
              <template #default="scope">
                {{ formatAccuracy(scope.row.accuracy) }}
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="开始时间" />
          </el-table>
        </el-card>

        <!-- 系统资源监控 -->
        <el-card class="system-monitor">
          <template #header>
            <div class="card-header">
              <span>系统资源监控</span>
              <el-switch
                v-model="autoRefresh"
                active-text="自动刷新" />
            </div>
          </template>

          <el-row :gutter="20">
            <el-col :span="12">
              <div class="monitor-chart">
                <h4>CPU 使用率</h4>
                <v-chart :option="cpuChartOption" autoresize />
              </div>
            </el-col>
            <el-col :span="12">
              <div class="monitor-chart">
                <h4>内存使用率</h4>
                <v-chart :option="memoryChartOption" autoresize />
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>

      <!-- 右侧：通知和快捷操作 -->
      <el-col :span="8">
        <!-- 快捷操作 -->
        <el-card class="quick-actions">
          <template #header>
            <div class="card-header">
              <span>快捷操作</span>
            </div>
          </template>

          <div class="action-buttons">
            <el-button type="primary" @click="$router.push('/data')">
              <el-icon><Upload /></el-icon>
              上传数据集
            </el-button>
            <el-button type="success" @click="$router.push('/model')">
              <el-icon><Edit /></el-icon>
              创建新模型
            </el-button>
            <el-button type="warning" @click="$router.push('/training')">
              <el-icon><VideoPlay /></el-icon>
              开始训练
            </el-button>
          </div>
        </el-card>

        <!-- 系统通知 -->
        <el-card class="notifications">
          <template #header>
            <div class="card-header">
              <span>系统通知</span>
              <div class="notification-actions">
                <el-tooltip content="通知统计">
                  <el-button type="text" @click="showNotificationStats">
                    <el-icon><DataLine /></el-icon>
                  </el-button>
                </el-tooltip>
                <el-tooltip content="清理通知">
                  <el-button type="text" @click="showCleanupDialog">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </el-tooltip>
                <el-button type="primary" link @click="markAllAsRead">
                  全部标记已读
                </el-button>
              </div>
            </div>
          </template>

          <el-scrollbar height="400px">
            <div
              v-for="notification in notifications"
              :key="notification.id"
              class="notification-item"
              :class="{ unread: !notification.read }">
              <div class="notification-title">
                {{ notification.title }}
                <el-tag
                  v-if="!notification.read"
                  size="small"
                  type="danger">
                  新
                </el-tag>
              </div>
              <div class="notification-content">
                {{ notification.content }}
              </div>
              <div class="notification-time">
                {{ formatTime(notification.time) }}
              </div>
            </div>
          </el-scrollbar>
        </el-card>
      </el-col>
    </el-row>

    <!-- 添加清理对话框 -->
    <el-dialog
      v-model="cleanupDialogVisible"
      title="清理通知"
      width="400px">
      <el-form :model="cleanupForm" label-width="100px">
        <el-form-item label="保留天数">
          <el-input-number
            v-model="cleanupForm.days"
            :min="1"
            :max="365" />
        </el-form-item>
        <el-form-item label="仅清理已读">
          <el-switch v-model="cleanupForm.readOnly" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="cleanupDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="cleanupNotifications">
            确认清理
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 添加统计对话框 -->
    <el-dialog
      v-model="statsDialogVisible"
      title="通知统计"
      width="400px">
      <el-descriptions :column="1" border>
        <el-descriptions-item label="总通知数">
          {{ notificationStats.total_count }}
        </el-descriptions-item>
        <el-descriptions-item label="未读通知">
          {{ notificationStats.unread_count }}
        </el-descriptions-item>
        <el-descriptions-item label="最早通知">
          {{ formatDate(notificationStats.oldest_date) }}
        </el-descriptions-item>
        <el-descriptions-item label="最新通知">
          {{ formatDate(notificationStats.newest_date) }}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { DataLine, Connection, VideoPlay, Cpu, Upload, Edit, Delete } from '@element-plus/icons-vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, GaugeChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import request from '@/utils/request'
import dayjs from 'dayjs'

// 注册 ECharts 组件
use([CanvasRenderer, LineChart, GaugeChart, GridComponent, TooltipComponent, LegendComponent])

// 状态变量
const statistics = ref({
  datasetsCount: 0,
  modelsCount: 0,
  activeTrainings: 0,
  deployedModels: 0
})

const recentTrainings = ref([])
const notifications = ref([])
const autoRefresh = ref(true)
let refreshTimer = null

// 获取统计数据
const fetchStatistics = async () => {
  try {
    const response = await request.get('/api/dashboard/statistics/')
    statistics.value = response.data
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
}

// 获取最近训练记录
const fetchRecentTrainings = async () => {
  try {
    const response = await request.get('/api/training/sessions/recent/')
    recentTrainings.value = response.data
  } catch (error) {
    console.error('获取最近训练记录失败:', error)
  }
}

// 获取系统通知
const fetchNotifications = async () => {
  try {
    const response = await request.get('/api/dashboard/notifications/')
    notifications.value = response.data
  } catch (error) {
    console.error('获取系统通知失败:', error)
  }
}

// CPU使用率图表配置
const cpuChartOption = ref({
  series: [{
    type: 'gauge',
    progress: {
      show: true,
      width: 18
    },
    axisLine: {
      lineStyle: {
        width: 18
      }
    },
    axisTick: {
      show: false
    },
    splitLine: {
      length: 15,
      lineStyle: {
        width: 2,
        color: '#999'
      }
    },
    pointer: {
      show: false
    },
    title: {
      show: false
    },
    detail: {
      valueAnimation: true,
      formatter: '{value}%'
    },
    data: [{
      value: 70
    }]
  }]
})

// 内存使用率图表配置
const memoryChartOption = ref({
  series: [{
    type: 'gauge',
    progress: {
      show: true,
      width: 18
    },
    axisLine: {
      lineStyle: {
        width: 18
      }
    },
    axisTick: {
      show: false
    },
    splitLine: {
      length: 15,
      lineStyle: {
        width: 2,
        color: '#999'
      }
    },
    pointer: {
      show: false
    },
    title: {
      show: false
    },
    detail: {
      valueAnimation: true,
      formatter: '{value}%'
    },
    data: [{
      value: 50
    }]
  }]
})

// 工具方法
const getStatusType = (status) => {
  const types = {
    'running': 'primary',
    'completed': 'success',
    'failed': 'danger',
    'pending': 'info',
    'stopped': 'warning'
  }
  return types[status] || 'info'
}

const formatAccuracy = (value) => {
  return value ? `${(value * 100).toFixed(2)}%` : '-'
}

const formatTime = (time) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
}

// 自动刷新
const startAutoRefresh = () => {
  if (refreshTimer) clearInterval(refreshTimer)
  refreshTimer = setInterval(() => {
    if (autoRefresh.value) {
      fetchStatistics()
      fetchRecentTrainings()
    }
  }, 30000) // 每30秒刷新一次
}

// 添加系统监控WebSocket连接
const connectSystemMonitor = () => {
  const wsScheme = window.location.protocol === 'https:' ? 'wss' : 'ws'
  const wsUrl = `${wsScheme}://${window.location.host}/ws/system-monitor/`
  const ws = new WebSocket(wsUrl)
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    if (data.type === 'system_metrics') {
      updateSystemMetrics(data.data)
    }
  }

  return ws
}

const updateSystemMetrics = (metrics) => {
  cpuChartOption.value.series[0].data[0].value = metrics.cpu_percent
  memoryChartOption.value.series[0].data[0].value = metrics.memory_percent
}

// 生命周期钩子
onMounted(() => {
  fetchStatistics()
  fetchRecentTrainings()
  fetchNotifications()
  startAutoRefresh()
  const ws = connectSystemMonitor()
  
  onUnmounted(() => {
    if (refreshTimer) clearInterval(refreshTimer)
    ws.close()
  })
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.statistics {
  margin-bottom: 20px;
}

.statistic-card {
  .statistic-value {
    font-size: 24px;
    font-weight: bold;
    color: #409eff;
    margin: 10px 0;
  }

  .statistic-label {
    color: #666;
    font-size: 14px;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.main-content {
  margin-top: 20px;
}

.recent-trainings {
  margin-bottom: 20px;
}

.system-monitor {
  .monitor-chart {
    height: 300px;
  }
}

.quick-actions {
  margin-bottom: 20px;

  .action-buttons {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
}

.notifications {
  .notification-item {
    padding: 10px;
    border-bottom: 1px solid #eee;

    &.unread {
      background-color: #f5f7fa;
    }
  }

  .notification-title {
    font-weight: bold;
    margin-bottom: 5px;
  }

  .notification-content {
    color: #666;
    font-size: 14px;
    margin-bottom: 5px;
  }

  .notification-time {
    color: #999;
    font-size: 12px;
  }
}
</style> 