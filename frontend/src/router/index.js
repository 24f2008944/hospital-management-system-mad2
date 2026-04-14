import { createRouter, createWebHistory } from 'vue-router'
import store from '../store'

// Import views
const LoginView = () => import('../views/LoginView.vue')
const RegisterView = () => import('../views/RegisterView.vue')
const DashboardView = () => import('../views/DashboardView.vue')
const ProfileView = () => import('../views/ProfileView.vue')

// Admin views
const DoctorsView = () => import('../views/admin/DoctorsView.vue')
const PatientsView = () => import('../views/admin/PatientsView.vue')
const DepartmentsView = () => import('../views/admin/DepartmentsView.vue')
const AppointmentsView = () => import('../views/admin/AppointmentsView.vue')
const BlacklistedDoctorsView = () => import('../views/admin/BlacklistedDoctorsView.vue')
const BlacklistedPatientsView = () => import('../views/admin/BlacklistedPatientsView.vue')

// Doctor views
const DoctorAppointmentsView = () => import('../views/doctor/AppointmentsView.vue')
const DoctorPatientsView = () => import('../views/doctor/PatientsView.vue')
const TreatmentView = () => import('../views/doctor/TreatmentView.vue')
const DoctorAvailabilityView = () => import('../components/DoctorAvailabilityView.vue')

// Patient views
const BookAppointmentView = () => import('../views/patient/BookAppointmentView.vue')
const PatientAppointmentsView = () => import('../views/patient/AppointmentsView.vue')
const TreatmentHistoryView = () => import('../views/patient/TreatmentHistoryView.vue')

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: { requiresGuest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterView,
    meta: { requiresGuest: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: DashboardView,
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: ProfileView,
    meta: { requiresAuth: true }
  },
  
  // Admin routes
  {
    path: '/doctors',
    name: 'Doctors',
    component: DoctorsView,
    meta: { requiresAuth: true, roles: ['admin'] }
  },
  {
    path: '/patients',
    name: 'Patients',
    component: PatientsView,
    meta: { requiresAuth: true, roles: ['admin'] }
  },
  {
    path: '/departments',
    name: 'Departments',
    component: DepartmentsView,
    meta: { requiresAuth: true, roles: ['admin'] }
  },
  {
    path: '/appointments',
    name: 'AllAppointments',
    component: AppointmentsView,
    meta: { requiresAuth: true, roles: ['admin'] }
  },
  {
    path: '/blacklisted-doctors',
    name: 'BlacklistedDoctors',
    component: BlacklistedDoctorsView,
    meta: { requiresAuth: true, roles: ['admin'] }
  },
  {
    path: '/blacklisted-patients',
    name: 'BlacklistedPatients',
    component: BlacklistedPatientsView,
    meta: { requiresAuth: true, roles: ['admin'] }
  },
  
  // Doctor routes
  {
    path: '/my-appointments',
    name: 'MyAppointments',
    component: DoctorAppointmentsView,
    meta: { requiresAuth: true, roles: ['doctor'] }
  },
  {
    path: '/availability',
    name: 'DoctorAvailability',
    component: DoctorAvailabilityView,
    meta: { requiresAuth: true, roles: ['doctor'] }
  },
  {
    path: '/my-patients',
    name: 'MyPatients',
    component: DoctorPatientsView,
    meta: { requiresAuth: true, roles: ['doctor'] }
  },
  {
    path: '/treatment/:appointmentId',
    name: 'Treatment',
    component: TreatmentView,
    meta: { requiresAuth: true, roles: ['doctor'] }
  },
  
  // Patient routes
  {
    path: '/book-appointment',
    name: 'BookAppointment',
    component: BookAppointmentView,
    meta: { requiresAuth: true, roles: ['patient'] }
  },
  {
    path: '/my-appointments',
    name: 'PatientAppointments',
    component: PatientAppointmentsView,
    meta: { requiresAuth: true, roles: ['patient'] }
  },
  {
    path: '/treatment-history',
    name: 'TreatmentHistory',
    component: TreatmentHistoryView,
    meta: { requiresAuth: true, roles: ['patient'] }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
  const isAuthenticated = store.state.auth.isAuthenticated
  const user = store.state.auth.user
  
  // Check if route requires authentication
  if (to.meta.requiresAuth && !isAuthenticated) {
    return next('/login')
  }
  
  // Check if route requires guest (not logged in)
  if (to.meta.requiresGuest && isAuthenticated) {
    return next('/dashboard')
  }
  
  // Check role-based access
  if (to.meta.roles && user) {
    const userRoles = user.roles || []
    const hasRequiredRole = to.meta.roles.some(role => userRoles.includes(role))
    
    if (!hasRequiredRole) {
      return next('/dashboard')
    }
  }
  
  next()
})

export default router
