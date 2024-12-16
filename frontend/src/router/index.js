import { createRouter, createWebHistory } from 'vue-router'
import BaseLayout from '@/layouts/BaseLayout.vue'
import AuthLayout from '@/layouts/AuthLayout.vue'

const routes = [
  {
    path: '/',
    component: BaseLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/dashboard'
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue')
      },
      {
        path: 'data',
        name: 'DataManagement',
        component: () => import('@/views/DataManagement.vue')
      },
      {
        path: 'model',
        name: 'ModelEditor',
        component: () => import('@/views/ModelEditor.vue')
      },
      {
        path: 'training',
        name: 'ModelTraining',
        component: () => import('@/views/ModelTraining.vue')
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/Settings.vue')
      }
    ]
  },
  {
    path: '/',
    component: AuthLayout,
    meta: { requiresAuth: false },
    children: [
      {
        path: 'login',
        name: 'Login',
        component: () => import('@/views/auth/Login.vue')
      },
      {
        path: 'register',
        name: 'Register',
        component: () => import('@/views/auth/Register.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true'
  
  if (to.matched.some(record => record.meta.requiresAuth) && !isAuthenticated) {
    next('/login')
  } else if ((to.path === '/login' || to.path === '/register') && isAuthenticated) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router 