<template>
  <div class="container-fluid py-4">
    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;"></div>
      <p class="mt-3 text-muted">Loading dashboard...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger">
      <i class="bi bi-exclamation-triangle"></i>
      {{ error }}
    </div>

    <!-- Dashboard Content -->
    <div v-else-if="dashboard">
      <!-- Header -->
      <div class="row mb-4">
        <div class="col">
          <h1 class="h2 mb-1">
            Welcome, {{ getWelcomeName() }}
          </h1>
          <p class="text-muted">{{ getRoleDescription() }}</p>
        </div>
      </div>

      <!-- Admin Dashboard -->
      <div v-if="dashboard.role === 'admin'">
        <!-- Stats Cards -->
        <div class="row mb-4">
          <div class="col-md-3 mb-3">
            <div class="card bg-primary text-white">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                  <div>
                    <h3 class="mb-0">{{ dashboard.stats.total_doctors }}</h3>
                    <p class="mb-0">Total Doctors</p>
                  </div>
                  <i class="bi bi-person-badge" style="font-size: 2rem;"></i>
                </div>
              </div>
            </div>
          </div>
          <div class="col-md-3 mb-3">
            <div class="card bg-success text-white">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                  <div>
                    <h3 class="mb-0">{{ dashboard.stats.total_patients }}</h3>
                    <p class="mb-0">Total Patients</p>
                  </div>
                  <i class="bi bi-people" style="font-size: 2rem;"></i>
                </div>
              </div>
            </div>
          </div>
          <div class="col-md-3 mb-3">
            <div class="card bg-info text-white">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                  <div>
                    <h3 class="mb-0">{{ dashboard.stats.total_appointments }}</h3>
                    <p class="mb-0">Total Appointments</p>
                  </div>
                  <i class="bi bi-calendar-check" style="font-size: 2rem;"></i>
                </div>
              </div>
            </div>
          </div>
          <div class="col-md-3 mb-3">
            <div class="card bg-warning text-white">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                  <div>
                    <h3 class="mb-0">{{ dashboard.stats.departments }}</h3>
                    <p class="mb-0">Departments</p>
                  </div>
                  <i class="bi bi-building" style="font-size: 2rem;"></i>
                </div>
              </div>
            </div>
          </div>
        </div>
        <!-- Recent Appointments -->
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Recent Appointments</h5>
            <router-link to="/appointments" class="btn btn-sm btn-outline-primary">
              View All
            </router-link>
          </div>
          <div class="card-body">
            <div v-if="dashboard.recent_appointments.length === 0" class="text-center text-muted py-3">
              No recent appointments
            </div>
            <div v-else class="table-responsive">
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th>Patient</th>
                    <th>Doctor</th>
                    <th>Date & Time</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="appointment in dashboard.recent_appointments" :key="appointment.id">
                    <td>{{ getPatientName(appointment) }}</td>
                    <td>{{ getDoctorName(appointment) }}</td>
                    <td>{{ formatDateTime(appointment) }}</td>
                    <td>
                      <span :class="getStatusBadgeClass(appointment.status)">
                        {{ appointment.status }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- Doctor Dashboard -->
      <div v-else-if="dashboard.role === 'doctor'">
        <!-- Stats Cards -->
        <div class="row mb-4">
          <div class="col-md-4 mb-3">
            <div class="card bg-primary text-white">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                  <div>
                    <h3 class="mb-0">{{ dashboard.stats.today_appointments }}</h3>
                    <p class="mb-0">Today's Appointments</p>
                  </div>
                  <i class="bi bi-calendar-day" style="font-size: 2rem;"></i>
                </div>
              </div>
            </div>
          </div>
          
          <div class="col-md-4 mb-3">
            <div class="card bg-success text-white">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                  <div>
                    <h3 class="mb-0">{{ dashboard.stats.total_patients }}</h3>
                    <p class="mb-0">Total Patients</p>
                  </div>
                  <i class="bi bi-people" style="font-size: 2rem;"></i>
                </div>
              </div>
            </div>
          </div>
          
          <div class="col-md-4 mb-3">
            <div class="card bg-info text-white">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                  <div>
                    <h3 class="mb-0">{{ dashboard.stats.completed_treatments }}</h3>
                    <p class="mb-0">Completed Treatments</p>
                  </div>
                  <i class="bi bi-check-circle" style="font-size: 2rem;"></i>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Upcoming Appointments -->
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Upcoming Appointments</h5>
            <router-link to="/my-appointments" class="btn btn-sm btn-outline-primary">
              View All
            </router-link>
          </div>
          <div class="card-body">
            <div v-if="dashboard.upcoming_appointments.length === 0" class="text-center text-muted py-3">
              No upcoming appointments
            </div>
            <div v-else class="table-responsive">
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th>Patient</th>
                    <th>Date & Time</th>
                    <th>Reason</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="appointment in dashboard.upcoming_appointments" :key="appointment.id">
                    <td>{{ getPatientName(appointment) }}</td>
                    <td>{{ formatDateTime(appointment) }}</td>
                    <td>{{ appointment.reason || 'General consultation' }}</td>
                    <td>
                      <router-link 
                        :to="`/treatment/${appointment.id}`" 
                        class="btn btn-sm btn-outline-primary"
                      >
                        View
                      </router-link>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- Patient Dashboard -->
      <div v-else-if="dashboard.role === 'patient'">
        <!-- Departments & Doctors Section -->
        <div class="card mb-4">
          <div class="card-header">
            <h5 class="mb-0">Available Departments & Doctors</h5>
          </div>
          <div class="card-body">
            <div v-if="departmentsLoading" class="text-center py-3">
              <div class="spinner-border text-primary"></div>
              <p class="mt-2 text-muted">Loading departments...</p>
            </div>
            <div v-else-if="departmentsError" class="alert alert-danger">
              {{ departmentsError }}
            </div>
            <div v-else>
              <div class="table-responsive">
                <table class="table table-bordered table-sm align-middle">
                  <thead class="table-light">
                    <tr>
                      <th>Department</th>
                      <th>Description</th>
                      <th>Doctors</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="dept in departments" :key="dept.id">
                      <td class="fw-bold">{{ dept.name }}</td>
                      <td class="text-muted">{{ dept.description }}</td>
                      <td>
                        <span v-if="dept.doctors.length === 0" class="text-muted">No doctors</span>
                        <span v-else>
                          <span v-for="(doc, idx) in dept.doctors" :key="doc.id">
                            Dr. {{ doc.user?.username || 'Unknown' }}<span v-if="doc.specialization"> ({{ doc.specialization }})</span><span v-if="doc.experience_years">, {{ doc.experience_years }} yrs</span><span v-if="idx < dept.doctors.length - 1">; </span>
                          </span>
                        </span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
        <!-- Stats Cards -->
        <div class="row mb-4">
          <div class="col-md-4 mb-3">
            <div class="card bg-primary text-white">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                  <div>
                    <h3 class="mb-0">{{ dashboard.stats.total_appointments }}</h3>
                    <p class="mb-0">Total Appointments</p>
                  </div>
                  <i class="bi bi-calendar-check" style="font-size: 2rem;"></i>
                </div>
              </div>
            </div>
          </div>
          
          <div class="col-md-4 mb-3">
            <div class="card bg-warning text-white">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                  <div>
                    <h3 class="mb-0">{{ dashboard.stats.upcoming_appointments }}</h3>
                    <p class="mb-0">Upcoming Appointments</p>
                  </div>
                  <i class="bi bi-clock" style="font-size: 2rem;"></i>
                </div>
              </div>
            </div>
          </div>
          
          <div class="col-md-4 mb-3">
            <div class="card bg-success text-white">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                  <div>
                    <h3 class="mb-0">{{ dashboard.stats.completed_treatments }}</h3>
                    <p class="mb-0">Completed Treatments</p>
                  </div>
                  <i class="bi bi-clipboard-check" style="font-size: 2rem;"></i>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="row mb-4">
          <div class="col-md-6 mb-3">
            <div class="card h-100">
              <div class="card-body text-center">
                <i class="bi bi-calendar-plus text-primary" style="font-size: 3rem;"></i>
                <h5 class="mt-3">Book New Appointment</h5>
                <p class="text-muted">Schedule a consultation with a doctor</p>
                <router-link to="/book-appointment" class="btn btn-primary">
                  Book Now
                </router-link>
              </div>
            </div>
          </div>
          
          <div class="col-md-6 mb-3">
            <div class="card h-100">
              <div class="card-body text-center">
                <i class="bi bi-clipboard-data text-success" style="font-size: 3rem;"></i>
                <h5 class="mt-3">View Treatment History</h5>
                <p class="text-muted">Access your medical records and treatments</p>
                <router-link to="/treatment-history" class="btn btn-success">
                  View History
                </router-link>
              </div>
            </div>
          </div>
        </div>

        <!-- Upcoming Appointments -->
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Upcoming Appointments</h5>
            <router-link to="/my-appointments" class="btn btn-sm btn-outline-primary">
              View All
            </router-link>
          </div>
          <div class="card-body">
            <div v-if="dashboard.upcoming_appointments.length === 0" class="text-center text-muted py-3">
              <i class="bi bi-calendar-x" style="font-size: 3rem;"></i>
              <p class="mt-2">No upcoming appointments</p>
              <router-link to="/book-appointment" class="btn btn-primary">
                Book Your First Appointment
              </router-link>
            </div>
            <div v-else class="table-responsive">
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th>Doctor</th>
                    <th>Department</th>
                    <th>Date & Time</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="appointment in dashboard.upcoming_appointments" :key="appointment.id">
                    <td>{{ getDoctorName(appointment) }}</td>
                    <td>{{ appointment.doctor?.department?.name || 'N/A' }}</td>
                    <td>{{ formatDateTime(appointment) }}</td>
                    <td>
                      <button
                        class="btn btn-outline-danger btn-sm"
                        @click="deleteAppointment(appointment.id)"
                        title="Delete Appointment"
                      >
                        <i class="bi bi-trash"></i> Delete
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
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
  name: 'DashboardView',
  data() {
    return {
      departments: [],
      departmentsLoading: false,
      departmentsError: '',
    }
  },
  computed: {
    ...mapState('hospital', ['dashboard', 'loading', 'error']),
    ...mapState('auth', ['user'])
  },
  methods: {
    ...mapActions('hospital', ['fetchDashboard']),
    async fetchDepartments() {
      this.departmentsLoading = true;
      this.departmentsError = '';
      try {
  const res = await axios.get('patient_dashboard_departments');
        this.departments = res.data;
      } catch (err) {
        this.departmentsError = err.response?.data?.error || 'Failed to load departments.';
      } finally {
        this.departmentsLoading = false;
      }
    },
    
    getWelcomeName() {
      if (this.dashboard?.role === 'admin') {
        return 'Administrator'
      } else if (this.dashboard?.doctor) {
        return `Dr. ${this.dashboard.doctor.user.username}`
      } else if (this.dashboard?.patient) {
        const patient = this.dashboard.patient
        return patient.first_name ? `${patient.first_name} ${patient.last_name || ''}`.trim() : patient.user.username
      }
      return this.user?.username || 'User'
    },
    
    getRoleDescription() {
      if (this.dashboard?.role === 'admin') {
        return 'Hospital Management Dashboard'
      } else if (this.dashboard?.role === 'doctor') {
        return 'Doctor Dashboard - Manage your appointments and patients'
      } else if (this.dashboard?.role === 'patient') {
        return 'Patient Dashboard - Manage your health appointments'
      }
      return ''
    },
    
    getPatientName(appointment) {
      const patient = appointment.patient
      if (!patient) return 'N/A'
      return patient.first_name ? `${patient.first_name} ${patient.last_name || ''}`.trim() : patient.user?.username || 'N/A'
    },
    
    getDoctorName(appointment) {
      const doctor = appointment.doctor
      if (!doctor) return 'N/A'
      return `Dr. ${doctor.user?.username || 'Unknown'}`
    },
    
    formatDateTime(appointment) {
      if (!appointment.appointment_date || !appointment.appointment_time) return 'N/A'
      const date = new Date(appointment.appointment_date + 'T' + appointment.appointment_time)
      return date.toLocaleString()
    },
    
    getStatusBadgeClass(status) {
      const baseClasses = 'badge '
      switch (status) {
        case 'Booked':
          return baseClasses + 'bg-warning'
        case 'Completed':
          return baseClasses + 'bg-success'
        case 'Cancelled':
          return baseClasses + 'bg-danger'
        default:
          return baseClasses + 'bg-secondary'
      }
    },
    
    async deleteAppointment(appointmentId) {
      if (confirm('Are you sure you want to delete this appointment?')) {
        try {
          await axios.delete(`/appointments/${appointmentId}`)
          await this.fetchDashboard()
        } catch (error) {
          alert('Failed to delete appointment: ' + (error.response?.data?.message || error.message))
        }
      }
    }
  },
  async created() {
    await this.fetchDashboard();
    if (this.dashboard?.role === 'patient') {
      await this.fetchDepartments();
    }
  }
}
</script>

<style scoped>
.card {
  border-radius: 15px;
  border: none;
  transition: transform 0.2s ease-in-out;
}

.card:hover {
  transform: translateY(-2px);
}

.card-body h3 {
  font-weight: 700;
}

.table th {
  border-top: none;
  font-weight: 600;
  background-color: #f8f9fa;
}

.btn {
  border-radius: 8px;
}

.text-primary {
  color: #0d6efd !important;
}

.text-success {
  color: #198754 !important;
}

.text-muted {
  color: #6c757d !important;
}
</style>
