import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import store from './store'
import request from './utils/request'
import VChart from 'vue-echarts'

const app = createApp(App)

// 全局配置
app.config.globalProperties.$http = request
app.component('v-chart', VChart)  // 全局注册 VChart 组件
app.use(ElementPlus)
app.use(router)
app.use(store)
app.mount('#app')