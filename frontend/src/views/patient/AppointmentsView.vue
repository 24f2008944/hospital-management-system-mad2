<template>
  <div class="container-fluid py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>My Appointments</h2>
      <div class="d-flex gap-3">
        <select v-model="statusFilter" class="form-select" style="width: 200px;">
          <option value="">All Appointments</option>
          <option value="scheduled">Scheduled</option>
          <option value="completed">Completed</option>
          <option value="cancelled">Cancelled</option>
        </select>
        <select v-model="dateFilter" class="form-select" style="width: 200px;">
          <option value="">All Dates</option>
          <option value="upcoming">Upcoming</option>
          <option value="past">Past</option>
          <option value="today">Today</option>
        </select>
      </div>
    </div>

    <!-- Loading / Error / No Appointments -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary"></div>
      <p class="mt-3">Loading appointments...</p>
    </div>

    <div v-else-if="error" class="alert alert-danger text-center py-5">
      <i class="bi bi-exclamation-triangle" style="font-size: 3rem;"></i>
      <p class="mt-3">{{ error }}</p>
    </div>

    <div v-else-if="!nextAppointment" class="text-center py-5">
      <i class="bi bi-calendar-x" style="font-size: 3rem; color: #6c757d;"></i>
      <p class="mt-3 text-muted">No upcoming appointments</p>
      <router-link to="/patient/book-appointment" class="btn btn-primary">
        <i class="bi bi-plus-circle me-2"></i>
        Book New Appointment
      </router-link>
    </div>

    <!-- Upcoming Appointment Card -->
    <div v-else class="row">
      <div class="col-md-8">
        <div class="card mb-4 border-primary">
          <div class="card-body d-flex justify-content-between align-items-start">
            <div>
              <h5 class="card-title mb-1">Upcoming Appointment</h5>
              <p class="mb-1"><strong>Dr. {{ nextAppointment.doctor_name }}</strong> — <small class="text-muted">{{ nextAppointment.doctor_specialization }}</small></p>
              <p class="mb-1"><strong>Department:</strong> {{ nextAppointment.department_name }}</p>
              <p class="mb-1"><strong>Status:</strong>
                <span class="badge" :class="getStatusClass(nextAppointment.status)">{{ nextAppointment.status }}</span>
              </p>
              <p class="mb-0 text-muted"><small>Appointment ID: #{{ nextAppointment.id }}</small></p>
            </div>

            <div class="d-flex flex-column align-items-end gap-2">
              <button class="btn btn-outline-primary btn-sm" @click="viewAppointment(nextAppointment)" title="View Details">
                <i class="bi bi-eye"></i> View
              </button>
              <button
                v-if="canCancel(nextAppointment)"
                class="btn btn-danger btn-sm"
                @click="cancelAppointment(nextAppointment.id)"
                title="Cancel Appointment"
              >
                <i class="bi bi-x-circle"></i> Cancel
              </button>
              <button class="btn btn-outline-danger btn-sm" @click="deleteAppointment(nextAppointment.id)" title="Delete Appointment">
                <i class="bi bi-trash"></i> Delete
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Optionally show a small list of "Other upcoming" (compact) -->
      <div class="col-md-4">
        <div class="card mb-4">
          <div class="card-body">
            <h6 class="card-title">Other Upcoming</h6>
            <ul class="list-unstyled mb-0">
              <li v-for="appt in otherUpcoming" :key="appt.id" class="mb-3">
                <div>
                  <strong>Dr. {{ appt.doctor_name }}</strong>
                  <div class="text-muted small">{{ formatDate(appt.appointment_date) }} • {{ formatTime(appt.appointment_time) }}</div>
                </div>
              </li>
            </ul>
            <div v-if="otherUpcoming.length === 0" class="text-muted small">No other upcoming appointments</div>
          </div>
        </div>
      </div>
    </div>

    <!-- View Appointment Modal (kept for details) -->
    <div class="modal fade" :class="{ show: showViewModal }" :style="{ display: showViewModal ? 'block' : 'none' }" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Appointment Details</h5>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>
          <div class="modal-body" v-if="selectedAppointment">
            <div class="row">
              <div class="col-md-6">
                <h6 class="fw-bold mb-3">Patient Information</h6>
                <p><strong>Name:</strong> {{ selectedAppointment.patient.full_name || 'N/A' }}</p>
                <p><strong>Email:</strong> {{ selectedAppointment.patient.user?.email || 'N/A' }}</p>
                <p><strong>Phone:</strong> {{ selectedAppointment.patient.contact_number || 'N/A' }}</p>
                <p><strong>Date of Birth:</strong> {{ selectedAppointment.patient.date_of_birth ? formatDate(selectedAppointment.patient.date_of_birth) : 'N/A' }}</p>
                <p><strong>Gender:</strong> {{ selectedAppointment.patient.gender || 'N/A' }}</p>
              </div>
              <div class="col-md-6">
                <h6 class="fw-bold mb-3">Doctor Information</h6>
                <p><strong>Name:</strong> Dr. {{ selectedAppointment.doctor.user?.username || 'N/A' }}</p>
                <p><strong>Email:</strong> {{ selectedAppointment.doctor.user?.email || 'N/A' }}</p>
                <p><strong>Specialization:</strong> {{ selectedAppointment.doctor.specialization || 'N/A' }}</p>
                <h6 class="fw-bold mb-3 mt-4">Appointment Details</h6>
                <p><strong>Date:</strong> {{ formatDate(selectedAppointment.appointment_date) }}</p>
                <p><strong>Time:</strong> {{ formatTime(selectedAppointment.appointment_time) }}</p>
                <p><strong>Status:</strong>
                  <span class="badge" :class="getStatusClass(selectedAppointment.status)">{{ selectedAppointment.status }}</span>
                </p>
                <p><strong>Reason:</strong> {{ selectedAppointment.reason || 'N/A' }}</p>
                <p><strong>Notes:</strong> {{ selectedAppointment.notes || 'N/A' }}</p>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeModal">Close</button>
            <button
              v-if="selectedAppointment?.status === 'Booked' && !isPast(selectedAppointment?.appointment_date)"
              type="button"
              class="btn btn-danger"
              @click="cancelAppointment(selectedAppointment.id)"
            >
              Cancel Appointment
            </button>
          </div>
        </div>
      </div>
    </div>
    <div v-if="showViewModal" class="modal-backdrop fade show"></div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'PatientAppointmentsView',
  data() {
    return {
      appointments: [],
      loading: false,
      error: null,
      statusFilter: '',
      dateFilter: '',
      showViewModal: false,
      selectedAppointment: null,
      appointmentTreatment: null
    }
  },
  computed: {
    // next upcoming appointment (after now) that matches filters
    nextAppointment() {
      const now = new Date()
      const filtered = this.appointments
        .filter(a => {
          // status filter
          if (this.statusFilter && a.status !== this.statusFilter) return false
          // date filter
          if (this.dateFilter) {
            const apptDate = new Date(a.appointment_date)
            apptDate.setHours(0,0,0,0)
            const today = new Date(); today.setHours(0,0,0,0)
            if (this.dateFilter === 'today' && apptDate.getTime() !== today.getTime()) return false
            if (this.dateFilter === 'past' && apptDate >= today) return false
            if (this.dateFilter === 'upcoming' && apptDate < today) return false
          }
          return new Date(a.appointment_date + ' ' + (a.appointment_time || '00:00')) >= now
        })
        .sort((a,b) => new Date(a.appointment_date + ' ' + (a.appointment_time || '00:00')) - new Date(b.appointment_date + ' ' + (b.appointment_time || '00:00')))

      return filtered.length ? filtered[0] : null
    },
    otherUpcoming() {
      const now = new Date()
      return this.appointments
        .filter(a => new Date(a.appointment_date + ' ' + (a.appointment_time || '00:00')) >= now && a.id !== (this.nextAppointment && this.nextAppointment.id))
        .sort((a,b) => new Date(a.appointment_date + ' ' + (a.appointment_time || '00:00')) - new Date(b.appointment_date + ' ' + (b.appointment_time || '00:00')))
        .slice(0,5)
    }
  },
  methods: {
    async loadAppointments() {
      try {
        this.loading = true
        this.error = null
        const response = await axios.get('/patient/appointments')
        this.appointments = response.data || []
      } catch (error) {
        console.error('Failed to load appointments:', error)
        this.error = error.response?.data?.message || error.message || 'Failed to load appointments.'
      } finally {
        this.loading = false
      }
    },

    async loadAppointmentTreatment(appointmentId) {
      try {
        const response = await axios.get(`/appointments/${appointmentId}/treatment`)
        this.appointmentTreatment = response.data
      } catch (error) {
        this.appointmentTreatment = null
      }
    },

    async cancelAppointment(appointmentId) {
      if (confirm('Are you sure you want to cancel this appointment?')) {
        try {
          await axios.delete(`/appointments/${appointmentId}`)
          await this.loadAppointments()
          if (this.showViewModal) this.closeModal()
        } catch (error) {
          console.error('Failed to cancel appointment:', error)
          alert('Failed to cancel appointment: ' + (error.response?.data?.message || error.message))
        }
      }
    },

    async deleteAppointment(appointmentId) {
      if (confirm('Are you sure you want to permanently delete this appointment? This action cannot be undone.')) {
        try {
          await axios.delete(`/appointments/${appointmentId}`)
          await this.loadAppointments()
          if (this.showViewModal) this.closeModal()
        } catch (error) {
          console.error('Failed to delete appointment:', error)
          alert('Failed to delete appointment: ' + (error.response?.data?.message || error.message))
        }
      }
    },

    async viewAppointment(appointment) {
      this.selectedAppointment = appointment
      this.appointmentTreatment = null
      if (appointment.status === 'completed') {
        await this.loadAppointmentTreatment(appointment.id)
      }
      this.showViewModal = true
    },

    isToday(dateString) {
      const today = new Date()
      const appointmentDate = new Date(dateString)
      return today.toDateString() === appointmentDate.toDateString()
    },

    isUpcoming(dateString) {
      const today = new Date()
      const appointmentDate = new Date(dateString)
      return appointmentDate > today
    },

    isPast(dateString) {
      const today = new Date()
      const appointmentDate = new Date(dateString)
      return appointmentDate < today
    },

    canCancel(appointment) {
      if (!appointment) return false
      const apptDate = new Date(appointment.appointment_date + ' ' + (appointment.appointment_time || '00:00'))
      return (appointment.status === 'Booked' || appointment.status === 'scheduled') && apptDate > new Date()
    },

    getStatusClass(status) {
      switch (status) {
        case 'Booked': case 'scheduled': return 'bg-primary'
        case 'Completed': case 'completed': return 'bg-success'
        case 'Cancelled': case 'cancelled': return 'bg-danger'
        default: return 'bg-secondary'
      }
    },

    formatDate(dateString) {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString()
    },

    formatTime(timeString) {
      if (!timeString) return 'N/A'
      return timeString
    },

    formatDateTime(dateTimeString) {
      if (!dateTimeString) return 'N/A'
      return new Date(dateTimeString).toLocaleString()
    },

    closeModal() {
      this.showViewModal = false
      this.selectedAppointment = null
      this.appointmentTreatment = null
    }
  },
  async created() {
    await this.loadAppointments()
  }
}
</script>

<style scoped>
.modal {
  background-color: rgba(0, 0, 0, 0.5);
}

.card {
  border-radius: 12px;
  border: none;
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  transition: transform 0.2s ease-in-out;
}

.card:hover {
  transform: translateY(-2px);
}

.card.border-primary {
  border: 2px solid #0d6efd !important;
}

.btn {
  border-radius: 8px;
}

.badge {
  font-size: 0.75rem;
  padding: 0.375rem 0.75rem;
  border-radius: 0.5rem;
}
</style>