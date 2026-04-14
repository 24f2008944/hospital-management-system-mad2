<template>
  <div class="container-fluid py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Manage Departments</h2>
      <button class="btn btn-primary" @click="showAddModal = true">
        <i class="bi bi-plus-circle"></i>
        Add Department
      </button>
    </div>

    <!-- Departments Cards -->
    <div class="row">
      <div v-if="loading" class="col-12 text-center py-5">
        <div class="spinner-border text-primary"></div>
        <p class="mt-3">Loading departments...</p>
      </div>
      
      <div v-else-if="departments.length === 0" class="col-12 text-center py-5">
        <i class="bi bi-building" style="font-size: 3rem; color: #6c757d;"></i>
        <p class="mt-3 text-muted">No departments found</p>
      </div>
      
      <div v-else v-for="department in departments" :key="department.id" class="col-md-6 col-lg-4 mb-4">
        <div class="card h-100">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start mb-3">
              <h5 class="card-title">{{ department.name }}</h5>
              <div class="dropdown">
                <button class="btn btn-sm btn-outline-secondary dropdown-toggle" data-bs-toggle="dropdown">
                  <i class="bi bi-three-dots"></i>
                </button>
                <ul class="dropdown-menu">
                  <li><a class="dropdown-item" href="#" @click="editDepartment(department)">Edit</a></li>
                  <li><a class="dropdown-item text-danger" href="#" @click="deleteDepartment(department.id)">Delete</a></li>
                </ul>
              </div>
            </div>
            
            <p class="card-text text-muted">{{ department.description || 'No description available' }}</p>
            
            <div class="mt-auto">
              <div class="d-flex justify-content-between align-items-center">
                <span class="badge bg-primary">{{ department.doctors_count || 0 }} Doctors</span>
                <small class="text-muted">{{ formatDate(department.created_at) }}</small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add/Edit Department Modal -->
    <div class="modal fade" :class="{ show: showAddModal || showEditModal }" 
         :style="{ display: showAddModal || showEditModal ? 'block' : 'none' }"
         tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ editingDepartment ? 'Edit Department' : 'Add Department' }}</h5>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveDepartment">
              <div class="mb-3">
                <label class="form-label">Department Name</label>
                <input 
                  type="text" 
                  v-model="departmentForm.name" 
                  class="form-control" 
                  required
                  placeholder="e.g., Cardiology"
                >
              </div>
              
              <div class="mb-3">
                <label class="form-label">Description</label>
                <textarea 
                  v-model="departmentForm.description" 
                  class="form-control" 
                  rows="4"
                  placeholder="Brief description of the department..."
                ></textarea>
              </div>
              
              <div class="text-end">
                <button type="button" class="btn btn-secondary me-2" @click="closeModal">Cancel</button>
                <button type="submit" class="btn btn-primary" :disabled="saving">
                  <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
                  {{ editingDepartment ? 'Update' : 'Create' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Modal backdrop -->
    <div v-if="showAddModal || showEditModal" class="modal-backdrop fade show"></div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'AdminDepartmentsView',
  data() {
    return {
      departments: [],
      loading: false,
      showAddModal: false,
      showEditModal: false,
      editingDepartment: null,
      saving: false,
      departmentForm: {
        name: '',
        description: ''
      }
    }
  },
  methods: {
    async loadDepartments() {
      try {
        this.loading = true
        const response = await axios.get('/departments')
        this.departments = response.data
      } catch (error) {
        console.error('Failed to load departments:', error)
      } finally {
        this.loading = false
      }
    },
    
    editDepartment(department) {
      this.editingDepartment = department
      this.departmentForm = {
        name: department.name,
        description: department.description || ''
      }
      this.showEditModal = true
    },
    
    async saveDepartment() {
      try {
        this.saving = true
        
        if (this.editingDepartment) {
          await axios.put(`/departments/${this.editingDepartment.id}`, this.departmentForm)
        } else {
          await axios.post('/departments', this.departmentForm)
        }
        
        await this.loadDepartments()
        this.closeModal()
      } catch (error) {
        console.error('Failed to save department:', error)
        alert('Failed to save department: ' + (error.response?.data?.message || error.message))
      } finally {
        this.saving = false
      }
    },
    
    async deleteDepartment(departmentId) {
      if (confirm('Are you sure you want to delete this department? This action cannot be undone.')) {
        try {
          await axios.delete(`/departments/${departmentId}`)
          await this.loadDepartments()
        } catch (error) {
          console.error('Failed to delete department:', error)
          alert('Failed to delete department. It may have associated doctors.')
        }
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString()
    },
    
    closeModal() {
      this.showAddModal = false
      this.showEditModal = false
      this.editingDepartment = null
      this.departmentForm = {
        name: '',
        description: ''
      }
    }
  },
  
  async created() {
    await this.loadDepartments()
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

.dropdown-toggle::after {
  display: none;
}
</style>
