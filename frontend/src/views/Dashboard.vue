<template>
  <div class="dashboard-container fade-in">
    <div class="d-flex justify-content-between align-items-center mb-5">
      <div>
        <h2 class="h3 fw-bold text-primary mb-1">Dashboard</h2>
        <p class="text-muted mb-0">Overview & Statistics</p>
      </div>
      <div class="text-end">
        <span class="text-muted small d-block">Welcome back</span>
        <span class="fw-semibold">{{ user?.username || 'User' }}</span>
      </div>
    </div>
    
    <!-- Admin Dashboard -->
    <div v-if="user && user.role === 'admin'">
      <div class="row g-4 mb-5">
        <div class="col-md-3 col-sm-6">
          <div class="card h-100 border-0 shadow-sm">
            <div class="card-body">
              <h6 class="text-muted text-uppercase small fw-bold mb-3">Doctors</h6>
              <div class="d-flex align-items-baseline">
                <h2 class="display-6 fw-bold text-primary mb-0">{{ stats.total_doctors }}</h2>
                <span class="ms-2 text-success small"></span>
              </div>
            </div>
          </div>
        </div>
        <div class="col-md-3 col-sm-6">
          <div class="card h-100 border-0 shadow-sm">
            <div class="card-body">
              <h6 class="text-muted text-uppercase small fw-bold mb-3">Patients</h6>
              <div class="d-flex align-items-baseline">
                <h2 class="display-6 fw-bold text-primary mb-0">{{ stats.total_patients }}</h2>
                <span class="ms-2 text-success small">Registered</span>
              </div>
            </div>
          </div>
        </div>
        <div class="col-md-3 col-sm-6">
          <div class="card h-100 border-0 shadow-sm">
            <div class="card-body">
              <h6 class="text-muted text-uppercase small fw-bold mb-3">Appointments</h6>
              <div class="d-flex align-items-baseline">
                <h2 class="display-6 fw-bold text-primary mb-0">{{ stats.total_appointments }}</h2>
                <span class="ms-2 text-muted small">Total</span>
              </div>
            </div>
          </div>
        </div>
        <div class="col-md-3 col-sm-6">
          <div class="card h-100 border-0 shadow-sm">
            <div class="card-body">
              <h6 class="text-muted text-uppercase small fw-bold mb-3">Today</h6>
              <div class="d-flex align-items-baseline">
                <h2 class="display-6 fw-bold text-primary mb-0">{{ stats.today_appointments }}</h2>
                <span class="ms-2 text-warning small">Scheduled</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="row mb-4">
        <div class="col-12">
          <router-link to="/admin/departments" class="btn btn-outline-primary">
            <i class="bi bi-building me-2"></i>Manage Departments
          </router-link>
        </div>
      </div>
      
      <!-- Recent Appointments -->
      <div class="card border-0 shadow-sm">
        <div class="card-header bg-white border-bottom py-3">
          <h5 class="mb-0 fw-bold text-primary">Recent Appointments</h5>
        </div>
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-hover mb-0 align-middle">
              <thead class="bg-light">
                <tr>
                  <th class="ps-4">Patient</th>
                  <th>Doctor</th>
                  <th>Date</th>
                  <th>Time</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="appt in recentAppointments" :key="appt.id">
                  <td class="ps-4 fw-medium">{{ appt.patient_name }}</td>
                  <td>{{ appt.doctor_name }}</td>
                  <td>{{ formatDate(appt.appointment_date) }}</td>
                  <td>{{ appt.appointment_time }}</td>
                  <td>
                    <span :class="`badge bg-${getStatusBadge(appt.status)} bg-opacity-10 text-${getStatusBadge(appt.status)} px-3 py-2 rounded-pill`">
                      {{ appt.status }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Doctor Dashboard -->
    <div v-else-if="user && user.role === 'doctor'">
      <div class="row g-4 mb-5">
        <div class="col-md-4 col-sm-6">
          <div class="card h-100 border-0 shadow-sm">
            <div class="card-body">
              <h6 class="text-muted text-uppercase small fw-bold mb-3">Today's Appointments</h6>
              <div class="d-flex align-items-baseline">
                <h2 class="display-6 fw-bold text-primary mb-0">{{ todayScheduled.length }}</h2>
                <span class="ms-2 text-warning small">Pending</span>
              </div>
            </div>
          </div>
        </div>
        <div class="col-md-4 col-sm-6">
          <div class="card h-100 border-0 shadow-sm">
            <div class="card-body">
              <h6 class="text-muted text-uppercase small fw-bold mb-3">Upcoming (7 days)</h6>
              <div class="d-flex align-items-baseline">
                <h2 class="display-6 fw-bold text-primary mb-0">{{ stats.upcoming_appointments_count }}</h2>
                <span class="ms-2 text-info small">Scheduled</span>
              </div>
            </div>
          </div>
        </div>
        <div class="col-md-4 col-sm-6">
          <div class="card h-100 border-0 shadow-sm">
            <div class="card-body">
              <h6 class="text-muted text-uppercase small fw-bold mb-3">Total Patients</h6>
              <div class="d-flex align-items-baseline">
                <h2 class="display-6 fw-bold text-primary mb-0">{{ stats.total_patients }}</h2>
                <span class="ms-2 text-success small">Assigned</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="row g-4">
        <!-- Today's Schedule -->
        <div class="col-lg-6">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-header bg-white border-bottom py-3">
              <h5 class="mb-0 fw-bold text-primary">Today's Schedule</h5>
            </div>
            <div class="card-body">
              <!-- Pending Appointments -->
              <h6 class="text-muted text-uppercase small fw-bold mb-3" v-if="todayScheduled.length > 0">Pending</h6>
              <div v-if="todayScheduled.length === 0 && todayCompleted.length === 0" class="text-center py-5 text-muted">
                <p class="mb-0">No appointments for today</p>
              </div>
              <div v-else-if="todayScheduled.length === 0" class="text-center py-3 text-muted">
                <p class="mb-0">No pending appointments</p>
              </div>
              
              <div v-for="appt in todayScheduled" :key="appt.id" class="card mb-3 border bg-light">
                <div class="card-body">
                  <div class="d-flex justify-content-between align-items-start mb-2">
                    <h6 class="fw-bold mb-0">{{ appt.patient_name }}</h6>
                    <span class="badge bg-primary">{{ appt.appointment_time }}</span>
                  </div>
                  <p class="text-muted small mb-3">{{ appt.reason }}</p>
                  <button class="btn btn-sm btn-primary w-100" @click="completeAppointment(appt)">
                    Complete Visit
                  </button>
                </div>
              </div>

              <!-- Completed Appointments -->
              <div v-if="todayCompleted.length > 0" class="mt-4 pt-3 border-top">
                <h6 class="text-muted text-uppercase small fw-bold mb-3">Completed Today</h6>
                <div v-for="appt in todayCompleted" :key="appt.id" class="card mb-2 border-0 bg-success bg-opacity-10">
                  <div class="card-body py-2">
                    <div class="d-flex justify-content-between align-items-center">
                      <div>
                        <h6 class="fw-bold mb-0 small">{{ appt.patient_name }}</h6>
                        <small class="text-muted">{{ appt.appointment_time }}</small>
                      </div>
                      <span class="badge bg-success">Completed</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Upcoming -->
        <div class="col-lg-6">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-header bg-white border-bottom py-3">
              <h5 class="mb-0 fw-bold text-primary">Upcoming</h5>
            </div>
            <div class="card-body">
              <div v-if="upcomingAppointments.length === 0" class="text-center py-5 text-muted">
                <p class="mb-0">No upcoming appointments</p>
              </div>
              <div v-else>
                <div v-for="appt in upcomingAppointments" :key="appt.id" class="d-flex align-items-center p-3 border-bottom">
                  <div class="flex-grow-1">
                    <h6 class="mb-1 fw-semibold">{{ appt.patient_name }}</h6>
                    <p class="mb-0 small text-muted">{{ formatDate(appt.appointment_date) }} at {{ appt.appointment_time }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Patient Dashboard -->
    <div v-else-if="user && user.role === 'patient'">
      <div class="row g-4">
        <div class="col-lg-6">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-header bg-white border-bottom py-3">
              <h5 class="mb-0 fw-bold text-primary">Upcoming Appointments</h5>
            </div>
            <div class="card-body">
              <div v-if="upcomingAppointments.length === 0" class="text-center py-5 text-muted">
                <p class="mb-0">No upcoming appointments</p>
              </div>
              <div v-else>
                <div v-for="appt in upcomingAppointments" :key="appt.id" class="card mb-3 border bg-light">
                  <div class="card-body">
                    <div class="d-flex justify-content-between mb-2">
                      <h6 class="fw-bold mb-0">Dr. {{ appt.doctor_name }}</h6>
                      <span class="badge bg-primary">{{ formatDate(appt.appointment_date) }}</span>
                    </div>
                    <div class="mb-3">
                      <p class="mb-1 small text-muted">Time: {{ appt.appointment_time }}</p>
                      <p class="mb-0 small text-muted">Specialization: {{ appt.specialization }}</p>
                    </div>
                    <button class="btn btn-sm btn-outline-danger w-100" @click="cancelAppointment(appt)">
                      Cancel Appointment
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="col-lg-6">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-header bg-white border-bottom py-3">
              <h5 class="mb-0 fw-bold text-primary">Treatment History</h5>
            </div>
            <div class="card-body">
              <div v-if="pastAppointments.length === 0" class="text-center py-5 text-muted">
                <p class="mb-0">No treatment history available</p>
              </div>
              <div v-else>
                <div v-for="appt in pastAppointments" :key="appt.id" class="card mb-3 border-0 bg-light">
                  <div class="card-body">
                    <div class="d-flex justify-content-between mb-2">
                      <h6 class="fw-bold mb-0">Dr. {{ appt.doctor_name }}</h6>
                      <span class="text-muted small">{{ formatDate(appt.appointment_date) }}</span>
                    </div>
                    <p v-if="appt.treatment" class="mb-2 small">
                      <span class="fw-semibold">Diagnosis:</span> {{ appt.treatment.diagnosis }}
                    </p>
                    <button class="btn btn-sm btn-link p-0 text-decoration-none" @click="viewDetails(appt)">
                      View Details &rarr;
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="row mt-4">
        <div class="col-12 text-center">
          <router-link to="/patient/profile" class="btn btn-outline-primary">
            Edit Profile
          </router-link>
        </div>
      </div>
    </div>

    <!-- Appointment Details Modal -->
    <BaseModal 
      :show="showDetailsModal" 
      title="Appointment Details" 
      @close="closeDetailsModal"
    >
      <div v-if="selectedAppointment">
        <div class="mb-4 border-bottom pb-3">
          <h6 class="fw-bold text-primary mb-1">Dr. {{ selectedAppointment.doctor_name }}</h6>
          <p class="text-muted small mb-0">{{ selectedAppointment.specialization }}</p>
          <p class="text-muted small mt-1">
            {{ formatDate(selectedAppointment.appointment_date) }} at {{ selectedAppointment.appointment_time }}
          </p>
        </div>

        <div v-if="selectedAppointment.treatment">
          <div class="mb-3">
            <label class="fw-bold small text-uppercase text-muted">Diagnosis</label>
            <p class="mb-0">{{ selectedAppointment.treatment.diagnosis }}</p>
          </div>
          
          <div class="mb-3" v-if="selectedAppointment.treatment.prescription">
            <label class="fw-bold small text-uppercase text-muted">Prescription</label>
            <div class="bg-light p-3 rounded border">
              <pre class="mb-0" style="white-space: pre-wrap; font-family: inherit;">{{ selectedAppointment.treatment.prescription }}</pre>
            </div>
          </div>
          
          <div class="mb-3" v-if="selectedAppointment.treatment.notes">
            <label class="fw-bold small text-uppercase text-muted">Notes</label>
            <p class="mb-0">{{ selectedAppointment.treatment.notes }}</p>
          </div>
          
          <div class="mb-3" v-if="selectedAppointment.treatment.follow_up_date">
            <label class="fw-bold small text-uppercase text-muted">Follow-up Date</label>
            <p class="mb-0 text-primary fw-medium">{{ formatDate(selectedAppointment.treatment.follow_up_date) }}</p>
          </div>
        </div>
        <div v-else class="alert alert-info">
          No treatment details available for this appointment.
        </div>
      </div>
      <template #footer>
        <button class="btn btn-secondary" @click="closeDetailsModal">Close</button>
      </template>
    </BaseModal>
  </div>
</template>

<script>
import { adminService, doctorService, patientService } from '@/services/api'
import axiosInstance from '@/services/api'
import BaseModal from '@/components/BaseModal.vue'

export default {
  name: 'Dashboard',
  components: {
    BaseModal
  },
  data() {
    return {
      stats: {
        total_doctors: 0,
        total_patients: 0,
        total_appointments: 0,
        today_appointments: 0,
        today_appointments_count: 0,
        upcoming_appointments_count: 0
      },
      recentAppointments: [],
      todayAppointments: [],
      upcomingAppointments: [],
      pastAppointments: [],
      jobLoading: false,
      jobMessage: '',
      jobMessageType: 'success',
      showJobInfo: false,
      showDetailsModal: false,
      selectedAppointment: null
    }
  },
  computed: {
    user() {
      return this.$store.state.user
    },
    isAuthenticated() {
      return this.$store.state.isAuthenticated
    },
    todayScheduled() {
      return this.todayAppointments.filter(appt => appt.status === 'scheduled')
    },
    todayCompleted() {
      return this.todayAppointments.filter(appt => appt.status === 'completed')
    }
  },
  async mounted() {
    if (!this.user || !this.user.role) {
      if (!this.isAuthenticated) {
        await this.$store.dispatch('initializeAuth')
      }
      
      let attempts = 0
      while ((!this.user || !this.user.role) && attempts < 10) {
        await new Promise(resolve => setTimeout(resolve, 100))
        attempts++
      }
    }
    
    if (this.user && this.user.role) {
      await this.loadDashboardData()
    } else {
      console.error('User not available, redirecting to login')
      this.$router.push('/login')
    }
  },
  methods: {
    async loadDashboardData() {
      try {
        const token = localStorage.getItem('token')
        console.log('[DASHBOARD] Loading data, token exists:', !!token)
        
        if (!token) {
          console.error('[DASHBOARD] No token found in localStorage, redirecting to login')
          this.$router.push('/login')
          return
        }
        
        const authHeader = `Bearer ${token}`
        axiosInstance.defaults.headers.common['Authorization'] = authHeader
        console.log('[DASHBOARD] Set axios default header:', authHeader.substring(0, 30) + '...')
        
        let response
        
        if (!this.user || !this.user.role) {
          console.error('User not loaded yet')
          return
        }
        
        switch (this.user.role) {
          case 'admin':
            response = await adminService.getDashboard()
            this.stats = response.data.stats
            this.recentAppointments = response.data.recent_appointments || []
            break
          case 'doctor':
            response = await doctorService.getDashboard()
            this.stats = response.data.stats
            this.todayAppointments = response.data.today_appointments || []
            this.upcomingAppointments = response.data.upcoming_appointments || []
            break
          case 'patient':
            response = await patientService.getDashboard()
            this.upcomingAppointments = response.data.upcoming_appointments || []
            this.pastAppointments = response.data.past_appointments || []
            break
        }
      } catch (error) {
        console.error('Failed to load dashboard data:', error)
        if (error.response?.status === 401) {
          this.$store.dispatch('logout')
          this.$router.push('/login')
        }
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString()
    },
    
    getStatusBadge(status) {
      switch (status) {
        case 'scheduled': return 'primary'
        case 'completed': return 'success'
        case 'cancelled': return 'danger'
        default: return 'secondary'
      }
    },
    
    completeAppointment(appointment) {
      this.$router.push(`/doctor/appointments/${appointment.id}/complete`)
    },
    
    async cancelAppointment(appointment) {
      if (!confirm('Are you sure you want to cancel this appointment?')) return
      
      try {
        const { patientService } = await import('@/services/api')
        await patientService.cancelAppointment(appointment.id)
        await this.loadDashboardData()
        alert('Appointment cancelled successfully!')
      } catch (error) {
        alert(error.response?.data?.message || 'Failed to cancel appointment!')
      }
    },
    
    viewDetails(appointment) {
      this.selectedAppointment = appointment
      this.showDetailsModal = true
    },
    
    closeDetailsModal() {
      this.showDetailsModal = false
      this.selectedAppointment = null
    },
    
    async triggerDailyReminders() {
      this.jobLoading = true
      this.jobMessage = ''
      try {
        const response = await adminService.triggerDailyReminders()
        this.jobMessage = response.data.message + ' ' + (response.data.result || '')
        this.jobMessageType = 'success'
        setTimeout(() => {
          this.jobMessage = ''
        }, 5000)
      } catch (error) {
        this.jobMessage = error.response?.data?.message || 'Failed to trigger daily reminders!'
        this.jobMessageType = 'danger'
      } finally {
        this.jobLoading = false
      }
    },
    
    async triggerMonthlyReports() {
      this.jobLoading = true
      this.jobMessage = ''
      try {
        const response = await adminService.triggerMonthlyReports()
        this.jobMessage = response.data.message + ' ' + (response.data.result || '')
        this.jobMessageType = 'success'
        setTimeout(() => {
          this.jobMessage = ''
        }, 5000)
      } catch (error) {
        this.jobMessage = error.response?.data?.message || 'Failed to trigger monthly reports!'
        this.jobMessageType = 'danger'
      } finally {
        this.jobLoading = false
      }
    }
  }
}
</script>

<style scoped>
.dashboard-container {
  padding-bottom: 2rem;
}
</style>