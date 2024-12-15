<template>
  <div class="data-preview">
    <el-table
      :data="tableData"
      style="width: 100%"
      height="400"
      border>
      <el-table-column
        v-for="col in columns"
        :key="col.name"
        :prop="col.name"
        :label="col.name"
        :width="getColumnWidth(col)">
        <template #default="scope">
          <span :class="getValueClass(scope.row[col.name])">
            {{ formatValue(scope.row[col.name]) }}
          </span>
        </template>
      </el-table-column>
    </el-table>

    <div class="column-stats">
      <el-descriptions
        v-for="col in columns"
        :key="col.name"
        :title="col.name"
        :column="4"
        border>
        <el-descriptions-item label="类型">
          {{ col.type }}
        </el-descriptions-item>
        <el-descriptions-item label="缺失值">
          {{ col.missing }}
        </el-descriptions-item>
        <el-descriptions-item label="唯一值">
          {{ col.unique }}
        </el-descriptions-item>
        <el-descriptions-item label="示例值">
          {{ getExampleValue(col.name) }}
        </el-descriptions-item>
      </el-descriptions>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: {
    type: Object,
    required: true
  },
  columns: {
    type: Array,
    required: true
  }
})

// 转换数据为表格格式
const tableData = computed(() => {
  const rows = []
  const firstCol = Object.keys(props.data)[0]
  const rowCount = props.data[firstCol].length

  for (let i = 0; i < rowCount; i++) {
    const row = {}
    for (const col of props.columns) {
      row[col.name] = props.data[col.name][i]
    }
    rows.push(row)
  }
  return rows
})

// 获取列宽
const getColumnWidth = (col) => {
  if (col.type === 'object') return 200
  return 150
}

// 格式化值
const formatValue = (value) => {
  if (value === null || value === undefined) return '-'
  if (typeof value === 'number') {
    return Number.isInteger(value) ? value : value.toFixed(4)
  }
  return value
}

// 获取值的样式类
const getValueClass = (value) => {
  if (value === null || value === undefined) return 'missing-value'
  return ''
}

// 获取示例值
const getExampleValue = (colName) => {
  const values = props.data[colName]
  return values && values.length > 0 ? formatValue(values[0]) : '-'
}
</script>

<style scoped>
.data-preview {
  padding: 20px;
}

.column-stats {
  margin-top: 20px;
}

.missing-value {
  color: #909399;
  font-style: italic;
}

:deep(.el-descriptions) {
  margin-bottom: 20px;
}
</style> 