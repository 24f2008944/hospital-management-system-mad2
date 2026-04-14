<template>
  <div class="doctor-availability-view">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2><i class="fas fa-calendar-alt"></i> Manage Availability</h2>
      <button 
        class="btn btn-primary" 
        @click="showAddModal = true"
      >
        <i class="fas fa-plus"></i> Add Availability Slot
      </button>
    </div>

    <!-- Filters -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row">
          <div class="col-md-4">
            <label class="form-label">Start Date</label>
            <input 
              type="date" 
              class="form-control" 
              v-model="filters.startDate"
              @change="loadAvailability"
            >
          </div>
          <div class="col-md-4">
            <label class="form-label">End Date</label>
            <input 
              type="date" 
              class="form-control" 
              v-model="filters.endDate"
              @change="loadAvailability"
            >
          </div>
          <div class="col-md-4 d-flex align-items-end">
            <button 
              class="btn btn-outline-secondary" 
              @click="resetFilters"
            >
              <i class="fas fa-refresh"></i> Reset
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Availability Slots -->
    <div class="card">
      <div class="card-header">
        <h5 class="mb-0">
          <i class="fas fa-clock"></i> Your Availability Slots
          <span class="badge bg-primary ms-2">{{ availabilitySlots.length }}</span>
        </h5>
      </div>
      <div class="card-body">
        <div v-if="loading" class="text-center py-4">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>

        <div v-else-if="availabilitySlots.length === 0" class="text-center py-4 text-muted">
          <i class="fas fa-calendar-times fa-3x mb-3"></i>
          <p>No availability slots found. Add your first slot to get started!</p>
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover">
            <thead class="table-light">
              <tr>
                <th>Date</th>
                <th>Time</th>
                <th>Max Appointments</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="slot in availabilitySlots" :key="slot.id">
                <td>
                  <strong>{{ formatDate(slot.available_date) }}</strong>
                </td>
                <td>
                  <span class="badge bg-info">
                    {{ formatTime(slot.start_time) }} - {{ formatTime(slot.end_time) }}
                  </span>
                </td>
                <td>
                  <span class="badge bg-secondary">{{ slot.max_appointments }}</span>
                </td>
                <td>
                  <span 
                    :class="['badge', slot.is_available ? 'bg-success' : 'bg-danger']"
                  >
                    {{ slot.is_available ? 'Available' : 'Unavailable' }}
                  </span>
                </td>
                <td>
                  <div class="btn-group btn-group-sm">
                    <button 
                      class="btn btn-outline-primary"
                      @click="editSlot(slot)"
                      title="Edit"
                    >
                      <i class="fas fa-edit"></i>
                    </button>
                    <button 
                      class="btn btn-outline-danger"
                      @click="confirmDelete(slot)"
                      title="Delete"
                    >
                      <i class="fas fa-trash"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Add/Edit Modal -->
    <div 
      class="modal fade" 
      :class="{ show: showAddModal || showEditModal }" 
      :style="{ display: showAddModal || showEditModal ? 'block' : 'none' }"
      tabindex="-1"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              {{ editingSlot ? 'Edit' : 'Add' }} Availability Slot
            </h5>
            <button 
              type="button" 
              class="btn-close" 
              @click="closeModal"
            ></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveSlot">
              <div class="mb-3">
                <label class="form-label">Date *</label>
                <input 
                  type="date" 
                  class="form-control" 
                  v-model="slotForm.date"
                  :min="minDate"
                  :max="maxDate"
                  required
                >
              </div>
              
              <div class="row">
                <div class="col-md-6">
                  <label class="form-label">Start Time *</label>
                  <input 
                    type="time" 
                    class="form-control" 
                    v-model="slotForm.start_time"
                    required
                  >
                </div>
                <div class="col-md-6">
                  <label class="form-label">End Time *</label>
                  <input 
                    type="time" 
                    class="form-control" 
                    v-model="slotForm.end_time"
                    required
                  >
                </div>
              </div>
              
              <div class="mb-3 mt-3">
                <label class="form-label">Maximum Appointments</label>
                <input 
                  type="number" 
                  class="form-control" 
                  v-model="slotForm.max_appointments"
                  min="1"
                  max="20"
                >
              </div>
              
              <div class="mb-3">
                <div class="form-check">
                  <input 
                    class="form-check-input" 
                    type="checkbox" 
                    v-model="slotForm.is_available"
                    id="availableCheck"
                  >
                  <label class="form-check-label" for="availableCheck">
                    Available for appointments
                  </label>
                </div>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button 
              type="button" 
              class="btn btn-secondary" 
              @click="closeModal"
            >
              Cancel
            </button>
            <button 
              type="button" 
              class="btn btn-primary" 
              @click="saveSlot"
              :disabled="saving"
            >
              <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
              {{ editingSlot ? 'Update' : 'Add' }} Slot
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div 
      class="modal fade" 
      :class="{ show: showDeleteModal }" 
      :style="{ display: showDeleteModal ? 'block' : 'none' }"
      tabindex="-1"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Confirm Delete</h5>
            <button 
              type="button" 
              class="btn-close" 
              @click="showDeleteModal = false"
            ></button>
          </div>
          <div class="modal-body">
            <p>Are you sure you want to delete this availability slot?</p>
            <div v-if="slotToDelete" class="alert alert-warning">
              <strong>{{ formatDate(slotToDelete.available_date) }}</strong><br>
              {{ formatTime(slotToDelete.start_time) }} - {{ formatTime(slotToDelete.end_time) }}
            </div>
            <p class="text-danger">
              <i class="fas fa-exclamation-triangle"></i>
              This action cannot be undone.
            </p>
          </div>
          <div class="modal-footer">
            <button 
              type="button" 
              class="btn btn-secondary" 
              @click="showDeleteModal = false"
            >
              Cancel
            </button>
            <button 
              type="button" 
              class="btn btn-danger" 
              @click="deleteSlot"
              :disabled="deleting"
            >
              <span v-if="deleting" class="spinner-border spinner-border-sm me-2"></span>
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal Backdrop -->
    <div 
      v-if="showAddModal || showEditModal || showDeleteModal" 
      class="modal-backdrop fade show"
      @click="closeModal"
    ></div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'DoctorAvailabilityView',
  data() {
    return {
      availabilitySlots: [],
      loading: false,
      saving: false,
      deleting: false,
      showAddModal: false,
      showEditModal: false,
      showDeleteModal: false,
      editingSlot: null,
      slotToDelete: null,
      filters: {
        startDate: new Date().toISOString().split('T')[0],
        endDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
      },
      slotForm: {
        date: '',
        start_time: '09:00',
        end_time: '10:00',
        max_appointments: 1,
        is_available: true
      }
    };
  },
  computed: {
    minDate() {
      return new Date().toISOString().split('T')[0];
    },
    maxDate() {
      const today = new Date();
      const max = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000);
      return max.toISOString().split('T')[0];
    }
  },
  mounted() {
    this.loadAvailability();
  },
  methods: {
    async loadAvailability() {
      this.loading = true;
      try {
        const params = {};
        if (this.filters.startDate) params.start_date = this.filters.startDate;
        if (this.filters.endDate) params.end_date = this.filters.endDate;

        const response = await axios.get('/doctor-availability', { params });
        this.availabilitySlots = response.data;
      } catch (error) {
        console.error('Error loading availability:', error);
        this.$store.dispatch('showAlert', {
          type: 'error',
          message: error.response?.data?.error || 'Failed to load availability slots'
        });
      } finally {
        this.loading = false;
      }
    },

    resetFilters() {
      this.filters.startDate = new Date().toISOString().split('T')[0];
      this.filters.endDate = new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
      this.loadAvailability();
    },

    editSlot(slot) {
      this.editingSlot = slot;
      this.slotForm = {
        date: slot.available_date,
        start_time: slot.start_time,
        end_time: slot.end_time,
        max_appointments: slot.max_appointments,
        is_available: slot.is_available
      };
      this.showEditModal = true;
    },

    confirmDelete(slot) {
      this.slotToDelete = slot;
      this.showDeleteModal = true;
    },

    async saveSlot() {
      this.saving = true;
      try {
        if (this.editingSlot) {
          // Update existing slot
          await axios.put(`/doctor-availability/${this.editingSlot.id}`, this.slotForm);
          this.$store.dispatch('showAlert', {
            type: 'success',
            message: 'Availability slot updated successfully'
          });
        } else {
          // Create new slot
          await axios.post('/doctor-availability', this.slotForm);
          this.$store.dispatch('showAlert', {
            type: 'success',
            message: 'Availability slot added successfully'
          });
        }
        
        this.closeModal();
        this.loadAvailability();
      } catch (error) {
        console.error('Error saving availability:', error);
        this.$store.dispatch('showAlert', {
          type: 'error',
          message: error.response?.data?.error || 'Failed to save availability slot'
        });
      } finally {
        this.saving = false;
      }
    },

    async deleteSlot() {
      this.deleting = true;
      try {
        await axios.delete(`/doctor-availability/${this.slotToDelete.id}`);
        this.$store.dispatch('showAlert', {
          type: 'success',
          message: 'Availability slot deleted successfully'
        });
        this.showDeleteModal = false;
        this.slotToDelete = null;
        this.loadAvailability();
      } catch (error) {
        console.error('Error deleting availability:', error);
        this.$store.dispatch('showAlert', {
          type: 'error',
          message: error.response?.data?.error || 'Failed to delete availability slot'
        });
      } finally {
        this.deleting = false;
      }
    },

    closeModal() {
      this.showAddModal = false;
      this.showEditModal = false;
      this.showDeleteModal = false;
      this.editingSlot = null;
      this.slotForm = {
        date: '',
        start_time: '09:00',
        end_time: '10:00',
        max_appointments: 1,
        is_available: true
      };
    },

    formatDate(dateStr) {
      const date = new Date(dateStr + 'T00:00:00');
      return date.toLocaleDateString('en-US', {
        weekday: 'short',
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    },

    formatTime(timeStr) {
      const [hours, minutes] = timeStr.split(':');
      const time = new Date();
      time.setHours(parseInt(hours), parseInt(minutes));
      return time.toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
      });
    }
  }
};
</script>

<style scoped>
.doctor-availability-view {
  padding: 20px;
}

.table th {
  background-color: #f8f9fa;
  font-weight: 600;
}

.btn-group-sm .btn {
  padding: 0.25rem 0.5rem;
}

.modal {
  background-color: rgba(0, 0, 0, 0.5);
}

.modal.show {
  display: block !important;
}

.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 1040;
  width: 100vw;
  height: 100vh;
  background-color: #000;
  opacity: 0.5;
}

.badge {
  font-size: 0.75em;
}

.alert {
  border-radius: 0.375rem;
}

.form-check-input:checked {
  background-color: #0d6efd;
  border-color: #0d6efd;
}
</style>
