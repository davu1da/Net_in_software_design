<template>
  <el-form
    ref="formRef"
    :model="stepForm"
    label-width="120px"
    @submit.prevent>
    <el-form-item label="步骤名称" prop="name">
      <el-input v-model="stepForm.name" />
    </el-form-item>

    <el-form-item label="步骤类型" prop="step_type">
      <el-select v-model="stepForm.step_type" @change="handleTypeChange">
        <el-option
          v-for="type in stepTypes"
          :key="type.value"
          :label="type.label"
          :value="type.value" />
      </el-select>
    </el-form-item>

    <!-- 数据清洗参数 -->
    <template v-if="stepForm.step_type === 'clean'">
      <el-form-item label="处理缺失值">
        <el-switch
          v-model="stepForm.parameters.handle_missing"
          @change="updateParameters" />
      </el-form-item>
      
      <el-form-item
        v-if="stepForm.parameters.handle_missing"
        label="缺失值策略">
        <el-select
          v-model="stepForm.parameters.missing_strategy"
          @change="updateParameters">
          <el-option label="均值" value="mean" />
          <el-option label="中位数" value="median" />
          <el-option label="众数" value="mode" />
        </el-select>
      </el-form-item>

      <el-form-item label="删除重复行">
        <el-switch
          v-model="stepForm.parameters.remove_duplicates"
          @change="updateParameters" />
      </el-form-item>
    </template>

    <!-- 数据转换参数 -->
    <template v-if="stepForm.step_type === 'transform'">
      <el-form-item label="转换配置">
        <div
          v-for="(transform, index) in stepForm.parameters.transformations"
          :key="index"
          class="transform-item">
          <el-select
            v-model="transform.column"
            placeholder="选择列"
            style="width: 200px">
            <el-option
              v-for="col in numericColumns"
              :key="col"
              :label="col"
              :value="col" />
          </el-select>
          
          <el-select
            v-model="transform.operation"
            placeholder="选择操作"
            style="width: 150px">
            <el-option label="对数" value="log" />
            <el-option label="平方根" value="sqrt" />
            <el-option label="平方" value="square" />
          </el-select>

          <el-button
            type="danger"
            circle
            @click="removeTransform(index)">
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>

        <el-button
          type="primary"
          plain
          @click="addTransform">
          添加转换
        </el-button>
      </el-form-item>
    </template>

    <!-- 编码转换参数 -->
    <template v-if="stepForm.step_type === 'encode'">
      <el-form-item label="编码配置">
        <div
          v-for="(encode, index) in stepForm.parameters.encoding"
          :key="index"
          class="encode-item">
          <el-select
            v-model="encode.column"
            placeholder="选择列"
            style="width: 200px">
            <el-option
              v-for="col in categoricalColumns"
              :key="col"
              :label="col"
              :value="col" />
          </el-select>
          
          <el-select
            v-model="encode.method"
            placeholder="选择编码方式"
            style="width: 150px">
            <el-option label="标签编码" value="label" />
            <el-option label="独热编码" value="onehot" />
            <el-option label="序数编码" value="ordinal" />
          </el-select>

          <el-button
            type="danger"
            circle
            @click="removeEncode(index)">
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>

        <el-button
          type="primary"
          plain
          @click="addEncode">
          添加编码
        </el-button>
      </el-form-item>
    </template>

    <!-- 数据缩放参数 -->
    <template v-if="stepForm.step_type === 'scale'">
      <el-form-item label="缩放配置">
        <div
          v-for="(scale, index) in stepForm.parameters.scaling"
          :key="index"
          class="scale-item">
          <el-select
            v-model="scale.columns"
            multiple
            placeholder="选择列"
            style="width: 300px">
            <el-option
              v-for="col in numericColumns"
              :key="col"
              :label="col"
              :value="col" />
          </el-select>
          
          <el-select
            v-model="scale.method"
            placeholder="选择缩放方式"
            style="width: 150px">
            <el-option label="标准化" value="standard" />
            <el-option label="归一化" value="minmax" />
          </el-select>

          <el-button
            type="danger"
            circle
            @click="removeScale(index)">
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>

        <el-button
          type="primary"
          plain
          @click="addScale">
          添加缩放
        </el-button>
      </el-form-item>
    </template>

    <!-- 数据分割参数 -->
    <template v-if="stepForm.step_type === 'split'">
      <el-form-item label="目标列" prop="parameters.target_column">
        <el-select v-model="stepForm.parameters.target_column">
          <el-option
            v-for="col in columns"
            :key="col"
            :label="col"
            :value="col" />
        </el-select>
      </el-form-item>

      <el-form-item label="测试集比例">
        <el-slider
          v-model="stepForm.parameters.test_size"
          :min="0.1"
          :max="0.4"
          :step="0.05" />
      </el-form-item>

      <el-form-item label="验证集比例">
        <el-slider
          v-model="stepForm.parameters.val_size"
          :min="0.1"
          :max="0.3"
          :step="0.05" />
      </el-form-item>
    </template>

    <el-form-item>
      <el-button type="primary" @click="handleSubmit">确认</el-button>
      <el-button @click="$emit('cancel')">取消</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  step: {
    type: Object,
    default: null
  },
  dataset: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['submit', 'cancel'])

// 步骤类型定义
const stepTypes = [
  { value: 'clean', label: '数据清洗' },
  { value: 'transform', label: '数据转换' },
  { value: 'encode', label: '编码转换' },
  { value: 'scale', label: '数据缩放' },
  { value: 'split', label: '数据分割' }
]

// 表单数据
const stepForm = ref({
  name: '',
  step_type: '',
  parameters: {}
})

// 计算属性
const columns = computed(() => {
  return props.dataset.columns.map(col => col.name)
})

const numericColumns = computed(() => {
  return props.dataset.columns
    .filter(col => ['int64', 'float64'].includes(col.type))
    .map(col => col.name)
})

const categoricalColumns = computed(() => {
  return props.dataset.columns
    .filter(col => !['int64', 'float64'].includes(col.type))
    .map(col => col.name)
})

// 方法
const handleTypeChange = () => {
  // 根据步骤类型初始化参数
  switch (stepForm.value.step_type) {
    case 'clean':
      stepForm.value.parameters = {
        handle_missing: false,
        missing_strategy: 'mean',
        remove_duplicates: false
      }
      break
    case 'transform':
      stepForm.value.parameters = {
        transformations: []
      }
      break
    case 'encode':
      stepForm.value.parameters = {
        encoding: []
      }
      break
    case 'scale':
      stepForm.value.parameters = {
        scaling: []
      }
      break
    case 'split':
      stepForm.value.parameters = {
        target_column: '',
        test_size: 0.2,
        val_size: 0.1
      }
      break
  }
}

const addTransform = () => {
  stepForm.value.parameters.transformations.push({
    column: '',
    operation: ''
  })
}

const removeTransform = (index) => {
  stepForm.value.parameters.transformations.splice(index, 1)
}

const addEncode = () => {
  stepForm.value.parameters.encoding.push({
    column: '',
    method: ''
  })
}

const removeEncode = (index) => {
  stepForm.value.parameters.encoding.splice(index, 1)
}

const addScale = () => {
  stepForm.value.parameters.scaling.push({
    columns: [],
    method: ''
  })
}

const removeScale = (index) => {
  stepForm.value.parameters.scaling.splice(index, 1)
}

const handleSubmit = () => {
  emit('submit', {
    name: stepForm.value.name,
    step_type: stepForm.value.step_type,
    parameters: stepForm.value.parameters
  })
}

// 监听编辑状态
watch(() => props.step, (newStep) => {
  if (newStep) {
    stepForm.value = {
      name: newStep.name,
      step_type: newStep.step_type,
      parameters: { ...newStep.parameters }
    }
  } else {
    stepForm.value = {
      name: '',
      step_type: '',
      parameters: {}
    }
  }
}, { immediate: true })
</script>

<style scoped>
.transform-item,
.encode-item,
.scale-item {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
  align-items: center;
}
</style> 