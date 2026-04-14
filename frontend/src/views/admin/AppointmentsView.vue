<template>
  <div class="container-fluid py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Manage Appointments</h2>
      <div class="d-flex gap-3">
        <button
          class="btn btn-warning"
          @click="triggerReminders"
          :disabled="remindersLoading"
        >
          <i class="bi bi-bell" v-if="!remindersLoading"></i>
          <div class="spinner-border spinner-border-sm" v-else></div>
          Send Daily Reminders
        </button>
        <div class="position-relative">
          <input
            type="text"
            v-model="searchQuery"
            class="form-control"
            placeholder="Search by patient name or doctor..."
            style="padding-left: 40px; width: 300px;"
          >
          <i class="bi bi-search position-absolute" style="left: 15px; top: 50%; transform: translateY(-50%);"></i>
        </div>
        <select v-model="statusFilter" class="form-select" style="width: 200px;">
          <option value="">All Status</option>
          <option value="Booked">Booked</option>
          <option value="Completed">Completed</option>
          <option value="Cancelled">Cancelled</option>
        </select>
      </div>
    </div>

    <!-- Appointments Table -->
    <div class="card">
      <div class="card-body">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary"></div>
          <p class="mt-3">Loading appointments...</p>
        </div>
        
        <div v-else-if="filteredAppointments.length === 0" class="text-center py-5">
          <i class="bi bi-calendar-x" style="font-size: 3rem; color: #6c757d;"></i>
          <p class="mt-3 text-muted">No appointments found</p>
        </div>
        
        <div v-else class="table-responsive">
          <table class="table table-hover">
            <thead class="table-light">
              <tr>
                <th>ID</th>
                <th>Patient</th>
                <th>Doctor</th>
                <th>Department</th>
                <th>Date & Time</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="appointment in filteredAppointments" :key="appointment.id">
                <td><strong>#{{ appointment.id }}</strong></td>
                <td>
                  <div>
                    <strong>{{ appointment.patient_name }}</strong>
                    <br>
                    <small class="text-muted">{{ appointment.patient_email }}</small>
                  </div>
                </td>
                <td>
                  <div>
                    <strong>Dr. {{ appointment.doctor_name }}</strong>
                    <br>
                    <small class="text-muted">{{ appointment.doctor_specialization }}</small>
                  </div>
                </td>
                <td>{{ appointment.department_name }}</td>
                <td>
                  <div>
                    <strong>{{ formatDate(appointment.appointment_date) }}</strong>
                    <br>
                    <small class="text-muted">{{ formatTime(appointment.appointment_time) }}</small>
                  </div>
                </td>
                <td>
                  <span class="badge" :class="getStatusClass(appointment.status)">
                    {{ appointment.status }}
                  </span>
                </td>
                <td>
                  <div class="btn-group btn-group-sm">
                    <button 
                      class="btn btn-outline-primary"
                      @click="viewAppointment(appointment)"
                      title="View Details"
                    >
                      <i class="bi bi-eye"></i>
                    </button>
                    <button
                      v-if="appointment.status === 'Booked'"
                      class="btn btn-outline-success"
                      @click="updateStatus(appointment.id, 'Completed')"
                      title="Mark as Completed"
                    >
                      <i class="bi bi-check-circle"></i>
                    </button>
                    <button
                      v-if="appointment.status === 'Booked'"
                      class="btn btn-outline-danger"
                      @click="cancelAppointment(appointment.id)"
                      title="Cancel"
                    >
                      <i class="bi bi-x-circle"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
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
              </div>
              <div class="col-md-6">
                <h6 class="fw-bold mb-3">Doctor Information</h6>
                <p><strong>Name:</strong> Dr. {{ selectedAppointment.doctor_name }}</p>
                <p><strong>Specialization:</strong> {{ selectedAppointment.doctor_specialization }}</p>
                <p><strong>Department:</strong> {{ selectedAppointment.department_name }}</p>
                <p><strong>Experience:</strong> {{ selectedAppointment.doctor_experience }} years</p>
              </div>
            </div>
            
            <hr>
            
            <div class="row">
              <div class="col-md-6">
                <h6 class="fw-bold mb-3">Appointment Details</h6>
                <p><strong>Date:</strong> {{ formatDate(selectedAppointment.appointment_date) }}</p>
                <p><strong>Time:</strong> {{ formatTime(selectedAppointment.appointment_time) }}</p>
                <p><strong>Status:</strong> 
                  <span class="badge" :class="getStatusClass(selectedAppointment.status)">
                    {{ selectedAppointment.status }}
                  </span>
                </p>
                <p><strong>Created:</strong> {{ formatDateTime(selectedAppointment.created_at) }}</p>
              </div>
              <div class="col-md-6">
                <h6 class="fw-bold mb-3">Notes</h6>
                <p>{{ selectedAppointment.notes || 'No notes available' }}</p>
              </div>
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
  name: 'AdminAppointmentsView',
  data() {
    return {
      appointments: [],
      loading: false,
      searchQuery: '',
      statusFilter: '',
      showViewModal: false,
      selectedAppointment: null,
      remindersLoading: false
    }
  },
  computed: {
    filteredAppointments() {
      let filtered = this.appointments
      
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        filtered = filtered.filter(appointment => 
          appointment.patient_name.toLowerCase().includes(query) ||
          appointment.doctor_name.toLowerCase().includes(query) ||
          appointment.department_name.toLowerCase().includes(query)
        )
      }
      
      if (this.statusFilter) {
        filtered = filtered.filter(appointment => 
          appointment.status === this.statusFilter
        )
      }
      
      return filtered
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
      } finally {
        this.loading = false
      }
    },
    
    async updateStatus(appointmentId, status) {
      try {
        await axios.put(`/appointments/${appointmentId}`, { status })
        await this.loadAppointments()
      } catch (error) {
        console.error('Failed to update appointment status:', error)
        alert('Failed to update appointment status')
      }
    },

    async cancelAppointment(appointmentId) {
      if (confirm('Are you sure you want to cancel this appointment?')) {
        try {
          await axios.delete(`/appointments/${appointmentId}`)
          await this.loadAppointments()
        } catch (error) {
          console.error('Failed to cancel appointment:', error)
          alert('Failed to cancel appointment')
        }
      }
    },
    
    viewAppointment(appointment) {
      this.selectedAppointment = appointment
      this.showViewModal = true
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
    },

    async triggerReminders() {
      try {
        this.remindersLoading = true
        await axios.post('/trigger-reminders')
        alert('Reminders sent successfully!')
      } catch (error) {
        console.error('Failed to send reminders:', error)
        alert('Failed to send reminders')
      } finally {
        this.remindersLoading = false
      }
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
  border: 1px solid #dee2e6;
  border-radius: 0;
}

.btn {
  border-radius: 0;
}

.table th {
  background-color: #f8f9fa;
  border-bottom: 2px solid #dee2e6;
  font-weight: 600;
}

.table td {
  border-bottom: 1px solid #dee2e6;
}

.form-control, .form-select {
  border-radius: 0;
}

.btn-primary {
  background-color: #007bff;
  border-color: #007bff;
}

.btn-outline-primary {
  color: #007bff;
  border-color: #007bff;
}

.btn-outline-success {
  color: #28a745;
  border-color: #28a745;
}

.btn-outline-warning {
  color: #ffc107;
  border-color: #ffc107;
}

.badge {
  font-size: 0.75rem;
  padding: 0.375rem 0.75rem;
  border-radius: 0;
}
</style>
