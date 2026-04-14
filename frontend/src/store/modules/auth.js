import axios from 'axios'

const state = {
  user: JSON.parse(localStorage.getItem('user')) || null,
  isAuthenticated: !!JSON.parse(localStorage.getItem('user')),
  loading: false,
  error: null
}

const mutations = {
  SET_USER(state, user) {
    state.user = user
    state.isAuthenticated = !!user
    if (user) {
      localStorage.setItem('user', JSON.stringify(user))
    } else {
      localStorage.removeItem('user')
    }
  },
  SET_LOADING(state, loading) {
    state.loading = loading
  },
  SET_ERROR(state, error) {
    state.error = error
  },
  CLEAR_ERROR(state) {
    state.error = null
  }
}

const actions = {
  async login({ commit }, credentials) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      const response = await axios.post('/auth', {
        action: 'login',
        ...credentials
      })
      
      if (response.data.success) {
        const { user } = response.data
        commit('SET_USER', user)
        return { success: true }
      } else {
        throw new Error(response.data.message || 'Login failed')
      }
    } catch (error) {
      const message = error.response?.data?.message || error.message || 'Login failed'
      commit('SET_ERROR', message)
      return { success: false, message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async register({ commit }, userData) {
    try {
      commit('SET_LOADING', true)
      commit('CLEAR_ERROR')
      
      const response = await axios.post('/auth', {
        action: 'register',
        ...userData
      })
      
      if (response.data.success) {
        const { user } = response.data
        return { success: true, user }
      } else {
        throw new Error(response.data.message || 'Registration failed')
      }
    } catch (error) {
      const message = error.response?.data?.message || error.message || 'Registration failed'
      commit('SET_ERROR', message)
      return { success: false, message }
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async logout({ commit }) {
    try {
      await axios.post('/auth', { action: 'logout' })
    } catch (error) {
      // Continue with logout even if API call fails
      console.error('Logout API call failed:', error)
    }
    
    commit('SET_USER', null)
  },

  async loadUser({ commit, state }) {
    if (!state.user) {
      return
    }
    
    try {
      const response = await axios.get('/dashboard')
      if (response.data && !response.data.error) {
        // Dashboard call successful, user is authenticated
        return
      }
    } catch (error) {
      commit('SET_USER', null)
      throw error
    }
  }
}

const getters = {
  isAuthenticated: state => state.isAuthenticated,
  user: state => state.user,
  userRole: state => state.user?.roles?.[0] || null,
  loading: state => state.loading,
  error: state => state.error
}

export default {
  namespaced: true,
  state,
  mutations,
  actions,
  getters
}
