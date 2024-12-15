<template>
  <div class="data-visualization">
    <div class="chart-controls">
      <el-form :inline="true" :model="chartConfig">
        <el-form-item label="图表类型">
          <el-select v-model="chartConfig.type" @change="updateChart">
            <el-option label="柱状图" value="bar" />
            <el-option label="折线图" value="line" />
            <el-option label="散点图" value="scatter" />
            <el-option label="箱线图" value="box" />
            <el-option label="直方图" value="histogram" />
            <el-option label="相关性热图" value="heatmap" />
          </el-select>
        </el-form-item>

        <template v-if="chartConfig.type !== 'heatmap'">
          <el-form-item label="X轴">
            <el-select v-model="chartConfig.xAxis" @change="updateChart">
              <el-option
                v-for="col in columns"
                :key="col.name"
                :label="col.name"
                :value="col.name" />
            </el-select>
          </el-form-item>

          <el-form-item label="Y轴">
            <el-select v-model="chartConfig.yAxis" @change="updateChart">
              <el-option
                v-for="col in numericColumns"
                :key="col.name"
                :label="col.name"
                :value="col.name" />
            </el-select>
          </el-form-item>
        </template>

        <el-form-item>
          <el-button type="primary" @click="updateChart">更新图表</el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="chart-container">
      <div ref="chartRef" class="chart"></div>
    </div>

    <div class="chart-stats" v-if="stats">
      <el-descriptions :column="3" border>
        <template v-if="chartConfig.type !== 'heatmap'">
          <el-descriptions-item label="平均值">
            {{ formatNumber(stats.mean) }}
          </el-descriptions-item>
          <el-descriptions-item label="中位数">
            {{ formatNumber(stats.median) }}
          </el-descriptions-item>
          <el-descriptions-item label="标准差">
            {{ formatNumber(stats.std) }}
          </el-descriptions-item>
          <el-descriptions-item label="最小值">
            {{ formatNumber(stats.min) }}
          </el-descriptions-item>
          <el-descriptions-item label="最大值">
            {{ formatNumber(stats.max) }}
          </el-descriptions-item>
          <el-descriptions-item label="数据点数">
            {{ stats.count }}
          </el-descriptions-item>
        </template>
        <template v-else>
          <el-descriptions-item label="最大相关性">
            {{ formatNumber(stats.maxCorr) }}
          </el-descriptions-item>
          <el-descriptions-item label="最小相关性">
            {{ formatNumber(stats.minCorr) }}
          </el-descriptions-item>
          <el-descriptions-item label="平均相关性">
            {{ formatNumber(stats.meanCorr) }}
          </el-descriptions-item>
        </template>
      </el-descriptions>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'

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

const chartRef = ref(null)
const chart = ref(null)
const stats = ref(null)

const chartConfig = ref({
  type: 'bar',
  xAxis: '',
  yAxis: ''
})

// 获取数值类型的列
const numericColumns = computed(() => {
  return props.columns.filter(col => 
    ['int64', 'float64'].includes(col.type)
  )
})

// 格式化数字
const formatNumber = (value) => {
  if (value === null || value === undefined) return '-'
  return Number.isFinite(value) ? value.toFixed(4) : value
}

// 计算统计信息
const calculateStats = (data) => {
  if (chartConfig.value.type === 'heatmap') {
    const corrValues = data.flat().filter(v => v !== 1)
    return {
      maxCorr: Math.max(...corrValues),
      minCorr: Math.min(...corrValues),
      meanCorr: corrValues.reduce((a, b) => a + b, 0) / corrValues.length
    }
  }

  const values = data.filter(v => !isNaN(v))
  return {
    mean: values.reduce((a, b) => a + b, 0) / values.length,
    median: values.sort((a, b) => a - b)[Math.floor(values.length / 2)],
    std: Math.sqrt(values.reduce((a, b) => a + Math.pow(b - values.reduce((a, b) => a + b, 0) / values.length, 2), 0) / values.length),
    min: Math.min(...values),
    max: Math.max(...values),
    count: values.length
  }
}

// 更新图表
const updateChart = async () => {
  if (!chart.value) return

  try {
    const option = await getChartOption()
    chart.value.setOption(option, true)
    
    // 更新统计信息
    if (chartConfig.value.type === 'heatmap') {
      stats.value = calculateStats(option.series[0].data)
    } else {
      stats.value = calculateStats(option.series[0].data)
    }
  } catch (error) {
    ElMessage.error('更新图表失败：' + error.message)
  }
}

// 获取图表配置
const getChartOption = async () => {
  const { type, xAxis, yAxis } = chartConfig.value
  
  if (type === 'heatmap') {
    return getHeatmapOption()
  }

  const xData = props.data[xAxis]
  const yData = props.data[yAxis]

  const baseOption = {
    title: {
      text: `${yAxis} vs ${xAxis}`,
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: xData,
      name: xAxis
    },
    yAxis: {
      type: 'value',
      name: yAxis
    },
    series: [{
      data: yData,
      type: type,
      name: yAxis
    }]
  }

  if (type === 'scatter') {
    baseOption.series[0].symbolSize = 10
  } else if (type === 'box') {
    // 计算箱线图数据
    const boxData = calculateBoxPlotData(yData)
    baseOption.series[0].data = [boxData]
  } else if (type === 'histogram') {
    // 计算直方图数据
    const histData = calculateHistogramData(yData)
    baseOption.series[0].data = histData
  }

  return baseOption
}

// 获取热图配置
const getHeatmapOption = () => {
  const numCols = numericColumns.value.map(col => col.name)
  const corrMatrix = calculateCorrelationMatrix(numCols)
  
  return {
    title: {
      text: '相关性热图',
      left: 'center'
    },
    tooltip: {
      position: 'top'
    },
    xAxis: {
      type: 'category',
      data: numCols,
      splitArea: {
        show: true
      }
    },
    yAxis: {
      type: 'category',
      data: numCols,
      splitArea: {
        show: true
      }
    },
    visualMap: {
      min: -1,
      max: 1,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: '15%'
    },
    series: [{
      name: '相关性',
      type: 'heatmap',
      data: corrMatrix,
      label: {
        show: true,
        formatter: (params) => params.value[2].toFixed(2)
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      }
    }]
  }
}

// 计算相关性矩阵
const calculateCorrelationMatrix = (columns) => {
  const matrix = []
  for (let i = 0; i < columns.length; i++) {
    for (let j = 0; j < columns.length; j++) {
      const col1 = props.data[columns[i]]
      const col2 = props.data[columns[j]]
      const corr = calculateCorrelation(col1, col2)
      matrix.push([i, j, corr])
    }
  }
  return matrix
}

// 计算相关系数
const calculateCorrelation = (x, y) => {
  const n = x.length
  const sum_x = x.reduce((a, b) => a + b, 0)
  const sum_y = y.reduce((a, b) => a + b, 0)
  const sum_xy = x.reduce((a, b, i) => a + b * y[i], 0)
  const sum_x2 = x.reduce((a, b) => a + b * b, 0)
  const sum_y2 = y.reduce((a, b) => a + b * b, 0)

  const numerator = n * sum_xy - sum_x * sum_y
  const denominator = Math.sqrt((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y))
  
  return denominator === 0 ? 0 : numerator / denominator
}

// 初始化图表
onMounted(() => {
  if (chartRef.value) {
    chart.value = echarts.init(chartRef.value)
    
    // 设置默认值
    if (numericColumns.value.length > 0) {
      chartConfig.value.xAxis = props.columns[0].name
      chartConfig.value.yAxis = numericColumns.value[0].name
      updateChart()
    }
  }
})

// 监听数据变化
watch(() => props.data, () => {
  updateChart()
}, { deep: true })

// 组件销毁时清理图表实例
onUnmounted(() => {
  if (chart.value) {
    chart.value.dispose()
  }
})
</script>

<style scoped>
.data-visualization {
  padding: 20px;
}

.chart-controls {
  margin-bottom: 20px;
}

.chart-container {
  width: 100%;
  height: 400px;
}

.chart {
  width: 100%;
  height: 100%;
}

.chart-stats {
  margin-top: 20px;
}
</style> 