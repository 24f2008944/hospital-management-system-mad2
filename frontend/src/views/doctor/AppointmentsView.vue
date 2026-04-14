<template>
  <div class="container-fluid py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>My Appointments</h2>
      <div class="d-flex gap-3">
        <select v-model="statusFilter" class="form-select" style="width: 200px;">
          <option value="">All Appointments</option>
          <option value="Booked">Booked</option>
          <option value="Completed">Completed</option>
          <option value="Cancelled">Cancelled</option>
        </select>
        <select v-model="dateFilter" class="form-select" style="width: 200px;">
          <option value="">All Dates</option>
          <option value="today">Today</option>
          <option value="tomorrow">Tomorrow</option>
          <option value="this_week">This Week</option>
          <option value="next_week">Next Week</option>
        </select>
      </div>
    </div>

    <!-- Appointments Cards -->
  <!-- Removed MonthlyReportButton -->
    <div class="row">
      <div v-if="loading" class="col-12 text-center py-5">
        <div class="spinner-border text-primary"></div>
        <p class="mt-3">Loading appointments...</p>
      </div>
      
      <div v-else-if="filteredAppointments.length === 0" class="col-12 text-center py-5">
        <i class="bi bi-calendar-x" style="font-size: 3rem; color: #6c757d;"></i>
        <p class="mt-3 text-muted">No appointments found</p>
      </div>
      
      <div v-else v-for="appointment in filteredAppointments" :key="appointment.id" class="col-md-6 col-lg-4 mb-4">
        <div class="card h-100" :class="{ 'border-primary': isToday(appointment.appointment_date) }">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start mb-3">
              <span class="badge" :class="getStatusClass(appointment.status)">
                {{ appointment.status }}
              </span>
              <span v-if="isToday(appointment.appointment_date)" class="badge bg-warning text-dark">
                Today
              </span>
            </div>
            
            <h5 class="card-title">{{ appointment.patient_name }}</h5>
            <p class="card-text">
              <i class="bi bi-person text-muted me-2"></i>{{ appointment.patient_email }}
            </p>
            
            <div class="mb-3">
              <p class="mb-1">
                <i class="bi bi-calendar text-muted me-2"></i>
                <strong>{{ formatDate(appointment.appointment_date) }}</strong>
              </p>
              <p class="mb-1">
                <i class="bi bi-clock text-muted me-2"></i>
                {{ formatTime(appointment.appointment_time) }}
              </p>
              <p class="mb-0">
                <i class="bi bi-building text-muted me-2"></i>
                {{ appointment.department_name }}
              </p>
            </div>
            
            <div class="mt-auto">
              <div class="d-flex gap-2">
                <button 
                  class="btn btn-outline-primary btn-sm flex-fill"
                  @click="viewAppointment(appointment)"
                >
                  <i class="bi bi-eye me-1"></i>
                  View Details
                </button>
                <button 
                  v-if="appointment.status === 'Booked'"
                  class="btn btn-success btn-sm"
                  @click="markCompleted(appointment.id)"
                  title="Mark as Completed"
                >
                  <i class="bi bi-check-circle"></i>
                </button>
                <button 
                  v-if="appointment.status === 'Booked'"
                  class="btn btn-outline-danger btn-sm"
                  @click="cancelAppointment(appointment.id)"
                  title="Cancel"
                >
                  <i class="bi bi-x-circle"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- View Appointment Modal -->
    <div class="modal fade" :class="{ show: showViewModal }" 
         :style="{ display: showViewModal ? 'block' : 'none' }"
         tabindex="-1">
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
                <p><strong>Name:</strong> {{ selectedAppointment.patient_name }}</p>
                <p><strong>Email:</strong> {{ selectedAppointment.patient_email }}</p>
                <p><strong>Phone:</strong> {{ selectedAppointment.patient_phone || 'N/A' }}</p>
                <p><strong>Date of Birth:</strong> {{ formatDate(selectedAppointment.patient_dob) }}</p>
                <p><strong>Medical History:</strong> {{ selectedAppointment.patient_medical_history || 'No history available' }}</p>
              </div>
              <div class="col-md-6">
                <h6 class="fw-bold mb-3">Appointment Details</h6>
                <p><strong>Date:</strong> {{ formatDate(selectedAppointment.appointment_date) }}</p>
                <p><strong>Time:</strong> {{ formatTime(selectedAppointment.appointment_time) }}</p>
                <p><strong>Department:</strong> {{ selectedAppointment.department_name }}</p>
                <p><strong>Status:</strong> 
                  <span class="badge" :class="getStatusClass(selectedAppointment.status)">
                    {{ selectedAppointment.status }}
                  </span>
                </p>
                <p><strong>Created:</strong> {{ formatDateTime(selectedAppointment.created_at) }}</p>
              </div>
            </div>
            
            <hr>
            
            <div v-if="selectedAppointment.notes">
              <h6 class="fw-bold mb-3">Notes</h6>
              <p class="text-muted">{{ selectedAppointment.notes }}</p>
            </div>
            
            <!-- Add Treatment Form for completed appointments -->
            <div v-if="selectedAppointment.status === 'Completed' && !selectedAppointment.has_treatment">
              <hr>
              <h6 class="fw-bold mb-3">Add Treatment Record</h6>
              <form @submit.prevent="addTreatment">
                <div class="mb-3">
                  <label class="form-label">Diagnosis</label>
                  <input 
                    type="text" 
                    v-model="treatmentForm.diagnosis" 
                    class="form-control" 
                    required
                    placeholder="Enter diagnosis..."
                  >
                </div>
                
                <div class="mb-3">
                  <label class="form-label">Prescription</label>
                  <textarea 
                    v-model="treatmentForm.prescription" 
                    class="form-control" 
                    rows="3"
                    placeholder="Enter prescription details..."
                  ></textarea>
                </div>
                
                <div class="mb-3">
                  <label class="form-label">Treatment Notes</label>
                  <textarea 
                    v-model="treatmentForm.notes" 
                    class="form-control" 
                    rows="3"
                    placeholder="Additional treatment notes..."
                  ></textarea>
                </div>
                
                <button type="submit" class="btn btn-primary" :disabled="saving">
                  <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
                  Add Treatment
                </button>
              </form>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeModal">Close</button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Modal backdrop -->
    <div v-if="showViewModal" class="modal-backdrop fade show"></div>
  </div>
</template>

<script>
import axios from 'axios'


export default {
  name: 'DoctorAppointmentsView',
  components: {
    // MonthlyReportButton removed
  },
  data() {
    return {
      appointments: [],
      loading: false,
      statusFilter: '',
      dateFilter: '',
      showViewModal: false,
      selectedAppointment: null,
      saving: false,
      treatmentForm: {
        diagnosis: '',
        prescription: '',
        notes: ''
      }
    }
  },
  computed: {
    filteredAppointments() {
      let filtered = this.appointments
      
      if (this.statusFilter) {
        filtered = filtered.filter(appointment => 
          appointment.status === this.statusFilter
        )
      }
      
      if (this.dateFilter) {
        const today = new Date()
        today.setHours(0, 0, 0, 0)
        
        filtered = filtered.filter(appointment => {
          const appointmentDate = new Date(appointment.appointment_date)
          appointmentDate.setHours(0, 0, 0, 0)
          
          switch (this.dateFilter) {
            case 'today':
              return appointmentDate.getTime() === today.getTime()
            case 'tomorrow': {
              const tomorrow = new Date(today)
              tomorrow.setDate(today.getDate() + 1)
              return appointmentDate.getTime() === tomorrow.getTime()
            }
            case 'this_week': {
              const endOfWeek = new Date(today)
              endOfWeek.setDate(today.getDate() + (6 - today.getDay()))
              return appointmentDate >= today && appointmentDate <= endOfWeek
            }
            case 'next_week': {
              const startOfNextWeek = new Date(today)
              startOfNextWeek.setDate(today.getDate() + (7 - today.getDay()))
              const endOfNextWeek = new Date(startOfNextWeek)
              endOfNextWeek.setDate(startOfNextWeek.getDate() + 6)
              return appointmentDate >= startOfNextWeek && appointmentDate <= endOfNextWeek
            }
            default:
              return true
          }
        })
      }
      
      return filtered.sort((a, b) => {
        const dateA = new Date(a.appointment_date + ' ' + a.appointment_time)
        const dateB = new Date(b.appointment_date + ' ' + b.appointment_time)
        return dateA - dateB
      })
    }
  },
  methods: {
    async loadAppointments() {
      try {
        this.loading = true
        const response = await axios.get('/appointments')
        this.appointments = response.data
      } catch (error) {
        console.error('Failed to load appointments:', error)
        alert('Failed to load appointments: ' + (error.response?.data?.error || error.message))
      } finally {
        this.loading = false
      }
    },
    
    async markCompleted(appointmentId) {
      if (confirm('Mark this appointment as completed?')) {
        try {
          await axios.put(`/appointments/${appointmentId}`, { status: 'Completed' })
          this.$toast?.success('Appointment marked as completed')
          await this.loadAppointments()
        } catch (error) {
          console.error('Failed to update appointment:', error)
          alert('Failed to update appointment status: ' + (error.response?.data?.error || error.message))
        }
      }
    },
    
    async cancelAppointment(appointmentId) {
      if (confirm('Are you sure you want to cancel this appointment?')) {
        try {
          await axios.delete(`/appointments/${appointmentId}`)
          this.$toast?.success('Appointment cancelled successfully')
          await this.loadAppointments()
        } catch (error) {
          console.error('Failed to cancel appointment:', error)
          alert('Failed to cancel appointment: ' + (error.response?.data?.error || error.message))
        }
      }
    },
    
    async addTreatment() {
      try {
        this.saving = true
        await axios.post(`/treatments/${this.selectedAppointment.id}`, {
          ...this.treatmentForm
        })
        
        this.treatmentForm = { diagnosis: '', prescription: '', notes: '' }
        this.closeModal()
        alert('Treatment record added successfully!')
        await this.loadAppointments()
      } catch (error) {
        console.error('Failed to add treatment:', error)
        alert('Failed to add treatment record: ' + (error.response?.data?.error || error.message))
      } finally {
        this.saving = false
      }
    },
    
    viewAppointment(appointment) {
      this.selectedAppointment = appointment
      this.showViewModal = true
    },
    
    isToday(dateString) {
      const today = new Date()
      const appointmentDate = new Date(dateString)
      return today.toDateString() === appointmentDate.toDateString()
    },
    
    getStatusClass(status) {
      switch (status) {
        case 'scheduled': return 'bg-primary'
        case 'completed': return 'bg-success'
        case 'cancelled': return 'bg-danger'
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
      this.treatmentForm = { diagnosis: '', prescription: '', notes: '' }
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
  border-radius: 15px;
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
