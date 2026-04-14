import axios from 'axios'

const state = {
  dashboard: null,
  departments: [],
  doctors: [],
  patients: [],
  appointments: [],
  loading: false,
  error: null
}

const mutations = {
  SET_DASHBOARD(state, data) {
    state.dashboard = data
  },
  SET_DEPARTMENTS(state, departments) {
    state.departments = departments
  },
  SET_DOCTORS(state, doctors) {
    state.doctors = doctors
  },
  SET_PATIENTS(state, patients) {
    state.patients = patients
  },
  SET_APPOINTMENTS(state, appointments) {
    state.appointments = appointments
  },
  SET_LOADING(state, loading) {
    state.loading = loading
  },
  SET_ERROR(state, error) {
    state.error = error
  },
  CLEAR_ERROR(state) {
    state.error = null
  },
  ADD_APPOINTMENT(state, appointment) {
    state.appointments.unshift(appointment)
  },
  UPDATE_APPOINTMENT(state, updatedAppointment) {
    const index = state.appointments.findIndex(apt => apt.id === updatedAppointment.id)
    if (index !== -1) {
      state.appointments.splice(index, 1, updatedAppointment)
    }
  },
  REMOVE_APPOINTMENT(state, appointmentId) {
    state.appointments = state.appointments.filter(apt => apt.id !== appointmentId)
  }
}

const actions = {
  async fetchDashboard({ commit }) {
    try {
      commit('SET_LOADING', true)
      const response = await axios.get('/dashboard')
      commit('SET_DASHBOARD', response.data)
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || 'Failed to fetch dashboard')
      throw error
    } finally {
      commit('SET_LOADING', false)
    }
  },

  async fetchDepartments({ commit }) {
    try {
      const response = await axios.get('/departments')
      commit('SET_DEPARTMENTS', response.data)
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || 'Failed to fetch departments')
      throw error
    }
  },

  async fetchDoctors({ commit }, params = {}) {
    try {
      const response = await axios.get('/doctors', { params })
      commit('SET_DOCTORS', response.data)
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || 'Failed to fetch doctors')
      throw error
    }
  },

  async fetchPatients({ commit }, params = {}) {
    try {
      const response = await axios.get('/patients', { params })
      commit('SET_PATIENTS', response.data)
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || 'Failed to fetch patients')
      throw error
    }
  },

  async fetchAppointments({ commit }, params = {}) {
    try {
      const response = await axios.get('/appointments', { params })
      commit('SET_APPOINTMENTS', response.data)
      return response.data
    } catch (error) {
      commit('SET_ERROR', error.response?.data?.message || 'Failed to fetch appointments')
      throw error
    }
  },

  async createAppointment({ commit }, appointmentData) {
    try {
      const response = await axios.post('/appointments', appointmentData)
      commit('ADD_APPOINTMENT', response.data)
      return response.data
    } catch (error) {
      const message = error.response?.data?.message || 'Failed to create appointment'
      commit('SET_ERROR', message)
      throw new Error(message)
    }
  },

  async updateAppointment({ commit }, { id, data }) {
    try {
      const response = await axios.put(`/appointments/${id}`, data)
      commit('UPDATE_APPOINTMENT', response.data)
      return response.data
    } catch (error) {
      const message = error.response?.data?.message || 'Failed to update appointment'
      commit('SET_ERROR', message)
      throw new Error(message)
    }
  },

  async cancelAppointment({ commit }, appointmentId) {
    try {
      const response = await axios.delete(`/appointments/${appointmentId}`)
      // Since backend does soft delete, update the appointment status
      commit('UPDATE_APPOINTMENT', { id: appointmentId, status: 'Cancelled', ...response.data })
    } catch (error) {
      const message = error.response?.data?.message || 'Failed to cancel appointment'
      commit('SET_ERROR', message)
      throw new Error(message)
    }
  },

  async createTreatment({ commit }, { appointmentId, treatmentData }) {
    try {
      const response = await axios.post(`/treatments/${appointmentId}`, treatmentData)
      return response.data
    } catch (error) {
      const message = error.response?.data?.message || 'Failed to create treatment'
      commit('SET_ERROR', message)
      throw new Error(message)
    }
  },

  async updateTreatment({ commit }, { appointmentId, treatmentData }) {
    try {
      const response = await axios.put(`/treatments/${appointmentId}`, treatmentData)
      return response.data
    } catch (error) {
      const message = error.response?.data?.message || 'Failed to update treatment'
      commit('SET_ERROR', message)
      throw new Error(message)
    }
  },

  async search({ commit }, { query, type = 'all' }) {
    try {
      const response = await axios.get('/search', { params: { q: query, type } })
      return response.data
    } catch (error) {
      const message = error.response?.data?.message || 'Search failed'
      commit('SET_ERROR', message)
      throw new Error(message)
    }
  },

  async exportData({ commit }, exportData) {
    try {
      const response = await axios.post('/export', exportData)
      return response.data
    } catch (error) {
      const message = error.response?.data?.message || 'Export failed'
      commit('SET_ERROR', message)
      throw new Error(message)
    }
  }
}

const getters = {
  dashboard: state => state.dashboard,
  departments: state => state.departments,
  doctors: state => state.doctors,
  patients: state => state.patients,
  appointments: state => state.appointments,
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
