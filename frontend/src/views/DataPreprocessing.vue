<template>
  <div class="data-preprocessing">
    <el-row :gutter="20">
      <!-- 数据集列表 -->
      <el-col :span="6">
        <el-card class="dataset-list">
          <template #header>
            <div class="card-header">
              <span>数据集列表</span>
              <el-button type="primary" @click="showUploadDialog">
                上传数据集
              </el-button>
            </div>
          </template>
          
          <el-menu
            :default-active="activeDataset?.id"
            @select="handleDatasetSelect">
            <el-menu-item
              v-for="dataset in datasets"
              :key="dataset.id"
              :index="dataset.id">
              <el-icon><Document /></el-icon>
              <span>{{ dataset.name }}</span>
            </el-menu-item>
          </el-menu>
        </el-card>
      </el-col>

      <!-- 预处理步骤 -->
      <el-col :span="18">
        <el-card v-if="activeDataset">
          <template #header>
            <div class="card-header">
              <span>{{ activeDataset.name }} - 预处理步骤</span>
              <div class="header-actions">
                <el-button type="primary" @click="showAddStepDialog">
                  添加步骤
                </el-button>
                <el-button type="info" @click="showTemplateManager">
                  模板管理
                </el-button>
                <el-button type="success" @click="executeAllSteps">
                  执行所有
                </el-button>
                <el-button @click="showPreviewDialog">
                  数据预览
                </el-button>
                <el-button @click="showVisualization = !showVisualization">
                  {{ showVisualization ? '隐藏可视化' : '数据可视化' }}
                </el-button>
              </div>
            </div>
          </template>

          <el-steps :active="activeStep" direction="vertical">
            <el-step
              v-for="step in preprocessingSteps"
              :key="step.id"
              :title="step.name"
              :description="step.description"
              :status="step.status">
              <template #icon>
                <el-icon>
                  <component :is="getStepIcon(step.step_type)" />
                </el-icon>
              </template>
              <template #default>
                <div class="step-actions">
                  <el-button-group>
                    <el-button
                      type="primary"
                      size="small"
                      @click="executeStep(step)">
                      执行
                    </el-button>
                    <el-button
                      type="info"
                      size="small"
                      @click="editStep(step)">
                      编辑
                    </el-button>
                    <el-button
                      type="danger"
                      size="small"
                      @click="deleteStep(step)">
                      删除
                    </el-button>
                  </el-button-group>
                </div>
              </template>
            </el-step>
          </el-steps>
        </el-card>

        <!-- 数据可视化面板 -->
        <el-card v-if="showVisualization && activeDataset" class="visualization-card">
          <template #header>
            <div class="card-header">
              <span>数据可视化分析</span>
            </div>
          </template>
          <DataVisualization
            :data="previewData"
            :columns="activeDataset.columns" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 上传数据集对话框 -->
    <el-dialog
      v-model="uploadDialogVisible"
      title="上传数据集"
      width="500px">
      <el-form
        ref="uploadFormRef"
        :model="uploadForm"
        label-width="100px">
        <el-form-item label="数据集名称" prop="name">
          <el-input v-model="uploadForm.name" />
        </el-form-item>
        <el-form-item label="文件类型" prop="file_type">
          <el-select v-model="uploadForm.file_type">
            <el-option label="CSV文件" value="csv" />
            <el-option label="Excel文件" value="excel" />
            <el-option label="JSON文件" value="json" />
          </el-select>
        </el-form-item>
        <el-form-item label="数据文件">
          <el-upload
            ref="uploadRef"
            :action="uploadUrl"
            :auto-upload="false"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError">
            <el-button type="primary">选择文件</el-button>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitUpload">确认</el-button>
      </template>
    </el-dialog>

    <!-- 添加预处理步骤对话框 -->
    <el-dialog
      v-model="stepDialogVisible"
      :title="editingStep ? '编辑预处理步骤' : '添加预处理步骤'"
      width="600px">
      <preprocessing-step-form
        ref="stepFormRef"
        :step="editingStep"
        :dataset="activeDataset"
        @submit="handleStepSubmit"
        @cancel="stepDialogVisible = false" />
    </el-dialog>

    <!-- 数据预览对话框 -->
    <el-dialog
      v-model="previewDialogVisible"
      title="数据预览"
      width="90%">
      <DataPreview
        :data="previewData"
        :columns="activeDataset.columns" />
    </el-dialog>

    <!-- 添加模板管理器组件 -->
    <TemplateManager
      ref="templateManagerRef"
      :steps="preprocessingSteps"
      :dataset="activeDataset"
      @template-applied="fetchPreprocessingSteps" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import PreprocessingStepForm from '@/components/DataPreprocessing/PreprocessingStepForm.vue'
import DataPreview from '@/components/DataPreprocessing/DataPreview.vue'
import DataVisualization from '@/components/DataPreprocessing/DataVisualization.vue'
import TemplateManager from '@/components/DataPreprocessing/TemplateManager.vue'

// 状态变量
const datasets = ref([])
const activeDataset = ref(null)
const preprocessingSteps = ref([])
const activeStep = ref(0)
const uploadDialogVisible = ref(false)
const stepDialogVisible = ref(false)
const previewDialogVisible = ref(false)
const editingStep = ref(null)
const previewData = ref(null)
const previewColumns = ref([])
const showVisualization = ref(false)

// 表单数据
const uploadForm = ref({
  name: '',
  file_type: 'csv',
  file: null
})

// 获取数据集列表
const fetchDatasets = async () => {
  try {
    const response = await axios.get('/api/preprocessing/datasets/')
    datasets.value = response.data
  } catch (error) {
    ElMessage.error('获取数据集列表失败')
  }
}

// 获取预处理步骤
const fetchPreprocessingSteps = async () => {
  if (!activeDataset.value) return
  
  try {
    const response = await axios.get(
      `/api/preprocessing/datasets/${activeDataset.value.id}/steps/`
    )
    preprocessingSteps.value = response.data
  } catch (error) {
    ElMessage.error('获取预处理步骤失败')
  }
}

// 处理数据集选择
const handleDatasetSelect = async (datasetId) => {
  try {
    const response = await axios.get(`/api/preprocessing/datasets/${datasetId}/`)
    activeDataset.value = response.data
    
    // 获取预览数据
    const previewResponse = await axios.get(`/api/preprocessing/datasets/${datasetId}/preview/`)
    previewData.value = previewResponse.data.head
    
    await fetchPreprocessingSteps()
  } catch (error) {
    ElMessage.error('获取数据集信息失败')
  }
}

// 执行预处理步骤
const executeStep = async (step) => {
  try {
    const response = await axios.post(
      `/api/preprocessing/steps/${step.id}/execute/`
    )
    ElMessage.success('步骤执行成功')
    await fetchPreprocessingSteps()
  } catch (error) {
    ElMessage.error('步骤执行失败')
  }
}

// 执行所有步骤
const executeAllSteps = async () => {
  for (const step of preprocessingSteps.value) {
    await executeStep(step)
  }
}

// 编辑步骤
const editStep = (step) => {
  editingStep.value = step
  stepDialogVisible.value = true
}

// 删除步骤
const deleteStep = async (step) => {
  try {
    await ElMessageBox.confirm('确认删除该预处理步骤？')
    await axios.delete(`/api/preprocessing/steps/${step.id}/`)
    ElMessage.success('步骤删除成功')
    await fetchPreprocessingSteps()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('步骤删除失败')
    }
  }
}

// 处理步骤提交
const handleStepSubmit = async (stepData) => {
  try {
    if (editingStep.value) {
      await axios.put(
        `/api/preprocessing/steps/${editingStep.value.id}/`,
        stepData
      )
    } else {
      await axios.post('/api/preprocessing/steps/', {
        ...stepData,
        dataset: activeDataset.value.id
      })
    }
    
    stepDialogVisible.value = false
    editingStep.value = null
    await fetchPreprocessingSteps()
    ElMessage.success('步骤保存成功')
  } catch (error) {
    ElMessage.error('步骤保存失败')
  }
}

// 获取步骤图标
const getStepIcon = (stepType) => {
  const icons = {
    clean: 'Delete',
    transform: 'Refresh',
    encode: 'Edit',
    scale: 'Scale',
    split: 'Split'
  }
  return icons[stepType] || 'Document'
}

// 获取预览数据
const fetchPreviewData = async () => {
  if (!activeDataset.value) return
  
  try {
    const response = await axios.get(`/api/preprocessing/datasets/${activeDataset.value.id}/preview/`)
    previewData.value = response.data.data
  } catch (error) {
    ElMessage.error('获取预览数据失败')
  }
}

// 显示预览对话框
const showPreviewDialog = async () => {
  await fetchPreviewData()
  previewDialogVisible.value = true
}

// 监听数据集变化，自动获取预览数据
watch(activeDataset, async () => {
  if (activeDataset.value) {
    await fetchPreviewData()
  }
})

onMounted(() => {
  fetchDatasets()
})
</script>

<style scoped>
.data-preprocessing {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dataset-list {
  height: calc(100vh - 140px);
  overflow-y: auto;
}

.step-actions {
  margin-top: 10px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.visualization-card {
  margin-top: 20px;
}
</style> 