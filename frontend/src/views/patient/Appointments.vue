<template>
  <div class="fade-in">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="h3 fw-bold text-primary mb-1">My Appointments</h2>
        <p class="text-muted mb-0">View and manage your scheduled visits</p>
      </div>
    </div>
    
    <!-- Filters and Search -->
    <div class="card border-0 shadow-sm mb-4">
      <div class="card-body p-4">
        <div class="row g-3 align-items-end">
          <div class="col-md-3">
            <label class="form-label fw-medium text-muted small text-uppercase">Status</label>
            <select class="form-select form-select-lg" v-model="statusFilter">
              <option value="">All Status</option>
              <option value="scheduled">Scheduled</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
          <div class="col-md-5">
            <label class="form-label fw-medium text-muted small text-uppercase">Search</label>
            <input 
              type="text" 
              class="form-control form-control-lg" 
              placeholder="Search by doctor name or specialization..."
              v-model="searchQuery"
              @keyup.enter="loadAppointments"
            >
          </div>
          <div class="col-md-2">
            <button class="btn btn-primary btn-lg w-100" @click="loadAppointments">
              Search
            </button>
          </div>
          <div class="col-md-2">
            <button class="btn btn-outline-secondary btn-lg w-100" @click="clearFilters">Clear</button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Appointments List -->
    <div class="row g-4">
      <div v-for="appt in appointments" :key="appt.id" class="col-md-6 col-lg-4">
        <div class="card border-0 shadow-sm h-100 hover-shadow transition-all">
          <div class="card-body p-4 d-flex flex-column">
            <div class="d-flex justify-content-between align-items-start mb-3">
              <div>
                <h5 class="card-title fw-bold text-primary mb-0">Dr. {{ appt.doctor_name }}</h5>
                <span class="text-muted small">{{ appt.specialization }}</span>
              </div>
              <span :class="`badge px-2 py-1 rounded-pill bg-${getStatusBadge(appt.status)} bg-opacity-10 text-${getStatusBadge(appt.status)}`">
                {{ appt.status }}
              </span>
            </div>
            
            <div class="mb-4 flex-grow-1">
              <div class="d-flex justify-content-between mb-2 border-bottom pb-2">
                <span class="text-muted">Date</span>
                <span class="fw-medium">{{ formatDate(appt.appointment_date) }}</span>
              </div>
              <div class="d-flex justify-content-between mb-2">
                <span class="text-muted">Time</span>
                <span class="fw-medium">{{ appt.appointment_time }}</span>
              </div>
            </div>
            
            <div v-if="appt.status === 'scheduled'" class="d-grid">
              <button class="btn btn-outline-danger" @click="cancelAppointment(appt.id)">
                Cancel Appointment
              </button>
            </div>
            
            <div v-if="appt.treatment" class="mt-3 pt-3 border-top bg-light rounded p-3">
              <h6 class="fw-bold text-primary mb-2 small text-uppercase">Treatment Details</h6>
              <p class="mb-1 small"><strong>Diagnosis:</strong> {{ appt.treatment.diagnosis }}</p>
              <p v-if="appt.treatment.prescription" class="mb-1 small">
                <strong>Prescription:</strong> {{ appt.treatment.prescription }}
              </p>
              <p v-if="appt.treatment.follow_up_date" class="mb-0 small text-info">
                <strong>Follow-up:</strong> {{ formatDate(appt.treatment.follow_up_date) }}
              </p>
            </div>
          </div>
        </div>
      </div>
      
      <div v-if="appointments.length === 0" class="col-12 text-center py-5">
        <p class="text-muted fs-5">No appointments found matching your criteria.</p>
      </div>
    </div>
  </div>
</template>

<script>
import { patientService } from '@/services/api'

export default {
  name: 'PatientAppointments',
  data() {
    return {
      appointments: [],
      allAppointments: [],
      statusFilter: '',
      searchQuery: ''
    }
  },
  async mounted() {
    await this.loadAppointments()
  },
  methods: {
    async loadAppointments() {
      try {
        const params = {}
        if (this.statusFilter) params.status = this.statusFilter
        const response = await patientService.getAppointments(params)
        this.allAppointments = response.data.appointments || []
        
        
        if (this.searchQuery && this.searchQuery.trim()) {
          const query = this.searchQuery.trim().toLowerCase()
          this.appointments = this.allAppointments.filter(appt => {
            const doctorName = (appt.doctor_name || '').toLowerCase()
            const specialization = (appt.specialization || '').toLowerCase()
            return doctorName.includes(query) || specialization.includes(query)
          })
        } else {
          this.appointments = this.allAppointments
        }
      } catch (error) {
        console.error('Failed to load appointments:', error)
      }
    },
    
    clearFilters() {
      this.statusFilter = ''
      this.searchQuery = ''
      this.loadAppointments()
    },
    
    async cancelAppointment(appointmentId) {
      if (!confirm('Are you sure you want to cancel this appointment?')) return
      
      try {
        await patientService.cancelAppointment(appointmentId)
        await this.loadAppointments()
        alert('Appointment cancelled successfully!')
      } catch (error) {
        alert(error.response?.data?.message || 'Failed to cancel appointment!')
      }
    },
    
    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString()
    },
    
    getStatusBadge(status) {
      switch (status) {
        case 'scheduled': return 'primary'
        case 'completed': return 'success'
        case 'cancelled': return 'danger'
        default: return 'secondary'
      }
    }
  }
}
</script>

