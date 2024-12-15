<template>
    <div class="model-training">
      <el-row :gutter="20">
        <!-- 左侧训练配置面板 -->
        <el-col :span="8">
          <el-card class="training-config">
            <template #header>
              <div class="card-header">
                <span>训练配置</span>
                <el-button type="primary" @click="startTraining" :disabled="isTraining">
                  开始训练
                </el-button>
              </div>
            </template>
  
            <el-form label-position="top">
              <el-form-item label="选择模型">
                <el-select v-model="selectedModel" placeholder="请选择模型">
                  <el-option
                    v-for="model in models"
                    :key="model.id"
                    :label="model.name"
                    :value="model.id" />
                </el-select>
              </el-form-item>
  
              <el-form-item label="训练数据集">
                <el-select v-model="trainingConfig.dataset" placeholder="请选择训练数据集">
                  <el-option
                    v-for="dataset in datasets"
                    :key="dataset.id"
                    :label="dataset.name"
                    :value="dataset.id" />
                </el-select>
              </el-form-item>
  
              <el-form-item label="验证数据集">
                <el-select
                  v-model="trainingConfig.validationDataset"
                  placeholder="请选择验证数据集">
                  <el-option
                    v-for="dataset in datasets"
                    :key="dataset.id"
                    :label="dataset.name"
                    :value="dataset.id" />
                </el-select>
              </el-form-item>
  
              <el-divider>超参数配置</el-divider>
  
              <el-form-item label="批次大小">
                <el-input-number
                  v-model="trainingConfig.batchSize"
                  :min="1"
                  :step="32" />
              </el-form-item>
  
              <el-form-item label="训练轮数">
                <el-input-number
                  v-model="trainingConfig.epochs"
                  :min="1" />
              </el-form-item>
  
              <el-form-item label="学习率">
                <el-select v-model="trainingConfig.learningRate">
                  <el-option label="0.1" value="0.1" />
                  <el-option label="0.01" value="0.01" />
                  <el-option label="0.001" value="0.001" />
                  <el-option label="0.0001" value="0.0001" />
                </el-select>
              </el-form-item>
  
              <el-form-item label="优化器">
                <el-select v-model="trainingConfig.optimizer">
                  <el-option label="Adam" value="adam" />
                  <el-option label="SGD" value="sgd" />
                  <el-option label="RMSprop" value="rmsprop" />
                </el-select>
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>
  
        <!-- 右侧训练监控面板 -->
        <el-col :span="16">
          <el-card class="training-monitor">
            <template #header>
              <div class="card-header">
                <span>训练监控</span>
                <el-button
                  v-if="isTraining"
                  type="danger"
                  @click="stopTraining">
                  停止训练
                </el-button>
              </div>
            </template>
  
            <!-- 训练进度 -->
            <div class="progress-section">
              <el-progress
                :percentage="trainingProgress"
                :status="trainingStatus"
                :stroke-width="20" />
              <div class="progress-info">
                <span>轮次: {{ currentEpoch }}/{{ trainingConfig.epochs }}</span>
                <span>耗时: {{ elapsedTime }}</span>
              </div>
            </div>
  
            <!-- 训练指标图表 -->
            <div class="metrics-charts">
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="chart-container">
                    <h4>损失函数</h4>
                    <v-chart :option="lossChartOption" autoresize />
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="chart-container">
                    <h4>准确率</h4>
                    <v-chart :option="accuracyChartOption" autoresize />
                  </div>
                </el-col>
              </el-row>
            </div>
  
            <!-- 训练日志 -->
            <div class="training-logs">
              <h4>训练日志</h4>
              <el-scrollbar height="200px">
                <div
                  v-for="(log, index) in trainingLogs"
                  :key="index"
                  class="log-item">
                  {{ log }}
                </div>
              </el-scrollbar>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </template>
  
  <script setup>
  import { ref, computed, onMounted } from 'vue'
  import { ElMessage } from 'element-plus'
  import request from '@/utils/request'
  import * as echarts from 'echarts/core'
  import { CanvasRenderer } from 'echarts/renderers'
  import { LineChart } from 'echarts/charts'
  import {
    GridComponent,
    TooltipComponent,
    LegendComponent
  } from 'echarts/components'
  import VChart, { THEME_KEY } from 'vue-echarts'
  
  // 注册必要的 echarts 组件
  echarts.use([
    CanvasRenderer,
    LineChart,
    GridComponent,
    TooltipComponent,
    LegendComponent
  ])
  
  // 状态变量
  const models = ref([])
  const datasets = ref([])
  const selectedModel = ref(null)
  const isTraining = ref(false)
  const currentEpoch = ref(0)
  const trainingLogs = ref([])
  const startTime = ref(null)
  
  // 训练配置
  const trainingConfig = ref({
    dataset: null,
    validationDataset: null,
    batchSize: 32,
    epochs: 10,
    learningRate: '0.001',
    optimizer: 'adam'
  })
  
  // 训练指标数据
  const metrics = ref({
    loss: [],
    accuracy: [],
    valLoss: [],
    valAccuracy: []
  })
  
  // 计算属性
  const trainingProgress = computed(() => {
    return Math.round((currentEpoch.value / trainingConfig.value.epochs) * 100)
  })
  
  const trainingStatus = computed(() => {
    if (!isTraining.value) return ''
    return trainingProgress.value === 100 ? 'success' : ''
  })
  
  const elapsedTime = computed(() => {
    if (!startTime.value) return '0:00'
    const elapsed = Math.floor((Date.now() - startTime.value) / 1000)
    const minutes = Math.floor(elapsed / 60)
    const seconds = elapsed % 60
    return `${minutes}:${seconds.toString().padStart(2, '0')}`
  })
  
  // 图表配置
  const lossChartOption = computed(() => ({
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['训练损失', '验证损失']
    },
    xAxis: {
      type: 'category',
      data: metrics.value.loss.map((_, index) => index + 1)
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '训练损失',
        type: 'line',
        data: metrics.value.loss
      },
      {
        name: '验证损失',
        type: 'line',
        data: metrics.value.valLoss
      }
    ]
  }))
  
  const accuracyChartOption = computed(() => ({
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['训练准确率', '验证准确率']
    },
    xAxis: {
      type: 'category',
      data: metrics.value.accuracy.map((_, index) => index + 1)
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '{value}%'
      }
    },
    series: [
      {
        name: '训练准确率',
        type: 'line',
        data: metrics.value.accuracy
      },
      {
        name: '验证准确率',
        type: 'line',
        data: metrics.value.valAccuracy
      }
    ]
  }))
  
  // 方法
  const fetchModels = async () => {
    try {
      const response = await request.get('/api/editor/networks/')
      models.value = response.data
    } catch (error) {
      ElMessage.error('获取模型列表失败')
    }
  }
  
  const fetchDatasets = async () => {
    try {
      const response = await request.get('/api/preprocessing/datasets/')
      datasets.value = response.data
    } catch (error) {
      ElMessage.error('获取数据集列表失败')
    }
  }
  
  const startTraining = async () => {
    if (!validateConfig()) return
  
    try {
      isTraining.value = true
      startTime.value = Date.now()
      currentEpoch.value = 0
      metrics.value = { loss: [], accuracy: [], valLoss: [], valAccuracy: [] }
      trainingLogs.value = []
  
      const response = await request.post('/api/training/sessions/', {
        network: selectedModel.value,
        ...trainingConfig.value
      })
  
      const sessionId = response.data.id
      startMonitoring(sessionId)
    } catch (error) {
      isTraining.value = false
      ElMessage.error('启动训练失败')
    }
  }
  
  const stopTraining = async () => {
    try {
      await request.post(`/api/training/sessions/${currentSession.value}/stop/`)
      isTraining.value = false
      ElMessage.success('训练已停止')
    } catch (error) {
      ElMessage.error('停止训练失败')
    }
  }
  
  const validateConfig = () => {
    if (!selectedModel.value) {
      ElMessage.warning('请选择模型')
      return false
    }
    if (!trainingConfig.value.dataset) {
      ElMessage.warning('请选择训练数据集')
      return false
    }
    return true
  }
  
  const startMonitoring = (sessionId) => {
    const wsScheme = window.location.protocol === 'https:' ? 'wss' : 'ws'
    const wsUrl = `${wsScheme}://${window.location.host}/ws/training/${sessionId}/`
    const ws = new WebSocket(wsUrl)
    
    ws.onopen = () => {
      console.log('WebSocket连接已建立')
    }
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      
      if (data.type === 'metrics') {
        updateMetrics(data.metrics)
      } else if (data.type === 'log') {
        trainingLogs.value.push(data.message)
      } else if (data.type === 'completed') {
        isTraining.value = false
        ElMessage.success('训练完成')
        ws.close()
      }
    }
  
    ws.onerror = (error) => {
      console.error('WebSocket错误:', error)
      isTraining.value = false
      ElMessage.error('训练监控连接失败')
    }
  
    ws.onclose = () => {
      console.log('WebSocket连接已关闭')
    }
  
    return ws
  }
  
  const updateMetrics = (newMetrics) => {
    currentEpoch.value = newMetrics.epoch
    metrics.value.loss.push(newMetrics.loss)
    metrics.value.accuracy.push(newMetrics.accuracy)
    metrics.value.valLoss.push(newMetrics.val_loss)
    metrics.value.valAccuracy.push(newMetrics.val_accuracy)
  }
  
  // 生命周期钩子
  onMounted(() => {
    fetchModels()
    fetchDatasets()
  })
  </script>
  
  <style scoped>
  .model-training {
    padding: 20px;
  }
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .training-config {
    height: calc(100vh - 100px);
    overflow-y: auto;
  }
  
  .training-monitor {
    height: calc(100vh - 100px);
    display: flex;
    flex-direction: column;
  }
  
  .progress-section {
    margin-bottom: 20px;
  }
  
  .progress-info {
    display: flex;
    justify-content: space-between;
    margin-top: 10px;
    color: #666;
  }
  
  .metrics-charts {
    flex-grow: 1;
    margin-bottom: 20px;
  }
  
  .chart-container {
    height: 300px;
  }
  
  .training-logs {
    height: 200px;
    margin-top: 20px;
  }
  
  .log-item {
    padding: 5px 10px;
    border-bottom: 1px solid #eee;
    font-family: monospace;
  }
  
  :deep(.el-progress-bar__outer) {
    background-color: #e9ecef;
  }
  
  :deep(.el-progress-bar__inner) {
    transition: width 0.3s ease;
  }
  </style>
  
