// ===================== PATIENT DASHBOARD =====================
const PatientDashboard = {
  name: 'PatientDashboard',
  emits: ['toast', 'navigate'],
  data() { return { data: null, loading: true }; },
  async mounted() { await this.load(); },
  methods: {
    async load() {
      this.loading = true;
      try { const res = await api.get('/patient/dashboard'); this.data = res.data; }
      catch(e) { this.$emit('toast',{msg:'Failed to load',type:'danger'}); }
      finally { this.loading = false; }
    },
    async cancel(id) {
      if (!confirm('Cancel this appointment?')) return;
      try { await api.post(`/appointment/${id}/cancel`); this.$emit('toast',{msg:'Appointment cancelled'}); await this.load(); }
      catch(e) { this.$emit('toast',{msg: e.response?.data?.error||'Failed',type:'danger'}); }
    },
    badgeClass(s) { return s==='Booked'?'badge-booked':s==='Completed'?'badge-completed':'badge-cancelled'; }
  },
  template: `
  <div>
    <h4 class="fw-bold mb-4"><i class="bi bi-speedometer2 me-2 text-primary"></i>Patient Dashboard</h4>
    <div v-if="loading" class="text-center py-5"><div class="spinner-border text-primary"></div></div>
    <div v-else-if="data">
      <!-- Departments -->
      <div class="card mb-4">
        <div class="card-header py-3"><h6 class="mb-0 fw-bold"><i class="bi bi-grid me-2"></i>Departments & Specializations</h6></div>
        <div class="card-body">
          <div class="d-flex flex-wrap">
            <div v-for="dept in data.departments" :key="dept.id" class="dept-pill" @click="$emit('navigate','/patient/doctors?dept='+dept.id)">
              <i class="bi bi-hospital me-2"></i>{{ dept.name }}
              <span class="badge bg-primary ms-2">{{ dept.doctor_count }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Upcoming Appointments -->
      <div class="card mb-4">
        <div class="card-header py-3 d-flex justify-content-between align-items-center">
          <h6 class="mb-0 fw-bold"><i class="bi bi-calendar-check me-2"></i>Upcoming Appointments</h6>
          <button class="btn btn-sm btn-primary" @click="$emit('navigate','/patient/doctors')">
            <i class="bi bi-plus me-1"></i>Book Appointment
          </button>
        </div>
        <div class="card-body">
          <div v-if="!data.upcoming_appointments.length" class="text-center text-muted py-4">
            <i class="bi bi-calendar-x fs-2 d-block mb-2"></i>No upcoming appointments
          </div>
          <div v-for="apt in data.upcoming_appointments" :key="apt.id" class="apt-card">
            <div class="d-flex justify-content-between align-items-start">
              <div>
                <strong>Dr. {{ apt.doctor_name }}</strong>
                <span class="badge bg-primary-subtle text-primary ms-2">{{ apt.department }}</span>
                <div class="text-muted small mt-1">
                  <i class="bi bi-calendar me-1"></i>{{ apt.date }}
                  <i class="bi bi-clock ms-3 me-1"></i>{{ apt.time }}
                </div>
              </div>
              <div class="d-flex flex-column gap-1">
                <span class="badge" :class="badgeClass(apt.status)">{{ apt.status }}</span>
                <button class="btn btn-sm btn-outline-danger" @click="cancel(apt.id)">Cancel</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent History -->
      <div class="card">
        <div class="card-header py-3"><h6 class="mb-0 fw-bold"><i class="bi bi-clock-history me-2"></i>Recent History</h6></div>
        <div class="card-body">
          <div v-if="!data.past_appointments.length" class="text-center text-muted py-3">No past appointments</div>
          <div v-for="apt in data.past_appointments" :key="apt.id" class="apt-card" :class="apt.status.toLowerCase()">
            <div class="d-flex justify-content-between">
              <div>
                <strong>Dr. {{ apt.doctor_name }}</strong> - {{ apt.date }}
                <div v-if="apt.treatment" class="small text-muted mt-1">
                  <i class="bi bi-clipboard-pulse me-1"></i>{{ apt.treatment.diagnosis }}
                </div>
              </div>
              <span class="badge" :class="badgeClass(apt.status)">{{ apt.status }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>`
};

// ===================== FIND DOCTORS =====================
const FindDoctors = {
  name: 'FindDoctors',
  emits: ['toast'],
  data() {
    return {
      doctors: [], departments: [], loading: true,
      search: '', deptFilter: '',
      showBookModal: false, selectedDoctor: null,
      selectedDate: '', slots: [], selectedSlot: '', loadingSlots: false,
      bookReason: ''
    };
  },
  async mounted() {
    try {
      const [dr, dep] = await Promise.all([api.get('/patient/doctors'), api.get('/admin/departments').catch(()=>({data:[]}))]);
      this.doctors = dr.data; this.departments = dep.data;
    } catch(e) { this.$emit('toast',{msg:'Failed to load',type:'danger'}); }
    finally { this.loading = false; }

    // Check if dept param in URL
    const hash = window.location.hash;
    const match = hash.match(/dept=(\d+)/);
    if (match) { this.deptFilter = match[1]; await this.applyFilter(); }
  },
  computed: {
    filtered() {
      return this.doctors.filter(d => {
        const matchSearch = !this.search || d.full_name.toLowerCase().includes(this.search.toLowerCase()) || (d.specialization||'').toLowerCase().includes(this.search.toLowerCase());
        const matchDept = !this.deptFilter || String(d.department_id) === String(this.deptFilter);
        return matchSearch && matchDept;
      });
    },
    next7Days() {
      const days = [];
      for (let i = 0; i < 7; i++) {
        const d = new Date(); d.setDate(d.getDate() + i);
        days.push(d.toISOString().split('T')[0]);
      }
      return days;
    }
  },
  methods: {
    async applyFilter() {
      this.loading = true;
      try { const res = await api.get('/patient/doctors', {params:{department_id: this.deptFilter}}); this.doctors = res.data; }
      catch(e) {} finally { this.loading = false; }
    },
    openBook(d) { this.selectedDoctor = d; this.selectedDate = ''; this.slots = []; this.selectedSlot = ''; this.bookReason = ''; this.showBookModal = true; },
    async loadSlots() {
      if (!this.selectedDate || !this.selectedDoctor) return;
      this.loadingSlots = true; this.slots = []; this.selectedSlot = '';
      try {
        const res = await api.get('/appointment/slots', {params:{doctor_id:this.selectedDoctor.id, date:this.selectedDate}});
        this.slots = res.data.slots || [];
        if (!res.data.available) this.$emit('toast',{msg:'Doctor not available on this date',type:'warning'});
      } catch(e) { this.$emit('toast',{msg:'Failed to load slots',type:'danger'}); }
      finally { this.loadingSlots = false; }
    },
    async book() {
      if (!this.selectedDate || !this.selectedSlot) { this.$emit('toast',{msg:'Select date and time slot',type:'warning'}); return; }
      try {
        await api.post('/appointment/book', {
          doctor_id: this.selectedDoctor.id,
          date: this.selectedDate,
          time: this.selectedSlot,
          reason: this.bookReason
        });
        this.$emit('toast',{msg:'Appointment booked successfully!'});
        this.showBookModal = false;
      } catch(e) { this.$emit('toast',{msg: e.response?.data?.error||'Booking failed',type:'danger'}); }
    }
  },
  template: `
  <div>
    <h4 class="fw-bold mb-4"><i class="bi bi-search me-2 text-primary"></i>Find Doctors</h4>

    <!-- Filters -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-6">
            <input v-model="search" class="form-control" placeholder="Search by name or specialization..."/>
          </div>
          <div class="col-md-4">
            <select v-model="deptFilter" class="form-select" @change="applyFilter">
              <option value="">All Departments</option>
              <option v-for="d in departments" :key="d.id" :value="d.id">{{ d.name }}</option>
            </select>
          </div>
          <div class="col-md-2">
            <button class="btn btn-outline-secondary w-100" @click="deptFilter=''; applyFilter()">Clear</button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="loading" class="text-center py-5"><div class="spinner-border text-primary"></div></div>
    <div v-else class="row g-4">
      <div class="col-md-6 col-lg-4" v-for="d in filtered" :key="d.id">
        <div class="card doctor-card h-100">
          <div class="card-body">
            <div class="d-flex align-items-center gap-3 mb-3">
              <div class="doctor-avatar">{{ (d.full_name||'?')[0] }}</div>
              <div>
                <strong>Dr. {{ d.full_name }}</strong>
                <div class="text-muted small">{{ d.specialization }}</div>
                <span class="badge bg-primary-subtle text-primary mt-1">{{ d.department }}</span>
              </div>
            </div>
            <div class="small mb-3">
              <div class="text-muted"><i class="bi bi-award me-1"></i>{{ d.qualification || 'MBBS' }}</div>
              <div class="text-muted"><i class="bi bi-briefcase me-1"></i>{{ d.experience_years }} years experience</div>
              <div class="text-success fw-medium mt-1"><i class="bi bi-currency-rupee"></i>{{ d.consultation_fee }} consultation fee</div>
            </div>
            <div v-if="d.availabilities && d.availabilities.length" class="mb-3">
              <div class="small text-muted fw-medium mb-1">Available on:</div>
              <div class="d-flex flex-wrap gap-1">
                <span v-for="a in d.availabilities.slice(0,3)" :key="a.id" class="badge bg-success-subtle text-success">{{ a.date }}</span>
                <span v-if="d.availabilities.length > 3" class="badge bg-light text-muted">+{{ d.availabilities.length - 3 }}</span>
              </div>
            </div>
            <div v-else class="text-muted small mb-3"><i class="bi bi-info-circle me-1"></i>No availability set</div>
            <button class="btn btn-primary w-100" @click="openBook(d)"
                    :disabled="!d.availabilities || !d.availabilities.length">
              <i class="bi bi-calendar-plus me-1"></i>Book Appointment
            </button>
          </div>
        </div>
      </div>
      <div v-if="!filtered.length" class="text-center text-muted py-5">
        <i class="bi bi-search fs-2 d-block mb-2"></i>No doctors found
      </div>
    </div>

    <!-- Book Modal -->
    <div v-if="showBookModal" class="modal d-block" style="background:rgba(0,0,0,0.5)">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title fw-bold">Book Appointment</h5>
            <button class="btn-close" @click="showBookModal=false"></button>
          </div>
          <div class="modal-body">
            <div class="d-flex align-items-center gap-3 mb-4 p-3 bg-light rounded">
              <div class="doctor-avatar" style="width:48px;height:48px;font-size:1.2rem">{{ (selectedDoctor?.full_name||'?')[0] }}</div>
              <div><strong>Dr. {{ selectedDoctor?.full_name }}</strong><br><small class="text-muted">{{ selectedDoctor?.specialization }}</small></div>
            </div>
            <div class="mb-3">
              <label class="form-label fw-medium">Select Date</label>
              <select v-model="selectedDate" class="form-select" @change="loadSlots">
                <option value="">Choose date</option>
                <option v-for="a in selectedDoctor?.availabilities" :key="a.date" :value="a.date">{{ a.date }}</option>
              </select>
            </div>
            <div class="mb-3" v-if="selectedDate">
              <label class="form-label fw-medium">Select Time Slot</label>
              <div v-if="loadingSlots" class="text-center"><div class="spinner-border spinner-border-sm text-primary"></div></div>
              <div v-else>
                <div v-if="!slots.length" class="text-muted small">No slots available for this date</div>
                <div class="d-flex flex-wrap">
                  <button v-for="slot in slots" :key="slot.time"
                          class="slot-btn"
                          :class="slot.available ? (selectedSlot===slot.time ? 'selected' : 'available') : 'booked'"
                          :disabled="!slot.available"
                          @click="slot.available && (selectedSlot=slot.time)">
                    {{ slot.time }}
                  </button>
                </div>
              </div>
            </div>
            <div class="mb-3">
              <label class="form-label fw-medium">Reason for Visit</label>
              <textarea v-model="bookReason" class="form-control" rows="2" placeholder="Brief description of your concern"></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showBookModal=false">Cancel</button>
            <button class="btn btn-primary" @click="book" :disabled="!selectedSlot">Confirm Booking</button>
          </div>
        </div>
      </div>
    </div>
  </div>`
};

// ===================== PATIENT APPOINTMENTS =====================
const PatientAppointments = {
  name: 'PatientAppointments',
  emits: ['toast'],
  data() { return { appointments: [], loading: true, showReschedule: false, selected: null, rescheduleSlots: [], selectedRescheduleDate: '', selectedRescheduleSlot: '', loadingRescheduleSlots: false }; },
  async mounted() { await this.load(); },
  methods: {
    async load() {
      this.loading = true;
      try { const res = await api.get('/patient/appointments/history'); this.appointments = res.data; }
      catch(e) { this.$emit('toast',{msg:'Failed',type:'danger'}); }
      finally { this.loading = false; }
    },
    async cancel(id) {
      if (!confirm('Cancel this appointment?')) return;
      try { await api.post(`/appointment/${id}/cancel`); this.$emit('toast',{msg:'Cancelled'}); await this.load(); }
      catch(e) { this.$emit('toast',{msg: e.response?.data?.error||'Failed',type:'danger'}); }
    },
    openReschedule(apt) { 
      this.selected = apt; 
      this.selectedRescheduleDate = ''; 
      this.rescheduleSlots = []; 
      this.selectedRescheduleSlot = ''; 
      this.showReschedule = true; 
    },
    async loadRescheduleSlots() {
      if (!this.selectedRescheduleDate || !this.selected) return;
      this.loadingRescheduleSlots = true; 
      this.rescheduleSlots = []; 
      this.selectedRescheduleSlot = '';
      try {
        const res = await api.get('/appointment/slots', {params:{doctor_id:this.selected.doctor_id, date:this.selectedRescheduleDate}});
        this.rescheduleSlots = res.data.slots || [];
        if (!res.data.available) this.$emit('toast',{msg:'Doctor not available on this date',type:'warning'});
      } catch(e) { this.$emit('toast',{msg:'Failed to load slots',type:'danger'}); }
      finally { this.loadingRescheduleSlots = false; }
    },
    async reschedule() {
      if (!this.selectedRescheduleDate || !this.selectedRescheduleSlot) { 
        this.$emit('toast',{msg:'Select date and time slot',type:'warning'}); 
        return; 
      }
      try {
        await api.put(`/appointment/${this.selected.id}/reschedule`, {date:this.selectedRescheduleDate, time:this.selectedRescheduleSlot});
        this.$emit('toast',{msg:'Appointment rescheduled successfully!'}); 
        this.showReschedule = false; 
        await this.load();
      } catch(e) { this.$emit('toast',{msg: e.response?.data?.error||'Failed',type:'danger'}); }
    },
    badgeClass(s) { return s==='Booked'?'badge-booked':s==='Completed'?'badge-completed':'badge-cancelled'; }
  },
  template: `
  <div>
    <h4 class="fw-bold mb-4"><i class="bi bi-calendar3 me-2 text-primary"></i>My Appointments</h4>
    <div v-if="loading" class="text-center py-5"><div class="spinner-border text-primary"></div></div>
    <div v-else>
      <div v-if="!appointments.length" class="text-center text-muted py-5">
        <i class="bi bi-calendar-x fs-2 d-block mb-2"></i>No appointments found
      </div>
      <div v-for="apt in appointments" :key="apt.id" class="apt-card mb-3" :class="apt.status.toLowerCase()">
        <div class="d-flex justify-content-between align-items-start">
          <div class="flex-grow-1">
            <div class="d-flex align-items-center gap-2 mb-1">
              <strong>Dr. {{ apt.doctor_name }}</strong>
              <span class="badge bg-primary-subtle text-primary small">{{ apt.department }}</span>
              <span class="badge" :class="badgeClass(apt.status)">{{ apt.status }}</span>
            </div>
            <div class="text-muted small">
              <i class="bi bi-calendar me-1"></i>{{ apt.date }}
              <i class="bi bi-clock ms-3 me-1"></i>{{ apt.time }}
            </div>
            <div v-if="apt.reason" class="text-muted small mt-1"><i class="bi bi-chat me-1"></i>{{ apt.reason }}</div>
            <div v-if="apt.treatment" class="mt-2 p-2 bg-light rounded small">
              <strong>Diagnosis:</strong> {{ apt.treatment.diagnosis }}<br>
              <strong>Prescription:</strong> {{ apt.treatment.prescription }}
              <span v-if="apt.treatment.next_visit"><br><strong>Next Visit:</strong> {{ apt.treatment.next_visit }}</span>
            </div>
          </div>
          <div class="d-flex flex-column gap-1 ms-3" v-if="apt.status==='Booked'">
            <button class="btn btn-sm btn-outline-primary" @click="openReschedule(apt)">Reschedule</button>
            <button class="btn btn-sm btn-outline-danger" @click="cancel(apt.id)">Cancel</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Reschedule Modal with Slot Selection -->
    <div v-if="showReschedule" class="modal d-block" style="background:rgba(0,0,0,0.5)">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title fw-bold">Reschedule Appointment</h5>
            <button class="btn-close" @click="showReschedule=false"></button>
          </div>
          <div class="modal-body">
            <div class="d-flex align-items-center gap-3 mb-4 p-3 bg-light rounded">
              <div class="doctor-avatar" style="width:48px;height:48px;font-size:1.2rem">{{ (selected?.doctor_name||'?')[0] }}</div>
              <div><strong>Dr. {{ selected?.doctor_name }}</strong><br><small class="text-muted">{{ selected?.specialization }}</small></div>
            </div>
            <div class="mb-3">
              <label class="form-label fw-medium">Select New Date</label>
              <input v-model="selectedRescheduleDate" type="date" class="form-control" @change="loadRescheduleSlots"/>
            </div>
            <div class="mb-3" v-if="selectedRescheduleDate">
              <label class="form-label fw-medium">Select New Time Slot</label>
              <div v-if="loadingRescheduleSlots" class="text-center"><div class="spinner-border spinner-border-sm text-primary"></div></div>
              <div v-else>
                <div v-if="!rescheduleSlots.length" class="text-muted small">No slots available for this date</div>
                <div class="d-flex flex-wrap">
                  <button v-for="slot in rescheduleSlots" :key="slot.time"
                          class="slot-btn"
                          :class="slot.available ? (selectedRescheduleSlot===slot.time ? 'selected' : 'available') : 'booked'"
                          :disabled="!slot.available"
                          @click="slot.available && (selectedRescheduleSlot=slot.time)">
                    {{ slot.time }}
                  </button>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showReschedule=false">Cancel</button>
            <button class="btn btn-primary" @click="reschedule" :disabled="!selectedRescheduleSlot">Confirm Reschedule</button>
          </div>
        </div>
      </div>
    </div>
  </div>`
};

// ===================== PATIENT PROFILE =====================
const PatientProfile = {
  name: 'PatientProfile',
  emits: ['toast'],
  data() { return { profile: null, form: {}, loading: true, saving: false }; },
  async mounted() {
    try { const res = await api.get('/auth/me'); this.profile = res.data; this.form = { full_name: res.data.full_name, phone: res.data.phone, ...res.data.patient_profile }; }
    catch(e) { this.$emit('toast',{msg:'Failed',type:'danger'}); }
    finally { this.loading = false; }
  },
  methods: {
    async save() {
      this.saving = true;
      try { await api.put('/patient/profile', this.form); this.$emit('toast',{msg:'Profile updated'}); }
      catch(e) { this.$emit('toast',{msg:'Failed',type:'danger'}); }
      finally { this.saving = false; }
    }
  },
  template: `
  <div>
    <h4 class="fw-bold mb-4"><i class="bi bi-person me-2 text-primary"></i>My Profile</h4>
    <div v-if="loading" class="text-center py-5"><div class="spinner-border text-primary"></div></div>
    <div v-else class="row g-4">
      <div class="col-md-4">
        <div class="card text-center p-4">
          <div class="profile-avatar">{{ (profile?.full_name||'?')[0] }}</div>
          <h5 class="fw-bold">{{ profile?.full_name }}</h5>
          <p class="text-muted">{{ profile?.email }}</p>
          <span class="badge bg-primary">Patient</span>
        </div>
      </div>
      <div class="col-md-8">
        <div class="card">
          <div class="card-header py-3"><h6 class="mb-0 fw-bold">Edit Profile</h6></div>
          <div class="card-body">
            <div class="row g-3">
              <div class="col-md-6"><label class="form-label">Full Name</label>
                <input v-model="form.full_name" class="form-control"/></div>
              <div class="col-md-6"><label class="form-label">Phone</label>
                <input v-model="form.phone" class="form-control"/></div>
              <div class="col-md-6"><label class="form-label">Date of Birth</label>
                <input v-model="form.date_of_birth" type="date" class="form-control"/></div>
              <div class="col-md-6"><label class="form-label">Gender</label>
                <select v-model="form.gender" class="form-select">
                  <option value="">Select</option>
                  <option>Male</option><option>Female</option><option>Other</option>
                </select></div>
              <div class="col-md-6"><label class="form-label">Blood Group</label>
                <select v-model="form.blood_group" class="form-select">
                  <option value="">Select</option>
                  <option v-for="bg in ['A+','A-','B+','B-','AB+','AB-','O+','O-']" :key="bg">{{ bg }}</option>
                </select></div>
              <div class="col-md-6"><label class="form-label">Emergency Contact</label>
                <input v-model="form.emergency_contact" class="form-control"/></div>
              <div class="col-12"><label class="form-label">Address</label>
                <textarea v-model="form.address" class="form-control" rows="2"></textarea></div>
              <div class="col-12"><label class="form-label">Medical History</label>
                <textarea v-model="form.medical_history" class="form-control" rows="3" placeholder="Known allergies, chronic conditions..."></textarea></div>
            </div>
            <button class="btn btn-primary mt-4" @click="save" :disabled="saving">
              <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
              {{ saving ? 'Saving...' : 'Save Profile' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>`
};

// ===================== PATIENT EXPORT =====================
const PatientExport = {
  name: 'PatientExport',
  emits: ['toast'],
  data() { return { jobs: [], loading: false, triggering: false }; },
  async mounted() { await this.loadJobs(); },
  methods: {
    async loadJobs() {
      // We'll just show recent jobs via local state
    },
    async trigger() {
      this.triggering = true;
      try {
        const res = await api.post('/patient/export/trigger');
        this.$emit('toast',{msg:'Export triggered! Polling for completion...'});
        this.jobs.unshift(res.data);
        this.pollJob(res.data.job_id);
      } catch(e) { this.$emit('toast',{msg:'Failed to trigger export',type:'danger'}); }
      finally { this.triggering = false; }
    },
    async pollJob(jobId) {
      const poll = async () => {
        try {
          const res = await api.get(`/patient/export/status/${jobId}`);
          const job = this.jobs.find(j => j.job_id === jobId);
          if (job) { job.status = res.data.status; job.file_path = res.data.file_path; }
          else this.jobs.unshift({...res.data, job_id: jobId});
          if (res.data.status === 'done') {
            this.$emit('toast',{msg:'Export ready! You can download now.'});
          } else if (res.data.status === 'failed') {
            this.$emit('toast',{msg:'Export failed',type:'danger'});
          } else {
            setTimeout(poll, 2000);
          }
        } catch(e) {}
      };
      setTimeout(poll, 1500);
    },
    download(jobId) {
      window.open(`${API_BASE}/patient/export/download/${jobId}`, '_blank');
    },
    statusBadge(s) {
      if (s === 'done') return 'bg-success';
      if (s === 'failed') return 'bg-danger';
      if (s === 'processing') return 'bg-warning text-dark';
      return 'bg-secondary';
    }
  },
  template: `
  <div>
    <h4 class="fw-bold mb-4"><i class="bi bi-download me-2 text-primary"></i>Export Treatment Records</h4>
    <div class="card mb-4">
      <div class="card-body text-center py-5">
        <i class="bi bi-file-earmark-spreadsheet fs-1 text-primary d-block mb-3"></i>
        <h5 class="fw-bold">Export Your Medical Records</h5>
        <p class="text-muted">Download a complete CSV of all your treatment history including diagnoses, prescriptions, and doctor notes.</p>
        <button class="btn btn-primary btn-lg" @click="trigger" :disabled="triggering">
          <span v-if="triggering" class="spinner-border spinner-border-sm me-2"></span>
          <i v-else class="bi bi-cloud-download me-2"></i>
          {{ triggering ? 'Processing...' : 'Generate Export' }}
        </button>
      </div>
    </div>
    <div v-if="jobs.length" class="card">
      <div class="card-header"><h6 class="mb-0 fw-bold">Export Jobs</h6></div>
      <div class="card-body p-0">
        <table class="table mb-0">
          <thead><tr><th>Job ID</th><th>Status</th><th>Action</th></tr></thead>
          <tbody>
            <tr v-for="job in jobs" :key="job.job_id">
              <td>#{{ job.job_id }}</td>
              <td><span class="badge" :class="statusBadge(job.status)">{{ job.status }}</span></td>
              <td>
                <button v-if="job.status==='done'" class="btn btn-sm btn-success" @click="download(job.job_id)">
                  <i class="bi bi-download me-1"></i>Download CSV
                </button>
                <span v-else-if="job.status==='processing'" class="text-muted small">
                  <span class="spinner-border spinner-border-sm me-1"></span>Processing...
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>`
};

// ===================== PATIENT HISTORY =====================
const PatientHistory = {
  name: 'PatientHistory',
  emits: ['toast'],
  data() { return { appointments: [], loading: true }; },
  async mounted() {
    try { const res = await api.get('/patient/appointments/history'); this.appointments = res.data.filter(a => a.status === 'Completed'); }
    catch(e) { this.$emit('toast',{msg:'Failed',type:'danger'}); }
    finally { this.loading = false; }
  },
  template: `
  <div>
    <h4 class="fw-bold mb-4"><i class="bi bi-clock-history me-2 text-primary"></i>Treatment History</h4>
    <div v-if="loading" class="text-center py-5"><div class="spinner-border text-primary"></div></div>
    <div v-else>
      <div v-if="!appointments.length" class="text-center text-muted py-5">
        <i class="bi bi-clipboard-x fs-2 d-block mb-2"></i>No completed treatments yet
      </div>
      <div v-for="apt in appointments" :key="apt.id" class="card mb-3">
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-start mb-3">
            <div>
              <h6 class="fw-bold mb-1">Dr. {{ apt.doctor_name }}</h6>
              <span class="badge bg-primary-subtle text-primary">{{ apt.department }}</span>
            </div>
            <div class="text-end">
              <div class="fw-medium">{{ apt.date }}</div>
              <div class="text-muted small">{{ apt.time }}</div>
            </div>
          </div>
          <div v-if="apt.treatment" class="row g-3">
            <div class="col-md-6">
              <div class="p-3 bg-light rounded">
                <div class="small text-muted fw-medium mb-1"><i class="bi bi-clipboard-pulse me-1"></i>DIAGNOSIS</div>
                <div>{{ apt.treatment.diagnosis || '-' }}</div>
              </div>
            </div>
            <div class="col-md-6">
              <div class="p-3 bg-light rounded">
                <div class="small text-muted fw-medium mb-1"><i class="bi bi-capsule me-1"></i>PRESCRIPTION</div>
                <div>{{ apt.treatment.prescription || '-' }}</div>
              </div>
            </div>
            <div class="col-12" v-if="apt.treatment.notes">
              <div class="p-3 bg-light rounded">
                <div class="small text-muted fw-medium mb-1"><i class="bi bi-journal me-1"></i>NOTES</div>
                <div>{{ apt.treatment.notes }}</div>
              </div>
            </div>
            <div class="col-12" v-if="apt.treatment.next_visit">
              <div class="alert alert-info py-2 mb-0">
                <i class="bi bi-calendar-event me-1"></i>Next visit recommended: <strong>{{ apt.treatment.next_visit }}</strong>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>`
};
