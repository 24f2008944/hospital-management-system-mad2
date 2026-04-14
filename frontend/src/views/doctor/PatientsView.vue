<template>
  <div class="container-fluid py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>My Patients</h2>
      <div class="position-relative">
        <input 
          type="text" 
          v-model="searchQuery" 
          class="form-control" 
          placeholder="Search patients..."
          style="padding-left: 40px; width: 300px;"
        >
        <i class="bi bi-search position-absolute" style="left: 15px; top: 50%; transform: translateY(-50%);"></i>
      </div>
    </div>

    <!-- Patients Cards -->
    <div class="row">
      <div v-if="loading" class="col-12 text-center py-5">
        <div class="spinner-border text-primary"></div>
        <p class="mt-3">Loading patients...</p>
      </div>
      
      <div v-else-if="filteredPatients.length === 0" class="col-12 text-center py-5">
        <i class="bi bi-people" style="font-size: 3rem; color: #6c757d;"></i>
        <p class="mt-3 text-muted">No patients found</p>
      </div>
      
      <div v-else v-for="patient in filteredPatients" :key="patient.id" class="col-md-6 col-lg-4 mb-4">
        <div class="card h-100">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start mb-3">
              <div class="d-flex align-items-center">
                <div class="bg-primary rounded-circle d-flex align-items-center justify-content-center me-3" 
                     style="width: 50px; height: 50px;">
                  <i class="bi bi-person-fill text-white fs-4"></i>
                </div>
                <div>
                  <h5 class="card-title mb-0">{{ patient.name }}</h5>
                  <small class="text-muted">Patient ID: #{{ patient.id }}</small>
                </div>
              </div>
            </div>
            
            <div class="mb-3">
              <p class="mb-1">
                <i class="bi bi-envelope text-muted me-2"></i>
                {{ patient.email }}
              </p>
              <p class="mb-1">
                <i class="bi bi-telephone text-muted me-2"></i>
                {{ patient.phone || 'N/A' }}
              </p>
              <p class="mb-1">
                <i class="bi bi-calendar text-muted me-2"></i>
                Age: {{ calculateAge(patient.date_of_birth) }}
              </p>
              <p class="mb-0">
                <i class="bi bi-gender-ambiguous text-muted me-2"></i>
                {{ patient.gender || 'N/A' }}
              </p>
            </div>
            
            <div class="row text-center mb-3">
              <div class="col">
                <div class="border-end">
                  <div class="fs-5 fw-bold text-primary">{{ patient.appointments_count || 0 }}</div>
                  <small class="text-muted">Appointments</small>
                </div>
              </div>
              <div class="col">
                <div class="fs-5 fw-bold text-success">{{ patient.treatments_count || 0 }}</div>
                <small class="text-muted">Treatments</small>
              </div>
            </div>
            
            <div class="mt-auto">
              <div class="d-flex gap-2">
                <button 
                  class="btn btn-outline-primary btn-sm flex-fill"
                  @click="viewPatient(patient)"
                >
                  <i class="bi bi-eye me-1"></i>
                  View Details
                </button>
                <button 
                  class="btn btn-primary btn-sm"
                  @click="viewHistory(patient)"
                >
                  <i class="bi bi-clipboard-data"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- View Patient Modal -->
    <div class="modal fade" :class="{ show: showViewModal }" 
         :style="{ display: showViewModal ? 'block' : 'none' }"
         tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Patient Details</h5>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>
          <div class="modal-body" v-if="selectedPatient">
            <div class="row">
              <div class="col-md-6">
                <h6 class="fw-bold mb-3">Personal Information</h6>
                <p><strong>Name:</strong> {{ selectedPatient.name }}</p>
                <p><strong>Email:</strong> {{ selectedPatient.email }}</p>
                <p><strong>Phone:</strong> {{ selectedPatient.phone || 'N/A' }}</p>
                <p><strong>Date of Birth:</strong> {{ formatDate(selectedPatient.date_of_birth) }}</p>
                <p><strong>Age:</strong> {{ calculateAge(selectedPatient.date_of_birth) }}</p>
                <p><strong>Gender:</strong> {{ selectedPatient.gender || 'N/A' }}</p>
                <p><strong>Address:</strong> {{ selectedPatient.address || 'N/A' }}</p>
              </div>
              <div class="col-md-6">
                <h6 class="fw-bold mb-3">Medical Information</h6>
                <p><strong>Blood Group:</strong> {{ selectedPatient.blood_group || 'N/A' }}</p>
                <p><strong>Emergency Contact:</strong> {{ selectedPatient.emergency_contact || 'N/A' }}</p>
                <p><strong>Registered:</strong> {{ formatDateTime(selectedPatient.created_at) }}</p>
                
                <div class="mt-4">
                  <h6 class="fw-bold mb-3">Medical History</h6>
                  <div class="border rounded p-3 bg-light">
                    <p class="mb-0">{{ selectedPatient.medical_history || 'No medical history recorded' }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-primary" @click="showAddNoteModal">
              <i class="bi bi-plus-circle me-2"></i>Add Medical Note
            </button>
            <button type="button" class="btn btn-secondary" @click="closeModal">Close</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Medical Note Modal -->
    <div class="modal fade" :class="{ show: showNoteModal }" 
         :style="{ display: showNoteModal ? 'block' : 'none' }"
         tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Add Medical Note for {{ selectedPatient?.name }}</h5>
            <button type="button" class="btn-close" @click="closeNoteModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveMedicalNote">
              <div class="mb-3">
                <label class="form-label">Note Type</label>
                <select v-model="noteForm.note_type" class="form-select" required>
                  <option value="Consultation">Consultation</option>
                  <option value="Follow-up">Follow-up</option>
                  <option value="Observation">Observation</option>
                  <option value="General">General</option>
                  <option value="Emergency">Emergency</option>
                </select>
              </div>
              
              <div class="mb-3">
                <label class="form-label">Title</label>
                <input 
                  type="text" 
                  v-model="noteForm.title" 
                  class="form-control" 
                  required
                  placeholder="Brief title for the note..."
                >
              </div>
              
              <div class="mb-3">
                <label class="form-label">Clinical Notes</label>
                <textarea 
                  v-model="noteForm.content" 
                  class="form-control" 
                  rows="5"
                  required
                  placeholder="Enter detailed clinical observations, findings, or notes..."
                ></textarea>
              </div>
              
              <div class="mb-3 form-check">
                <input 
                  type="checkbox" 
                  v-model="noteForm.is_private" 
                  class="form-check-input" 
                  id="isPrivate"
                >
                <label class="form-check-label" for="isPrivate">
                  Private note (only visible to doctors)
                </label>
              </div>
              
              <div class="d-flex gap-2">
                <button type="submit" class="btn btn-primary flex-fill" :disabled="saving">
                  <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
                  Save Note
                </button>
                <button type="button" class="btn btn-secondary" @click="closeNoteModal">Cancel</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- View History Modal -->
    <div class="modal fade" :class="{ show: showHistoryModal }" 
         :style="{ display: showHistoryModal ? 'block' : 'none' }"
         tabindex="-1">
      <div class="modal-dialog modal-xl">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Patient History - {{ selectedPatient?.name }}</h5>
            <button type="button" class="btn-close" @click="closeHistoryModal"></button>
          </div>
          <div class="modal-body">
            <ul class="nav nav-tabs mb-4">
              <li class="nav-item">
                <a class="nav-link" :class="{ active: activeTab === 'appointments' }" 
                   @click="activeTab = 'appointments'" href="#">
                  Appointments
                </a>
              </li>
              <li class="nav-item">
                <a class="nav-link" :class="{ active: activeTab === 'treatments' }" 
                   @click="activeTab = 'treatments'" href="#">
                  Treatments
                </a>
              </li>
              <li class="nav-item">
                <a class="nav-link" :class="{ active: activeTab === 'notes' }" 
                   @click="activeTab = 'notes'" href="#">
                  Medical Notes
                </a>
              </li>
            </ul>

            <!-- Appointments Tab -->
            <div v-if="activeTab === 'appointments'">
              <div v-if="patientAppointments.length === 0" class="text-center py-4">
                <p class="text-muted">No appointments found</p>
              </div>
              <div v-else class="table-responsive">
                <table class="table table-hover">
                  <thead class="table-light">
                    <tr>
                      <th>Date</th>
                      <th>Time</th>
                      <th>Status</th>
                      <th>Notes</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="appointment in patientAppointments" :key="appointment.id">
                      <td>{{ formatDate(appointment.appointment_date) }}</td>
                      <td>{{ formatTime(appointment.appointment_time) }}</td>
                      <td>
                        <span class="badge" :class="getStatusClass(appointment.status)">
                          {{ appointment.status }}
                        </span>
                      </td>
                      <td>{{ appointment.notes || 'No notes' }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- Treatments Tab -->
            <div v-if="activeTab === 'treatments'">
              <div v-if="patientTreatments.length === 0" class="text-center py-4">
                <p class="text-muted">No treatments found</p>
              </div>
              <div v-else>
                <div v-for="treatment in patientTreatments" :key="treatment.id" class="card mb-3">
                  <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                      <h6 class="card-title mb-0">{{ treatment.diagnosis }}</h6>
                      <small class="text-muted">{{ formatDateTime(treatment.created_at) }}</small>
                    </div>
                    <p class="card-text">
                      <strong>Prescription:</strong> {{ treatment.prescription || 'No prescription' }}
                    </p>
                    <p class="card-text">
                      <strong>Notes:</strong> {{ treatment.notes || 'No notes' }}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Medical Notes Tab -->
            <div v-if="activeTab === 'notes'">
              <div v-if="patientNotes.length === 0" class="text-center py-4">
                <p class="text-muted">No medical notes found</p>
              </div>
              <div v-else>
                <div v-for="note in patientNotes" :key="note.id" class="card mb-3">
                  <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                      <div>
                        <span class="badge bg-primary me-2">{{ note.note_type }}</span>
                        <h6 class="card-title d-inline mb-0">{{ note.title }}</h6>
                        <span v-if="note.is_private" class="badge bg-warning text-dark ms-2">
                          <i class="bi bi-lock-fill"></i> Private
                        </span>
                      </div>
                      <small class="text-muted">{{ formatDateTime(note.created_at) }}</small>
                    </div>
                    <p class="card-text mt-2">{{ note.content }}</p>
                    <small class="text-muted">By: Dr. {{ note.doctor_name }}</small>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button v-if="activeTab === 'notes'" type="button" class="btn btn-primary" @click="showAddNoteFromHistory">
              <i class="bi bi-plus-circle me-2"></i>Add Note
            </button>
            <button type="button" class="btn btn-secondary" @click="closeHistoryModal">Close</button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Modal backdrop -->
    <div v-if="showViewModal || showHistoryModal" class="modal-backdrop fade show"></div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'DoctorPatientsView',
  data() {
    return {
      patients: [],
      loading: false,
      searchQuery: '',
      showViewModal: false,
      showHistoryModal: false,
      showNoteModal: false,
      selectedPatient: null,
      patientAppointments: [],
      patientTreatments: [],
      patientNotes: [],
      activeTab: 'appointments',
      saving: false,
      noteForm: {
        note_type: 'General',
        title: '',
        content: '',
        is_private: false
      }
    }
  },
  computed: {
    filteredPatients() {
      if (!this.searchQuery) return this.patients
      
      const query = this.searchQuery.toLowerCase()
      return this.patients.filter(patient =>
        patient.name.toLowerCase().includes(query) ||
        patient.email.toLowerCase().includes(query) ||
        patient.phone?.toLowerCase().includes(query)
      )
    }
  },
  methods: {
    async loadPatients() {
      try {
        this.loading = true
        const response = await axios.get('/doctor/patients')
        this.patients = response.data
      } catch (error) {
        console.error('Failed to load patients:', error)
      } finally {
        this.loading = false
      }
    },
    
    async loadPatientHistory(patientId) {
      try {
        const [appointmentsResponse, treatmentsResponse, notesResponse] = await Promise.all([
          axios.get(`/patients/${patientId}/appointments`),
          axios.get(`/patients/${patientId}/treatments`),
          axios.get(`/medical-notes?patient_id=${patientId}`)
        ])
        
        this.patientAppointments = appointmentsResponse.data
        this.patientTreatments = treatmentsResponse.data
        this.patientNotes = notesResponse.data
      } catch (error) {
        console.error('Failed to load patient history:', error)
      }
    },
    
    viewPatient(patient) {
      this.selectedPatient = patient
      this.showViewModal = true
    },
    
    async viewHistory(patient) {
      this.selectedPatient = patient
      this.activeTab = 'appointments'
      this.showHistoryModal = true
      await this.loadPatientHistory(patient.id)
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
      this.selectedPatient = null
    },
    
    closeHistoryModal() {
      this.showHistoryModal = false
      this.selectedPatient = null
      this.patientAppointments = []
      this.patientTreatments = []
      this.patientNotes = []
    },
    
    showAddNoteModal() {
      this.showViewModal = false
      this.showNoteModal = true
    },
    
    showAddNoteFromHistory() {
      this.showHistoryModal = false
      this.showNoteModal = true
    },
    
    closeNoteModal() {
      this.showNoteModal = false
      this.noteForm = {
        note_type: 'General',
        title: '',
        content: '',
        is_private: false
      }
    },
    
    async saveMedicalNote() {
      if (!this.selectedPatient) return
      
      try {
        this.saving = true
        await axios.post('/medical-notes', {
          patient_id: this.selectedPatient.id,
          ...this.noteForm
        })
        
        alert('Medical note added successfully!')
        this.closeNoteModal()
        
        // Reload patient history if the history modal was open
        await this.loadPatientHistory(this.selectedPatient.id)
        this.showHistoryModal = true
        this.activeTab = 'notes'
      } catch (error) {
        console.error('Failed to add medical note:', error)
        alert('Failed to add medical note: ' + (error.response?.data?.error || error.message))
      } finally {
        this.saving = false
      }
    }
  },
  
  async created() {
    await this.loadPatients()
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

.nav-tabs .nav-link {
  border-radius: 0.5rem 0.5rem 0 0;
}

.table th {
  border-top: none;
  font-weight: 600;
}
</style>
