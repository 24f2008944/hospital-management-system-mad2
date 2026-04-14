<template>
  <div id="app">
    <!-- Navigation Bar -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary" v-if="isAuthenticated">
      <div class="container">
        <a class="navbar-brand" href="#">
          <i class="bi bi-hospital"></i>
          Hospital Management
        </a>
        
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>
        
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav me-auto">
            <li class="nav-item">
              <router-link class="nav-link" to="/dashboard">
                <i class="bi bi-speedometer2"></i>
                Dashboard
              </router-link>
            </li>
            
            <!-- Admin Navigation -->
            <template v-if="userRole === 'admin'">
              <li class="nav-item dropdown">
                <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown">
                  <i class="bi bi-people"></i>
                  Manage
                </a>
                <ul class="dropdown-menu">
                  <li><router-link class="dropdown-item" to="/doctors">Doctors</router-link></li>
                  <li><router-link class="dropdown-item" to="/patients">Patients</router-link></li>
                  <li><router-link class="dropdown-item" to="/departments">Departments</router-link></li>
                </ul>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/appointments">
                  <i class="bi bi-calendar-check"></i>
                  All Appointments
                </router-link>
              </li>
            </template>
            
            <!-- Doctor Navigation -->
            <template v-if="userRole === 'doctor'">
              <li class="nav-item">
                <router-link class="nav-link" to="/my-appointments">
                  <i class="bi bi-calendar-check"></i>
                  My Appointments
                </router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/availability">
                  <i class="bi bi-calendar-week"></i>
                  Manage Availability
                </router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/my-patients">
                  <i class="bi bi-person-hearts"></i>
                  My Patients
                </router-link>
              </li>
            </template>
            
            <!-- Patient Navigation -->
            <template v-if="userRole === 'patient'">
              <li class="nav-item">
                <router-link class="nav-link" to="/book-appointment">
                  <i class="bi bi-calendar-plus"></i>
                  Book Appointment
                </router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/my-appointments">
                  <i class="bi bi-calendar-check"></i>
                  My Appointments
                </router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/treatment-history">
                  <i class="bi bi-clipboard-data"></i>
                  Treatment History
                </router-link>
              </li>
            </template>
          </ul>
          
          <!-- User Menu -->
          <ul class="navbar-nav">
            <li class="nav-item dropdown">
              <a class="nav-link dropdown-toggle" href="#" data-bs-toggle="dropdown">
                <i class="bi bi-person-circle"></i>
                {{ user?.username || user?.email }}
              </a>
              <ul class="dropdown-menu">
                <li><router-link class="dropdown-item" to="/profile">Profile</router-link></li>
                <li><hr class="dropdown-divider"></li>
                <li><a class="dropdown-item" href="#" @click="handleLogout">Logout</a></li>
              </ul>
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="container-fluid p-0">
      <router-view></router-view>
    </main>

    <!-- Footer -->
    <footer class="bg-light text-center text-muted py-3 mt-5" v-if="isAuthenticated">
      <div class="container">
        <p>&copy; 2025 Hospital Management System. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'

export default {
  name: 'App',
  computed: {
    ...mapState('auth', ['user', 'isAuthenticated']),
    userRole() {
      return this.user?.roles?.[0] || null
    }
  },
  methods: {
    ...mapActions('auth', ['logout']),
    async handleLogout() {
      await this.logout()
      this.$router.push('/login')
    }
  },
  async created() {
    // Check if user is already logged in
    const user = localStorage.getItem('user')
    if (user && !this.isAuthenticated) {
      try {
        await this.$store.dispatch('auth/loadUser')
      } catch (error) {
        localStorage.removeItem('token')
        this.$router.push('/login')
      }
    }
  }
}
</script>

<style>
#app {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

main {
  flex: 1;
}

.navbar-brand {
  font-weight: bold;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  border: 1px solid rgba(0, 0, 0, 0.125);
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.table th {
  border-top: none;
  font-weight: 600;
}

.badge {
  font-size: 0.75em;
}

.text-success { color: #198754 !important; }
.text-warning { color: #ffc107 !important; }
.text-danger { color: #dc3545 !important; }
.text-info { color: #0dcaf0 !important; }

/* Loading spinner */
.spinner-border-sm {
  width: 1rem;
  height: 1rem;
}

/* Custom animations */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
