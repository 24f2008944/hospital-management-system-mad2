<template>
  <div class="container-fluid py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Manage Patients</h2>
      <div class="btn-group">
        <router-link to="/blacklisted-patients" class="btn btn-outline-danger">
          <i class="bi bi-ban"></i>
          Blacklisted Patients
        </router-link>
        <button class="btn btn-primary" @click="showAddModal = true">
          <i class="bi bi-plus-circle"></i>
          Add Patient
        </button>
      </div>
    </div>

    <!-- Search -->
    <div class="card mb-4">
      <div class="card-body">
        <input
          type="text"
          v-model="searchQuery"
          @input="searchPatients"
          class="form-control"
          placeholder="Search patients by name, email, or contact..."
        >
      </div>
    </div>

    <!-- Patients Table -->
    <div class="card">
      <div class="card-body">
        <div v-if="loading" class="text-center py-3">
          <div class="spinner-border text-primary"></div>
        </div>
        
        <div v-else-if="patients.length === 0" class="text-center py-5">
          <i class="bi bi-people" style="font-size: 3rem; color: #6c757d;"></i>
          <p class="mt-3 text-muted">No patients found</p>
        </div>
        
        <div v-else class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Contact</th>
                <th>Age</th>
                <th>Blood Group</th>
                <th>Appointments</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="patient in patients" :key="patient.id">
                <td>{{ patient.full_name || patient.user.username }}</td>
                <td>{{ patient.user.email }}</td>
                <td>{{ patient.contact_number || 'N/A' }}</td>
                <td>{{ calculateAge(patient.date_of_birth) }}</td>
                <td>{{ patient.blood_group || 'N/A' }}</td>
                <td>{{ patient.appointments_count || 0 }}</td>
                <td>
                  <span :class="patient.is_active ? 'badge bg-success' : 'badge bg-danger'">
                    {{ patient.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td>
                  <div class="btn-group">
                    <button class="btn btn-sm btn-outline-primary" @click="viewPatient(patient)">
                      <i class="bi bi-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-info" @click="editPatient(patient)">
                      <i class="bi bi-pencil"></i>
                    </button>
                    <button 
                      class="btn btn-sm btn-outline-warning" 
                      @click="blockPatient(patient)"
                      v-if="patient.is_active"
                      title="Block Patient"
                    >
                      <i class="bi bi-ban"></i>
                    </button>
                    <button 
                      class="btn btn-sm btn-outline-danger" 
                      @click="deletePatient(patient)"
                      v-if="patient.is_active"
                      title="Delete Patient"
                    >
                      <i class="bi bi-trash"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Add Patient Modal -->
    <div class="modal fade" :class="{ show: showAddModal }" 
         :style="{ display: showAddModal ? 'block' : 'none' }"
         tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Add Patient</h5>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="savePatient">
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Username</label>
                  <input type="text" v-model="patientForm.username" class="form-control" required>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Email</label>
                  <input type="email" v-model="patientForm.email" class="form-control" required>
                </div>
              </div>
              
              <div class="mb-3">
                <label class="form-label">Password</label>
                <input type="password" v-model="patientForm.password" class="form-control" required>
              </div>
              
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">First Name</label>
                  <input type="text" v-model="patientForm.first_name" class="form-control">
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Last Name</label>
                  <input type="text" v-model="patientForm.last_name" class="form-control">
                </div>
              </div>
              
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Contact Number</label>
                  <input type="tel" v-model="patientForm.contact_number" class="form-control">
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Date of Birth</label>
                  <input type="date" v-model="patientForm.date_of_birth" class="form-control">
                </div>
              </div>
              
              <div class="text-end">
                <button type="button" class="btn btn-secondary me-2" @click="closeModal">Cancel</button>
                <button type="submit" class="btn btn-primary" :disabled="saving">
                  <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
                  Create Patient
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Edit Patient Modal -->
    <div class="modal fade" :class="{ show: showEditModal }" 
         :style="{ display: showEditModal ? 'block' : 'none' }"
         tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              Edit Patient
              <small v-if="editingPatient" class="text-muted ms-2">
                ({{ editingPatient.user?.username || editingPatient.user?.email }})
              </small>
            </h5>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="savePatient">
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">First Name</label>
                  <input type="text" v-model="patientForm.first_name" class="form-control" required>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Last Name</label>
                  <input type="text" v-model="patientForm.last_name" class="form-control" required>
                </div>
              </div>
              <div class="row">
                <div class="col-md-12 mb-3">
                  <label class="form-label">Email</label>
                  <input type="email" v-model="patientForm.email" class="form-control" required>
                </div>
              </div>
              
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Contact Number</label>
                  <input type="tel" v-model="patientForm.contact_number" class="form-control">
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Date of Birth</label>
                  <input type="date" v-model="patientForm.date_of_birth" class="form-control">
                </div>
              </div>
              
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Gender</label>
                  <select v-model="patientForm.gender" class="form-select">
                    <option value="">Select Gender</option>
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                  </select>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Blood Group</label>
                  <select v-model="patientForm.blood_group" class="form-select">
                    <option value="">Select Blood Group</option>
                    <option value="A+">A+</option>
                    <option value="A-">A-</option>
                    <option value="B+">B+</option>
                    <option value="B-">B-</option>
                    <option value="AB+">AB+</option>
                    <option value="AB-">AB-</option>
                    <option value="O+">O+</option>
                    <option value="O-">O-</option>
                  </select>
                </div>
              </div>
              
              <div class="mb-3">
                <label class="form-label">Address</label>
                <textarea v-model="patientForm.address" class="form-control" rows="2"></textarea>
              </div>
              
              <div class="mb-3">
                <label class="form-label">Emergency Contact</label>
                <input type="tel" v-model="patientForm.emergency_contact" class="form-control">
              </div>
              
              <div class="mb-3">
                <label class="form-label">Allergies</label>
                <textarea v-model="patientForm.allergies" class="form-control" rows="2" 
                          placeholder="List any known allergies..."></textarea>
              </div>
              
              <div class="mb-3">
                <label class="form-label">Medical History</label>
                <textarea v-model="patientForm.medical_history" class="form-control" rows="3" 
                          placeholder="Brief medical history..."></textarea>
              </div>
              
              <div class="mb-3">
                <label class="form-label">Insurance Details</label>
                <input type="text" v-model="patientForm.insurance_details" class="form-control" 
                       placeholder="Insurance provider and policy number">
              </div>
              
              <div class="text-end">
                <button type="button" class="btn btn-secondary me-2" @click="closeModal">Cancel</button>
                <button type="submit" class="btn btn-primary" :disabled="saving">
                  <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
                  Update Patient
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- Block Modal -->
    <div class="modal fade" :class="{ show: showBlockModal }"
         :style="{ display: showBlockModal ? 'block' : 'none' }"
         tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header bg-warning text-dark">
            <h5 class="modal-title">Block Patient</h5>
            <button type="button" class="btn-close" @click="cancelBlock"></button>
          </div>
          <div class="modal-body">
            <p class="mb-3"><strong>Patient:</strong> {{ blockingPatient?.full_name || blockingPatient?.user?.username }}</p>
            <p class="text-warning"><i class="bi bi-exclamation-triangle"></i> The patient will be blocked and unable to access the system.</p>
            <div class="mb-3">
              <label class="form-label">Reason for Blocking</label>
              <textarea v-model="blockReason" class="form-control" rows="3" placeholder="e.g., Fraud, Abusive behavior, etc."></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="cancelBlock">Cancel</button>
            <button type="button" class="btn btn-warning" @click="confirmBlock" :disabled="blocking">
              <span v-if="blocking" class="spinner-border spinner-border-sm me-2"></span>
              Block Patient
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Modal -->
    <div class="modal fade" :class="{ show: showDeleteModal }"
         :style="{ display: showDeleteModal ? 'block' : 'none' }"
         tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header bg-danger text-white">
            <h5 class="modal-title">Delete Patient Permanently</h5>
            <button type="button" class="btn-close btn-close-white" @click="cancelDelete"></button>
          </div>
          <div class="modal-body">
            <p class="mb-3"><strong>Patient:</strong> {{ deletingPatient?.full_name || deletingPatient?.user?.username }}</p>
            <p class="text-danger"><i class="bi bi-exclamation-triangle-fill"></i> <strong>WARNING:</strong> This action cannot be undone. The patient record will be permanently deleted from the system.</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="cancelDelete">Cancel</button>
            <button type="button" class="btn btn-danger" @click="confirmDelete" :disabled="deleting">
              <span v-if="deleting" class="spinner-border spinner-border-sm me-2"></span>
              Delete Permanently
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal backdrop -->
    <div v-if="showAddModal || showEditModal || showBlockModal || showDeleteModal" class="modal-backdrop fade show"></div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'AdminPatientsView',
  data() {
    return {
      searchQuery: '',
      patients: [],
      loading: false,
      showAddModal: false,
      showEditModal: false,
      saving: false,
      editingPatient: null,
      showBlockModal: false,
      blockingPatient: null,
      blockReason: '',
      blocking: false,
      showDeleteModal: false,
      deletingPatient: null,
      deleting: false,
      patientForm: {
        username: '',
        email: '',
        password: '',
        first_name: '',
        last_name: '',
        contact_number: '',
        date_of_birth: ''
      }
    }
  },
  methods: {
    async loadPatients() {
      try {
        this.loading = true
        const params = this.searchQuery ? { search: this.searchQuery } : {}
        const response = await axios.get('/patients', { params })
        this.patients = response.data
      } catch (error) {
        console.error('Failed to load patients:', error)
      } finally {
        this.loading = false
      }
    },
    
    async searchPatients() {
      await this.loadPatients()
    },
    
    viewPatient(patient) {
      // Navigate to patient details or show modal
      console.log('View patient:', patient)
    },
    
    editPatient(patient) {
      console.log('Editing patient:', patient) // Debug log
      this.editingPatient = patient
      
      // Format date properly for input[type="date"]
      let formattedDate = ''
      if (patient.date_of_birth) {
        const date = new Date(patient.date_of_birth)
        if (!isNaN(date.getTime())) {
          formattedDate = date.toISOString().split('T')[0]
        }
      }

      this.patientForm = {
        first_name: patient.first_name || '',
        last_name: patient.last_name || '',
        contact_number: patient.contact_number || '',
        date_of_birth: formattedDate,
        gender: patient.gender || '',
        blood_group: patient.blood_group || '',
        address: patient.address || '',
        emergency_contact: patient.emergency_contact || '',
        allergies: patient.allergies || '',
        medical_history: patient.medical_history || '',
        insurance_details: patient.insurance_details || '',
        email: (patient.user && patient.user.email) ? patient.user.email : ''
      }
      this.showEditModal = true
    },
    
    async savePatient() {
      try {
        this.saving = true
        if (this.editingPatient) {
          // Update existing patient
          console.log('Updating patient:', this.editingPatient.id, this.patientForm)
          await axios.put(`/patients/${this.editingPatient.id}`, this.patientForm)
          alert('✅ Patient updated successfully!')
        } else {
          // Create new patient
          await axios.post('/patients', this.patientForm)
          alert('✅ Patient created successfully!')
        }
        await this.loadPatients()
        this.closeModal()
      } catch (error) {
        console.error('Failed to save patient:', error)
        alert('❌ Failed to save patient: ' + (error.response?.data?.error || error.message))
      } finally {
        this.saving = false
      }
    },
    
    blockPatient(patient) {
      this.blockingPatient = patient
      this.blockReason = ''
      this.showBlockModal = true
    },

    async confirmBlock() {
      if (!this.blockingPatient) return
      try {
        this.blocking = true
        await axios.delete(`/patients/${this.blockingPatient.id}`, {
          data: { reason: this.blockReason || 'No reason provided' }
        })
        alert('✅ Patient blocked successfully')
        await this.loadPatients()
        this.cancelBlock()
      } catch (error) {
        console.error('Failed to block patient:', error)
        alert('❌ Failed to block patient: ' + (error.response?.data?.message || error.message))
      } finally {
        this.blocking = false
      }
    },

    cancelBlock() {
      this.showBlockModal = false
      this.blockingPatient = null
      this.blockReason = ''
    },

    deletePatient(patient) {
      this.deletingPatient = patient
      this.showDeleteModal = true
    },

    async confirmDelete() {
      if (!this.deletingPatient) return
      try {
        this.deleting = true
        await axios.delete(`/patients/${this.deletingPatient.id}?action=delete`)
        alert('✅ Patient permanently deleted')
        await this.loadPatients()
        this.cancelDelete()
      } catch (error) {
        console.error('Failed to delete patient:', error)
        alert('❌ Failed to delete patient: ' + (error.response?.data?.message || error.message))
      } finally {
        this.deleting = false
      }
    },

    cancelDelete() {
      this.showDeleteModal = false
      this.deletingPatient = null
    },
    
    calculateAge(dateOfBirth) {
      if (!dateOfBirth) return 'N/A'
      const today = new Date()
      const birth = new Date(dateOfBirth)
      const age = today.getFullYear() - birth.getFullYear()
      const monthDiff = today.getMonth() - birth.getMonth()
      if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
        return age - 1
      }
      return age
    },
    
    closeModal() {
      this.showAddModal = false
      this.showEditModal = false
      this.editingPatient = null
      this.patientForm = {
        username: '',
        email: '',
        password: '',
        first_name: '',
        last_name: '',
        contact_number: '',
        date_of_birth: '',
        gender: '',
        blood_group: '',
        address: '',
        emergency_contact: '',
        allergies: '',
        medical_history: ''
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
}

.btn {
  border-radius: 8px;
}
</style>
