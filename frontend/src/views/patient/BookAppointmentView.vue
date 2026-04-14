<template>
  <div class="container py-4">
    <div class="row justify-content-center">
      <div class="col-md-8">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">
              <i class="bi bi-calendar-plus"></i>
              Book New Appointment
            </h5>
          </div>
          <div class="card-body">
            <form @submit.prevent="bookAppointment">
              <div class="mb-3">
                <label for="department" class="form-label">Department</label>
                <select
                  id="department"
                  v-model="selectedDepartment"
                  @change="loadDoctors"
                  class="form-select"
                  required
                >
                  <option value="">Select Department</option>
                  <option
                    v-for="department in departments"
                    :key="department.id"
                    :value="department.id"
                  >
                    {{ department.name }}
                  </option>
                </select>
              </div>

              <div class="mb-3">
                <label for="doctor" class="form-label">Doctor</label>
                <div class="d-flex gap-2">
                  <select
                    id="doctor"
                    v-model="form.doctor_id"
                    @change="loadDoctorAvailability"
                    class="form-select"
                    :disabled="!selectedDepartment"
                    required
                  >
                    <option value="">Select Doctor</option>
                    <option
                      v-for="doctor in filteredDoctors"
                      :key="doctor.id"
                      :value="doctor.id"
                    >
                      Dr. {{ doctor.user.username }} - {{ doctor.specialization }}
                    </option>
                  </select>
                  <button
                    type="button"
                    class="btn btn-outline-primary"
                    :disabled="!form.doctor_id"
                    @click="showDoctorDetails"
                    title="View Doctor Details"
                  >
                    <i class="bi bi-eye"></i>
                    View Detail
                  </button>
                </div>
              </div>

              <!-- Doctor Availability Section -->
              <div v-if="form.doctor_id && doctorAvailability.length > 0" class="mb-4">
                <h6 class="text-primary">
                  <i class="bi bi-calendar-week"></i>
                  Available Time Slots
                </h6>
                <div class="availability-grid">
                  <div 
                    v-for="slot in doctorAvailability" 
                    :key="slot.id"
                    class="availability-slot"
                    :class="{ 'selected': isSlotSelected(slot) }"
                    @click="selectAvailabilitySlot(slot)"
                  >
                    <div class="slot-date">{{ formatDate(slot.date || slot.available_date) }}</div>
                    <div class="slot-time">{{ formatTime(slot.start_time) }} - {{ formatTime(slot.end_time) }}</div>
                    <div class="slot-availability">
                      <small :class="{'text-muted': !isSlotSelected(slot), 'text-white-50': isSlotSelected(slot)}">
                        {{ slot.available_appointments || slot.max_appointments }} of {{ slot.max_appointments }} available
                      </small>
                    </div>
                  </div>
                </div>
              </div>
              
              <div v-else-if="form.doctor_id && loadingAvailability" class="mb-4 text-center">
                <div class="spinner-border text-primary" role="status">
                  <span class="visually-hidden">Loading availability...</span>
                </div>
                <p class="text-muted mt-2">Loading doctor availability...</p>
              </div>

              <div v-else-if="form.doctor_id && doctorAvailability.length === 0 && !loadingAvailability" class="mb-4">
                <div class="alert alert-warning">
                  <i class="bi bi-exclamation-triangle"></i>
                  No availability slots found for the selected doctor in the next 30 days.
                </div>
              </div>

              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="appointmentDate" class="form-label">Appointment Date</label>
                  <input
                    type="date"
                    id="appointmentDate"
                    v-model="form.appointment_date"
                    class="form-control"
                    :min="minDate"
                    required
                  >
                </div>
                <div class="col-md-6 mb-3">
                  <label for="appointmentTime" class="form-label">Appointment Time</label>
                  <select
                    id="appointmentTime"
                    v-model="form.appointment_time"
                    class="form-select"
                    required
                  >
                    <option value="">Select Time</option>
                    <option v-for="time in filteredAvailableTimes" :key="time" :value="time">
                      {{ formatTime(time) }}
                    </option>
                  </select>
                </div>
              </div>

              <div class="mb-3">
                <label for="reason" class="form-label">Reason for Visit</label>
                <textarea
                  id="reason"
                  v-model="form.reason"
                  class="form-control"
                  rows="3"
                  placeholder="Describe your symptoms or reason for the appointment..."
                ></textarea>
              </div>

              <div v-if="error" class="alert alert-danger">
                {{ error }}
              </div>

              <div v-if="successMessage" class="alert alert-success">
                {{ successMessage }}
              </div>

              <div class="text-end">
                <button type="button" class="btn btn-secondary me-2" @click="$router.go(-1)">
                  Cancel
                </button>
                <button type="submit" class="btn btn-primary" :disabled="loading">
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                  Book Appointment
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- EMBEDDED DOCTOR DETAIL MODAL -->
    <div v-if="showDoctorModal" class="modal-backdrop" @click.self="closeDoctorModal">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content border-0 shadow-lg">
          <div class="modal-header border-bottom-0 pb-0">
            <h5 class="modal-title fw-bold">Doctor Details</h5>
            <button type="button" class="btn-close" @click="closeDoctorModal"></button>
          </div>
          <div class="modal-body py-4">
            <div v-if="loadingDoctorDetails" class="text-center py-4">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            <div v-else-if="doctorDetails" class="px-2">
              <!-- Name -->
              <div class="text-center mb-4">
                <h3 class="fw-bold text-dark mb-0">{{ doctorDetails.user?.username || doctorDetails.name }}</h3>
              </div>
              <!-- Grid Details -->
              <div class="row g-3">
                <div class="col-md-6">
                  <div class="detail-item">
                    <label>Department</label>
                    <div class="value text-primary fw-medium">{{ doctorDetails.department?.name || 'N/A' }}</div>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="detail-item">
                    <label>Qualification</label>
                    <div class="value">{{ doctorDetails.qualification || 'N/A' }}</div>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="detail-item">
                    <label>Experience</label>
                    <div class="value">{{ doctorDetails.experience_years ? `${doctorDetails.experience_years} years` : 'N/A' }}</div>
                  </div>
                </div>
                <div class="col-md-6">
                  <div class="detail-item">
                    <label>License Number</label>
                    <div class="value font-monospace">{{ doctorDetails.license_number || 'N/A' }}</div>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="text-center py-4 text-muted">
              <p>Could not load doctor details.</p>
            </div>
          </div>
          <div class="modal-footer border-top-0 pt-0">
            <button type="button" class="btn btn-secondary w-100" @click="closeDoctorModal">Close</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'
import axios from 'axios'

export default {
  name: 'BookAppointmentView',
  data() {
    return {
      form: {
        doctor_id: '',
        appointment_date: '',
        appointment_time: '',
        reason: ''
      },
      selectedDepartment: '',
      departments: [],
      doctors: [],
      doctorAvailability: [],
      loadingAvailability: false,
      selectedSlot: null,
      loading: false,
      error: null,
      successMessage: '',
      availableTimes: [
        '09:00', '09:30', '10:00', '10:30', '11:00', '11:30',
        '14:00', '14:30', '15:00', '15:30', '16:00', '16:30'
      ],
      // Modal Data
      showDoctorModal: false,
      doctorDetails: null,
      loadingDoctorDetails: false
    }
  },
  computed: {
    ...mapState('hospital', ['dashboard']),
    minDate() {
      const today = new Date()
      return today.toISOString().split('T')[0]
    },
    filteredDoctors() {
      return this.doctors.filter(doctor => 
        doctor.department?.id === this.selectedDepartment && doctor.is_active
      )
    },
    filteredAvailableTimes() {
      if (!this.selectedSlot) return [];
      const start = this.selectedSlot.start_time;
      const end = this.selectedSlot.end_time;
      // Only include times between start and end
      return this.availableTimes.filter(time => time >= start && time <= end);
    }
  },
  methods: {
    ...mapActions('hospital', ['createAppointment']),
    
    async loadDepartments() {
      try {
        const response = await axios.get('/departments')
        this.departments = response.data
      } catch (error) {
        console.error('Error loading departments:', error)
        this.error = 'Failed to load departments'
      }
    },
    
    async loadDoctors() {
      if (!this.selectedDepartment) {
        this.doctors = []
        return
      }
      
      try {
        const response = await axios.get('/doctors', {
          params: { department_id: this.selectedDepartment }
        })
        this.doctors = response.data
        this.form.doctor_id = '' // Reset doctor selection
        this.doctorAvailability = [] // Reset availability
        this.selectedSlot = null
      } catch (error) {
        console.error('Error loading doctors:', error)
        this.error = 'Failed to load doctors'
      }
    },
    
    formatTime(time) {
      if (!time) return ''
      const [hours, minutes] = time.split(':')
      const hour12 = hours % 12 || 12
      const ampm = hours >= 12 ? 'PM' : 'AM'
      return `${hour12}:${minutes} ${ampm}`
    },
    
    async bookAppointment() {
      try {
        this.loading = true
        this.error = null
        this.successMessage = ''
        
        await this.createAppointment(this.form)
        
        this.successMessage = 'Appointment booked successfully!'
        this.form = {
          doctor_id: '',
          appointment_date: '',
          appointment_time: '',
          reason: ''
        }
        this.selectedDepartment = ''
        this.doctorAvailability = []
        this.selectedSlot = null
        
        // Redirect to appointments after 2 seconds
        setTimeout(() => {
          this.$router.push('/my-appointments')
        }, 2000)
        
      } catch (error) {
        console.error('Booking error:', error)
        this.error = error.response?.data?.message || error.message || 'Failed to book appointment'
      } finally {
        this.loading = false
      }
    },

    async loadDoctorAvailability() {
      if (!this.form.doctor_id) {
        this.doctorAvailability = []
        this.selectedSlot = null
        return
      }

      this.loadingAvailability = true
      this.error = null
      
      try {
        const today = new Date()
        const endDate = new Date(today)
        endDate.setDate(endDate.getDate() + 30)
        
        const response = await axios.get(`/doctors/${this.form.doctor_id}/availability`, {
          params: {
            start_date: today.toISOString().split('T')[0],
            end_date: endDate.toISOString().split('T')[0]
          }
        })
        
        let slots = []
        if (response.data.available_slots) {
          slots = response.data.available_slots
        } else if (Array.isArray(response.data)) {
          slots = response.data
        }
        
        this.doctorAvailability = slots.map(slot => ({
          ...slot,
          date: slot.date || slot.available_date,
          available_appointments: slot.available_appointments !== undefined 
            ? slot.available_appointments 
            : slot.max_appointments
        }))
        
        this.selectedSlot = null
        this.form.appointment_date = ''
        this.form.appointment_time = ''
        
      } catch (error) {
        console.error('Error loading doctor availability:', error)
        this.error = 'Failed to load doctor availability. Please try again.'
        this.doctorAvailability = []
      } finally {
        this.loadingAvailability = false
      }
    },

    selectAvailabilitySlot(slot) {
      this.selectedSlot = slot
      this.form.appointment_date = slot.date || slot.available_date
      this.form.appointment_time = slot.start_time
    },

    isSlotSelected(slot) {
      return this.selectedSlot && this.selectedSlot.id === slot.id
    },

    formatDate(dateStr) {
      if (!dateStr) return 'Invalid Date'
      try {
        const date = new Date(dateStr.includes('T') ? dateStr : dateStr + 'T00:00:00')
        if (isNaN(date.getTime())) return 'Invalid Date'
        return date.toLocaleDateString('en-US', {
          weekday: 'short',
          month: 'short',
          day: 'numeric'
        })
      } catch (error) {
        console.error('Error formatting date:', error)
        return 'Invalid Date'
      }
    },

    // --- MODAL LOGIC ---
    async showDoctorDetails() {
      if (!this.form.doctor_id) return
      
      this.showDoctorModal = true
      this.loadingDoctorDetails = true
      this.doctorDetails = null
      
      try {
        const response = await axios.get(`/doctors/${this.form.doctor_id}`)
        this.doctorDetails = response.data
      } catch (error) {
        console.error('Error loading doctor details:', error)
      } finally {
        this.loadingDoctorDetails = false
      }
    },
    
    closeDoctorModal() {
      this.showDoctorModal = false
      this.doctorDetails = null
    }
  },
  async created() {
    await this.loadDepartments()
  }
}
</script>

<style scoped>
.card {
  border-radius: 15px;
  border: none;
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.form-control:focus,
.form-select:focus {
  border-color: #0d6efd;
  box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25);
}

.btn {
  border-radius: 8px;
  padding: 10px 20px;
}

.availability-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
  margin-top: 12px;
}

.availability-slot {
  border: 2px solid #e9ecef;
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: #f8f9fa;
}

.availability-slot:hover {
  border-color: #0d6efd;
  background: #e7f1ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.availability-slot.selected {
  border-color: #0d6efd;
  background: #0d6efd;
  color: white;
}

.availability-slot .slot-date {
  font-weight: 600;
  font-size: 0.9rem;
  margin-bottom: 4px;
}

.availability-slot .slot-time {
  font-size: 0.85rem;
  margin-bottom: 6px;
}

.availability-slot .slot-availability {
  font-size: 0.75rem;
}

.text-white-50 {
  color: rgba(255, 255, 255, 0.8) !important;
}

/* --- MODAL STYLES --- */
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1055;
}

.modal-dialog {
  width: 100%;
  max-width: 500px;
  margin: 1.75rem auto;
}

.modal-content {
  border-radius: 1rem;
  overflow: hidden;
  background-color: white;
}

.detail-item {
  background-color: #f8f9fa;
  padding: 1rem;
  border-radius: 0.75rem;
  height: 100%;
  border: 1px solid #e9ecef;
}

.detail-item label {
  display: block;
  font-size: 0.75rem;
  text-transform: uppercase;
  color: #6c757d;
  font-weight: 700;
  margin-bottom: 0.25rem;
}

.detail-item .value {
  font-size: 1rem;
  color: #212529;
}
</style>