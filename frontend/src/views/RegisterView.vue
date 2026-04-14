<template>
  <div class="min-vh-100 d-flex align-items-center bg-light">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-8 col-lg-6">
          <div class="card shadow">
            <div class="card-body p-4">
              <div class="text-center mb-4">
                <i class="bi bi-person-plus text-primary" style="font-size: 3rem;"></i>
                <h3 class="mt-2">Patient Registration</h3>
                <p class="text-muted">Create your account</p>
              </div>

              <form @submit.prevent="handleRegister">
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label for="email" class="form-label">Email</label>
                    <input
                      type="email"
                      id="email"
                      v-model="form.email"
                      class="form-control"
                      :class="{ 'is-invalid': errors.email }"
                      required
                    >
                    <div v-if="errors.email" class="invalid-feedback">
                      {{ errors.email }}
                    </div>
                  </div>

                  <div class="col-md-6 mb-3">
                    <label for="username" class="form-label">Username</label>
                    <input
                      type="text"
                      id="username"
                      v-model="form.username"
                      class="form-control"
                      :class="{ 'is-invalid': errors.username }"
                      required
                    >
                    <div v-if="errors.username" class="invalid-feedback">
                      {{ errors.username }}
                    </div>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label for="password" class="form-label">Password</label>
                    <input
                      type="password"
                      id="password"
                      v-model="form.password"
                      class="form-control"
                      :class="{ 'is-invalid': errors.password }"
                      required
                    >
                    <div v-if="errors.password" class="invalid-feedback">
                      {{ errors.password }}
                    </div>
                  </div>

                  <div class="col-md-6 mb-3">
                    <label for="confirmPassword" class="form-label">Confirm Password</label>
                    <input
                      type="password"
                      id="confirmPassword"
                      v-model="form.confirmPassword"
                      class="form-control"
                      :class="{ 'is-invalid': errors.confirmPassword }"
                      required
                    >
                    <div v-if="errors.confirmPassword" class="invalid-feedback">
                      {{ errors.confirmPassword }}
                    </div>
                  </div>
                </div>

                <div class="mb-3">
                  <label for="role" class="form-label">Register as</label>
                  <select
                    id="role"
                    v-model="form.role"
                    class="form-select"
                    required
                  >
                    <option value="patient">Patient</option>
                  </select>
                  <div class="form-text">
                    Note: Doctor accounts are created by administrators
                  </div>
                </div>

                <div v-if="error" class="alert alert-danger">
                  {{ error }}
                </div>

                <div v-if="successMessage" class="alert alert-success">
                  {{ successMessage }}
                </div>

                <button
                  type="submit"
                  class="btn btn-primary w-100 mb-3"
                  :disabled="loading"
                >
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                  Register
                </button>
              </form>

              <div class="text-center">
                <p class="text-muted">
                  Already have an account?
                  <router-link to="/login" class="text-decoration-none">Sign in here</router-link>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'

export default {
  name: 'RegisterView',
  data() {
    return {
      form: {
        email: '',
        username: '',
        password: '',
        confirmPassword: '',
        role: 'patient'
      },
      errors: {},
      successMessage: ''
    }
  },
  computed: {
    ...mapState('auth', ['loading', 'error'])
  },
  methods: {
    ...mapActions('auth', ['register']),
    
    async handleRegister() {
      this.errors = {}
      this.successMessage = ''
      
      // Validation
      if (!this.form.email) {
        this.errors.email = 'Email is required'
        return
      }
      if (!this.form.username) {
        this.errors.username = 'Username is required'
        return
      }
      if (!this.form.password) {
        this.errors.password = 'Password is required'
        return
      }
      if (this.form.password.length < 6) {
        this.errors.password = 'Password must be at least 6 characters'
        return
      }
      if (this.form.password !== this.form.confirmPassword) {
        this.errors.confirmPassword = 'Passwords do not match'
        return
      }
      
      const result = await this.register({
        email: this.form.email,
        username: this.form.username,
        password: this.form.password,
        role: this.form.role
      })
      
      if (result.success) {
        this.successMessage = 'Registration successful! You can now sign in.'
        this.form = {
          email: '',
          username: '',
          password: '',
          confirmPassword: '',
          role: 'patient'
        }
        
        // Redirect to login after 2 seconds
        setTimeout(() => {
          this.$router.push('/login')
        }, 2000)
      }
    }
  }
}
</script>

<style scoped>
.card {
  border: none;
  border-radius: 15px;
}

.form-control:focus,
.form-select:focus {
  border-color: #0d6efd;
  box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25);
}

.btn-primary {
  border-radius: 10px;
  padding: 12px;
  font-weight: 600;
}
</style>
