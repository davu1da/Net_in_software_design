import axios from 'axios'

export default {
  namespaced: true,
  
  state: {
    notifications: [],
    unreadCount: 0,
    ws: null
  },

  mutations: {
    setNotifications(state, notifications) {
      state.notifications = notifications
    },
    setUnreadCount(state, count) {
      state.unreadCount = count
    },
    addNotification(state, notification) {
      state.notifications.unshift(notification)
      if (!notification.read) {
        state.unreadCount++
      }
    },
    markAsRead(state, notificationId) {
      const notification = state.notifications.find(n => n.id === notificationId)
      if (notification && !notification.read) {
        notification.read = true
        state.unreadCount--
      }
    },
    markAllAsRead(state) {
      state.notifications.forEach(n => n.read = true)
      state.unreadCount = 0
    }
  },

  actions: {
    async fetchNotifications({ commit }) {
      try {
        const response = await axios.get('/api/notifications/')
        commit('setNotifications', response.data)
      } catch (error) {
        console.error('获取通知失败:', error)
      }
    },

    async fetchUnreadCount({ commit }) {
      try {
        const response = await axios.get('/api/notifications/unread_count/')
        commit('setUnreadCount', response.data.count)
      } catch (error) {
        console.error('获取未读数量失败:', error)
      }
    },

    async markAsRead({ commit }, notificationId) {
      try {
        await axios.post(`/api/notifications/${notificationId}/mark_read/`)
        commit('markAsRead', notificationId)
      } catch (error) {
        console.error('标记已读失败:', error)
      }
    },

    async markAllAsRead({ commit }) {
      try {
        await axios.post('/api/notifications/mark_all_read/')
        commit('markAllAsRead')
      } catch (error) {
        console.error('标记全部已读失败:', error)
      }
    },

    connectWebSocket({ commit, state }) {
      const wsScheme = window.location.protocol === 'https:' ? 'wss' : 'ws'
      const ws = new WebSocket(`${wsScheme}://${window.location.host}/ws/notifications/`)
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data)
        if (data.type === 'notification') {
          commit('addNotification', data.notification)
        }
      }

      state.ws = ws
    },

    async cleanupNotifications({ commit }, { days = 30, readOnly = true }) {
      try {
        const response = await axios.post('/api/notifications/cleanup/', {
          days,
          read_only: readOnly
        })
        await dispatch('fetchNotifications')
        return response.data
      } catch (error) {
        console.error('清理通知失败:', error)
        throw error
      }
    },

    async getNotificationStats({ commit }) {
      try {
        const response = await axios.get('/api/notifications/stats/')
        return response.data
      } catch (error) {
        console.error('获取通知统计失败:', error)
        throw error
      }
    }
  }
} 