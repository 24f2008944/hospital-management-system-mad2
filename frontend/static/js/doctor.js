// ===================== DOCTOR DASHBOARD =====================
const DoctorDashboard = {
  name: 'DoctorDashboard',
  emits: ['toast'],
  data() { return { data: null, loading: true, showCompleteModal: false, selectedApt: null, treatmentForm: {diagnosis:'',prescription:'',notes:'',next_visit:''} }; },
  async mounted() { await this.load(); },
  methods: {
    async load() {
      this.loading = true;
      try { const res = await api.get('/doctor/dashboard'); this.data = res.data; }
      catch(e) { this.$emit('toast',{msg:'Failed to load',type:'danger'}); }
      finally { this.loading = false; }
    },
    openComplete(apt) {
      this.selectedApt = apt;
      this.treatmentForm = {diagnosis:'',prescription:'',notes:'',next_visit:''};
      this.showCompleteModal = true;
    },
    async complete() {
      try {
        await api.post(`/doctor/appointments/${this.selectedApt.id}/complete`, this.treatmentForm);
        this.$emit('toast',{msg:'Appointment completed'});
        this.showCompleteModal = false; await this.load();
      } catch(e) { this.$emit('toast',{msg:'Failed',type:'danger'}); }
    },
    async cancel(id) {
      if (!confirm('Cancel this appointment?')) return;
      try { await api.post(`/doctor/appointments/${id}/cancel`); this.$emit('toast',{msg:'Appointment cancelled'}); await this.load(); }
      catch(e) { this.$emit('toast',{msg:'Failed',type:'danger'}); }
    }
  },
  template: `
  <div>
    <h4 class="fw-bold mb-4"><i class="bi bi-speedometer2 me-2 text-primary"></i>Doctor Dashboard</h4>
    <div v-if="loading" class="text-center py-5"><div class="spinner-border text-primary"></div></div>
    <div v-else-if="data">
      <div class="row g-4 mb-4">
        <div class="col-md-4">
          <div class="stat-card card text-white" style="background:linear-gradient(135deg,#1a6b8a,#27ae8f)">
            <div class="card-body d-flex justify-content-between align-items-center">
              <div><div class="stat-num">{{ data.patients_today }}</div><div class="stat-label">Patients Today</div></div>
              <i class="bi bi-person-check stat-icon"></i>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="stat-card card text-white" style="background:linear-gradient(135deg,#8e44ad,#3498db)">
            <div class="card-body d-flex justify-content-between align-items-center">
              <div><div class="stat-num">{{ data.upcoming_appointments.length }}</div><div class="stat-label">Upcoming</div></div>
              <i class="bi bi-calendar-check stat-icon"></i>
            </div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header py-3">
          <h6 class="mb-0 fw-bold"><i class="bi bi-list-ul me-2"></i>Upcoming Appointments</h6>
        </div>
        <div class="card-body">
          <div v-if="!data.upcoming_appointments.length" class="text-center text-muted py-4">
            <i class="bi bi-calendar-x fs-2 d-block mb-2"></i>No upcoming appointments
          </div>
          <div v-for="apt in data.upcoming_appointments" :key="apt.id" class="apt-card mb-3">
            <div class="d-flex justify-content-between align-items-start">
              <div>
                <strong>{{ apt.patient_name }}</strong>
                <div class="text-muted small">
                  <i class="bi bi-calendar me-1"></i>{{ apt.date }}
                  <i class="bi bi-clock ms-3 me-1"></i>{{ apt.time }}
                </div>
                <div class="text-muted small mt-1" v-if="apt.reason">{{ apt.reason }}</div>
              </div>
              <div class="d-flex gap-2">
                <button class="btn btn-sm btn-success" @click="openComplete(apt)">
                  <i class="bi bi-check2-circle me-1"></i>Complete
                </button>
                <button class="btn btn-sm btn-outline-danger" @click="cancel(apt.id)">
                  <i class="bi bi-x-circle me-1"></i>Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Complete Modal -->
    <div v-if="showCompleteModal" class="modal d-block" style="background:rgba(0,0,0,0.5)">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title fw-bold">Complete Appointment</h5>
            <button class="btn-close" @click="showCompleteModal=false"></button>
          </div>
          <div class="modal-body">
            <p class="text-muted">Patient: <strong>{{ selectedApt?.patient_name }}</strong></p>
            <div class="mb-3">
              <label class="form-label">Diagnosis</label>
              <textarea v-model="treatmentForm.diagnosis" class="form-control" rows="2" placeholder="Enter diagnosis"></textarea>
            </div>
            <div class="mb-3">
              <label class="form-label">Prescription</label>
              <textarea v-model="treatmentForm.prescription" class="form-control" rows="3" placeholder="Medications and dosage"></textarea>
            </div>
            <div class="mb-3">
              <label class="form-label">Notes</label>
              <textarea v-model="treatmentForm.notes" class="form-control" rows="2" placeholder="Additional notes"></textarea>
            </div>
            <div class="mb-3">
              <label class="form-label">Next Visit Date</label>
              <input v-model="treatmentForm.next_visit" type="date" class="form-control"/>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showCompleteModal=false">Cancel</button>
            <button class="btn btn-success" @click="complete">Mark as Completed</button>
          </div>
        </div>
      </div>
    </div>
  </div>`
};

// ===================== DOCTOR APPOINTMENTS =====================
const DoctorAppointments = {
  name: 'DoctorAppointments',
  emits: ['toast'],
  data() { return { appointments: [], loading: true, filter: '' }; },
  async mounted() { await this.load(); },
  methods: {
    async load() {
      this.loading = true;
      try { const res = await api.get('/doctor/appointments', {params:{status:this.filter}}); this.appointments = res.data; }
      catch(e) { this.$emit('toast',{msg:'Failed',type:'danger'}); }
      finally { this.loading = false; }
    },
    badgeClass(s) { return s==='Booked'?'badge-booked':s==='Completed'?'badge-completed':'badge-cancelled'; }
  },
  template: `
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h4 class="fw-bold mb-0"><i class="bi bi-calendar3 me-2 text-primary"></i>My Appointments</h4>
      <select v-model="filter" class="form-select w-auto" @change="load">
        <option value="">All</option><option>Booked</option><option>Completed</option><option>Cancelled</option>
      </select>
    </div>
    <div v-if="loading" class="text-center py-5"><div class="spinner-border text-primary"></div></div>
    <div v-else class="card"><div class="card-body p-0">
      <table class="table table-hover mb-0">
        <thead><tr><th>Patient</th><th>Date</th><th>Time</th><th>Status</th><th>Reason</th><th>Treatment</th></tr></thead>
        <tbody>
          <tr v-for="a in appointments" :key="a.id">
            <td><strong>{{ a.patient_name }}</strong></td>
            <td>{{ a.date }}</td>
            <td>{{ a.time }}</td>
            <td><span class="badge" :class="badgeClass(a.status)">{{ a.status }}</span></td>
            <td>{{ a.reason || '-' }}</td>
            <td>
              <span v-if="a.treatment" class="text-success small"><i class="bi bi-check2 me-1"></i>Recorded</span>
              <span v-else class="text-muted small">-</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div></div>
  </div>`
};

// ===================== DOCTOR PATIENTS =====================
const DoctorPatients = {
  name: 'DoctorPatients',
  emits: ['toast'],
  data() { return { patients: [], loading: true, selectedPatient: null, history: [], showHistory: false }; },
  async mounted() {
    try { const res = await api.get('/doctor/patients'); this.patients = res.data; }
    catch(e) { this.$emit('toast',{msg:'Failed',type:'danger'}); }
    finally { this.loading = false; }
  },
  methods: {
    async viewHistory(p) {
      this.selectedPatient = p; this.showHistory = true;
      try { const res = await api.get(`/doctor/patients/${p.id}/history`); this.history = res.data; }
      catch(e) { this.$emit('toast',{msg:'Failed',type:'danger'}); }
    }
  },
  template: `
  <div>
    <h4 class="fw-bold mb-4"><i class="bi bi-people me-2 text-primary"></i>My Patients</h4>
    <div v-if="loading" class="text-center py-5"><div class="spinner-border text-primary"></div></div>
    <div v-else class="row g-3">
      <div class="col-md-6 col-lg-4" v-for="p in patients" :key="p.id">
        <div class="card doctor-card h-100">
          <div class="card-body">
            <div class="d-flex align-items-center gap-3 mb-3">
              <div class="doctor-avatar" style="width:48px;height:48px;font-size:1.2rem">{{ (p.full_name||'?')[0] }}</div>
              <div><strong>{{ p.full_name }}</strong><br><small class="text-muted">{{ p.email }}</small></div>
            </div>
            <div class="small text-muted">
              <div><i class="bi bi-droplet me-1"></i>{{ p.blood_group || '-' }}</div>
              <div><i class="bi bi-gender-ambiguous me-1"></i>{{ p.gender || '-' }}</div>
            </div>
            <button class="btn btn-outline-primary btn-sm mt-3 w-100" @click="viewHistory(p)">
              <i class="bi bi-clock-history me-1"></i>View History
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showHistory" class="modal d-block" style="background:rgba(0,0,0,0.5)">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title fw-bold">Patient History - {{ selectedPatient?.full_name }}</h5>
            <button class="btn-close" @click="showHistory=false"></button>
          </div>
          <div class="modal-body">
            <div v-if="!history.length" class="text-center text-muted py-4">No history found</div>
            <div v-for="apt in history" :key="apt.id" class="apt-card" :class="apt.status.toLowerCase()">
              <div class="d-flex justify-content-between">
                <div><strong>{{ apt.date }}</strong> at {{ apt.time }}</div>
                <span class="badge" :class="apt.status==='Completed'?'bg-success':apt.status==='Cancelled'?'bg-danger':'badge-booked'">{{ apt.status }}</span>
              </div>
              <div v-if="apt.treatment" class="mt-2 small">
                <div><strong>Diagnosis:</strong> {{ apt.treatment.diagnosis }}</div>
                <div><strong>Prescription:</strong> {{ apt.treatment.prescription }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>`
};

// ===================== DOCTOR AVAILABILITY =====================
const DoctorAvailability = {
  name: 'DoctorAvailability',
  emits: ['toast'],
  data() {
    return {
      availabilities: [], loading: true,
      form: { date: '', start_time: '09:00', end_time: '17:00', max_appointments: 10, is_available: true }
    };
  },
  computed: {
    next7Days() {
      const days = [];
      for (let i = 0; i < 7; i++) {
        const d = new Date(); d.setDate(d.getDate() + i);
        days.push(d.toISOString().split('T')[0]);
      }
      return days;
    }
  },
  async mounted() { await this.load(); },
  methods: {
    async load() {
      this.loading = true;
      try { const res = await api.get('/doctor/availability'); this.availabilities = res.data; }
      catch(e) { this.$emit('toast',{msg:'Failed',type:'danger'}); }
      finally { this.loading = false; }
    },
    async save() {
      try { await api.post('/doctor/availability', this.form); this.$emit('toast',{msg:'Availability saved'}); await this.load(); }
      catch(e) { this.$emit('toast',{msg:'Failed',type:'danger'}); }
    },
    getAvail(date) { return this.availabilities.find(a => a.date === date); }
  },
  template: `
  <div>
    <h4 class="fw-bold mb-4"><i class="bi bi-clock me-2 text-primary"></i>My Availability</h4>
    <div class="row g-4">
      <div class="col-md-5">
        <div class="card">
          <div class="card-header"><h6 class="mb-0 fw-bold">Set Availability</h6></div>
          <div class="card-body">
            <div class="mb-3">
              <label class="form-label">Date (next 7 days)</label>
              <select v-model="form.date" class="form-select">
                <option value="">Select date</option>
                <option v-for="d in next7Days" :key="d" :value="d">{{ d }}</option>
              </select>
            </div>
            <div class="row g-2 mb-3">
              <div class="col-6">
                <label class="form-label">Start Time</label>
                <input v-model="form.start_time" type="time" class="form-control"/>
              </div>
              <div class="col-6">
                <label class="form-label">End Time</label>
                <input v-model="form.end_time" type="time" class="form-control"/>
              </div>
            </div>
            <div class="mb-3">
              <label class="form-label">Max Appointments</label>
              <input v-model.number="form.max_appointments" type="number" class="form-control" min="1" max="30"/>
            </div>
            <div class="mb-3 form-check">
              <input v-model="form.is_available" type="checkbox" class="form-check-input" id="avail"/>
              <label class="form-check-label" for="avail">Available on this day</label>
            </div>
            <button class="btn btn-primary w-100" @click="save">Save Availability</button>
          </div>
        </div>
      </div>
      <div class="col-md-7">
        <div class="card">
          <div class="card-header"><h6 class="mb-0 fw-bold">Availability Overview (Next 7 Days)</h6></div>
          <div class="card-body">
            <div v-if="loading" class="text-center"><div class="spinner-border text-primary"></div></div>
            <div v-else>
              <div v-for="d in next7Days" :key="d" class="d-flex justify-content-between align-items-center py-2 border-bottom">
                <span class="fw-medium">{{ d }}</span>
                <div v-if="getAvail(d)">
                  <span class="badge" :class="getAvail(d).is_available ? 'bg-success' : 'bg-secondary'">
                    {{ getAvail(d).is_available ? getAvail(d).start_time + ' - ' + getAvail(d).end_time : 'Unavailable' }}
                  </span>
                </div>
                <span v-else class="badge bg-light text-muted">Not set</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>`
};
