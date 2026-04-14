<template>
  <div class="min-vh-100 d-flex align-items-center bg-light">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-6 col-lg-4">
          <div class="card shadow">
            <div class="card-body p-4">
              <div class="text-center mb-4">
                <i class="bi bi-hospital text-primary" style="font-size: 3rem;"></i>
                <h3 class="mt-2">Hospital Management</h3>
                <p class="text-muted">Sign in to your account</p>
              </div>

              <form @submit.prevent="handleLogin">
                <div class="mb-3">
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

                <div class="mb-3">
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

                <div v-if="error" class="alert alert-danger">
                  {{ error }}
                </div>

                <button
                  type="submit"
                  class="btn btn-primary w-100 mb-3"
                  :disabled="loading"
                >
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                  Sign In
                </button>
              </form>

              <div class="text-center">
                <p class="text-muted">
                  Don't have an account?
                  <router-link to="/register" class="text-decoration-none">Register here</router-link>
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
  name: 'LoginView',
  data() {
    return {
      form: {
        email: '',
        password: ''
      },
      errors: {}
    }
  },
  computed: {
    ...mapState('auth', ['loading', 'error'])
  },
  methods: {
    ...mapActions('auth', ['login']),
    
    async handleLogin() {
      this.errors = {}
      
      // Basic validation
      if (!this.form.email) {
        this.errors.email = 'Email is required'
        return
      }
      if (!this.form.password) {
        this.errors.password = 'Password is required'
        return
      }
      
      const result = await this.login(this.form)
      
      if (result.success) {
        this.$router.push('/dashboard')
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

.form-control:focus {
  border-color: #0d6efd;
  box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25);
}

.btn-primary {
  border-radius: 10px;
  padding: 12px;
  font-weight: 600;
}
</style>
