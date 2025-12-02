<template>
  <div class="fade-in">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="h3 fw-bold text-primary mb-1">Find Doctors</h2>
        <p class="text-muted mb-0">Search and book appointments with top specialists</p>
      </div>
    </div>
    
    <!-- Search and Filters -->
    <div class="card border-0 shadow-sm mb-4">
      <div class="card-body p-4">
        <div class="row g-3 align-items-end">
          <div class="col-md-4">
            <label class="form-label fw-medium text-muted small text-uppercase">Search Doctors</label>
            <input 
              type="text" 
              class="form-control form-control-lg" 
              placeholder="Search by name or specialization..."
              v-model="searchQuery"
              @keyup.enter="performSearch"
            >
          </div>
          <div class="col-md-4">
            <label class="form-label fw-medium text-muted small text-uppercase">Department</label>
            <select class="form-select form-select-lg" v-model="selectedDepartment">
              <option value="">All Departments</option>
              <option v-for="dept in departments" :key="dept.id" :value="dept.id">
                {{ dept.name }}
              </option>
            </select>
          </div>
          <div class="col-md-4">
            <button class="btn btn-primary btn-lg w-100" @click="performSearch">
              Search
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Departments List -->
    <div class="card border-0 shadow-sm mb-4">
      <div class="card-header bg-white border-bottom py-3">
        <h5 class="mb-0 fw-bold text-primary">Available Specializations</h5>
      </div>
      <div class="card-body p-4">
        <div class="row g-3">
          <div v-for="dept in departments" :key="dept.id" class="col-md-3">
            <button class="btn btn-outline-primary w-100 py-2" @click="filterByDepartment(dept.id)">
              {{ dept.name }}
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Doctors List -->
    <div class="row g-4">
      <div v-for="doctor in doctors" :key="doctor.id" class="col-md-6 col-lg-4">
        <div class="card border-0 shadow-sm h-100 hover-shadow transition-all">
          <div class="card-body p-4 d-flex flex-column">
            <div class="mb-3">
              <h5 class="card-title fw-bold text-primary mb-1">Dr. {{ doctor.full_name }}</h5>
              <span class="badge bg-primary bg-opacity-10 text-primary px-2 py-1 rounded-pill">
                {{ doctor.specialization }}
              </span>
            </div>
            
            <div class="mb-4 flex-grow-1">
              <div class="d-flex justify-content-between mb-2 border-bottom pb-2">
                <span class="text-muted">Department</span>
                <span class="fw-medium">{{ doctor.department }}</span>
              </div>
              <div class="d-flex justify-content-between mb-2 border-bottom pb-2">
                <span class="text-muted">Experience</span>
                <span class="fw-medium">{{ doctor.experience || 'N/A' }} years</span>
              </div>
              <div class="d-flex justify-content-between">
                <span class="text-muted">Consultation Fee</span>
                <span class="fw-bold text-success">${{ doctor.consultation_fee || '0.00' }}</span>
              </div>
            </div>
            
            <button class="btn btn-primary w-100 mt-auto" @click="viewDoctor(doctor)">
              Book Appointment
            </button>
          </div>
        </div>
      </div>
      
      <div v-if="doctors.length === 0" class="col-12 text-center py-5">
        <p class="text-muted fs-5">No doctors found matching your criteria.</p>
      </div>
    </div>
    
    <!-- Doctor Details & Booking Modal -->
    <BaseModal 
      :show="showBookingModal" 
      :title="`Book Appointment with Dr. ${selectedDoctor?.full_name}`" 
      @close="closeBookingModal"
    >
      <div v-if="selectedDoctor">
        <h6 class="fw-bold text-primary mb-3">Availability for Next 7 Days</h6>
        
        <div v-if="availabilities.length === 0" class="alert alert-light border text-center py-3 mb-4">
          No availability set for the next 7 days
        </div>
        <div v-else class="d-flex flex-wrap gap-2 mb-4">
          <button 
            v-for="avail in availabilities" 
            :key="avail.id"
            class="btn btn-outline-primary btn-sm"
            @click="selectTimeSlot(avail)"
          >
            {{ formatDate(avail.date) }} <br>
            <small>{{ avail.start_time }} - {{ avail.end_time }}</small>
          </button>
        </div>
        
        <form @submit.prevent="bookAppointment">
          <div class="row g-3 mb-3">
            <div class="col-md-6">
              <label class="form-label">Appointment Date <span class="text-danger">*</span></label>
              <input 
                type="date" 
                class="form-control" 
                v-model="appointmentForm.appointment_date"
                :min="minDate"
                required
              >
            </div>
            <div class="col-md-6">
              <label class="form-label">Appointment Time <span class="text-danger">*</span></label>
              <input 
                type="time" 
                class="form-control" 
                v-model="appointmentForm.appointment_time"
                required
              >
            </div>
          </div>
          <div class="mb-4">
            <label class="form-label">Reason for Visit <span class="text-danger">*</span></label>
            <textarea 
              class="form-control" 
              v-model="appointmentForm.reason"
              rows="3"
              required
              placeholder="Describe your symptoms or reason for visit..."
            ></textarea>
          </div>
          <div class="d-grid">
            <button type="submit" class="btn btn-primary btn-lg" :disabled="loading">
              <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
              {{ loading ? 'Booking...' : 'Confirm Appointment' }}
            </button>
          </div>
        </form>
      </div>
    </BaseModal>
  </div>
</template>

<script>
import { patientService, commonService } from '@/services/api'
import BaseModal from '@/components/BaseModal.vue'

export default {
  name: 'FindDoctors',
  components: {
    BaseModal
  },
  data() {
    return {
      doctors: [],
      departments: [],
      searchQuery: '',
      selectedDepartment: '',
      showBookingModal: false,
      selectedDoctor: null,
      availabilities: [],
      appointmentForm: {
        doctor_id: null,
        appointment_date: '',
        appointment_time: '',
        reason: ''
      },
      loading: false
    }
  },
  computed: {
    minDate() {
      return new Date().toISOString().split('T')[0]
    }
  },
  async mounted() {
    await this.loadDoctors()
    await this.loadDepartments()
  },
  methods: {
    async loadDoctors() {
      try {
        const params = {}
        if (this.selectedDepartment) params.department_id = this.selectedDepartment
        const response = await commonService.getDoctors(params)
        this.doctors = response.data.doctors || []
      } catch (error) {
        console.error('Failed to load doctors:', error)
      }
    },
    
    async loadDepartments() {
      try {
        const response = await commonService.getDepartments()
        this.departments = response.data.departments || []
      } catch (error) {
        console.error('Failed to load departments:', error)
      }
    },
    
    async performSearch() {
      
      if (!this.searchQuery || !this.searchQuery.trim()) {
        await this.loadDoctors()
        return
      }
      
      try {
        
        const response = await patientService.searchDoctors({ 
          q: this.searchQuery.trim() 
        })
        let doctors = response.data.doctors || []
        
        
        if (this.selectedDepartment) {
          doctors = doctors.filter(doctor => 
            doctor.department_id === parseInt(this.selectedDepartment)
          )
        }
        
        this.doctors = doctors
      } catch (error) {
        console.error('Search failed:', error)
        alert('Search failed. Please try again.')
      }
    },
    
    filterByDepartment(departmentId) {
      this.selectedDepartment = departmentId
      this.performSearch()
    },
    
    async viewDoctor(doctor) {
      this.selectedDoctor = doctor
      this.appointmentForm.doctor_id = doctor.id
      this.showBookingModal = true
      
      try {
        const response = await patientService.getDoctorAvailability(doctor.id)
        this.availabilities = response.data.availabilities || []
      } catch (error) {
        console.error('Failed to load availability:', error)
      }
    },
    
    selectTimeSlot(availability) {
      this.appointmentForm.appointment_date = availability.date
      this.appointmentForm.appointment_time = availability.start_time
    },
    
    async bookAppointment() {
      this.loading = true
      
      try {
        await patientService.bookAppointment(this.appointmentForm)
        alert('Appointment booked successfully!')
        this.closeBookingModal()
        this.$router.push('/patient/appointments')
      } catch (error) {
        alert(error.response?.data?.message || 'Failed to book appointment!')
      } finally {
        this.loading = false
      }
    },
    
    closeBookingModal() {
      this.showBookingModal = false
      this.selectedDoctor = null
      this.availabilities = []
      this.appointmentForm = {
        doctor_id: null,
        appointment_date: '',
        appointment_time: '',
        reason: ''
      }
    },
    
    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString()
    }
  }
}
</script>

