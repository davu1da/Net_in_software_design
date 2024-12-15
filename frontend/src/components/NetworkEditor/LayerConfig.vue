<template>
  <div class="layer-config">
    <el-form
      ref="formRef"
      :model="configForm"
      label-width="120px"
      @submit.prevent>
      <!-- 基本信息 -->
      <el-form-item label="层名称" required>
        <el-input v-model="configForm.name" />
      </el-form-item>

      <!-- 参数预设 -->
      <el-form-item label="参数预设">
        <div class="preset-controls">
          <el-select
            v-model="selectedPreset"
            placeholder="选择预设"
            @change="applyPreset">
            <el-option
              v-for="preset in layerPresets[layer.type] || []"
              :key="preset.name"
              :label="preset.label"
              :value="preset.name">
              <span>{{ preset.label }}</span>
              <el-tooltip :content="preset.description" placement="right">
                <el-icon class="preset-info"><InfoFilled /></el-icon>
              </el-tooltip>
            </el-option>
          </el-select>
          <el-button
            type="primary"
            plain
            size="small"
            @click="saveAsPreset">
            保存为预设
          </el-button>
        </div>
      </el-form-item>

      <!-- 卷积层参数 -->
      <template v-if="layer.type === 'conv2d'">
        <el-divider>卷积参数</el-divider>
        <el-form-item label="卷积核大小">
          <el-input-group>
            <el-input-number
              v-model="configForm.config.kernel_size[0]"
              :min="1"
              :max="7"
              controls-position="right" />
            <el-input-number
              v-model="configForm.config.kernel_size[1]"
              :min="1"
              :max="7"
              controls-position="right" />
          </el-input-group>
        </el-form-item>
        <el-form-item label="卷积核数量">
          <el-input-number
            v-model="configForm.config.filters"
            :min="1"
            :step="32"
            :step-strictly="true"
            controls-position="right" />
        </el-form-item>
        <el-form-item label="步长">
          <el-input-group>
            <el-input-number
              v-model="configForm.config.strides[0]"
              :min="1"
              :max="4"
              controls-position="right" />
            <el-input-number
              v-model="configForm.config.strides[1]"
              :min="1"
              :max="4"
              controls-position="right" />
          </el-input-group>
        </el-form-item>
        <el-form-item label="填充方式">
          <el-select v-model="configForm.config.padding">
            <el-option label="valid" value="valid" />
            <el-option label="same" value="same" />
          </el-select>
        </el-form-item>
      </template>

      <!-- 池化层参数 -->
      <template v-else-if="layer.type === 'maxpool2d'">
        <el-divider>池化参数</el-divider>
        <el-form-item label="池化窗口">
          <el-input-group>
            <el-input-number
              v-model="configForm.config.pool_size[0]"
              :min="1"
              :max="4"
              controls-position="right" />
            <el-input-number
              v-model="configForm.config.pool_size[1]"
              :min="1"
              :max="4"
              controls-position="right" />
          </el-input-group>
        </el-form-item>
        <el-form-item label="步长">
          <el-input-group>
            <el-input-number
              v-model="configForm.config.strides[0]"
              :min="1"
              :max="4"
              controls-position="right" />
            <el-input-number
              v-model="configForm.config.strides[1]"
              :min="1"
              :max="4"
              controls-position="right" />
          </el-input-group>
        </el-form-item>
      </template>

      <!-- 全连接层参数 -->
      <template v-else-if="layer.type === 'dense'">
        <el-divider>全连接参数</el-divider>
        <el-form-item label="神经元数量">
          <el-input-number
            v-model="configForm.config.units"
            :min="1"
            :step="64"
            :step-strictly="true"
            controls-position="right" />
        </el-form-item>
        <el-form-item label="使用偏置">
          <el-switch v-model="configForm.config.use_bias" />
        </el-form-item>
      </template>

      <!-- 激活层参数 -->
      <template v-else-if="layer.type === 'activation'">
        <el-divider>激活函数</el-divider>
        <el-form-item label="激活类型">
          <el-select v-model="configForm.config.activation">
            <el-option label="ReLU" value="relu" />
            <el-option label="Sigmoid" value="sigmoid" />
            <el-option label="Tanh" value="tanh" />
            <el-option label="LeakyReLU" value="leaky_relu" />
            <el-option label="PReLU" value="prelu" />
          </el-select>
        </el-form-item>
        <el-form-item
          v-if="configForm.config.activation === 'leaky_relu'"
          label="斜率">
          <el-input-number
            v-model="configForm.config.alpha"
            :min="0"
            :max="1"
            :step="0.01"
            controls-position="right" />
        </el-form-item>
      </template>

      <!-- 丢弃层参数 -->
      <template v-else-if="layer.type === 'dropout'">
        <el-divider>丢弃参数</el-divider>
        <el-form-item label="丢弃率">
          <el-slider
            v-model="configForm.config.rate"
            :min="0"
            :max="0.9"
            :step="0.1"
            show-stops />
        </el-form-item>
      </template>

      <!-- 批归一化层参数 -->
      <template v-else-if="layer.type === 'batch_norm'">
        <el-divider>归一化参数</el-divider>
        <el-form-item label="动量">
          <el-slider
            v-model="configForm.config.momentum"
            :min="0"
            :max="1"
            :step="0.1"
            show-stops />
        </el-form-item>
        <el-form-item label="epsilon">
          <el-input-number
            v-model="configForm.config.epsilon"
            :min="0.000001"
            :max="0.1"
            :step="0.000001"
            :precision="6"
            controls-position="right" />
        </el-form-item>
      </template>

      <!-- 通用参数 -->
      <el-divider>高级选项</el-divider>
      <el-form-item label="初始化器">
        <el-select v-model="configForm.config.initializer">
          <el-option label="Glorot均匀" value="glorot_uniform" />
          <el-option label="Glorot正态" value="glorot_normal" />
          <el-option label="He均匀" value="he_uniform" />
          <el-option label="He正态" value="he_normal" />
        </el-select>
      </el-form-item>
      <el-form-item label="正则化器">
        <el-select v-model="configForm.config.regularizer">
          <el-option label="无" value="" />
          <el-option label="L1" value="l1" />
          <el-option label="L2" value="l2" />
          <el-option label="L1L2" value="l1_l2" />
        </el-select>
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="handleSubmit">确认</el-button>
        <el-button @click="handleCancel">取消</el-button>
      </el-form-item>
    </el-form>

    <!-- 添加保存预设对话框 -->
    <el-dialog
      v-model="presetDialogVisible"
      title="保存参数预设"
      width="500px">
      <el-form
        ref="presetFormRef"
        :model="presetForm"
        label-width="100px">
        <el-form-item
          label="预设名称"
          prop="name"
          :rules="[{ required: true, message: '请输入预设名称' }]">
          <el-input v-model="presetForm.name" />
        </el-form-item>
        <el-form-item label="预设说明">
          <el-input
            v-model="presetForm.description"
            type="textarea"
            rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="presetDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSavePreset">确认</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { InfoFilled } from '@element-plus/icons-vue'
import axios from 'axios'

const props = defineProps({
  layer: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['update', 'cancel'])

// 获取默认配置
const getDefaultConfig = (type) => {
  const configs = {
    conv2d: {
      kernel_size: [3, 3],
      filters: 32,
      strides: [1, 1],
      padding: 'valid',
      initializer: 'glorot_uniform',
      regularizer: ''
    },
    maxpool2d: {
      pool_size: [2, 2],
      strides: [2, 2]
    },
    dense: {
      units: 64,
      use_bias: true,
      initializer: 'glorot_uniform',
      regularizer: ''
    },
    activation: {
      activation: 'relu',
      alpha: 0.01
    },
    dropout: {
      rate: 0.5
    },
    batch_norm: {
      momentum: 0.99,
      epsilon: 0.001
    }
  }
  return configs[type] || {}
}

const configForm = ref({
  name: props.layer.name,
  config: { ...getDefaultConfig(props.layer.type), ...props.layer.config }
})

const handleSubmit = () => {
  emit('update', {
    ...props.layer,
    name: configForm.value.name,
    config: configForm.value.config
  })
}

const handleCancel = () => {
  emit('cancel')
}

watch(() => props.layer, (newLayer) => {
  configForm.value = {
    name: newLayer.name,
    config: { ...getDefaultConfig(newLayer.type), ...newLayer.config }
  }
}, { deep: true })

// 预设相关的状态
const selectedPreset = ref('')
const presetDialogVisible = ref(false)
const presetForm = ref({
  name: '',
  description: ''
})

// 层参数预设配置
const layerPresets = {
  conv2d: [
    {
      name: 'vgg_block',
      label: 'VGG风格',
      description: '3x3卷积核，较多的过滤器',
      config: {
        kernel_size: [3, 3],
        filters: 64,
        strides: [1, 1],
        padding: 'same',
        use_bias: true
      }
    },
    {
      name: 'resnet_block',
      label: 'ResNet风格',
      description: '带残差连接的卷积块',
      config: {
        kernel_size: [3, 3],
        filters: 32,
        strides: [1, 1],
        padding: 'same',
        use_bias: false
      }
    }
  ],
  dense: [
    {
      name: 'classifier_head',
      label: '分类器头部',
      description: '用于分类任务的全连接层',
      config: {
        units: 512,
        use_bias: true,
        activation: 'relu',
        dropout_rate: 0.5
      }
    },
    {
      name: 'embedding',
      label: '嵌入层',
      description: '用于特征嵌入的全连接层',
      config: {
        units: 256,
        use_bias: false,
        activation: 'linear'
      }
    }
  ],
  dropout: [
    {
      name: 'light_dropout',
      label: '轻度丢弃',
      description: '轻度正则化，丢弃率0.2',
      config: {
        rate: 0.2
      }
    },
    {
      name: 'heavy_dropout',
      label: '重度丢弃',
      description: '强正则化，丢弃率0.5',
      config: {
        rate: 0.5
      }
    }
  ]
}

// 应用预设参数
const applyPreset = () => {
  const preset = layerPresets[layer.value.type]?.find(
    p => p.name === selectedPreset.value
  )
  
  if (preset) {
    configForm.value.config = { ...preset.config }
    ElMessage.success('已应用预设参数')
  }
}

// 保存为预设
const saveAsPreset = () => {
  presetForm.value = {
    name: '',
    description: ''
  }
  presetDialogVisible.value = true
}

// 处理保存预设
const handleSavePreset = async () => {
  try {
    const newPreset = {
      name: presetForm.value.name,
      label: presetForm.value.name,
      description: presetForm.value.description,
      config: { ...configForm.value.config }
    }
    
    // 如果预设数组不存在，则创建
    if (!layerPresets[layer.value.type]) {
      layerPresets[layer.value.type] = []
    }
    
    // 添加新预设
    layerPresets[layer.value.type].push(newPreset)
    
    // 保存到本地存储
    localStorage.setItem('layerPresets', JSON.stringify(layerPresets))
    
    ElMessage.success('预设保存成功')
    presetDialogVisible.value = false
    selectedPreset.value = newPreset.name
  } catch (error) {
    ElMessage.error('预设保存失败')
  }
}

// 加载本地存储的预设
const loadLocalPresets = () => {
  const localPresets = localStorage.getItem('layerPresets')
  if (localPresets) {
    Object.assign(layerPresets, JSON.parse(localPresets))
  }
}

// 组件挂载时加载预设
onMounted(() => {
  loadLocalPresets()
})
</script>

<style scoped>
.layer-config {
  padding: 20px;
}

:deep(.el-input-group) {
  display: flex;
  gap: 10px;
}

:deep(.el-divider__text) {
  font-size: 14px;
  font-weight: bold;
  color: var(--el-text-color-secondary);
}

:deep(.el-form-item:last-child) {
  margin-bottom: 0;
}

.preset-controls {
  display: flex;
  gap: 10px;
  align-items: center;
}

.preset-info {
  margin-left: 8px;
  color: var(--el-text-color-secondary);
}
</style> 