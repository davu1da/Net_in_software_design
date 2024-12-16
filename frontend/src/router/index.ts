import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    component: () => import('@/layouts/BaseLayout.vue'),
    children: [
      {
        path: '',
        redirect: '/dashboard'
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: {
          requiresAuth: true,
          title: '仪表盘'
        }
      },
      {
        path: 'data-management',
        name: 'DataManagement',
        component: () => import('@/views/DataManagement.vue'),
        meta: {
          requiresAuth: true,
          title: '数据集管理'
        }
      },
      {
        path: 'data-preprocessing',
        name: 'DataPreprocessing',
        component: () => import('@/views/DataPreprocessing.vue'),
        meta: {
          requiresAuth: true,
          title: '数据预处理'
        }
      },
      {
        path: 'data-processing',
        name: 'DataProcessing',
        component: () => import('@/views/DataProcessing.vue'),
        meta: {
          requiresAuth: true,
          title: '���据处理'
        }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!token) {
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router 