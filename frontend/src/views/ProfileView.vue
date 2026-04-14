<template>
  <div class="container py-4">
    <div class="row justify-content-center">
      <div class="col-md-8">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">
              <i class="bi bi-person-circle"></i>
              Profile Settings
            </h5>
          </div>
          <div class="card-body">
            <form @submit.prevent="updateProfile">
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="username" class="form-label">Username</label>
                  <input
                    type="text"
                    id="username"
                    v-model="form.username"
                    class="form-control"
                    readonly
                  >
                </div>
                <div class="col-md-6 mb-3">
                  <label for="email" class="form-label">Email</label>
                  <input
                    type="email"
                    id="email"
                    v-model="form.email"
                    class="form-control"
                    readonly
                  >
                </div>
              </div>

              <!-- Patient specific fields -->
              <div v-if="userRole === 'patient'">
                <h6 class="mt-4 mb-3">Personal Information</h6>
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label for="firstName" class="form-label">First Name</label>
                    <input
                      type="text"
                      id="firstName"
                      v-model="form.first_name"
                      class="form-control"
                    >
                  </div>
                  <div class="col-md-6 mb-3">
                    <label for="lastName" class="form-label">Last Name</label>
                    <input
                      type="text"
                      id="lastName"
                      v-model="form.last_name"
                      class="form-control"
                    >
                  </div>
                </div>
                
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label for="dateOfBirth" class="form-label">Date of Birth</label>
                    <input
                      type="date"
                      id="dateOfBirth"
                      v-model="form.date_of_birth"
                      class="form-control"
                    >
                  </div>
                  <div class="col-md-6 mb-3">
                    <label for="gender" class="form-label">Gender</label>
                    <select id="gender" v-model="form.gender" class="form-select">
                      <option value="">Select Gender</option>
                      <option value="Male">Male</option>
                      <option value="Female">Female</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>
                </div>
                
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label for="contactNumber" class="form-label">Contact Number</label>
                    <input
                      type="tel"
                      id="contactNumber"
                      v-model="form.contact_number"
                      class="form-control"
                    >
                  </div>
                  <div class="col-md-6 mb-3">
                    <label for="emergencyContact" class="form-label">Emergency Contact</label>
                    <input
                      type="tel"
                      id="emergencyContact"
                      v-model="form.emergency_contact"
                      class="form-control"
                    >
                  </div>
                </div>
                
                <div class="mb-3">
                  <label for="address" class="form-label">Address</label>
                  <textarea
                    id="address"
                    v-model="form.address"
                    class="form-control"
                    rows="3"
                  ></textarea>
                </div>
                
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label for="bloodGroup" class="form-label">Blood Group</label>
                    <select id="bloodGroup" v-model="form.blood_group" class="form-select">
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
                  <label for="allergies" class="form-label">Allergies</label>
                  <textarea
                    id="allergies"
                    v-model="form.allergies"
                    class="form-control"
                    rows="2"
                    placeholder="List any known allergies..."
                  ></textarea>
                </div>
                
                <div class="mb-3">
                  <label for="medicalHistory" class="form-label">Medical History</label>
                  <textarea
                    id="medicalHistory"
                    v-model="form.medical_history"
                    class="form-control"
                    rows="3"
                    placeholder="Previous medical conditions, surgeries, etc..."
                  ></textarea>
                </div>
              </div>

              <!-- Doctor specific fields -->
              <div v-if="userRole === 'doctor'">
                <h6 class="mt-4 mb-3">Professional Information</h6>
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label for="specialization" class="form-label">Specialization</label>
                    <input
                      type="text"
                      id="specialization"
                      v-model="form.specialization"
                      class="form-control"
                    >
                  </div>
                  <div class="col-md-6 mb-3">
                    <label for="experienceYears" class="form-label">Years of Experience</label>
                    <input
                      type="number"
                      id="experienceYears"
                      v-model="form.experience_years"
                      class="form-control"
                      min="0"
                    >
                  </div>
                </div>
                
                <div class="mb-3">
                  <label for="qualification" class="form-label">Qualification</label>
                  <input
                    type="text"
                    id="qualification"
                    v-model="form.qualification"
                    class="form-control"
                  >
                </div>
                
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label for="contactNumber" class="form-label">Contact Number</label>
                    <input
                      type="tel"
                      id="contactNumber"
                      v-model="form.contact_number"
                      class="form-control"
                    >
                  </div>
                  <div class="col-md-6 mb-3">
                    <label for="consultationFee" class="form-label">Consultation Fee</label>
                    <input
                      type="number"
                      id="consultationFee"
                      v-model="form.consultation_fee"
                      class="form-control"
                      min="0"
                      step="0.01"
                    >
                  </div>
                </div>
              </div>

              <div v="if error" class="alert alert-danger">
                {{ error }}
              </div>

              <div v-if="successMessage" class="alert alert-success">
                {{ successMessage }}
              </div>

              <div class="text-end">
                <button type="submit" class="btn btn-primary" :disabled="loading">
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                  Update Profile
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex'
import axios from 'axios'

export default {
  name: 'ProfileView',
  data() {
    return {
      form: {},
      loading: false,
      error: null,
      successMessage: '',
      profileData: null
    }
  },
  computed: {
    ...mapState('auth', ['user']),
    userRole() {
      return this.user?.roles?.[0] || null
    }
  },
  methods: {
    async loadProfile() {
      try {
        this.loading = true
        const response = await axios.get('/dashboard')
        
        if (response.data.role === 'patient' && response.data.patient) {
          this.profileData = response.data.patient
          this.form = {
            username: response.data.patient.user.username,
            email: response.data.patient.user.email,
            ...response.data.patient
          }
        } else if (response.data.role === 'doctor' && response.data.doctor) {
          this.profileData = response.data.doctor
          this.form = {
            username: response.data.doctor.user.username,
            email: response.data.doctor.user.email,
            ...response.data.doctor
          }
        }
      } catch (error) {
        this.error = 'Failed to load profile'
      } finally {
        this.loading = false
      }
    },
    
    async updateProfile() {
      try {
        this.loading = true
        this.error = null
        this.successMessage = ''
        
        let endpoint = ''
        let updateData = { ...this.form }
        
        // Remove read-only fields
        delete updateData.username
        delete updateData.email
        delete updateData.user
        delete updateData.id
        
        if (this.userRole === 'patient') {
          endpoint = `/patients/${this.profileData.id}`
        } else if (this.userRole === 'doctor') {
          endpoint = `/doctors/${this.profileData.id}`
        }
        
        await axios.put(endpoint, updateData)
        this.successMessage = 'Profile updated successfully!'
        
        // Clear success message after 3 seconds
        setTimeout(() => {
          this.successMessage = ''
        }, 3000)
        
      } catch (error) {
        this.error = error.response?.data?.message || 'Failed to update profile'
      } finally {
        this.loading = false
      }
    }
  },
  async created() {
    await this.loadProfile()
  }
}
</script>

<style scoped>
.card {
  border-radius: 15px;
  border: none;
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.form-control:focus,
.form-select:focus {
  border-color: #0d6efd;
  box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25);
}

.btn-primary {
  border-radius: 8px;
  padding: 10px 20px;
}
</style>
