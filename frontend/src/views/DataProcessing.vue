<template>
  <div class="data-processing">
    <el-card class="data-table-card">
      <!-- 工具栏 -->
      <div class="toolbar">
        <div class="left-tools">
          <el-button-group>
            <el-tooltip content="保存">
              <el-button type="primary" @click="saveChanges">
                <el-icon><Save /></el-icon>
              </el-button>
            </el-tooltip>
            <el-tooltip content="撤销">
              <el-button :disabled="!canUndo" @click="undo">
                <el-icon><Back /></el-icon>
              </el-button>
            </el-tooltip>
            <el-tooltip content="重做">
              <el-button :disabled="!canRedo" @click="redo">
                <el-icon><Right /></el-icon>
              </el-button>
            </el-tooltip>
          </el-button-group>

          <el-divider direction="vertical" />

          <el-button-group>
            <el-tooltip content="添加行">
              <el-button @click="addRow">
                <el-icon><Plus /></el-icon>
              </el-button>
            </el-tooltip>
            <el-tooltip content="删除选中行">
              <el-button 
                :disabled="!selectedRows.length"
                @click="deleteRows">
                <el-icon><Delete /></el-icon>
              </el-button>
            </el-tooltip>
          </el-button-group>

          <el-divider direction="vertical" />

          <el-select 
            v-model="currentDataset" 
            placeholder="选择数据集"
            @change="handleDatasetChange">
            <el-option
              v-for="dataset in datasets"
              :key="dataset.id"
              :label="dataset.name"
              :value="dataset.id" />
          </el-select>
        </div>

        <div class="right-tools">
          <el-input
            v-model="searchText"
            placeholder="搜索..."
            prefix-icon="Search"
            clearable
            @input="handleSearch" />
        </div>
      </div>

      <!-- 数据表格 -->
      <el-table
        ref="dataTable"
        v-loading="loading"
        :data="filteredData"
        :height="tableHeight"
        border
        @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="55" />
        <el-table-column type="index" width="50" label="#" />
        <el-table-column
          v-for="column in columns"
          :key="column.name"
          :prop="column.name"
          :label="column.name"
          :width="column.width">
          <template #default="scope">
            <el-input
              v-if="scope.row.editing"
              v-model="scope.row[column.name]"
              size="small" />
            <span v-else>{{ scope.row[column.name] }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="scope">
            <el-button-group>
              <el-button
                :icon="scope.row.editing ? 'Check' : 'Edit'"
                size="small"
                @click="toggleEdit(scope.row)" />
              <el-button
                v-if="scope.row.editing"
                icon="Close"
                size="small"
                @click="cancelEdit(scope.row)" />
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页器 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="totalRows"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Save, Back, Right, Plus, Delete, Search, Edit, Check, Close } from '@element-plus/icons-vue'
import request from '@/utils/request'

// 状态变量
const loading = ref(false)
const datasets = ref([])
const currentDataset = ref(null)
const columns = ref([])
const tableData = ref([])
const searchText = ref('')
const selectedRows = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const totalRows = ref(0)
const tableHeight = ref('calc(100vh - 220px)')

// 编辑历史
const history = ref([])
const historyIndex = ref(-1)
const canUndo = computed(() => historyIndex.value > 0)
const canRedo = computed(() => historyIndex.value < history.value.length - 1)

// 过滤后的数据
const filteredData = computed(() => {
  if (!searchText.value) return tableData.value
  
  const searchRegex = new RegExp(searchText.value, 'i')
  return tableData.value.filter(row => {
    return Object.values(row).some(value => 
      String(value).match(searchRegex)
    )
  })
})

// 获取数据集列表
const fetchDatasets = async () => {
  try {
    console.log('Fetching datasets...')
    const response = await request.get('/api/preprocessing/datasets/')
    console.log('Datasets response:', response)
    datasets.value = response.data
    if (datasets.value.length > 0) {
      currentDataset.value = datasets.value[0].id
      await loadDataset(currentDataset.value)
    }
  } catch (error) {
    console.error('Error fetching datasets:', error)
    ElMessage.error('获取数据集列表失败')
  }
}

// 加载数据集
const loadDataset = async (datasetId) => {
  if (!datasetId) return
  
  loading.value = true
  try {
    console.log('Loading dataset:', datasetId)
    const response = await request.get(`/api/preprocessing/datasets/${datasetId}/data/`, {
      params: {
        page: currentPage.value,
        page_size: pageSize.value,
        search: searchText.value
      }
    })
    console.log('Dataset data response:', response)
    
    columns.value = response.data.columns || []
    tableData.value = (response.data.data || []).map(row => ({
      ...row,
      editing: false,
      _original: { ...row }
    }))
    totalRows.value = response.data.total || 0
    
    // 重置历史记录
    history.value = [JSON.stringify(tableData.value)]
    historyIndex.value = 0
    
  } catch (error) {
    console.error('Error loading dataset:', error)
    ElMessage.error('加载数据集失败')
  } finally {
    loading.value = false
  }
}

// 保存更改
const saveChanges = async () => {
  try {
    const changes = tableData.value
      .filter(row => row.editing)
      .map(row => ({
        id: row.id,
        changes: Object.keys(row)
          .filter(key => key !== 'editing' && key !== '_original')
          .reduce((acc, key) => {
            if (row[key] !== row._original[key]) {
              acc[key] = row[key]
            }
            return acc
          }, {})
      }))
      .filter(change => Object.keys(change.changes).length > 0)

    if (changes.length === 0) {
      ElMessage.info('没有需要保存的更改')
      return
    }

    await request.post(`/api/preprocessing/datasets/${currentDataset.value}/update/`, {
      changes
    })

    // 更新原始数据
    tableData.value.forEach(row => {
      if (row.editing) {
        row._original = { ...row }
        row.editing = false
      }
    })

    ElMessage.success('保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

// 编辑相关方法
const toggleEdit = (row) => {
  if (row.editing) {
    // 保存编辑
    row.editing = false
    row._original = { ...row }
    addToHistory()
  } else {
    row.editing = true
  }
}

const cancelEdit = (row) => {
  Object.assign(row, row._original)
  row.editing = false
}

const addToHistory = () => {
  historyIndex.value++
  history.value = history.value.slice(0, historyIndex.value)
  history.value.push(JSON.stringify(tableData.value))
}

const undo = () => {
  if (canUndo.value) {
    historyIndex.value--
    tableData.value = JSON.parse(history.value[historyIndex.value])
  }
}

const redo = () => {
  if (canRedo.value) {
    historyIndex.value++
    tableData.value = JSON.parse(history.value[historyIndex.value])
  }
}

// 行操作
const handleSelectionChange = (rows) => {
  selectedRows.value = rows
}

const addRow = () => {
  const newRow = columns.value.reduce((acc, col) => {
    acc[col.name] = ''
    return acc
  }, {})
  
  newRow.editing = true
  newRow._original = { ...newRow }
  tableData.value.unshift(newRow)
  addToHistory()
}

const deleteRows = async () => {
  try {
    await request.post(`/api/preprocessing/datasets/${currentDataset.value}/delete-rows/`, {
      row_ids: selectedRows.value.map(row => row.id)
    })
    
    tableData.value = tableData.value.filter(
      row => !selectedRows.value.includes(row)
    )
    addToHistory()
    ElMessage.success('删除成功')
  } catch (error) {
    ElMessage.error('��除失败')
  }
}

// 分页处理
const handleSizeChange = (size) => {
  pageSize.value = size
  loadDataset(currentDataset.value)
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  loadDataset(currentDataset.value)
}

// 搜索处理
const handleSearch = () => {
  currentPage.value = 1
}

// 监听数据集变化
const handleDatasetChange = async (datasetId) => {
  currentDataset.value = datasets.value.find(d => d.id === datasetId)
  currentPage.value = 1
  await loadDataset(datasetId)
}

// 添加初始化函数
const init = async () => {
  loading.value = true
  try {
    await fetchDatasets()
  } catch (error) {
    ElMessage.error('初始化失败')
  } finally {
    loading.value = false
  }
}

// 修改 onMounted
onMounted(() => {
  init()
})
</script>

<style scoped>
.data-processing {
  padding: 20px;
}

.data-table-card {
  height: calc(100vh - 80px);
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.left-tools {
  display: flex;
  align-items: center;
  gap: 10px;
}

.right-tools {
  display: flex;
  align-items: center;
  gap: 10px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style> 