<template>
  <div class="fade-in">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="h3 fw-bold text-primary mb-1">Manage Appointments</h2>
        <p class="text-muted mb-0">Schedule and track patient visits</p>
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
          <div class="col-md-3">
            <label class="form-label fw-medium text-muted small text-uppercase">Date</label>
            <input type="date" class="form-control form-control-lg" v-model="dateFilter">
          </div>
          <div class="col-md-4">
            <label class="form-label fw-medium text-muted small text-uppercase">Search</label>
            <input 
              type="text" 
              class="form-control form-control-lg" 
              placeholder="Search by patient or doctor..."
              v-model="searchQuery"
              @keyup.enter="loadAppointments"
            >
          </div>
          <div class="col-md-2">
            <button class="btn btn-primary btn-lg w-100" @click="loadAppointments">
              Search
            </button>
          </div>
        </div>
        
        <div class="row g-3 mt-2">
          <div class="col-md-2">
            <button class="btn btn-outline-secondary w-100" @click="clearFilters">Clear Filters</button>
          </div>
          <div class="col-md-5">
            <button class="btn btn-outline-success w-100" @click="exportCsv" :disabled="exporting">
               <span v-if="exporting" class="spinner-border spinner-border-sm me-2"></span>
               {{ exporting ? 'Exporting...' : 'Export CSV' }}
            </button>
          </div>
          <div class="col-md-5">
            <button class="btn btn-outline-danger w-100" @click="exportPdf" :disabled="exportingPdf">
               <span v-if="exportingPdf" class="spinner-border spinner-border-sm me-2"></span>
               {{ exportingPdf ? 'Generating...' : 'Export PDF Report' }}
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Tabs -->
    <ul class="nav nav-tabs mb-4 border-bottom-0">
      <li class="nav-item">
        <a class="nav-link border-0 rounded-pill px-4 me-2" :class="{ 'active bg-primary text-white': activeTab === 'all', 'bg-light text-muted': activeTab !== 'all' }" href="#" @click.prevent="activeTab = 'all'">
          All Appointments
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link border-0 rounded-pill px-4 me-2" :class="{ 'active bg-primary text-white': activeTab === 'upcoming', 'bg-light text-muted': activeTab !== 'upcoming' }" href="#" @click.prevent="activeTab = 'upcoming'">
          Upcoming
        </a>
      </li>
      <li class="nav-item">
        <a class="nav-link border-0 rounded-pill px-4" :class="{ 'active bg-primary text-white': activeTab === 'past', 'bg-light text-muted': activeTab !== 'past' }" href="#" @click.prevent="activeTab = 'past'">
          Past
        </a>
      </li>
    </ul>
    
    <!-- Appointments Table -->
    <div class="card border-0 shadow-sm">
      <div class="card-header bg-white border-bottom py-3">
        <h5 class="mb-0 fw-bold text-primary">Appointments List</h5>
      </div>
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-hover mb-0 align-middle">
            <thead class="bg-light">
              <tr>
                <th class="ps-4">ID</th>
                <th>Patient</th>
                <th>Doctor</th>
                <th>Date</th>
                <th>Time</th>
                <th>Status</th>
                <th>Reason</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="appt in appointments" :key="appt.id">
                <td class="ps-4 text-muted">#{{ appt.id }}</td>
                <td class="fw-medium">{{ appt.patient_name }}</td>
                <td>{{ appt.doctor_name }}</td>
                <td>{{ formatDate(appt.appointment_date) }}</td>
                <td>{{ appt.appointment_time }}</td>
                <td>
                  <span :class="`badge bg-${getStatusBadge(appt.status)} bg-opacity-10 text-${getStatusBadge(appt.status)} px-3 py-2 rounded-pill`">
                    {{ appt.status }}
                  </span>
                </td>
                <td class="text-muted small">{{ appt.reason || 'N/A' }}</td>
              </tr>
              <tr v-if="appointments.length === 0">
                <td colspan="7" class="text-center py-5 text-muted">
                  No appointments found
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { adminService } from '@/services/api'

export default {
  name: 'AdminAppointments',
  data() {
    return {
      appointments: [],
      allAppointments: [],
      activeTab: 'all',
      statusFilter: '',
      dateFilter: '',
      searchQuery: '',
      exporting: false,
      exportingPdf: false
    }
  },
  async mounted() {
    await this.loadAppointments()
  },
  watch: {
    activeTab() {
      this.loadAppointments()
    }
  },
  methods: {
    async loadAppointments() {
      try {
        let response
        if (this.activeTab === 'upcoming') {
          response = await adminService.getAppointments({ status: 'scheduled' })
        } else if (this.activeTab === 'past') {
          response = await adminService.getAppointments({ status: 'completed' })
        } else {
          const params = {}
          if (this.statusFilter) params.status = this.statusFilter
          if (this.dateFilter) params.date = this.dateFilter
          response = await adminService.getAppointments(params)
        }
        this.allAppointments = response.data.appointments || []
        
        
        if (this.searchQuery && this.searchQuery.trim()) {
          const query = this.searchQuery.trim().toLowerCase()
          this.appointments = this.allAppointments.filter(appt => {
            const patientName = (appt.patient_name || '').toLowerCase()
            const doctorName = (appt.doctor_name || '').toLowerCase()
            return patientName.includes(query) || doctorName.includes(query)
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
      this.dateFilter = ''
      this.searchQuery = ''
      this.loadAppointments()
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
    },
    
    async exportCsv() {
      this.exporting = true
      try {
        let date = new Date()
        if (this.dateFilter) {
          date = new Date(this.dateFilter)
        }
        
        const month = date.getMonth() + 1
        const year = date.getFullYear()
        
        const response = await adminService.exportAppointments(month, year)
        
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `appointments_${year}_${month}.csv`)
        document.body.appendChild(link)
        link.click()
        link.remove()
      } catch (error) {
        console.error('Export failed:', error)
        alert('Failed to export CSV')
      } finally {
        this.exporting = false
      }
    },

    async exportPdf() {
      this.exportingPdf = true
      try {
        let date = new Date()
        if (this.dateFilter) {
          date = new Date(this.dateFilter)
        }
        
        const month = date.getMonth() + 1
        const year = date.getFullYear()
        
        const response = await adminService.exportMonthlyReportPdf(month, year)
        
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `report_${year}_${month}.pdf`)
        document.body.appendChild(link)
        link.click()
        link.remove()
      } catch (error) {
        console.error('PDF Export failed:', error)
        alert('Failed to export PDF. Make sure xhtml2pdf is installed on backend.')
      } finally {
        this.exportingPdf = false
      }
    }
  }
}
</script>

