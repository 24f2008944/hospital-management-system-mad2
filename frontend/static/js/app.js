// ========================= ROUTER SETUP =========================
const { createRouter, createWebHashHistory } = VueRouter;
const { createApp, ref, computed, onMounted } = Vue;

const routes = [
  { path: '/', redirect: () => {
    const user = JSON.parse(localStorage.getItem('hms_user') || 'null');
    if (!user) return '/login';
    return user.role === 'admin' ? '/admin' : user.role === 'doctor' ? '/doctor' : '/patient';
  }},
  { path: '/login', component: LoginPage },
  { path: '/register', component: RegisterPage },
  // Admin
  { path: '/admin', component: AdminDashboard },
  { path: '/admin/doctors', component: AdminDoctors },
  { path: '/admin/patients', component: AdminPatients },
  { path: '/admin/appointments', component: AdminAppointments },
  { path: '/admin/search', component: AdminSearch },
  // Doctor
  { path: '/doctor', component: DoctorDashboard },
  { path: '/doctor/appointments', component: DoctorAppointments },
  { path: '/doctor/patients', component: DoctorPatients },
  { path: '/doctor/availability', component: DoctorAvailability },
  // Patient
  { path: '/patient', component: PatientDashboard },
  { path: '/patient/doctors', component: FindDoctors },
  { path: '/patient/appointments', component: PatientAppointments },
  { path: '/patient/history', component: PatientHistory },
  { path: '/patient/profile', component: PatientProfile },
  { path: '/patient/export', component: PatientExport },
];

const router = createRouter({ history: createWebHashHistory(), routes });

// ========================= ROOT APP =========================
const App = {
  name: 'App',
  components: { ToastComp, NavbarComp, SidebarComp },
  setup() {
    const user = ref(JSON.parse(localStorage.getItem('hms_user') || 'null'));
    const toasts = ref([]);
    let toastId = 0;

    const isAuth = computed(() => !!user.value);
    const isPublic = computed(() => {
      const h = window.location.hash;
      return h === '#/login' || h === '#/register' || h === '' || h === '#/';
    });

    function addToast(t) {
      const id = ++toastId;
      toasts.value.push({...t, id});
      setTimeout(() => dismissToast(id), 4000);
    }
    function dismissToast(id) {
      toasts.value = toasts.value.filter(t => t.id !== id);
    }

    function onLoggedIn(u) {
      user.value = u;
      const dest = u.role === 'admin' ? '/admin' : u.role === 'doctor' ? '/doctor' : '/patient';
      router.push(dest);
    }

    function logout() {
      localStorage.removeItem('hms_token');
      localStorage.removeItem('hms_user');
      user.value = null;
      router.push('/login');
    }

    function navigate(path) {
      router.push(path);
    }

    // Route guard
    router.beforeEach((to, from, next) => {
      const publicPaths = ['/login', '/register'];
      if (publicPaths.includes(to.path)) { next(); return; }
      const u = JSON.parse(localStorage.getItem('hms_user') || 'null');
      if (!u) { next('/login'); return; }
      // Role guards
      if (to.path.startsWith('/admin') && u.role !== 'admin') { next('/login'); return; }
      if (to.path.startsWith('/doctor') && u.role !== 'doctor') { next('/login'); return; }
      if (to.path.startsWith('/patient') && u.role !== 'patient') { next('/login'); return; }
      next();
    });

    const currentPath = ref('/');
    router.afterEach((to) => { currentPath.value = to.path; });

    return { user, toasts, isAuth, addToast, dismissToast, onLoggedIn, logout, navigate, currentPath };
  },
  template: `
  <div>
    <ToastComp :toasts="toasts" @dismiss="dismissToast"/>
    
    <!-- Auth pages (no layout) -->
    <template v-if="!user || currentPath==='/login' || currentPath==='/register'">
      <router-view @logged-in="onLoggedIn" @toast="addToast"/>
    </template>

    <!-- App layout -->
    <template v-else>
      <NavbarComp :user="user" @logout="logout"/>
      <SidebarComp :role="user.role" :current="currentPath" @navigate="navigate"/>
      <div class="main-content">
        <router-view @toast="addToast" @navigate="navigate"/>
      </div>
    </template>
  </div>`
};

const app = createApp(App);
app.use(router);
app.mount('#app');
