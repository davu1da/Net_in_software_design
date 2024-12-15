import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import DataManagement from '../views/DataManagement.vue'
import ModelEditor from '../views/ModelEditor.vue'
import ModelTraining from '../views/ModelTraining.vue'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard
  },
  {
    path: '/data',
    name: 'DataManagement',
    component: DataManagement
  },
  {
    path: '/model',
    name: 'ModelEditor',
    component: ModelEditor
  },
  {
    path: '/training',
    name: 'ModelTraining',
    component: ModelTraining
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 