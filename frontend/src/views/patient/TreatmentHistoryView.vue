<template>
  <div class="container-fluid py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>My Treatment History</h2>
      <div class="d-flex gap-3">
        <div class="position-relative">
          <input 
            type="text" 
            v-model="searchQuery" 
            class="form-control" 
            placeholder="Search by diagnosis or doctor..."
            style="padding-left: 40px; width: 300px;"
          >
          <i class="bi bi-search position-absolute" style="left: 15px; top: 50%; transform: translateY(-50%);"></i>
        </div>
        <select v-model="sortBy" class="form-select" style="width: 200px;">
          <option value="date_desc">Newest First</option>
          <option value="date_asc">Oldest First</option>
          <option value="doctor_name">Doctor Name</option>
        </select>
      </div>
    </div>

    <!-- Treatment History -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary"></div>
      <p class="mt-3">Loading treatment history...</p>
    </div>
    
    <div v-else-if="filteredTreatments.length === 0" class="text-center py-5">
      <i class="bi bi-clipboard-data" style="font-size: 3rem; color: #6c757d;"></i>
      <p class="mt-3 text-muted">No treatment records found</p>
      <router-link to="/patient/appointments" class="btn btn-primary">
        <i class="bi bi-calendar me-2"></i>
        View My Appointments
      </router-link>
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
                      <i class="bi bi-person-badge me-2"></i>Dr. {{ treatment.doctor_name }}
                      <span class="mx-2">•</span>
                      <i class="bi bi-building me-2"></i>{{ treatment.department_name }}
                      <span class="mx-2">•</span>
                      <i class="bi bi-calendar me-2"></i>{{ formatDate(treatment.created_at) }}
                    </p>
                  </div>
                  <div class="text-end">
                    <span class="badge bg-success">Treatment #{{ treatment.id }}</span>
                  </div>
                </div>
                
                <div class="mb-3">
                  <h6 class="fw-bold mb-2">
                    <i class="bi bi-prescription2 me-2"></i>Prescription
                  </h6>
                  <div class="bg-light rounded p-3">
                    <p class="mb-0">{{ treatment.prescription || 'No prescription provided' }}</p>
                  </div>
                </div>
                
                <div v-if="treatment.notes" class="mb-3">
                  <h6 class="fw-bold mb-2">
                    <i class="bi bi-chat-text me-2"></i>Doctor's Notes
                  </h6>
                  <div class="bg-light rounded p-3">
                    <p class="mb-0">{{ treatment.notes }}</p>
                  </div>
                </div>
              </div>
              
              <div class="col-md-4">
                <div class="border rounded p-3 h-100">
                  <h6 class="fw-bold mb-3">Treatment Details</h6>
                  <p class="mb-2">
                    <i class="bi bi-calendar3 text-muted me-2"></i>
                    <strong>Date:</strong> {{ formatDateTime(treatment.created_at) }}
                  </p>
                  <p class="mb-2">
                    <i class="bi bi-hospital text-muted me-2"></i>
                    <strong>Department:</strong> {{ treatment.department_name }}
                  </p>
                  <p class="mb-2">
                    <i class="bi bi-person-check text-muted me-2"></i>
                    <strong>Doctor:</strong> Dr. {{ treatment.doctor_name }}
                  </p>
                  <p class="mb-3">
                    <i class="bi bi-clipboard-check text-muted me-2"></i>
                    <strong>Appointment:</strong> #{{ treatment.appointment_id }}
                  </p>
                  
                  <div class="d-grid gap-2">
                    <button 
                      class="btn btn-outline-primary btn-sm"
                      @click="viewTreatment(treatment)"
                    >
                      <i class="bi bi-eye me-1"></i>
                      View Full Details
                    </button>
                    <button 
                      class="btn btn-outline-secondary btn-sm"
                      @click="downloadReport(treatment)"
                    >
                      <i class="bi bi-filetype-csv me-1"></i>
                      Download CSV Report
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
            <h5 class="modal-title">Treatment Report</h5>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>
          <div class="modal-body" v-if="selectedTreatment">
            <div class="text-center mb-4">
              <h4 class="text-primary">Hospital Management System</h4>
              <p class="text-muted">Treatment Report</p>
            </div>
            
            <div class="row">
              <div class="col-md-6">
                <h6 class="fw-bold mb-3">Patient Information</h6>
                <!-- UPDATED: Fallback to username if name is missing -->
                <p><strong>Name:</strong> {{ $store.state.auth.user.username || $store.state.auth.user.name }}</p>
                <p><strong>Email:</strong> {{ $store.state.auth.user.email }}</p>
                <p><strong>Patient ID:</strong> #{{ $store.state.auth.user.id }}</p>
              </div>
              <div class="col-md-6">
                <h6 class="fw-bold mb-3">Doctor Information</h6>
                <p><strong>Name:</strong> Dr. {{ selectedTreatment.doctor_name }}</p>
                <p><strong>Department:</strong> {{ selectedTreatment.department_name }}</p>
                <p><strong>Specialization:</strong> {{ selectedTreatment.doctor_specialization }}</p>
              </div>
            </div>
            
            <hr>
            
            <div class="row">
              <div class="col-md-6">
                <h6 class="fw-bold mb-3">Treatment Details</h6>
                <p><strong>Treatment ID:</strong> #{{ selectedTreatment.id }}</p>
                <p><strong>Date:</strong> {{ formatDateTime(selectedTreatment.created_at) }}</p>
                <p><strong>Appointment ID:</strong> #{{ selectedTreatment.appointment_id }}</p>
              </div>
              <div class="col-md-6">
                <h6 class="fw-bold mb-3">Appointment Details</h6>
                <p><strong>Date:</strong> {{ formatDate(selectedTreatment.appointment_date) }}</p>
                <p><strong>Time:</strong> {{ formatTime(selectedTreatment.appointment_time) }}</p>
              </div>
            </div>
            
            <hr>
            
            <div class="mb-4">
              <h6 class="fw-bold mb-3">Diagnosis</h6>
              <div class="border rounded p-3 bg-light">
                <p class="mb-0">{{ selectedTreatment.diagnosis }}</p>
              </div>
            </div>
            
            <div class="mb-4">
              <h6 class="fw-bold mb-3">Prescription</h6>
              <div class="border rounded p-3 bg-light">
                <p class="mb-0">{{ selectedTreatment.prescription || 'No prescription provided' }}</p>
              </div>
            </div>
            
            <div v-if="selectedTreatment.notes" class="mb-4">
              <h6 class="fw-bold mb-3">Doctor's Notes</h6>
              <div class="border rounded p-3 bg-light">
                <p class="mb-0">{{ selectedTreatment.notes }}</p>
              </div>
            </div>
            
            <div class="text-center text-muted">
              <small>This report was generated on {{ new Date().toLocaleString() }}</small>
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
  name: 'PatientTreatmentHistoryView',
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
          treatment.diagnosis.toLowerCase().includes(query) ||
          treatment.doctor_name.toLowerCase().includes(query) ||
          treatment.department_name.toLowerCase().includes(query) ||
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
          case 'doctor_name':
            return a.doctor_name.localeCompare(b.doctor_name)
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
        const response = await axios.get('/patient/treatments')
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
    
    // UPDATED: Now generates a CSV file instead of HTML
    downloadReport(treatment) {
      // 1. Prepare Data Headers
      const headers = [
        'Treatment ID',
        'Date/Time',
        'Doctor Name',
        'Department',
        'Diagnosis',
        'Prescription',
        'Doctor Notes',
        'Appointment ID',
        'Appointment Date',
        'Patient Name',
        'Patient ID'
      ];

      // 2. Prepare Data Row (handle commas and quotes in content)
      const escapeCsv = (val) => {
        if (val === null || val === undefined) return '';
        const stringVal = String(val);
        // Wrap in quotes if contains comma, quote, or newline
        if (stringVal.includes(',') || stringVal.includes('"') || stringVal.includes('\n')) {
          return `"${stringVal.replace(/"/g, '""')}"`;
        }
        return stringVal;
      };

      const patientName = this.$store.state.auth.user.username || this.$store.state.auth.user.name || 'N/A';
      const patientId = this.$store.state.auth.user.id;

      const row = [
        treatment.id,
        this.formatDateTime(treatment.created_at),
        `Dr. ${treatment.doctor_name}`,
        treatment.department_name,
        treatment.diagnosis,
        treatment.prescription,
        treatment.notes,
        treatment.appointment_id,
        `${this.formatDate(treatment.appointment_date)} ${this.formatTime(treatment.appointment_time)}`,
        patientName,
        patientId
      ].map(escapeCsv);

      // 3. Construct CSV Content
      const csvContent = [
        headers.join(','),
        row.join(',')
      ].join('\n');

      // 4. Create Blob and Trigger Download
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `Treatment_Report_${treatment.id}.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    },
    
    printTreatment() {
      if (!this.selectedTreatment) return
      
      const printContent = this.generateReportContent(this.selectedTreatment)
      const printWindow = window.open('', '_blank')
      printWindow.document.write(printContent)
      printWindow.document.close()
      printWindow.print()
    },
    
    generateReportContent(treatment) {
      // UPDATED: Use username/name fallback here as well for the print view
      const patientName = this.$store.state.auth.user.username || this.$store.state.auth.user.name || 'N/A';
      
      return `
        <!DOCTYPE html>
        <html>
        <head>
          <title>Treatment Report #${treatment.id}</title>
          <style>
            body { 
              font-family: Arial, sans-serif; 
              padding: 20px; 
              line-height: 1.6;
            }
            .header { 
              text-align: center; 
              border-bottom: 2px solid #0d6efd; 
              padding-bottom: 20px; 
              margin-bottom: 30px; 
            }
            .section { 
              margin-bottom: 25px; 
            }
            .row { 
              display: flex; 
              margin-bottom: 20px; 
            }
            .col { 
              flex: 1; 
              padding-right: 20px; 
            }
            .diagnosis-box, .prescription-box, .notes-box { 
              border: 1px solid #ddd; 
              padding: 15px; 
              background-color: #f8f9fa; 
              border-radius: 5px; 
            }
            .footer { 
              text-align: center; 
              color: #666; 
              margin-top: 40px; 
              font-size: 0.9em; 
            }
          </style>
        </head>
        <body>
          <div class="header">
            <h1 style="color: #0d6efd; margin: 0;">Hospital Management System</h1>
            <h2 style="margin: 10px 0 0 0;">Treatment Report</h2>
          </div>
          
          <div class="row">
            <div class="col">
              <h3>Patient Information</h3>
              <p><strong>Name:</strong> ${patientName}</p>
              <p><strong>Email:</strong> ${this.$store.state.auth.user.email}</p>
              <p><strong>Patient ID:</strong> #${this.$store.state.auth.user.id}</p>
            </div>
            <div class="col">
              <h3>Doctor Information</h3>
              <p><strong>Name:</strong> Dr. ${treatment.doctor_name}</p>
              <p><strong>Department:</strong> ${treatment.department_name}</p>
              <p><strong>Specialization:</strong> ${treatment.doctor_specialization || 'N/A'}</p>
            </div>
          </div>
          
          <div class="row">
            <div class="col">
              <h3>Treatment Details</h3>
              <p><strong>Treatment ID:</strong> #${treatment.id}</p>
              <p><strong>Date:</strong> ${this.formatDateTime(treatment.created_at)}</p>
              <p><strong>Appointment ID:</strong> #${treatment.appointment_id}</p>
            </div>
            <div class="col">
              <h3>Appointment Details</h3>
              <p><strong>Date:</strong> ${this.formatDate(treatment.appointment_date)}</p>
              <p><strong>Time:</strong> ${this.formatTime(treatment.appointment_time)}</p>
            </div>
          </div>
          
          <div class="section">
            <h3>Diagnosis</h3>
            <div class="diagnosis-box">
              ${treatment.diagnosis}
            </div>
          </div>
          
          <div class="section">
            <h3>Prescription</h3>
            <div class="prescription-box">
              ${treatment.prescription || 'No prescription provided'}
            </div>
          </div>
          
          ${treatment.notes ? `
          <div class="section">
            <h3>Doctor's Notes</h3>
            <div class="notes-box">
              ${treatment.notes}
            </div>
          </div>
          ` : ''}
          
          <div class="footer">
            <p>This report was generated on ${new Date().toLocaleString()}</p>
            <p>Hospital Management System - Confidential Medical Record</p>
          </div>
        </body>
        </html>
      `
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

.badge {
  font-size: 0.75rem;
  padding: 0.375rem 0.75rem;
  border-radius: 0.5rem;
}

.bg-light {
  background-color: #f8f9fa !important;
}

.border {
  border: 1px solid #dee2e6 !important;
}

.d-grid {
  display: grid !important;
}

.gap-2 {
  gap: 0.5rem !important;
}
</style>