import { createStore } from 'vuex'
import axiosInstance from '../services/api'

export default createStore({
  state: {
    isAuthenticated: false,
    user: null,
    token: localStorage.getItem('token') || null,
    loading: false,
    notifications: []
  },
  mutations: {
    SET_LOADING(state, loading) {
      state.loading = loading
    },

    SET_AUTH(state, { user, token }) {
      state.isAuthenticated = true
      state.user = user
      state.token = token
      localStorage.setItem('token', token)
      localStorage.setItem('user', JSON.stringify(user))

      if (token) {
        axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${token}`
      }
    },

    CLEAR_AUTH(state) {
      state.isAuthenticated = false
      state.user = null
      state.token = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      delete axiosInstance.defaults.headers.common['Authorization']
    },

    UPDATE_USER(state, userData) {
      state.user = { ...state.user, ...userData }
      localStorage.setItem('user', JSON.stringify(state.user))
    },

    ADD_NOTIFICATION(state, notification) {
      state.notifications.push({
        id: Date.now(),
        ...notification
      })
    },

    REMOVE_NOTIFICATION(state, notificationId) {
      state.notifications = state.notifications.filter(
        n => n.id !== notificationId
      )
    }
  },
  actions: {
    async login({ commit }, credentials) {
      commit('SET_LOADING', true)
      try {
        const response = await axiosInstance.post('/login', credentials)
        console.log('[STORE] Login response:', response.data)
        const token = response.data.access_token
        if (!token) {
          console.error('[STORE] No token in response!', response.data)
          throw new Error('No token received from server')
        }

        console.log('[STORE] Token received:', token.substring(0, 20) + '...')


        localStorage.setItem('token', token)
        axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${token}`

        console.log('[STORE] Token stored in localStorage and axios defaults')

        commit('SET_AUTH', {
          user: response.data.user,
          token: token
        })


        const verifyToken = localStorage.getItem('token')
        const verifyAxios = axiosInstance.defaults.headers.common['Authorization']
        console.log('[STORE] Verification - localStorage:', verifyToken ? 'OK' : 'MISSING')
        console.log('[STORE] Verification - axios defaults:', verifyAxios ? 'OK' : 'MISSING')

        if (!verifyToken) {
          console.error('[STORE] Token was not stored properly!')
        }

        return response.data
      } catch (error) {
        console.error('[STORE] Login error:', error)
        throw error.response?.data || error
      } finally {
        commit('SET_LOADING', false)
      }
    },

    async register({ commit }, userData) {
      commit('SET_LOADING', true)
      try {
        const response = await axiosInstance.post('/register', userData)
        commit('SET_AUTH', {
          user: response.data.user,
          token: response.data.access_token
        })
        return response.data
      } catch (error) {
        throw error.response?.data || error
      } finally {
        commit('SET_LOADING', false)
      }
    },

    logout({ commit }) {
      commit('CLEAR_AUTH')
      // Redirect to login page
      if (window.$router) {
        window.$router.push('/login')
      } else {
        window.location.href = '/login'
      }
    },

    initializeAuth({ commit }) {
      const token = localStorage.getItem('token')
      const user = localStorage.getItem('user')

      if (token && user) {
        try {
          const userData = JSON.parse(user)
          commit('SET_AUTH', {
            user: userData,
            token
          })

          if (token) {
            axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${token}`
          }
        } catch (error) {
          console.error('Error parsing user data:', error)
          commit('CLEAR_AUTH')
        }
      }
    },

    updateUser({ commit }, userData) {
      commit('UPDATE_USER', userData)
    },

    addNotification({ commit }, notification) {
      commit('ADD_NOTIFICATION', notification)


      setTimeout(() => {
        commit('REMOVE_NOTIFICATION', notification.id)
      }, 5000)
    },

    removeNotification({ commit }, notificationId) {
      commit('REMOVE_NOTIFICATION', notificationId)
    }
  },

  getters: {
    isAdmin: state => state.user?.role === 'admin',
    isDoctor: state => state.user?.role === 'doctor',
    isPatient: state => state.user?.role === 'patient',
    userRole: state => state.user?.role,
    userName: state => state.user?.username,
    fullName: state => {
      if (!state.user) return ''
      return state.user.first_name && state.user.last_name
        ? `${state.user.first_name} ${state.user.last_name}`
        : state.user.username
    },
    unreadNotifications: state => state.notifications.length,
    isLoading: state => state.loading
  }
})