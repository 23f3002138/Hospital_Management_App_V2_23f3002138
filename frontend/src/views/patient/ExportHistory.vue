<template>
  <div class="fade-in">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="h3 fw-bold text-primary mb-1">Export Treatment History</h2>
        <p class="text-muted mb-0">Download your medical records</p>
      </div>
    </div>
    
    <div class="row g-4">
      <div class="col-md-8">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-header bg-white border-bottom py-3">
            <h5 class="mb-0 fw-bold text-primary">Export Your Medical History</h5>
          </div>
          <div class="card-body p-4">
            <p class="text-muted mb-4">You can export your complete treatment history as a CSV file. The export will include:</p>
            <ul class="list-unstyled mb-4">
              <li class="mb-2 d-flex align-items-center text-muted">
                <span class="badge bg-primary bg-opacity-10 text-primary rounded-pill me-2">1</span>
                All your completed appointments
              </li>
              <li class="mb-2 d-flex align-items-center text-muted">
                <span class="badge bg-primary bg-opacity-10 text-primary rounded-pill me-2">2</span>
                Diagnosis information
              </li>
              <li class="mb-2 d-flex align-items-center text-muted">
                <span class="badge bg-primary bg-opacity-10 text-primary rounded-pill me-2">3</span>
                Prescriptions and treatment notes
              </li>
              <li class="d-flex align-items-center text-muted">
                <span class="badge bg-primary bg-opacity-10 text-primary rounded-pill me-2">4</span>
                Doctor details and appointment dates
              </li>
            </ul>
            
            <form @submit.prevent="triggerExport">
              <div class="mb-4">
                <label class="form-label fw-medium">Email for Export Delivery</label>
                <input type="email" class="form-control form-control-lg" v-model="exportData.email" 
                       :placeholder="user.email" required>
                <div class="form-text mt-2">
                  The CSV file will be sent to this email address
                </div>
              </div>
              
              <button type="submit" class="btn btn-primary btn-lg px-5" :disabled="loading">
                <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                {{ loading ? 'Starting Export...' : 'Start Export' }}
              </button>
            </form>
            
            <div v-if="exportResult" class="alert alert-info mt-4 border-0 bg-info bg-opacity-10 text-info">
              {{ exportResult }}
            </div>
          </div>
        </div>
      </div>
      
      <div class="col-md-4">
        <div class="card border-0 shadow-sm h-100">
          <div class="card-header bg-white border-bottom py-3">
            <h5 class="mb-0 fw-bold text-primary">Export Information</h5>
          </div>
          <div class="card-body p-4">
            <h6 class="fw-bold text-muted small text-uppercase mb-3">What's included in the export:</h6>
            <ul class="small text-muted ps-3 mb-4">
              <li class="mb-2">Appointment dates and times</li>
              <li class="mb-2">Consulting doctor details</li>
              <li class="mb-2">Diagnosis for each visit</li>
              <li class="mb-2">Prescriptions provided</li>
              <li class="mb-2">Treatment notes</li>
              <li>Follow-up recommendations</li>
            </ul>
            
            <h6 class="fw-bold text-muted small text-uppercase mb-2">Processing Time:</h6>
            <p class="small text-muted mb-0">The export process may take a few minutes depending on the number of records. You will receive an email with the CSV file attached when it's ready.</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Recent Exports -->
    <div class="card border-0 shadow-sm mt-4">
      <div class="card-header bg-white border-bottom py-3">
        <h5 class="mb-0 fw-bold text-primary">Recent Exports</h5>
      </div>
      <div class="card-body p-4">
        <div class="text-center py-4 text-muted" v-if="!exports.length">
          No recent exports found
        </div>
        <div v-else>
          <div v-for="exportItem in exports" :key="exportItem.id" class="export-item border-bottom py-3">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <strong class="text-primary">Export #{{ exportItem.id }}</strong>
                <br>
                <small class="text-muted">Requested: {{ formatDate(exportItem.created_at) }}</small>
              </div>
              <div>
                <span class="badge px-3 py-2 rounded-pill" :class="getExportStatusBadge(exportItem.status)">
                  {{ exportItem.status }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { patientService } from '@/services/api'
import { mapState } from 'vuex'

export default {
  name: 'ExportHistory',
  data() {
    return {
      exportData: {
        email: ''
      },
      loading: false,
      exportResult: '',
      exports: []
    }
  },
  computed: {
    ...mapState(['user'])
  },
  mounted() {
    this.exportData.email = this.user?.email || ''
  },
  methods: {
    async triggerExport() {
      this.loading = true
      this.exportResult = ''
      
      try {
        const response = await patientService.exportTreatmentHistory(this.exportData.email)
        this.exportResult = response.data.message
        alert('Export started successfully! Check your email in a few minutes.')
      } catch (error) {
        console.error('Failed to trigger export:', error)
        this.exportResult = error.response?.data?.message || 'Failed to start export. Please try again.'
        alert(this.exportResult)
      } finally {
        this.loading = false
      }
    },
    
    formatDate(dateString) {
      return new Date(dateString).toLocaleString()
    },
    
    getExportStatusBadge(status) {
      switch (status) {
        case 'completed': return 'bg-success bg-opacity-10 text-success'
        case 'processing': return 'bg-warning bg-opacity-10 text-warning'
        case 'failed': return 'bg-danger bg-opacity-10 text-danger'
        default: return 'bg-secondary bg-opacity-10 text-secondary'
      }
    }
  }
}
</script>