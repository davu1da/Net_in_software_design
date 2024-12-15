<template>
  <div class="model-editor">
    <el-container>
      <el-aside width="250px" class="layer-panel">
        <el-card class="layer-list">
          <template #header>
            <div class="panel-header">
              <span>网络层组件</span>
            </div>
          </template>
          
          <div class="layer-items">
            <div
              v-for="layer in availableLayers"
              :key="layer.type"
              class="layer-item"
              draggable="true"
              @dragstart="handleDragStart($event, layer)">
              <el-card shadow="hover">
                <div class="layer-item-content">
                  <el-icon><component :is="layer.icon" /></el-icon>
                  <span>{{ layer.name }}</span>
                </div>
              </el-card>
            </div>
          </div>
        </el-card>
      </el-aside>

      <el-main class="editor-main">
        <el-card class="editor-container">
          <template #header>
            <div class="editor-header">
              <div class="model-info">
                <el-input
                  v-model="modelName"
                  placeholder="模型名称"
                  class="model-name-input" />
              </div>
              <div class="editor-actions">
                <el-button-group>
                  <el-button type="primary" @click="saveModel">
                    保存模型
                  </el-button>
                  <el-button @click="validateModel">
                    验证结构
                  </el-button>
                  <el-button type="success" @click="exportModel">
                    导出模型
                  </el-button>
                </el-button-group>
              </div>
            </div>
          </template>

          <div
            class="editor-canvas"
            @dragover.prevent
            @drop="handleDrop">
            <!-- 这里将使用SVG来绘制网络结构 -->
            <svg class="network-svg" ref="networkSvg">
              <!-- 连接线 -->
              <g class="connections">
                <path
                  v-for="conn in connections"
                  :key="conn.id"
                  :d="getConnectionPath(conn)"
                  class="connection-path" />
              </g>
              <!-- 层节点 -->
              <g class="layers">
                <g
                  v-for="layer in layers"
                  :key="layer.id"
                  :transform="`translate(${layer.x}, ${layer.y})`"
                  class="layer-node"
                  @mousedown="startDragLayer(layer, $event)">
                  <rect
                    :width="nodeWidth"
                    :height="nodeHeight"
                    rx="5"
                    class="layer-rect" />
                  <text
                    :x="nodeWidth / 2"
                    :y="nodeHeight / 2"
                    class="layer-text">
                    {{ layer.name }}
                  </text>
                  <!-- 连接点 -->
                  <circle
                    class="connection-point input"
                    cx="0"
                    cy="30"
                    r="4" />
                  <circle
                    class="connection-point output"
                    :cx="nodeWidth"
                    cy="30"
                    r="4" />
                </g>
              </g>
            </svg>
          </div>
        </el-card>
      </el-main>

      <el-aside width="300px" class="properties-panel">
        <el-card v-if="selectedLayer" class="layer-properties">
          <template #header>
            <div class="panel-header">
              <span>层属性</span>
              <el-button
                type="danger"
                size="small"
                @click="deleteLayer(selectedLayer)">
                删除
              </el-button>
            </div>
          </template>

          <el-form label-position="top">
            <el-form-item label="层名称">
              <el-input v-model="selectedLayer.name" />
            </el-form-item>
            
            <!-- 根据层类型显示不同的参数配置 -->
            <template v-if="selectedLayer.type === 'conv2d'">
              <el-form-item label="卷积核大小">
                <el-input-number
                  v-model="selectedLayer.parameters.kernelSize"
                  :min="1"
                  :max="7" />
              </el-form-item>
              <el-form-item label="过滤器数量">
                <el-input-number
                  v-model="selectedLayer.parameters.filters"
                  :min="1"
                  :step="16" />
              </el-form-item>
            </template>

            <template v-if="selectedLayer.type === 'dense'">
              <el-form-item label="神经元数量">
                <el-input-number
                  v-model="selectedLayer.parameters.units"
                  :min="1"
                  :step="16" />
              </el-form-item>
            </template>

            <template v-if="selectedLayer.type === 'dropout'">
              <el-form-item label="丢弃率">
                <el-slider
                  v-model="selectedLayer.parameters.rate"
                  :min="0"
                  :max="1"
                  :step="0.1" />
              </el-form-item>
            </template>
          </el-form>
        </el-card>
      </el-aside>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Monitor,
  Connection,
  Share,
  Switch,
  Histogram,
  Operation
} from '@element-plus/icons-vue'
import axios from 'axios'

// 可用的层类型
const availableLayers = [
  { type: 'input', name: '输入层', icon: 'Monitor' },
  { type: 'conv2d', name: '卷积层', icon: 'Operation' },
  { type: 'maxpool2d', name: '池化层', icon: 'Share' },
  { type: 'dense', name: '全连接层', icon: 'Connection' },
  { type: 'dropout', name: '丢弃层', icon: 'Switch' },
  { type: 'activation', name: '激活层', icon: 'Histogram' }
]

// 模型基本信息
const modelName = ref('')
const layers = ref([])
const connections = ref([])
const selectedLayer = ref(null)

// 节点尺寸
const nodeWidth = 120
const nodeHeight = 60

// 拖拽相关
let isDragging = false
let dragStartX = 0
let dragStartY = 0

// 处理层拖拽开始
const handleDragStart = (event, layer) => {
  event.dataTransfer.setData('layerType', layer.type)
}

// 处理层拖放
const handleDrop = (event) => {
  const layerType = event.dataTransfer.getData('layerType')
  const rect = event.target.getBoundingClientRect()
  const x = event.clientX - rect.left
  const y = event.clientY - rect.top

  addLayer(layerType, x, y)
}

// 添加新层
const addLayer = (type, x, y) => {
  const layer = {
    id: Date.now(),
    type,
    name: `${type}_${layers.value.length + 1}`,
    x,
    y,
    parameters: getDefaultParameters(type)
  }
  
  layers.value.push(layer)
  selectedLayer.value = layer
}

// 获取层的默认参数
const getDefaultParameters = (type) => {
  switch (type) {
    case 'conv2d':
      return { kernelSize: 3, filters: 32 }
    case 'dense':
      return { units: 64 }
    case 'dropout':
      return { rate: 0.5 }
    default:
      return {}
  }
}

// 开始拖动层
const startDragLayer = (layer, event) => {
  if (event.target.classList.contains('connection-point')) {
    // 处理连接点的拖动
    return
  }

  isDragging = true
  dragStartX = event.clientX - layer.x
  dragStartY = event.clientY - layer.y
  selectedLayer.value = layer

  const handleMouseMove = (e) => {
    if (!isDragging) return
    
    layer.x = e.clientX - dragStartX
    layer.y = e.clientY - dragStartY
  }

  const handleMouseUp = () => {
    isDragging = false
    document.removeEventListener('mousemove', handleMouseMove)
    document.removeEventListener('mouseup', handleMouseUp)
  }

  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

// 获取连接线路径
const getConnectionPath = (conn) => {
  const fromLayer = layers.value.find(l => l.id === conn.fromId)
  const toLayer = layers.value.find(l => l.id === conn.toId)
  
  if (!fromLayer || !toLayer) return ''

  const startX = fromLayer.x + nodeWidth
  const startY = fromLayer.y + nodeHeight / 2
  const endX = toLayer.x
  const endY = toLayer.y + nodeHeight / 2
  
  const controlPoint1X = startX + (endX - startX) / 3
  const controlPoint2X = startX + (endX - startX) * 2 / 3
  
  return `M ${startX} ${startY} C ${controlPoint1X} ${startY}, ${controlPoint2X} ${endY}, ${endX} ${endY}`
}

// 删除层
const deleteLayer = (layer) => {
  const index = layers.value.findIndex(l => l.id === layer.id)
  if (index > -1) {
    layers.value.splice(index, 1)
    // 删除相关的连接
    connections.value = connections.value.filter(
      conn => conn.fromId !== layer.id && conn.toId !== layer.id
    )
    selectedLayer.value = null
  }
}

// 保存模型
const saveModel = async () => {
  try {
    const modelData = {
      name: modelName.value,
      layers: layers.value,
      connections: connections.value
    }
    
    await axios.post('/api/editor/networks/', modelData)
    ElMessage.success('模型保存成功')
  } catch (error) {
    ElMessage.error('模型保存失败')
  }
}

// 验证模型结构
const validateModel = async () => {
  try {
    const response = await axios.post('/api/editor/networks/validate/', {
      layers: layers.value,
      connections: connections.value
    })
    ElMessage.success('模型结构有效')
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '模型结构验证失败')
  }
}

// 导出模型
const exportModel = () => {
  const modelData = {
    name: modelName.value,
    layers: layers.value,
    connections: connections.value
  }
  
  const blob = new Blob([JSON.stringify(modelData, null, 2)], {
    type: 'application/json'
  })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${modelName.value || 'model'}.json`
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.model-editor {
  height: 100%;
}

.layer-panel {
  background-color: #f5f7fa;
  border-right: 1px solid #dcdfe6;
}

.layer-items {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.layer-item {
  cursor: move;
}

.layer-item-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.editor-container {
  height: 100%;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.model-name-input {
  width: 200px;
}

.editor-canvas {
  height: calc(100vh - 200px);
  background-color: #fff;
  position: relative;
  overflow: hidden;
}

.network-svg {
  width: 100%;
  height: 100%;
}

.layer-node {
  cursor: move;
}

.layer-rect {
  fill: #fff;
  stroke: #409eff;
  stroke-width: 2;
}

.layer-text {
  text-anchor: middle;
  dominant-baseline: middle;
  font-size: 12px;
}

.connection-point {
  fill: #409eff;
  cursor: pointer;
}

.connection-point:hover {
  fill: #66b1ff;
}

.connection-path {
  fill: none;
  stroke: #409eff;
  stroke-width: 2;
}

.properties-panel {
  background-color: #f5f7fa;
  border-left: 1px solid #dcdfe6;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style> 