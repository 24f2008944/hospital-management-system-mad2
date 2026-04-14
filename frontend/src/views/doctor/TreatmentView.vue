<template>
  <div class="container-fluid py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Treatment Records</h2>
      <div class="d-flex gap-3">
        <div class="position-relative">
          <input 
            type="text" 
            v-model="searchQuery" 
            class="form-control" 
            placeholder="Search by patient name or diagnosis..."
            style="padding-left: 40px; width: 300px;"
          >
          <i class="bi bi-search position-absolute" style="left: 15px; top: 50%; transform: translateY(-50%);"></i>
        </div>
        <select v-model="sortBy" class="form-select" style="width: 200px;">
          <option value="date_desc">Newest First</option>
          <option value="date_asc">Oldest First</option>
          <option value="patient_name">Patient Name</option>
        </select>
      </div>
    </div>

    <!-- Treatment Records -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary"></div>
      <p class="mt-3">Loading treatment records...</p>
    </div>
    
    <div v-else-if="filteredTreatments.length === 0" class="text-center py-5">
      <i class="bi bi-clipboard-data" style="font-size: 3rem; color: #6c757d;"></i>
      <p class="mt-3 text-muted">No treatment records found</p>
    </div>
    
    <div v-else class="row">
      <div v-for="treatment in filteredTreatments" :key="treatment.id" class="col-12 mb-4">
        <div class="card">
          <div class="card-body">
            <div class="row">
              <div class="col-md-8">
                <div class="d-flex justify-content-between align-items-start mb-3">
                  <div>
                    <h5 class="card-title mb-1">{{ treatment.diagnosis }}</h5>
                    <p class="text-muted mb-0">
                      <i class="bi bi-person me-2"></i>{{ treatment.patient_name }}
                      <span class="mx-2">•</span>
                      <i class="bi bi-calendar me-2"></i>{{ formatDateTime(treatment.created_at) }}
                    </p>
                  </div>
                  <div class="text-end">
                    <span class="badge bg-info">Treatment #{{ treatment.id }}</span>
                  </div>
                </div>
                
                <div class="mb-3">
                  <h6 class="fw-bold mb-2">Prescription</h6>
                  <p class="mb-0">{{ treatment.prescription || 'No prescription provided' }}</p>
                </div>
                
                <div v-if="treatment.notes" class="mb-3">
                  <h6 class="fw-bold mb-2">Treatment Notes</h6>
                  <p class="mb-0">{{ treatment.notes }}</p>
                </div>
              </div>
              
              <div class="col-md-4">
                <div class="bg-light rounded p-3 h-100">
                  <h6 class="fw-bold mb-3">Patient Information</h6>
                  <p class="mb-2">
                    <i class="bi bi-envelope text-muted me-2"></i>
                    {{ treatment.patient_email }}
                  </p>
                  <p class="mb-2">
                    <i class="bi bi-telephone text-muted me-2"></i>
                    {{ treatment.patient_phone || 'N/A' }}
                  </p>
                  <p class="mb-2">
                    <i class="bi bi-calendar text-muted me-2"></i>
                    Age: {{ calculateAge(treatment.patient_dob) }}
                  </p>
                  <p class="mb-0">
                    <i class="bi bi-gender-ambiguous text-muted me-2"></i>
                    {{ treatment.patient_gender || 'N/A' }}
                  </p>
                  
                  <div class="mt-3">
                    <button 
                      class="btn btn-outline-primary btn-sm"
                      @click="viewTreatment(treatment)"
                    >
                      <i class="bi bi-eye me-1"></i>
                      View Details
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- View Treatment Modal -->
    <div class="modal fade" :class="{ show: showViewModal }" 
         :style="{ display: showViewModal ? 'block' : 'none' }"
         tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Treatment Details</h5>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>
          <div class="modal-body" v-if="selectedTreatment">
            <div class="row">
              <div class="col-md-6">
                <h6 class="fw-bold mb-3">Patient Information</h6>
                <p><strong>Name:</strong> {{ selectedTreatment.patient_name }}</p>
                <p><strong>Email:</strong> {{ selectedTreatment.patient_email }}</p>
                <p><strong>Phone:</strong> {{ selectedTreatment.patient_phone || 'N/A' }}</p>
                <p><strong>Date of Birth:</strong> {{ formatDate(selectedTreatment.patient_dob) }}</p>
                <p><strong>Age:</strong> {{ calculateAge(selectedTreatment.patient_dob) }}</p>
                <p><strong>Gender:</strong> {{ selectedTreatment.patient_gender || 'N/A' }}</p>
              </div>
              <div class="col-md-6">
                <h6 class="fw-bold mb-3">Treatment Information</h6>
                <p><strong>Treatment ID:</strong> #{{ selectedTreatment.id }}</p>
                <p><strong>Date:</strong> {{ formatDateTime(selectedTreatment.created_at) }}</p>
                <p><strong>Appointment ID:</strong> #{{ selectedTreatment.appointment_id }}</p>
                <p><strong>Doctor:</strong> Dr. {{ selectedTreatment.doctor_name }}</p>
                <p><strong>Department:</strong> {{ selectedTreatment.department_name }}</p>
              </div>
            </div>
            
            <hr>
            
            <div class="row">
              <div class="col-12">
                <h6 class="fw-bold mb-3">Diagnosis</h6>
                <div class="bg-light rounded p-3 mb-4">
                  <p class="mb-0">{{ selectedTreatment.diagnosis }}</p>
                </div>
                
                <h6 class="fw-bold mb-3">Prescription</h6>
                <div class="bg-light rounded p-3 mb-4">
                  <p class="mb-0">{{ selectedTreatment.prescription || 'No prescription provided' }}</p>
                </div>
                
                <h6 class="fw-bold mb-3">Treatment Notes</h6>
                <div class="bg-light rounded p-3">
                  <p class="mb-0">{{ selectedTreatment.notes || 'No additional notes' }}</p>
                </div>
              </div>
            </div>
            
            <hr>
            
            <div v-if="selectedTreatment.patient_medical_history">
              <h6 class="fw-bold mb-3">Patient Medical History</h6>
              <div class="bg-warning bg-opacity-10 rounded p-3">
                <p class="mb-0">{{ selectedTreatment.patient_medical_history }}</p>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeModal">Close</button>
            <button type="button" class="btn btn-primary" @click="printTreatment">
              <i class="bi bi-printer me-1"></i>
              Print Report
            </button>
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
  name: 'DoctorTreatmentView',
  data() {
    return {
      treatments: [],
      loading: false,
      searchQuery: '',
      sortBy: 'date_desc',
      showViewModal: false,
      selectedTreatment: null
    }
  },
  computed: {
    filteredTreatments() {
      let filtered = this.treatments
      
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        filtered = filtered.filter(treatment =>
          treatment.patient_name.toLowerCase().includes(query) ||
          treatment.diagnosis.toLowerCase().includes(query) ||
          treatment.prescription?.toLowerCase().includes(query)
        )
      }
      
      // Sort treatments
      filtered.sort((a, b) => {
        switch (this.sortBy) {
          case 'date_asc':
            return new Date(a.created_at) - new Date(b.created_at)
          case 'date_desc':
            return new Date(b.created_at) - new Date(a.created_at)
          case 'patient_name':
            return a.patient_name.localeCompare(b.patient_name)
          default:
            return 0
        }
      })
      
      return filtered
    }
  },
  methods: {
    async loadTreatments() {
      try {
        this.loading = true
        const response = await axios.get('/doctor/treatments')
        this.treatments = response.data
      } catch (error) {
        console.error('Failed to load treatments:', error)
      } finally {
        this.loading = false
      }
    },
    
    viewTreatment(treatment) {
      this.selectedTreatment = treatment
      this.showViewModal = true
    },
    
    printTreatment() {
      if (!this.selectedTreatment) return
      
      const printContent = `
        <div style="padding: 20px; font-family: Arial, sans-serif;">
          <h1 style="text-align: center; color: #0d6efd;">Treatment Report</h1>
          <hr>
          
          <div style="margin-bottom: 20px;">
            <h3>Patient Information</h3>
            <p><strong>Name:</strong> ${this.selectedTreatment.patient_name}</p>
            <p><strong>Email:</strong> ${this.selectedTreatment.patient_email}</p>
            <p><strong>Phone:</strong> ${this.selectedTreatment.patient_phone || 'N/A'}</p>
            <p><strong>Age:</strong> ${this.calculateAge(this.selectedTreatment.patient_dob)}</p>
            <p><strong>Gender:</strong> ${this.selectedTreatment.patient_gender || 'N/A'}</p>
          </div>
          
          <div style="margin-bottom: 20px;">
            <h3>Treatment Information</h3>
            <p><strong>Treatment ID:</strong> #${this.selectedTreatment.id}</p>
            <p><strong>Date:</strong> ${this.formatDateTime(this.selectedTreatment.created_at)}</p>
            <p><strong>Doctor:</strong> Dr. ${this.selectedTreatment.doctor_name}</p>
            <p><strong>Department:</strong> ${this.selectedTreatment.department_name}</p>
          </div>
          
          <div style="margin-bottom: 20px;">
            <h3>Diagnosis</h3>
            <p>${this.selectedTreatment.diagnosis}</p>
          </div>
          
          <div style="margin-bottom: 20px;">
            <h3>Prescription</h3>
            <p>${this.selectedTreatment.prescription || 'No prescription provided'}</p>
          </div>
          
          <div style="margin-bottom: 20px;">
            <h3>Treatment Notes</h3>
            <p>${this.selectedTreatment.notes || 'No additional notes'}</p>
          </div>
        </div>
      `
      
      const printWindow = window.open('', '_blank')
      printWindow.document.write(printContent)
      printWindow.document.close()
      printWindow.print()
    },
    
    calculateAge(dateOfBirth) {
      if (!dateOfBirth) return 'N/A'
      const today = new Date()
      const birthDate = new Date(dateOfBirth)
      let age = today.getFullYear() - birthDate.getFullYear()
      const monthDiff = today.getMonth() - birthDate.getMonth()
      
      if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
        age--
      }
      
      return age
    },
    
    formatDate(dateString) {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString()
    },
    
    formatDateTime(dateTimeString) {
      if (!dateTimeString) return 'N/A'
      return new Date(dateTimeString).toLocaleString()
    },
    
    closeModal() {
      this.showViewModal = false
      this.selectedTreatment = null
    }
  },
  
  async created() {
    await this.loadTreatments()
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

.btn {
  border-radius: 8px;
}

.bg-light {
  background-color: #f8f9fa !important;
}

.bg-warning.bg-opacity-10 {
  background-color: rgba(255, 193, 7, 0.1) !important;
}
</style>
