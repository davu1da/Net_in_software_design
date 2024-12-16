import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const request = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => response,
  async error => {
    if (error.response) {
      const { status } = error.response
      if (status === 401) {
        // Token 过期，尝试刷新
        const refreshToken = localStorage.getItem('refresh_token')
        if (refreshToken) {
          try {
            const { data } = await axios.post('/api/auth/token/refresh/', {
              refresh: refreshToken
            })
            localStorage.setItem('access_token', data.access)
            error.config.headers.Authorization = `Bearer ${data.access}`
            return request(error.config)
          } catch (e) {
            localStorage.removeItem('access_token')
            localStorage.removeItem('refresh_token')
            router.push('/login')
          }
        }
      }
      ElMessage.error(error.response.data.message || '请求失败')
    } else {
      ElMessage.error('网络错误，请稍后重试')
    }
    return Promise.reject(error)
  }
)

export default request