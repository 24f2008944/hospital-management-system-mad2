<template>
  <div class="container-fluid py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Blacklisted Doctors</h2>
      <router-link to="/doctors" class="btn btn-secondary">
        <i class="bi bi-arrow-left"></i>
        Back to Doctors
      </router-link>
    </div>

    <!-- Blacklisted Doctors Table -->
    <div class="card">
      <div class="card-body">
        <div v-if="loading" class="text-center py-3">
          <div class="spinner-border text-primary"></div>
        </div>
        
        <div v-else-if="doctors.length === 0" class="text-center py-5">
          <i class="bi bi-check-circle" style="font-size: 3rem; color: #28a745;"></i>
          <p class="mt-3 text-muted">No blacklisted doctors</p>
        </div>
        
        <div v-else class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Department</th>
                <th>Specialization</th>
                <th>Blacklist Reason</th>
                <th>Blacklist Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="doctor in doctors" :key="doctor.id" class="table-danger">
                <td>{{ doctor.user.username }}</td>
                <td>{{ doctor.user.email }}</td>
                <td>{{ doctor.department?.name || 'N/A' }}</td>
                <td>{{ doctor.specialization || 'N/A' }}</td>
                <td>
                  <span v-if="doctor.blacklist_reason" :title="doctor.blacklist_reason" class="text-truncate d-inline-block" style="max-width: 200px;">
                    {{ doctor.blacklist_reason }}
                  </span>
                  <span v-else class="text-muted">-</span>
                </td>
                <td>{{ formatDate(doctor.blacklist_date) }}</td>
                <td>
                  <button class="btn btn-sm btn-success" @click="unblockDoctor(doctor.id)" title="Unblock Doctor">
                    <i class="bi bi-check-circle"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'BlacklistedDoctorsView',
  data() {
    return {
      doctors: [],
      loading: false
    }
  },
  methods: {
    async loadBlacklistedDoctors() {
      try {
        this.loading = true
        const response = await axios.get('/blacklisted-doctors')
        this.doctors = response.data
      } catch (error) {
        console.error('Failed to load blacklisted doctors:', error)
        alert('Failed to load blacklisted doctors')
      } finally {
        this.loading = false
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return '-'
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    
    async unblockDoctor(doctorId) {
      if (!confirm('Are you sure you want to unblock this doctor?')) return
      try {
        this.loading = true
        await axios.put(`/doctors/${doctorId}/unblock`)
        alert('✅ Doctor unblocked successfully')
        await this.loadBlacklistedDoctors()
      } catch (error) {
        console.error('Failed to unblock doctor:', error)
        alert('❌ Failed to unblock doctor: ' + (error.response?.data?.message || error.message))
      } finally {
        this.loading = false
      }
    }
  },
  
  async created() {
    await this.loadBlacklistedDoctors()
  }
}
</script>

<style scoped>
.card {
  border: 1px solid #dee2e6;
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

.btn {
  border-radius: 0;
}

.table-danger {
  background-color: #f8d7da !important;
}

.text-truncate {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
