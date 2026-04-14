<template>
  <div class="modal fade" :class="{ show: showModal }" :style="{ display: showModal ? 'block' : 'none' }" tabindex="-1" aria-labelledby="doctorDetailModalLabel" aria-hidden="true">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="doctorDetailModalLabel">
            <i class="bi bi-person-badge"></i>
            Doctor Details
          </h5>
          <button type="button" class="btn-close" @click="closeModal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <div v-if="loading" class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading doctor details...</span>
            </div>
            <p class="text-muted mt-2">Loading doctor details...</p>
          </div>
          <div v-else-if="error" class="alert alert-danger">
            <i class="bi bi-exclamation-triangle"></i>
            {{ error }}
          </div>
          <div v-else-if="doctor">
            <div class="row">
              <div class="col-md-4 text-center mb-3">
                <div class="doctor-avatar">
                  <i class="bi bi-person-circle" style="font-size: 4rem; color: #6c757d;"></i>
                </div>
                <h5 class="mt-2">{{ doctor.user?.username || 'N/A' }}</h5>
                <p class="text-muted mb-0">{{ doctor.specialization || 'N/A' }}</p>
              </div>
              <div class="col-md-8">
                <div class="row g-3">
                  <div class="col-sm-6">
                    <div class="detail-item">
                      <label class="form-label fw-bold">Department</label>
                      <p class="mb-0">{{ doctor.department?.name || 'N/A' }}</p>
                    </div>
                  </div>
                  <div class="col-sm-6">
                    <div class="detail-item">
                      <label class="form-label fw-bold">Experience</label>
                      <p class="mb-0">{{ doctor.experience_years ? `${doctor.experience_years} years` : 'N/A' }}</p>
                    </div>
                  </div>
                  <div class="col-sm-6">
                    <div class="detail-item">
                      <label class="form-label fw-bold">Qualification</label>
                      <p class="mb-0">{{ doctor.qualification || 'N/A' }}</p>
                    </div>
                  </div>
                  <div class="col-sm-6">
                    <div class="detail-item">
                      <label class="form-label fw-bold">Consultation Fee</label>
                      <p class="mb-0">{{ doctor.consultation_fee ? `$${doctor.consultation_fee}` : 'N/A' }}</p>
                    </div>
                  </div>
                  <div class="col-sm-6">
                    <div class="detail-item">
                      <label class="form-label fw-bold">License Number</label>
                      <p class="mb-0">{{ doctor.license_number || 'N/A' }}</p>
                    </div>
                  </div>
                  <div class="col-sm-6">
                    <div class="detail-item">
                      <label class="form-label fw-bold">Contact Number</label>
                      <p class="mb-0">{{ doctor.contact_number || 'N/A' }}</p>
                    </div>
                  </div>
                  <div class="col-12">
                    <div class="detail-item">
                      <label class="form-label fw-bold">Available Days</label>
                      <p class="mb-0">{{ doctor.available_days || 'N/A' }}</p>
                    </div>
                  </div>
                  <div class="col-sm-6">
                    <div class="detail-item">
                      <label class="form-label fw-bold">Available Time (Start)</label>
                      <p class="mb-0">{{ doctor.available_time_start || 'N/A' }}</p>
                    </div>
                  </div>
                  <div class="col-sm-6">
                    <div class="detail-item">
                      <label class="form-label fw-bold">Available Time (End)</label>
                      <p class="mb-0">{{ doctor.available_time_end || 'N/A' }}</p>
                    </div>
                  </div>
                  <div class="col-12">
                    <div class="detail-item">
                      <label class="form-label fw-bold">Email</label>
                      <p class="mb-0">{{ doctor.user?.email || 'N/A' }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="closeModal">Close</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Modal backdrop -->
  <div v-if="showModal" class="modal-backdrop fade show" @click="closeModal"></div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'DoctorDetailDialog',
  props: {
    doctorId: {
      type: Number,
      required: true
    },
    modalId: {
      type: String,
      default: 'doctorDetailModal'
    }
  },
  data() {
    return {
      doctor: null,
      loading: false,
      error: null,
      showModal: false
    }
  },
  watch: {
    doctorId: {
      handler(newId) {
        if (newId) {
          this.fetchDoctorDetails()
        }
      },
      immediate: true
    }
  },
  methods: {
    async fetchDoctorDetails() {
      if (!this.doctorId) return

      this.loading = true
      this.error = null

      try {
        const response = await axios.get(`/doctors/${this.doctorId}`)
        this.doctor = response.data
      } catch (error) {
        console.error('Error fetching doctor details:', error)
        this.error = 'Failed to load doctor details. Please try again.'
      } finally {
        this.loading = false
      }
    },

    closeModal() {
      this.showModal = false
    }
  },

  mounted() {
    // Show modal when component is mounted
    this.showModal = true
  }
}
</script>

<style scoped>
.doctor-avatar {
  margin-bottom: 1rem;
}

.detail-item {
  padding: 0.75rem;
  border: 1px solid #e9ecef;
  border-radius: 0.375rem;
  background: #f8f9fa;
}

.detail-item label {
  font-size: 0.875rem;
  color: #6c757d;
  margin-bottom: 0.25rem;
}

.detail-item p {
  font-size: 0.95rem;
  color: #212529;
}

.modal-content {
  border-radius: 15px;
  border: none;
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
}

.modal-header {
  border-bottom: 1px solid #e9ecef;
  border-radius: 15px 15px 0 0;
}

.modal-footer {
  border-top: 1px solid #e9ecef;
  border-radius: 0 0 15px 15px;
}
</style>
