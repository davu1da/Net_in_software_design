<template>
  <div class="template-manager">
    <!-- 模板列表对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="预处理模板"
      width="800px">
      <div class="template-actions">
        <el-button type="primary" @click="showSaveDialog">
          保存为模板
        </el-button>
        <el-button type="success" @click="showApplyDialog">
          应用模板
        </el-button>
      </div>

      <el-table :data="templates" style="width: 100%">
        <el-table-column prop="name" label="模板名称" />
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="created_at" label="创建时间" />
        <el-table-column prop="is_public" label="是否公开">
          <template #default="scope">
            <el-tag :type="scope.row.is_public ? 'success' : ''">
              {{ scope.row.is_public ? '公开' : '私有' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <el-button-group>
              <el-button
                size="small"
                @click="applyTemplate(scope.row)">
                应用
              </el-button>
              <el-button
                size="small"
                type="danger"
                @click="deleteTemplate(scope.row)">
                删除
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <!-- 保存模板对话框 -->
    <el-dialog
      v-model="saveDialogVisible"
      title="保存为模板"
      width="500px">
      <el-form
        ref="templateFormRef"
        :model="templateForm"
        label-width="100px">
        <el-form-item
          label="模板名称"
          prop="name"
          :rules="[{ required: true, message: '请输入模板名称' }]">
          <el-input v-model="templateForm.name" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="templateForm.description"
            type="textarea"
            rows="3" />
        </el-form-item>
        <el-form-item label="是否公开">
          <el-switch v-model="templateForm.is_public" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="saveDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveTemplate">确认</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const props = defineProps({
  steps: {
    type: Array,
    required: true
  },
  dataset: {
    type: Object,
    required: true
  }
})

const dialogVisible = ref(false)
const saveDialogVisible = ref(false)
const templates = ref([])
const templateForm = ref({
  name: '',
  description: '',
  is_public: false
})

// 获取模板列表
const fetchTemplates = async () => {
  try {
    const response = await axios.get('/api/preprocessing/templates/')
    templates.value = response.data
  } catch (error) {
    ElMessage.error('获取模板列表失败')
  }
}

// 保存为模板
const saveTemplate = async () => {
  try {
    await axios.post('/api/preprocessing/templates/', {
      ...templateForm.value,
      steps: props.steps
    })
    ElMessage.success('模板保存成功')
    saveDialogVisible.value = false
    await fetchTemplates()
  } catch (error) {
    ElMessage.error('模板保存失败')
  }
}

// 应用模板
const applyTemplate = async (template) => {
  try {
    await axios.post(`/api/preprocessing/templates/${template.id}/apply/`, {
      dataset_id: props.dataset.id
    })
    ElMessage.success('模板应用成功')
    dialogVisible.value = false
    emit('template-applied')
  } catch (error) {
    ElMessage.error('模板应用失败')
  }
}

// 删除模板
const deleteTemplate = async (template) => {
  try {
    await axios.delete(`/api/preprocessing/templates/${template.id}/`)
    ElMessage.success('模板删除成功')
    await fetchTemplates()
  } catch (error) {
    ElMessage.error('模板删除失败')
  }
}

const showSaveDialog = () => {
  templateForm.value = {
    name: '',
    description: '',
    is_public: false
  }
  saveDialogVisible.value = true
}

const showDialog = async () => {
  dialogVisible.value = true
  await fetchTemplates()
}

defineExpose({
  showDialog
})

const emit = defineEmits(['template-applied'])
</script>

<style scoped>
.template-manager {
  .template-actions {
    margin-bottom: 20px;
    display: flex;
    gap: 10px;
  }
}
</style> 