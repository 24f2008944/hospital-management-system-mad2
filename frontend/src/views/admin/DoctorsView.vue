<template>
  <div class="container-fluid py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Manage Doctors</h2>
      <div class="btn-group">
        <router-link to="/blacklisted-doctors" class="btn btn-outline-danger">
          <i class="bi bi-ban"></i>
          Blacklisted Doctors
        </router-link>
        <button class="btn btn-primary" @click="showAddModal = true">
          <i class="bi bi-plus-circle"></i>
          Add Doctor
        </button>
      </div>
    </div>

    <!-- Search and Filter -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row">
          <div class="col-md-6">
            <input
              type="text"
              v-model="searchQuery"
              @input="searchDoctors"
              class="form-control"
              placeholder="Search doctors..."
            >
          </div>
          <div class="col-md-6">
            <select v-model="selectedDepartment" @change="filterDoctors" class="form-select">
              <option value="">All Departments</option>
              <option v-for="dept in departments" :key="dept.id" :value="dept.id">
                {{ dept.name }}
              </option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- Doctors Table -->
    <div class="card">
      <div class="card-body">
        <div v-if="loading" class="text-center py-3">
          <div class="spinner-border text-primary"></div>
        </div>
        
        <div v-else-if="doctors.length === 0" class="text-center py-5">
          <i class="bi bi-person-x" style="font-size: 3rem; color: #6c757d;"></i>
          <p class="mt-3 text-muted">No doctors found</p>
        </div>
        
        <div v-else class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Department</th>
                <th>Specialization</th>
                <th>Experience</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="doctor in doctors" :key="doctor.id">
                <td>{{ doctor.user.username }}</td>
                <td>{{ doctor.user.email }}</td>
                <td>{{ doctor.department?.name || 'N/A' }}</td>
                <td>{{ doctor.specialization || 'N/A' }}</td>
                <td>{{ doctor.experience_years }} years</td>
                <td>
                  <span :class="doctor.is_active ? 'badge bg-success' : 'badge bg-danger'">
                    {{ doctor.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td>
                  <div class="btn-group">
                    <button class="btn btn-sm btn-outline-primary" @click="editDoctor(doctor)">
                      <i class="bi bi-pencil"></i>
                    </button>
                    <button 
                      class="btn btn-sm btn-outline-warning" 
                      @click="blockDoctor(doctor)"
                      v-if="doctor.is_active"
                      title="Block Doctor"
                    >
                      <i class="bi bi-ban"></i>
                    </button>
                    <button 
                      class="btn btn-sm btn-outline-danger" 
                      @click="deleteDoctor(doctor)"
                      v-if="doctor.is_active"
                      title="Delete Doctor"
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

    <!-- Add/Edit Doctor Modal -->
    <div class="modal fade" :class="{ show: showAddModal || showEditModal }"
         :style="{ display: showAddModal || showEditModal ? 'block' : 'none' }"
         tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ editingDoctor ? 'Edit Doctor' : 'Add Doctor' }}</h5>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveDoctor">
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Username</label>
                  <input type="text" v-model="doctorForm.username" class="form-control" required>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Email</label>
                  <input type="email" v-model="doctorForm.email" class="form-control" required>
                </div>
              </div>

              <div class="mb-3" v-if="!editingDoctor">
                <label class="form-label">Password</label>
                <input type="password" v-model="doctorForm.password" class="form-control" required>
              </div>

              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Department</label>
                  <select v-model="doctorForm.department_id" class="form-select" required>
                    <option value="">Select Department</option>
                    <option v-for="dept in departments" :key="dept.id" :value="dept.id">
                      {{ dept.name }}
                    </option>
                  </select>
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Specialization</label>
                  <input type="text" v-model="doctorForm.specialization" class="form-control">
                </div>
              </div>

              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label">Experience (Years)</label>
                  <input type="number" v-model="doctorForm.experience_years" class="form-control" min="0">
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label">Contact Number</label>
                  <input type="tel" v-model="doctorForm.contact_number" class="form-control">
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label">Qualification</label>
                <input type="text" v-model="doctorForm.qualification" class="form-control">
              </div>

              <div class="mb-3">
                <label class="form-label">License Number <span class="text-danger">*</span></label>
                <input type="text" v-model="doctorForm.license_number" class="form-control" required>
              </div>

              <div class="d-flex justify-content-end gap-2">
                <button type="button" class="btn btn-secondary" @click="closeModal">Cancel</button>
                <button type="submit" class="btn btn-primary" :disabled="saving">
                  <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
                  {{ editingDoctor ? 'Update' : 'Create' }}
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
            <h5 class="modal-title">Block Doctor</h5>
            <button type="button" class="btn-close" @click="cancelBlock"></button>
          </div>
          <div class="modal-body">
            <p class="mb-3"><strong>Doctor:</strong> {{ blockingDoctor?.user?.username }}</p>
            <p class="text-warning"><i class="bi bi-exclamation-triangle"></i> The doctor will be blocked and unable to access the system.</p>
            <div class="mb-3">
              <label class="form-label">Reason for Blocking</label>
              <textarea v-model="blockReason" class="form-control" rows="3" placeholder="e.g., License suspended, Misconduct, etc."></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="cancelBlock">Cancel</button>
            <button type="button" class="btn btn-warning" @click="confirmBlock" :disabled="blocking">
              <span v-if="blocking" class="spinner-border spinner-border-sm me-2"></span>
              Block Doctor
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
            <h5 class="modal-title">Delete Doctor Permanently</h5>
            <button type="button" class="btn-close btn-close-white" @click="cancelDelete"></button>
          </div>
          <div class="modal-body">
            <p class="mb-3"><strong>Doctor:</strong> {{ deletingDoctor?.user?.username }}</p>
            <p class="text-danger"><i class="bi bi-exclamation-triangle-fill"></i> <strong>WARNING:</strong> This action cannot be undone. The doctor record will be permanently deleted from the system.</p>
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
  name: 'AdminDoctorsView',
  data() {
    return {
      searchQuery: '',
      selectedDepartment: '',
      doctors: [],
      departments: [],
      loading: false,
      showAddModal: false,
      showEditModal: false,
      editingDoctor: null,
      saving: false,
      showBlockModal: false,
      blockingDoctor: null,
      blockReason: '',
      blocking: false,
      showDeleteModal: false,
      deletingDoctor: null,
      deleting: false,
      doctorForm: {
        username: '',
        email: '',
        password: '',
        department_id: '',
        specialization: '',
        experience_years: 0,
        contact_number: '',
        qualification: '',
        license_number: ''
      }
    }
  },
  methods: {
    async loadDoctors() {
      try {
        this.loading = true
        const params = {}
        if (this.searchQuery) {
          params.search = this.searchQuery
        }
        if (this.selectedDepartment) {
          params.department_id = this.selectedDepartment
        }
        const response = await axios.get('/doctors', { params })
        this.doctors = response.data
      } catch (error) {
        console.error('Failed to load doctors:', error)
      } finally {
        this.loading = false
      }
    },
    
    async loadDepartments() {
      try {
        const response = await axios.get('/departments')
        this.departments = response.data
      } catch (error) {
        console.error('Failed to load departments:', error)
      }
    },
    
    async searchDoctors() {
      await this.loadDoctors()
    },
    
    async filterDoctors() {
      await this.loadDoctors()
    },
    
    editDoctor(doctor) {
      this.editingDoctor = doctor
      this.doctorForm = {
        username: doctor.user.username,
        email: doctor.user.email,
        department_id: doctor.department_id,
        specialization: doctor.specialization || '',
        experience_years: doctor.experience_years || 0,
        contact_number: doctor.contact_number || '',
        qualification: doctor.qualification || ''
      }
      this.showEditModal = true
    },
    
    async saveDoctor() {
      try {
        this.saving = true
        
        if (this.editingDoctor) {
          await axios.put(`/doctors/${this.editingDoctor.id}`, this.doctorForm)
        } else {
          await axios.post('/doctors', this.doctorForm)
        }
        
        await this.loadDoctors()
        this.closeModal()
      } catch (error) {
        console.error('Failed to save doctor:', error)
        alert('Failed to save doctor: ' + (error.response?.data?.message || error.message))
      } finally {
        this.saving = false
      }
    },
    
    blockDoctor(doctor) {
      this.blockingDoctor = doctor
      this.blockReason = ''
      this.showBlockModal = true
    },

    async confirmBlock() {
      if (!this.blockingDoctor) return
      try {
        this.blocking = true
        await axios.delete(`/doctors/${this.blockingDoctor.id}`, {
          data: { reason: this.blockReason || 'No reason provided' }
        })
        alert('✅ Doctor blocked successfully')
        await this.loadDoctors()
        this.cancelBlock()
      } catch (error) {
        console.error('Failed to block doctor:', error)
        alert('❌ Failed to block doctor: ' + (error.response?.data?.message || error.message))
      } finally {
        this.blocking = false
      }
    },

    cancelBlock() {
      this.showBlockModal = false
      this.blockingDoctor = null
      this.blockReason = ''
    },

    deleteDoctor(doctor) {
      this.deletingDoctor = doctor
      this.showDeleteModal = true
    },

    async confirmDelete() {
      if (!this.deletingDoctor) return
      try {
        this.deleting = true
        await axios.delete(`/doctors/${this.deletingDoctor.id}?action=delete`)
        alert('✅ Doctor permanently deleted')
        await this.loadDoctors()
        this.cancelDelete()
      } catch (error) {
        console.error('Failed to delete doctor:', error)
        alert('❌ Failed to delete doctor: ' + (error.response?.data?.message || error.message))
      } finally {
        this.deleting = false
      }
    },

    cancelDelete() {
      this.showDeleteModal = false
      this.deletingDoctor = null
    },
    
    closeModal() {
      this.showAddModal = false
      this.showEditModal = false
      this.editingDoctor = null
      this.doctorForm = {
        username: '',
        email: '',
        password: '',
        department_id: '',
        specialization: '',
        experience_years: 0,
        contact_number: '',
        qualification: '',
        license_number: ''
      }
    }
  },
  
  async created() {
    await Promise.all([
      this.loadDoctors(),
      this.loadDepartments()
    ])
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

.btn-outline-danger {
  color: #dc3545;
  border-color: #dc3545;
}
</style>
