<template>
  <div class="data-management">
    <!-- 数据集列表 -->
    <el-card>
      <template #header>
        <div class="card-header">
          <span>数据集管理</span>
          <el-button type="primary" @click="uploadDialogVisible = true">
            上传数据集
          </el-button>
        </div>
      </template>

      <el-table :data="datasets">
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="file_type" label="文件类型" />
        <el-table-column prop="created_at" label="创建时间" />
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button link @click="previewDataset(scope.row)">预览</el-button>
            <el-button link type="danger" @click="deleteDataset(scope.row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 上传对话框 -->
    <el-dialog v-model="uploadDialogVisible" title="上传数据集">
      <el-form :model="uploadForm" label-width="100px">
        <el-form-item label="数据集名称">
          <el-input v-model="uploadForm.name" />
        </el-form-item>
        <el-form-item label="数据集描述">
          <el-input v-model="uploadForm.description" type="textarea" />
        </el-form-item>
        <el-form-item label="文件类型">
          <el-select v-model="uploadForm.file_type">
            <el-option label="CSV文件" value="csv" />
            <el-option label="Excel文件" value="excel" />
            <el-option label="JSON文件" value="json" />
          </el-select>
        </el-form-item>
        <el-form-item label="数据文件">
          <el-upload
            :action="`${baseURL}/api/preprocessing/upload/`"
            :headers="uploadHeaders"
            :with-credentials="true"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            :before-upload="beforeUpload">
            <el-button>选择文件</el-button>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitUpload">确定</el-button>
      </template>
    </el-dialog>

    <!-- 预览对话框 -->
    <el-dialog v-model="previewDialogVisible" title="数据预览" width="80%">
      <el-table :data="previewData">
        <el-table-column
          v-for="column in previewColumns"
          :key="column"
          :prop="column"
          :label="column" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'
import { useRouter } from 'vue-router'

const baseURL = import.meta.env.VITE_APP_API_URL || 'http://localhost:8000'
const router = useRouter()

// 状态变量
const datasets = ref([])
const previewData = ref([])  // 预览数据
const previewColumns = ref([])
const uploadDialogVisible = ref(false)
const previewDialogVisible = ref(false)
const uploadForm = ref({
  name: '',
  description: '',
  file: null,
  file_type: 'csv'
})

// 获取CSRF Token
const getCsrfToken = () => {
  return document.cookie.match(/csrftoken=([\w-]+)/)?.[1] || ''
}

// 上传请求头
const uploadHeaders = computed(() => ({
  'X-CSRFToken': getCsrfToken(),
  'Authorization': `Bearer ${localStorage.getItem('token')}`
}))

// 上传前检查
const beforeUpload = (file) => {
  const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true'
  if (!isAuthenticated) {
    ElMessage.error('请先登录')
    router.push('/login')
    return false
  }
  return true
}

// 处理上传成功
const handleUploadSuccess = (response) => {
  ElMessage.success('文件上传成功')
  // 刷新数据集列表
  fetchDatasets()
}

// 处理上传失败
const handleUploadError = (error) => {
  console.error('上传错误:', error)
  if (error.response?.status === 401) {
    ElMessage.error('请先登录')
  } else {
    ElMessage.error(error.response?.data?.message || '文件上传失败')
  }
}

// 获取数据集列表
const fetchDatasets = async () => {
  try {
    const response = await request.get('/api/preprocessing/datasets/')
    datasets.value = response.data
  } catch (error) {
    ElMessage.error('获取数据集列表失败')
  }
}

// 提交上传表单
const submitUpload = async () => {
  try {
    await request.post('/api/preprocessing/datasets/', uploadForm.value)
    ElMessage.success('数据集创建成功')
    uploadDialogVisible.value = false
    fetchDatasets()
  } catch (error) {
    ElMessage.error('数据集创建失败')
  }
}

// 预览数据集
const previewDataset = async (dataset) => {
  try {
    const response = await request.get(`/api/preprocessing/datasets/${dataset.id}/preview/`)
    previewData.value = response.data.head
    previewColumns.value = response.data.columns
    previewDialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取数据预览失败')
  }
}

// 删除数据集
const deleteDataset = async (dataset) => {
  try {
    await request.delete(`/api/preprocessing/datasets/${dataset.id}/`)
    ElMessage.success('数据集删除成功')
    fetchDatasets()
  } catch (error) {
    ElMessage.error('数据集删除失败')
  }
}

onMounted(() => {
  fetchDatasets()
})
</script>

<style scoped>
.data-management {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style> 