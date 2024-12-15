import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: import.meta.env.VITE_APP_API_URL || 'http://localhost:8000',
  timeout: 5000,
  withCredentials: true
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    // 添加 CSRF Token
    const csrfToken = document.cookie.match(/csrftoken=([\w-]+)/)?.[1]
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken
    }
    return config
  },
  error => {
    console.error('请求错误：', error)
    return Promise.reject(error)
  }
)

export default request