// ===================== API SERVICE =====================
const API_BASE = '/api';
const api = axios.create({ baseURL: API_BASE });
api.interceptors.request.use(config => {
  const token = localStorage.getItem('hms_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});
api.interceptors.response.use(r => r, err => {
  if (err.response?.status === 401) {
    localStorage.removeItem('hms_token');
    localStorage.removeItem('hms_user');
    window.location.hash = '#/login';
  }
  return Promise.reject(err);
});

// ===================== TOAST =====================
const ToastComp = {
  name: 'ToastComp',
  props: ['toasts'],
  template: `
  <div class="toast-container">
    <div v-for="t in toasts" :key="t.id" class="toast show align-items-center border-0 mb-2"
         :class="'text-bg-' + (t.type||'success')">
      <div class="d-flex">
        <div class="toast-body">{{ t.msg }}</div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" @click="$emit('dismiss',t.id)"></button>
      </div>
    </div>
  </div>`
};

// ===================== NAVBAR =====================
const NavbarComp = {
  name: 'NavbarComp',
  props: ['user'],
  emits: ['logout'],
  template: `
  <nav class="navbar navbar-expand-lg navbar-custom fixed-top">
    <div class="container-fluid px-4">
      <a class="navbar-brand"><i class="bi bi-heart-pulse-fill me-2"></i>HealthCare HMS</a>
      <div class="ms-auto d-flex align-items-center gap-3">
        <span class="text-white opacity-75 small d-none d-md-block">
          <i class="bi bi-person-circle me-1"></i>{{ user?.full_name }}
          <span class="badge bg-white text-primary ms-1">{{ user?.role }}</span>
        </span>
        <button class="btn btn-sm btn-outline-light" @click="$emit('logout')">
          <i class="bi bi-box-arrow-right me-1"></i>Logout
        </button>
      </div>
    </div>
  </nav>`
};

// ===================== SIDEBAR =====================
const SidebarComp = {
  name: 'SidebarComp',
  props: ['role', 'current'],
  emits: ['navigate'],
  computed: {
    links() {
      const adminLinks = [
        { to: '/admin', icon: 'bi-speedometer2', label: 'Dashboard' },
        { to: '/admin/doctors', icon: 'bi-person-badge', label: 'Doctors' },
        { to: '/admin/patients', icon: 'bi-people', label: 'Patients' },
        { to: '/admin/appointments', icon: 'bi-calendar3', label: 'Appointments' },
        { to: '/admin/search', icon: 'bi-search', label: 'Search' },
      ];
      const doctorLinks = [
        { to: '/doctor', icon: 'bi-speedometer2', label: 'Dashboard' },
        { to: '/doctor/appointments', icon: 'bi-calendar3', label: 'Appointments' },
        { to: '/doctor/patients', icon: 'bi-people', label: 'My Patients' },
        { to: '/doctor/availability', icon: 'bi-clock', label: 'Availability' },
      ];
      const patientLinks = [
        { to: '/patient', icon: 'bi-speedometer2', label: 'Dashboard' },
        { to: '/patient/doctors', icon: 'bi-person-badge', label: 'Find Doctors' },
        { to: '/patient/appointments', icon: 'bi-calendar3', label: 'Appointments' },
        { to: '/patient/history', icon: 'bi-clock-history', label: 'History' },
        { to: '/patient/profile', icon: 'bi-person', label: 'Profile' },
        { to: '/patient/export', icon: 'bi-download', label: 'Export Records' },
      ];
      return this.role === 'admin' ? adminLinks : this.role === 'doctor' ? doctorLinks : patientLinks;
    }
  },
  template: `
  <div class="sidebar d-flex flex-column">
    <ul class="nav flex-column mt-2">
      <li class="nav-item" v-for="link in links" :key="link.to">
        <a class="nav-link" :class="{active: current===link.to}" href="#"
           @click.prevent="$emit('navigate', link.to)">
          <i class="bi" :class="link.icon"></i>{{ link.label }}
        </a>
      </li>
    </ul>
  </div>`
};

// ===================== LOGIN =====================
const LoginPage = {
  name: 'LoginPage',
  emits: ['logged-in', 'toast'],
  data() {
    return { username: '', password: '', loading: false, error: '' };
  },
  template: `
  <div class="auth-wrapper">
    <div class="auth-card">
      <div class="auth-header">
        <div class="logo"><i class="bi bi-heart-pulse-fill"></i></div>
        <h3 class="mt-2 fw-bold">HealthCare HMS</h3>
        <p class="mb-0 opacity-75">Hospital Management System</p>
      </div>
      <div class="auth-body">
        <h5 class="fw-semibold mb-4 text-center">Sign In</h5>
        <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>
        <div class="mb-3">
          <label class="form-label fw-medium">Username / Email</label>
          <input v-model="username" type="text" class="form-control" placeholder="Enter username or email"
                 @keyup.enter="login" required/>
        </div>
        <div class="mb-4">
          <label class="form-label fw-medium">Password</label>
          <input v-model="password" type="password" class="form-control" placeholder="Enter password"
                 @keyup.enter="login" required/>
        </div>
        <button class="btn btn-auth w-100" @click="login" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          {{ loading ? 'Signing in...' : 'Sign In' }}
        </button>
        <hr class="my-4"/>
        <p class="text-center text-muted mb-0">New patient?
          <a href="#/register" class="text-primary fw-medium">Register here</a>
        </p>
        <div class="mt-3 p-2 bg-light rounded small text-muted text-center">
          <strong>Demo:</strong> admin / admin123
        </div>
      </div>
    </div>
  </div>`,
  methods: {
    async login() {
      if (!this.username || !this.password) { this.error = 'All fields required'; return; }
      this.loading = true; this.error = '';
      try {
        const res = await api.post('/auth/login', { username: this.username, password: this.password });
        localStorage.setItem('hms_token', res.data.token);
        localStorage.setItem('hms_user', JSON.stringify(res.data.user));
        this.$emit('logged-in', res.data.user);
      } catch (e) {
        this.error = e.response?.data?.error || 'Login failed';
      } finally { this.loading = false; }
    }
  }
};

// ===================== REGISTER =====================
const RegisterPage = {
  name: 'RegisterPage',
  emits: ['logged-in', 'toast'],
  data() {
    return {
      form: { username: '', email: '', password: '', full_name: '', phone: '', gender: '', blood_group: '' },
      loading: false, error: ''
    };
  },
  template: `
  <div class="auth-wrapper">
    <div class="auth-card" style="max-width:480px">
      <div class="auth-header">
        <div class="logo"><i class="bi bi-person-plus-fill"></i></div>
        <h3 class="mt-2 fw-bold">Patient Registration</h3>
      </div>
      <div class="auth-body">
        <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>
        <div class="row g-3">
          <div class="col-12">
            <label class="form-label fw-medium">Full Name *</label>
            <input v-model="form.full_name" class="form-control" placeholder="Enter full name" required/>
          </div>
          <div class="col-md-6">
            <label class="form-label fw-medium">Username *</label>
            <input v-model="form.username" class="form-control" placeholder="Choose username" required/>
          </div>
          <div class="col-md-6">
            <label class="form-label fw-medium">Email *</label>
            <input v-model="form.email" type="email" class="form-control" placeholder="Email address" required/>
          </div>
          <div class="col-md-6">
            <label class="form-label fw-medium">Password *</label>
            <input v-model="form.password" type="password" class="form-control" placeholder="Password" required/>
          </div>
          <div class="col-md-6">
            <label class="form-label fw-medium">Phone</label>
            <input v-model="form.phone" class="form-control" placeholder="Phone number"/>
          </div>
          <div class="col-md-6">
            <label class="form-label fw-medium">Gender</label>
            <select v-model="form.gender" class="form-select">
              <option value="">Select</option>
              <option>Male</option><option>Female</option><option>Other</option>
            </select>
          </div>
          <div class="col-md-6">
            <label class="form-label fw-medium">Blood Group</label>
            <select v-model="form.blood_group" class="form-select">
              <option value="">Select</option>
              <option v-for="bg in ['A+','A-','B+','B-','AB+','AB-','O+','O-']" :key="bg">{{ bg }}</option>
            </select>
          </div>
        </div>
        <button class="btn btn-auth w-100 mt-4" @click="register" :disabled="loading">
          <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
          {{ loading ? 'Creating Account...' : 'Create Account' }}
        </button>
        <p class="text-center mt-3 mb-0 text-muted">Already have an account?
          <a href="#/login" class="text-primary fw-medium">Login here</a>
        </p>
      </div>
    </div>
  </div>`,
  methods: {
    async register() {
      const req = ['username','email','password','full_name'];
      for (const f of req) { if (!this.form[f]) { this.error = `${f} is required`; return; } }
      this.loading = true; this.error = '';
      try {
        await api.post('/auth/register', this.form);
        this.$emit('toast', {msg: 'Registration successful! Please login with your credentials.', type: 'success'});
        window.location.hash = '#/login';
      } catch (e) {
        this.error = e.response?.data?.error || 'Registration failed';
      } finally { this.loading = false; }
    }
  }
};
