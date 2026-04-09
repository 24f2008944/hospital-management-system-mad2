// ===================== ADMIN DASHBOARD =====================
const AdminDashboard = {
  name: 'AdminDashboard',
  emits: ['toast'],
  data() { return { stats: null, loading: true }; },
  async mounted() {
    try {
      const res = await api.get('/admin/dashboard');
      this.stats = res.data;
    } catch(e) { this.$emit('toast', {msg: 'Failed to load dashboard', type: 'danger'}); }
    finally { this.loading = false; }
  },
  template: `
  <div>
    <h4 class="fw-bold mb-4"><i class="bi bi-speedometer2 me-2 text-primary"></i>Admin Dashboard</h4>
    <div v-if="loading" class="text-center py-5"><div class="spinner-border text-primary"></div></div>
    <div v-else-if="stats" class="row g-4">
      <div class="col-md-4">
        <div class="stat-card card text-white" style="background:linear-gradient(135deg,#1a6b8a,#27ae8f)">
          <div class="card-body d-flex justify-content-between align-items-center">
            <div><div class="stat-num">{{ stats.total_doctors }}</div><div class="stat-label">Total Doctors</div></div>
            <i class="bi bi-person-badge stat-icon"></i>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="stat-card card text-white" style="background:linear-gradient(135deg,#8e44ad,#3498db)">
          <div class="card-body d-flex justify-content-between align-items-center">
            <div><div class="stat-num">{{ stats.total_patients }}</div><div class="stat-label">Total Patients</div></div>
            <i class="bi bi-people stat-icon"></i>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="stat-card card text-white" style="background:linear-gradient(135deg,#f39c12,#e74c3c)">
          <div class="card-body d-flex justify-content-between align-items-center">
            <div><div class="stat-num">{{ stats.total_appointments }}</div><div class="stat-label">Total Appointments</div></div>
            <i class="bi bi-calendar3 stat-icon"></i>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="stat-card card" style="border-left:4px solid #3498db">
          <div class="card-body"><div class="fw-bold text-primary fs-3">{{ stats.booked_appointments }}</div>
          <div class="text-muted">Booked</div></div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="stat-card card" style="border-left:4px solid #27ae60">
          <div class="card-body"><div class="fw-bold text-success fs-3">{{ stats.completed_appointments }}</div>
          <div class="text-muted">Completed</div></div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="stat-card card" style="border-left:4px solid #e74c3c">
          <div class="card-body"><div class="fw-bold text-danger fs-3">{{ stats.cancelled_appointments }}</div>
          <div class="text-muted">Cancelled</div></div>
        </div>
      </div>
    </div>
  </div>`
};

// ===================== ADMIN DOCTORS =====================
const AdminDoctors = {
  name: 'AdminDoctors',
  emits: ['toast'],
  data() {
    return {
      doctors: [], departments: [], loading: true, showModal: false, editMode: false,
      form: { username:'', email:'', password:'', full_name:'', phone:'', specialization:'', department_id:'', qualification:'', experience_years:0, consultation_fee:500, bio:'' },
      editId: null
    };
  },
  async mounted() { await this.load(); },
  methods: {
    async load() {
      this.loading = true;
      try {
        const [dr, dep] = await Promise.all([api.get('/admin/doctors'), api.get('/admin/departments')]);
        this.doctors = dr.data; this.departments = dep.data;
      } catch(e) { this.$emit('toast', {msg:'Failed to load', type:'danger'}); }
      finally { this.loading = false; }
    },
    openAdd() {
      this.editMode = false; this.editId = null;
      this.form = { username:'', email:'', password:'', full_name:'', phone:'', specialization:'', department_id:'', qualification:'', experience_years:0, consultation_fee:500, bio:'' };
      this.showModal = true;
    },
    openEdit(d) {
      this.editMode = true; this.editId = d.id;
      this.form = { full_name:d.full_name, email:d.email, phone:d.phone, specialization:d.specialization, department_id:d.department_id, qualification:d.qualification||'', experience_years:d.experience_years||0, consultation_fee:d.consultation_fee||500, bio:d.bio||'' };
      this.showModal = true;
    },
    async save() {
      try {
        if (this.editMode) {
          await api.put(`/admin/doctors/${this.editId}`, this.form);
          this.$emit('toast', {msg:'Doctor updated'});
        } else {
          await api.post('/admin/doctors', this.form);
          this.$emit('toast', {msg:'Doctor added'});
        }
        this.showModal = false; await this.load();
      } catch(e) { this.$emit('toast', {msg: e.response?.data?.error||'Failed', type:'danger'}); }
    },
    async deactivate(id) {
      if (!confirm('Deactivate this doctor?')) return;
      try { await api.delete(`/admin/doctors/${id}`); this.$emit('toast',{msg:'Doctor deactivated'}); await this.load(); }
      catch(e) { this.$emit('toast',{msg:'Failed',type:'danger'}); }
    },
    async toggleStatus(id, currentStatus) {
      const action = currentStatus ? 'deactivate' : 'activate';
      if (!confirm(`${action.charAt(0).toUpperCase() + action.slice(1)} this doctor?`)) return;
      try { 
        await api.post(`/admin/doctors/${id}/toggle`); 
        this.$emit('toast',{msg:`Doctor ${action}d`}); 
        await this.load(); 
      }
      catch(e) { this.$emit('toast',{msg:'Failed',type:'danger'}); }
    }
  },
  template: `
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h4 class="fw-bold mb-0"><i class="bi bi-person-badge me-2 text-primary"></i>Manage Doctors</h4>
      <button class="btn btn-primary" @click="openAdd"><i class="bi bi-plus-circle me-2"></i>Add Doctor</button>
    </div>
    <div v-if="loading" class="text-center py-5"><div class="spinner-border text-primary"></div></div>
    <div v-else class="card">
      <div class="card-body p-0">
        <table class="table table-hover mb-0">
          <thead><tr>
            <th>Name</th><th>Specialization</th><th>Department</th>
            <th>Experience</th><th>Fee</th><th>Status</th><th>Actions</th>
          </tr></thead>
          <tbody>
            <tr v-for="d in doctors" :key="d.id">
              <td><strong>Dr. {{ d.full_name }}</strong><br><small class="text-muted">{{ d.email }}</small></td>
              <td>{{ d.specialization }}</td>
              <td><span class="badge bg-primary-subtle text-primary">{{ d.department }}</span></td>
              <td>{{ d.experience_years }} yrs</td>
              <td>₹{{ d.consultation_fee }}</td>
              <td><span class="badge" :class="d.is_active ? 'bg-success' : 'bg-danger'">{{ d.is_active ? 'Active' : 'Inactive' }}</span></td>
              <td>
                <button class="btn btn-sm btn-outline-primary me-1" @click="openEdit(d)"><i class="bi bi-pencil"></i></button>
                <button class="btn btn-sm" :class="d.is_active ? 'btn-outline-danger' : 'btn-outline-success'" @click="toggleStatus(d.id, d.is_active)"><i class="bi" :class="d.is_active ? 'bi-slash-circle' : 'bi-check-circle'"></i></button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="modal d-block" style="background:rgba(0,0,0,0.5)">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title fw-bold">{{ editMode ? 'Edit Doctor' : 'Add New Doctor' }}</h5>
            <button class="btn-close" @click="showModal=false"></button>
          </div>
          <div class="modal-body">
            <div class="row g-3">
              <div class="col-md-6" v-if="!editMode">
                <label class="form-label">Username *</label>
                <input v-model="form.username" class="form-control" placeholder="Username"/>
              </div>
              <div class="col-md-6" v-if="!editMode">
                <label class="form-label">Password *</label>
                <input v-model="form.password" type="password" class="form-control" placeholder="Password"/>
              </div>
              <div class="col-md-6">
                <label class="form-label">Full Name *</label>
                <input v-model="form.full_name" class="form-control" placeholder="Full name"/>
              </div>
              <div class="col-md-6">
                <label class="form-label">Email *</label>
                <input v-model="form.email" type="email" class="form-control" placeholder="Email"/>
              </div>
              <div class="col-md-6">
                <label class="form-label">Phone</label>
                <input v-model="form.phone" class="form-control" placeholder="Phone"/>
              </div>
              <div class="col-md-6">
                <label class="form-label">Department *</label>
                <select v-model="form.department_id" class="form-select">
                  <option value="">Select department</option>
                  <option v-for="d in departments" :key="d.id" :value="d.id">{{ d.name }}</option>
                </select>
              </div>
              <div class="col-md-6">
                <label class="form-label">Specialization *</label>
                <input v-model="form.specialization" class="form-control" placeholder="e.g. Cardiologist"/>
              </div>
              <div class="col-md-6">
                <label class="form-label">Qualification</label>
                <input v-model="form.qualification" class="form-control" placeholder="e.g. MBBS, MD"/>
              </div>
              <div class="col-md-6">
                <label class="form-label">Experience (years)</label>
                <input v-model.number="form.experience_years" type="number" class="form-control"/>
              </div>
              <div class="col-md-6">
                <label class="form-label">Consultation Fee (₹)</label>
                <input v-model.number="form.consultation_fee" type="number" class="form-control"/>
              </div>
              <div class="col-12">
                <label class="form-label">Bio</label>
                <textarea v-model="form.bio" class="form-control" rows="2"></textarea>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showModal=false">Cancel</button>
            <button class="btn btn-primary" @click="save">{{ editMode ? 'Update' : 'Add Doctor' }}</button>
          </div>
        </div>
      </div>
    </div>
  </div>`
};

// ===================== ADMIN PATIENTS =====================
const AdminPatients = {
  name: 'AdminPatients',
  emits: ['toast'],
  data() { 
    return { 
      patients: [], 
      loading: true,
      showModal: false,
      editId: null,
      form: { full_name: '', email: '', phone: '', gender: '', blood_group: '', address: '' }
    }; 
  },
  async mounted() { await this.load(); },
  methods: {
    async load() {
      this.loading = true;
      try { const res = await api.get('/admin/patients'); this.patients = res.data; }
      catch(e) { this.$emit('toast',{msg:'Failed',type:'danger'}); }
      finally { this.loading = false; }
    },
    openEdit(p) {
      this.editId = p.id;
      this.form = { 
        full_name: p.full_name || '', 
        email: p.email || '', 
        phone: p.phone || '', 
        gender: p.gender || '', 
        blood_group: p.blood_group || '', 
        address: p.address || '' 
      };
      this.showModal = true;
    },
    async save() {
      try {
        await api.put(`/admin/patients/${this.editId}`, this.form);
        this.$emit('toast', {msg: 'Patient profile updated'});
        this.showModal = false;
        await this.load();
      } catch(e) {
        this.$emit('toast', {msg: e.response?.data?.error || 'Failed to update', type: 'danger'});
      }
    },
    async toggle(id) {
      try { await api.post(`/admin/patients/${id}/toggle`); this.$emit('toast',{msg:'Status updated'}); await this.load(); }
      catch(e) { this.$emit('toast',{msg:'Failed',type:'danger'}); }
    }
  },
  template: `
  <div>
    <h4 class="fw-bold mb-4"><i class="bi bi-people me-2 text-primary"></i>All Patients</h4>
    <div v-if="loading" class="text-center py-5"><div class="spinner-border text-primary"></div></div>
    <div v-else class="card">
      <div class="card-body p-0">
        <table class="table table-hover mb-0">
          <thead><tr><th>Name</th><th>Email</th><th>Phone</th><th>Gender</th><th>Blood Group</th><th>Status</th><th>Actions</th></tr></thead>
          <tbody>
            <tr v-for="p in patients" :key="p.id">
              <td><strong>{{ p.full_name }}</strong></td>
              <td>{{ p.email }}</td>
              <td>{{ p.phone || '-' }}</td>
              <td>{{ p.gender || '-' }}</td>
              <td>{{ p.blood_group || '-' }}</td>
              <td><span class="badge" :class="p.is_active ? 'bg-success' : 'bg-danger'">{{ p.is_active ? 'Active' : 'Blacklisted' }}</span></td>
              <td>
                <button class="btn btn-sm btn-outline-primary me-1" @click="openEdit(p)"><i class="bi bi-pencil"></i></button>
                <button class="btn btn-sm" :class="p.is_active ? 'btn-outline-danger' : 'btn-outline-success'" @click="toggle(p.id)">
                  {{ p.is_active ? 'Blacklist' : 'Activate' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Edit Patient Modal -->
    <div v-if="showModal" class="modal d-block" style="background:rgba(0,0,0,0.5)">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title fw-bold">Edit Patient Profile</h5>
            <button class="btn-close" @click="showModal=false"></button>
          </div>
          <div class="modal-body">
            <div class="row g-3">
              <div class="col-md-6">
                <label class="form-label">Full Name *</label>
                <input v-model="form.full_name" class="form-control" placeholder="Full name"/>
              </div>
              <div class="col-md-6">
                <label class="form-label">Email *</label>
                <input v-model="form.email" type="email" class="form-control" placeholder="Email"/>
              </div>
              <div class="col-md-6">
                <label class="form-label">Phone</label>
                <input v-model="form.phone" class="form-control" placeholder="Phone number"/>
              </div>
              <div class="col-md-6">
                <label class="form-label">Gender</label>
                <select v-model="form.gender" class="form-select">
                  <option value="">Select gender</option>
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                </select>
              </div>
              <div class="col-md-6">
                <label class="form-label">Blood Group</label>
                <select v-model="form.blood_group" class="form-select">
                  <option value="">Select blood group</option>
                  <option value="O+">O+</option>
                  <option value="O-">O-</option>
                  <option value="A+">A+</option>
                  <option value="A-">A-</option>
                  <option value="B+">B+</option>
                  <option value="B-">B-</option>
                  <option value="AB+">AB+</option>
                  <option value="AB-">AB-</option>
                </select>
              </div>
              <div class="col-12">
                <label class="form-label">Address</label>
                <textarea v-model="form.address" class="form-control" rows="2" placeholder="Street address"></textarea>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showModal=false">Cancel</button>
            <button class="btn btn-primary" @click="save">Update Profile</button>
          </div>
        </div>
      </div>
    </div>
  </div>`
};

// ===================== ADMIN APPOINTMENTS =====================
const AdminAppointments = {
  name: 'AdminAppointments',
  emits: ['toast'],
  data() { return { appointments: [], loading: true }; },
  async mounted() {
    try { const res = await api.get('/admin/appointments'); this.appointments = res.data; }
    catch(e) { this.$emit('toast',{msg:'Failed',type:'danger'}); }
    finally { this.loading = false; }
  },
  methods: {
    badgeClass(s) { return s==='Booked'?'badge-booked':s==='Completed'?'badge-completed':'badge-cancelled'; }
  },
  template: `
  <div>
    <h4 class="fw-bold mb-4"><i class="bi bi-calendar3 me-2 text-primary"></i>All Appointments</h4>
    <div v-if="loading" class="text-center py-5"><div class="spinner-border text-primary"></div></div>
    <div v-else class="card">
      <div class="card-body p-0">
        <table class="table table-hover mb-0">
          <thead><tr><th>Patient</th><th>Doctor</th><th>Department</th><th>Date</th><th>Time</th><th>Status</th><th>Reason</th></tr></thead>
          <tbody>
            <tr v-for="a in appointments" :key="a.id">
              <td>{{ a.patient_name }}</td>
              <td>Dr. {{ a.doctor_name }}</td>
              <td>{{ a.department }}</td>
              <td>{{ a.date }}</td>
              <td>{{ a.time }}</td>
              <td><span class="badge" :class="badgeClass(a.status)">{{ a.status }}</span></td>
              <td>{{ a.reason || '-' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>`
};

// ===================== ADMIN SEARCH =====================
const AdminSearch = {
  name: 'AdminSearch',
  emits: ['toast'],
  data() { return { q: '', type: 'all', results: null, loading: false }; },
  methods: {
    async search() {
      if (!this.q.trim()) return;
      this.loading = true;
      try { const res = await api.get('/admin/search', {params:{q:this.q, type:this.type}}); this.results = res.data; }
      catch(e) { this.$emit('toast',{msg:'Search failed',type:'danger'}); }
      finally { this.loading = false; }
    }
  },
  template: `
  <div>
    <h4 class="fw-bold mb-4"><i class="bi bi-search me-2 text-primary"></i>Search</h4>
    <div class="card mb-4">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-6">
            <input v-model="q" class="form-control" placeholder="Search by name, email, specialization..." @keyup.enter="search"/>
          </div>
          <div class="col-md-3">
            <select v-model="type" class="form-select">
              <option value="all">All</option>
              <option value="doctor">Doctors</option>
              <option value="patient">Patients</option>
            </select>
          </div>
          <div class="col-md-3">
            <button class="btn btn-primary w-100" @click="search" :disabled="loading">
              <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>Search
            </button>
          </div>
        </div>
      </div>
    </div>
    <div v-if="results">
      <div v-if="results.doctors && results.doctors.length" class="mb-4">
        <h6 class="fw-bold text-primary">Doctors ({{ results.doctors.length }})</h6>
        <div class="card"><div class="card-body p-0">
          <table class="table mb-0"><thead><tr><th>Name</th><th>Specialization</th><th>Department</th><th>Experience</th></tr></thead>
          <tbody><tr v-for="d in results.doctors" :key="d.id">
            <td>Dr. {{ d.full_name }}</td><td>{{ d.specialization }}</td>
            <td>{{ d.department }}</td><td>{{ d.experience_years }} yrs</td>
          </tr></tbody></table>
        </div></div>
      </div>
      <div v-if="results.patients && results.patients.length">
        <h6 class="fw-bold text-primary">Patients ({{ results.patients.length }})</h6>
        <div class="card"><div class="card-body p-0">
          <table class="table mb-0"><thead><tr><th>Name</th><th>Email</th><th>Phone</th><th>Status</th></tr></thead>
          <tbody><tr v-for="p in results.patients" :key="p.id">
            <td>{{ p.full_name }}</td><td>{{ p.email }}</td>
            <td>{{ p.phone||'-' }}</td>
            <td><span class="badge" :class="p.is_active?'bg-success':'bg-danger'">{{ p.is_active?'Active':'Inactive' }}</span></td>
          </tr></tbody></table>
        </div></div>
      </div>
      <p v-if="(!results.doctors||!results.doctors.length) && (!results.patients||!results.patients.length)" class="text-muted text-center py-3">No results found.</p>
    </div>
  </div>`
};
