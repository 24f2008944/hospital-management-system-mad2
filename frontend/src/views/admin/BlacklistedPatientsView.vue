<template>
  <div class="container-fluid py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Blacklisted Patients</h2>
      <router-link to="/patients" class="btn btn-secondary">
        <i class="bi bi-arrow-left"></i>
        Back to Patients
      </router-link>
    </div>

    <!-- Blacklisted Patients Table -->
    <div class="card">
      <div class="card-body">
        <div v-if="loading" class="text-center py-3">
          <div class="spinner-border text-primary"></div>
        </div>
        
        <div v-else-if="patients.length === 0" class="text-center py-5">
          <i class="bi bi-check-circle" style="font-size: 3rem; color: #28a745;"></i>
          <p class="mt-3 text-muted">No blacklisted patients</p>
        </div>
        
        <div v-else class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Contact</th>
                <th>Blood Group</th>
                <th>Blacklist Reason</th>
                <th>Blacklist Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="patient in patients" :key="patient.id" class="table-danger">
                <td>{{ patient.full_name || patient.user.username }}</td>
                <td>{{ patient.user.email }}</td>
                <td>{{ patient.contact_number || 'N/A' }}</td>
                <td>{{ patient.blood_group || 'N/A' }}</td>
                <td>
                  <span v-if="patient.blacklist_reason" :title="patient.blacklist_reason" class="text-truncate d-inline-block" style="max-width: 200px;">
                    {{ patient.blacklist_reason }}
                  </span>
                  <span v-else class="text-muted">-</span>
                </td>
                <td>{{ formatDate(patient.blacklist_date) }}</td>
                <td>
                  <button class="btn btn-sm btn-success" @click="unblockPatient(patient.id)" title="Unblock Patient">
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
  name: 'BlacklistedPatientsView',
  data() {
    return {
      patients: [],
      loading: false
    }
  },
  methods: {
    async loadBlacklistedPatients() {
      try {
        this.loading = true
        const response = await axios.get('/blacklisted-patients')
        this.patients = response.data
      } catch (error) {
        console.error('Failed to load blacklisted patients:', error)
        alert('Failed to load blacklisted patients')
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
    
    async unblockPatient(patientId) {
      if (!confirm('Are you sure you want to unblock this patient?')) return
      try {
        this.loading = true
        await axios.put(`/patients/${patientId}/unblock`)
        alert('✅ Patient unblocked successfully')
        await this.loadBlacklistedPatients()
      } catch (error) {
        console.error('Failed to unblock patient:', error)
        alert('❌ Failed to unblock patient: ' + (error.response?.data?.message || error.message))
      } finally {
        this.loading = false
      }
    }
  },
  
  async created() {
    await this.loadBlacklistedPatients()
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
