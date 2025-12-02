<template>
  <div class="fade-in">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="h3 fw-bold text-primary mb-1">Complete Treatment</h2>
        <p class="text-muted mb-0">Record diagnosis and treatment details</p>
      </div>
    </div>
    
    <div class="card border-0 shadow-sm mb-4">
      <div class="card-header bg-white border-bottom py-3">
        <h5 class="mb-0 fw-bold text-primary">Appointment Details</h5>
      </div>
      <div class="card-body p-4">
        <div v-if="appointment" class="row g-4">
          <div class="col-md-6">
            <div class="mb-3">
              <label class="text-muted small text-uppercase fw-bold">Patient</label>
              <p class="fs-5 fw-medium mb-0">{{ appointment.patient_name }}</p>
            </div>
            <div class="row">
              <div class="col-6">
                <label class="text-muted small text-uppercase fw-bold">Date</label>
                <p class="mb-0">{{ formatDate(appointment.appointment_date) }}</p>
              </div>
              <div class="col-6">
                <label class="text-muted small text-uppercase fw-bold">Time</label>
                <p class="mb-0">{{ appointment.appointment_time }}</p>
              </div>
            </div>
          </div>
          <div class="col-md-6">
            <div class="mb-3">
              <label class="text-muted small text-uppercase fw-bold">Reason for Visit</label>
              <p class="mb-0">{{ appointment.reason }}</p>
            </div>
            <div>
              <label class="text-muted small text-uppercase fw-bold d-block mb-1">Status</label>
              <span class="badge px-3 py-2 rounded-pill" :class="getStatusBadge(appointment.status)">
                {{ appointment.status }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="card border-0 shadow-sm">
      <div class="card-header bg-white border-bottom py-3">
        <h5 class="mb-0 fw-bold text-primary">Treatment Details</h5>
      </div>
      <div class="card-body p-4">
        <form @submit.prevent="completeTreatment">
          <div class="mb-4">
            <label class="form-label fw-medium">Diagnosis <span class="text-danger">*</span></label>
            <textarea class="form-control" v-model="treatment.diagnosis" 
                      rows="3" required placeholder="Enter diagnosis..."></textarea>
          </div>
          
          <div class="mb-4">
            <label class="form-label fw-medium">Prescription</label>
            <textarea class="form-control" v-model="treatment.prescription" 
                      rows="3" placeholder="Enter prescription details..."></textarea>
          </div>
          
          <div class="mb-4">
            <label class="form-label fw-medium">Treatment Notes</label>
            <textarea class="form-control" v-model="treatment.notes" 
                      rows="3" placeholder="Enter additional notes..."></textarea>
          </div>
          
          <div class="mb-4">
            <label class="form-label fw-medium">Follow-up Date</label>
            <input type="date" class="form-control" v-model="treatment.follow_up_date">
          </div>
          
          <div class="d-flex justify-content-end gap-3">
            <button type="button" class="btn btn-outline-secondary px-4" @click="$router.back()">
              Cancel
            </button>
            <button type="submit" class="btn btn-primary px-4" :disabled="loading">
              <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
              {{ loading ? 'Saving...' : 'Complete Treatment' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { doctorService } from '@/services/api'

export default {
  name: 'CompleteTreatment',
  data() {
    return {
      appointment: null,
      treatment: {
        diagnosis: '',
        prescription: '',
        notes: '',
        follow_up_date: ''
      },
      loading: false
    }
  },
  async mounted() {
    await this.loadAppointment()
    
    const twoWeeks = new Date()
    twoWeeks.setDate(twoWeeks.getDate() + 14)
    this.treatment.follow_up_date = twoWeeks.toISOString().split('T')[0]
  },
  methods: {
    async loadAppointment() {
      try {
        const appointmentId = this.$route.params.id
        const response = await doctorService.getAppointments()
        const appointments = response.data.appointments || []
        this.appointment = appointments.find(a => a.id === parseInt(appointmentId))
        if (!this.appointment) {
          throw new Error('Appointment not found')
        }
      } catch (error) {
        console.error('Failed to load appointment:', error)
        alert('Failed to load appointment details')
        this.$router.push('/doctor/appointments')
      }
    },
    
    async completeTreatment() {
      if (!this.treatment.diagnosis.trim()) {
        alert('Diagnosis is required')
        return
      }
      
      this.loading = true
      
      try {
        await doctorService.completeAppointment(this.$route.params.id, this.treatment)
        alert('Treatment completed successfully!')
        this.$router.push('/doctor/appointments')
      } catch (error) {
        console.error('Failed to complete treatment:', error)
        alert(error.response?.data?.message || 'Failed to complete treatment')
      } finally {
        this.loading = false
      }
    },
    
    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString()
    },
    
    getStatusBadge(status) {
      switch (status) {
        case 'scheduled': return 'bg-primary bg-opacity-10 text-primary'
        case 'completed': return 'bg-success bg-opacity-10 text-success'
        case 'cancelled': return 'bg-danger bg-opacity-10 text-danger'
        default: return 'bg-secondary bg-opacity-10 text-secondary'
      }
    }
  }
}
</script>