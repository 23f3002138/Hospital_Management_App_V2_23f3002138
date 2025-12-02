<template>
  <div class="fade-in">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="h3 fw-bold text-primary mb-1">My Patients</h2>
        <p class="text-muted mb-0">View patient records and history</p>
      </div>
    </div>
    
    <!-- Search -->
    <div class="card border-0 shadow-sm mb-4">
      <div class="card-body p-4">
        <div class="row g-3 align-items-end">
          <div class="col-md-8">
            <label class="form-label fw-medium text-muted small text-uppercase">Search Patients</label>
            <input 
              type="text" 
              class="form-control form-control-lg" 
              placeholder="Search by name, phone, or blood group..."
              v-model="searchQuery"
              @keyup.enter="performSearch"
            >
          </div>
          <div class="col-md-4">
            <button class="btn btn-primary btn-lg w-100" @click="performSearch">
              Search
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Patients List -->
    <div class="row g-4">
      <div v-for="patient in patients" :key="patient.id" class="col-md-6 col-lg-4">
        <div class="card border-0 shadow-sm h-100 hover-shadow transition-all">
          <div class="card-body p-4 d-flex flex-column">
            <div class="d-flex align-items-center mb-3">
              <div class="bg-primary bg-opacity-10 text-primary rounded-circle p-3 me-3">
                <span class="fw-bold fs-5">{{ patient.full_name.charAt(0) }}</span>
              </div>
              <div>
                <h5 class="card-title fw-bold text-primary mb-0">{{ patient.full_name }}</h5>
                <span class="text-muted small">{{ patient.gender }}, {{ patient.age }} years</span>
              </div>
            </div>
            
            <div class="mb-4 flex-grow-1">
              <div class="d-flex justify-content-between mb-2 border-bottom pb-2">
                <span class="text-muted">Phone</span>
                <span class="fw-medium">{{ patient.phone }}</span>
              </div>
              <div class="d-flex justify-content-between mb-2">
                <span class="text-muted">Blood Group</span>
                <span class="badge bg-danger bg-opacity-10 text-danger rounded-pill">{{ patient.blood_group || 'N/A' }}</span>
              </div>
            </div>
            
            <div class="d-grid gap-2">
              <button class="btn btn-outline-primary" @click="viewHistory(patient.id)">
                View Recent History
              </button>
              <button class="btn btn-primary" @click="viewFullHistory(patient.id)">
                View Full History
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <div v-if="patients.length === 0" class="col-12 text-center py-5">
        <p class="text-muted fs-5">No patients found matching your criteria.</p>
      </div>
    </div>
    
    <!-- History Modal -->
    <BaseModal :show="showHistoryModal" title="Patient History" @close="closeHistoryModal">
      <div v-if="history.length === 0" class="text-center py-4 text-muted">
        No history records found for this patient
      </div>
      <div v-else>
        <div v-for="record in history" :key="record.id" class="card border-0 bg-light mb-3 rounded-3">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h6 class="fw-bold text-primary mb-0">Visit Date: {{ formatDate(record.appointment_date) }}</h6>
              <span class="badge bg-secondary bg-opacity-10 text-secondary rounded-pill">Completed</span>
            </div>
            <div v-if="record.treatment">
              <div class="mb-2">
                <span class="text-muted small text-uppercase fw-bold d-block mb-1">Diagnosis</span>
                <p class="mb-0">{{ record.treatment.diagnosis }}</p>
              </div>
              <div class="row">
                <div class="col-md-6" v-if="record.treatment.prescription">
                  <span class="text-muted small text-uppercase fw-bold d-block mb-1">Prescription</span>
                  <p class="mb-0 small">{{ record.treatment.prescription }}</p>
                </div>
                <div class="col-md-6" v-if="record.treatment.notes">
                  <span class="text-muted small text-uppercase fw-bold d-block mb-1">Notes</span>
                  <p class="mb-0 small">{{ record.treatment.notes }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <button type="button" class="btn btn-secondary px-4 rounded-pill" @click="closeHistoryModal">Close</button>
      </template>
    </BaseModal>
  </div>
</template>

<script>
import { doctorService } from '@/services/api'
import BaseModal from '@/components/BaseModal.vue'

export default {
  name: 'DoctorPatients',
  components: {
    BaseModal
  },
  data() {
    return {
      patients: [],
      allPatients: [],
      searchQuery: '',
      showHistoryModal: false,
      history: [],
      currentPatientId: null,
      isFullHistory: false
    }
  },
  async mounted() {
    await this.loadPatients()
  },
  methods: {
    async loadPatients() {
      try {
        const response = await doctorService.getPatients()
        this.allPatients = response.data.patients || []
        this.performSearch()
      } catch (error) {
        console.error('Failed to load patients:', error)
      }
    },
    
    performSearch() {
      if (!this.searchQuery || !this.searchQuery.trim()) {
        
        this.patients = this.allPatients
        return
      }
      
      
      const query = this.searchQuery.trim().toLowerCase()
      this.patients = this.allPatients.filter(patient => {
        const fullName = (patient.full_name || '').toLowerCase()
        const phone = (patient.phone || '').toLowerCase()
        const bloodGroup = (patient.blood_group || '').toLowerCase()
        return fullName.includes(query) || phone.includes(query) || bloodGroup.includes(query)
      })
    },
    
    async viewHistory(patientId) {
      this.currentPatientId = patientId
      this.isFullHistory = false
      try {
        const response = await doctorService.getPatientHistory(patientId)
        this.history = response.data.history || []
        this.showHistoryModal = true
      } catch (error) {
        console.error('Failed to load history:', error)
        alert('Failed to load patient history!')
      }
    },
    
    async viewFullHistory(patientId) {
      this.currentPatientId = patientId
      this.isFullHistory = true
      try {
        const response = await doctorService.getPatientFullHistory(patientId)
        this.history = response.data.patient_history || []
        this.showHistoryModal = true
      } catch (error) {
        console.error('Failed to load full history:', error)
        alert('Failed to load full patient history!')
      }
    },
    
    closeHistoryModal() {
      this.showHistoryModal = false
      this.history = []
      this.currentPatientId = null
    },
    
    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString()
    }
  }
}
</script>

