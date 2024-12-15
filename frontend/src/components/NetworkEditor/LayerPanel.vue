<template>
  <div class="layer-panel">
    <el-collapse v-model="activeNames">
      <!-- 基础层 -->
      <el-collapse-item name="basic">
        <template #title>
          <div class="panel-title">
            <el-icon><Connection /></el-icon>
            <span>基础层</span>
          </div>
        </template>
        <div class="layer-items">
          <div
            v-for="layer in basicLayers"
            :key="layer.type"
            class="layer-item"
            draggable="true"
            @dragstart="handleDragStart($event, layer)">
            <el-icon><component :is="layer.icon" /></el-icon>
            <span>{{ layer.label }}</span>
            <el-tooltip
              :content="layer.description"
              placement="right">
              <el-icon><InfoFilled /></el-icon>
            </el-tooltip>
          </div>
        </div>
      </el-collapse-item>

      <!-- 卷积层 -->
      <el-collapse-item name="conv">
        <template #title>
          <div class="panel-title">
            <el-icon><Grid /></el-icon>
            <span>卷积层</span>
          </div>
        </template>
        <div class="layer-items">
          <div
            v-for="layer in convLayers"
            :key="layer.type"
            class="layer-item"
            draggable="true"
            @dragstart="handleDragStart($event, layer)">
            <el-icon><component :is="layer.icon" /></el-icon>
            <span>{{ layer.label }}</span>
            <el-tooltip
              :content="layer.description"
              placement="right">
              <el-icon><InfoFilled /></el-icon>
            </el-tooltip>
          </div>
        </div>
      </el-collapse-item>

      <!-- 循环层 -->
      <el-collapse-item name="recurrent">
        <template #title>
          <div class="panel-title">
            <el-icon><Refresh /></el-icon>
            <span>循环层</span>
          </div>
        </template>
        <div class="layer-items">
          <div
            v-for="layer in recurrentLayers"
            :key="layer.type"
            class="layer-item"
            draggable="true"
            @dragstart="handleDragStart($event, layer)">
            <el-icon><component :is="layer.icon" /></el-icon>
            <span>{{ layer.label }}</span>
            <el-tooltip
              :content="layer.description"
              placement="right">
              <el-icon><InfoFilled /></el-icon>
            </el-tooltip>
          </div>
        </div>
      </el-collapse-item>

      <!-- 正则化层 -->
      <el-collapse-item name="regularization">
        <template #title>
          <div class="panel-title">
            <el-icon><SetUp /></el-icon>
            <span>正则化层</span>
          </div>
        </template>
        <div class="layer-items">
          <div
            v-for="layer in regularizationLayers"
            :key="layer.type"
            class="layer-item"
            draggable="true"
            @dragstart="handleDragStart($event, layer)">
            <el-icon><component :is="layer.icon" /></el-icon>
            <span>{{ layer.label }}</span>
            <el-tooltip
              :content="layer.description"
              placement="right">
              <el-icon><InfoFilled /></el-icon>
            </el-tooltip>
          </div>
        </div>
      </el-collapse-item>
    </el-collapse>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { layerDefinitions } from '@/config/layers'

const activeNames = ref(['basic', 'conv'])

// 按类别分类层定义
const basicLayers = layerDefinitions.filter(l => l.category === 'basic')
const convLayers = layerDefinitions.filter(l => l.category === 'conv')
const recurrentLayers = layerDefinitions.filter(l => l.category === 'recurrent')
const regularizationLayers = layerDefinitions.filter(l => l.category === 'regularization')

// 处理拖拽开始事件
const handleDragStart = (event, layer) => {
  event.dataTransfer.setData('layer', JSON.stringify(layer))
  // 添加拖拽效果
  event.target.classList.add('dragging')
  setTimeout(() => {
    event.target.classList.remove('dragging')
  }, 0)
}
</script>

<style scoped>
.layer-panel {
  border-right: 1px solid var(--el-border-color);
  height: 100%;
  overflow-y: auto;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.layer-items {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 10px;
  padding: 10px;
}

.layer-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  cursor: move;
  transition: all 0.3s;
  
  &:hover {
    background-color: var(--el-color-primary-light-9);
    border-color: var(--el-color-primary);
  }
  
  &.dragging {
    opacity: 0.5;
  }
}

:deep(.el-collapse-item__header) {
  font-size: 16px;
  font-weight: bold;
}

:deep(.el-collapse-item__content) {
  padding: 0;
}
</style> 