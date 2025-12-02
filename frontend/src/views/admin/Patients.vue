<template>
  <div class="fade-in">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="h3 fw-bold text-primary mb-1">Manage Patients</h2>
        <p class="text-muted mb-0">View and manage patient records</p>
      </div>
    </div>
    
    <!-- Search -->
    <div class="card border-0 shadow-sm mb-4">
      <div class="card-body p-4">
        <div class="row align-items-end g-3">
          <div class="col-md-3">
            <label class="form-label fw-medium text-muted small text-uppercase">Search By</label>
            <select class="form-select form-select-lg" v-model="searchField">
              <option value="name">Search by Name</option>
              <option value="id">Search by ID</option>
              <option value="contact">Search by Contact</option>
            </select>
          </div>
          <div class="col-md-6">
            <label class="form-label fw-medium text-muted small text-uppercase">Search Query</label>
            <input 
              type="text" 
              class="form-control form-control-lg" 
              placeholder="Enter search query..."
              v-model="searchQuery"
              @keyup.enter="performSearch"
            >
          </div>
          <div class="col-md-3">
            <button class="btn btn-primary btn-lg w-100" @click="performSearch">
              Search
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Patients Table -->
    <div class="card border-0 shadow-sm">
      <div class="card-header bg-white border-bottom py-3">
        <h5 class="mb-0 fw-bold text-primary">Patients List</h5>
      </div>
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-hover mb-0 align-middle">
            <thead class="bg-light">
              <tr>
                <th class="ps-4">ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Gender</th>
                <th>Age</th>
                <th>Account</th>
                <th class="text-end pe-4">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="patient in patients" :key="patient.id">
                <td class="ps-4 text-muted">#{{ patient.id }}</td>
                <td class="fw-medium">{{ patient.full_name }}</td>
                <td>{{ patient.user?.email || 'N/A' }}</td>
                <td>{{ patient.phone }}</td>
                <td>
                  <span class="badge bg-light text-dark border">{{ patient.gender }}</span>
                </td>
                <td>{{ patient.age }}</td>
                <td>
                  <span v-if="patient.is_blocked" class="badge bg-danger bg-opacity-10 text-danger px-3 py-2 rounded-pill">
                    Blocked
                  </span>
                  <span v-else class="badge bg-success bg-opacity-10 text-success px-3 py-2 rounded-pill">
                    Active
                  </span>
                </td>
                <td class="text-end pe-4">
                  <div class="d-flex flex-column gap-1" style="min-width: 90px;">
                    <button class="btn btn-xs btn-outline-primary px-2 py-1" @click="editPatient(patient)" style="font-size: 0.75rem;">
                      Edit
                    </button>
                    <button 
                      v-if="patient.is_blocked" 
                      class="btn btn-xs btn-outline-success px-2 py-1" 
                      @click="unblockPatient(patient.id)"
                      style="font-size: 0.75rem;"
                    >
                      Unblock
                    </button>
                    <button 
                      v-else 
                      class="btn btn-xs btn-outline-warning px-2 py-1" 
                      @click="blockPatient(patient.id)"
                      style="font-size: 0.75rem;"
                    >
                      Block
                    </button>
                    <button class="btn btn-xs btn-outline-danger px-2 py-1" @click="deletePatient(patient.id)" style="font-size: 0.75rem;">
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="patients.length === 0">
                <td colspan="8" class="text-center py-5 text-muted">
                  No patients found
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    
    <!-- Edit Modal -->
    <BaseModal :show="showEditModal" title="Edit Patient" @close="closeModal">
      <form @submit.prevent="savePatient">
        <div class="row g-3 mb-3">
          <div class="col-md-6">
            <label class="form-label">First Name <span class="text-danger">*</span></label>
            <input type="text" class="form-control" v-model="patientForm.first_name" required>
          </div>
          <div class="col-md-6">
            <label class="form-label">Last Name <span class="text-danger">*</span></label>
            <input type="text" class="form-control" v-model="patientForm.last_name" required>
          </div>
        </div>
        <div class="mb-3">
          <label class="form-label">Phone <span class="text-danger">*</span></label>
          <input type="tel" class="form-control" v-model="patientForm.phone" required>
        </div>
        <div class="mb-3">
          <label class="form-label">Address</label>
          <textarea class="form-control" v-model="patientForm.address" rows="2"></textarea>
        </div>
        <div class="row g-3 mb-3">
          <div class="col-md-6">
            <label class="form-label">Emergency Contact</label>
            <input type="tel" class="form-control" v-model="patientForm.emergency_contact">
          </div>
          <div class="col-md-6">
            <label class="form-label">Blood Group</label>
            <select class="form-select" v-model="patientForm.blood_group">
              <option value="">Select Blood Group</option>
              <option value="A+">A+</option>
              <option value="A-">A-</option>
              <option value="B+">B+</option>
              <option value="B-">B-</option>
              <option value="AB+">AB+</option>
              <option value="AB-">AB-</option>
              <option value="O+">O+</option>
              <option value="O-">O-</option>
            </select>
          </div>
        </div>
      </form>
      <template #footer>
        <button type="button" class="btn btn-outline-secondary" @click="closeModal">Cancel</button>
        <button type="button" class="btn btn-primary px-4" @click="savePatient">Save Changes</button>
      </template>
    </BaseModal>
  </div>
</template>


<script>
import { adminService } from '@/services/api'
import BaseModal from '@/components/BaseModal.vue'

export default {
  name: 'AdminPatients',
  components: {
    BaseModal
  },
  data() {
    return {
      patients: [],
      searchQuery: '',
      searchField: 'name',
      showEditModal: false,
      editingPatient: null,
      patientForm: {
        first_name: '',
        last_name: '',
        phone: '',
        address: '',
        emergency_contact: '',
        blood_group: ''
      }
    }
  },
  async mounted() {
    await this.loadPatients()
  },
  methods: {
    async loadPatients() {
      try {
        const response = await adminService.getPatients()
        this.patients = response.data.patients
      } catch (error) {
        console.error('Failed to load patients:', error)
      }
    },
    
    async performSearch() {
      if (!this.searchQuery || !this.searchQuery.trim()) {
        
        await this.loadPatients()
        return
      }
      
      try {
        const response = await adminService.advancedSearch({
          type: 'patients',
          q: this.searchQuery.trim(),
          field: this.searchField
        })
        this.patients = response.data.patients || []
      } catch (error) {
        console.error('Search failed:', error)
        alert('Search failed. Please try again.')
      }
    },
    
    editPatient(patient) {
      this.editingPatient = patient
      this.patientForm = {
        first_name: patient.first_name,
        last_name: patient.last_name,
        phone: patient.phone,
        address: patient.address || '',
        emergency_contact: patient.emergency_contact || '',
        blood_group: patient.blood_group || ''
      }
      this.showEditModal = true
    },
    
    async savePatient() {
      try {
        await adminService.updatePatient(this.editingPatient.id, this.patientForm)
        this.closeModal()
        await this.loadPatients()
        alert('Patient updated successfully!')
      } catch (error) {
        alert(error.response?.data?.message || 'Failed to update patient!')
      }
    },
    
    
    async blockPatient(patientId) {
      if (!confirm('Are you sure you want to block this patient? They will not be able to log in.')) return
      
      try {
        await adminService.blockPatient(patientId)
        await this.loadPatients()
        alert('Patient blocked successfully!')
      } catch (error) {
        alert(error.response?.data?.message || 'Failed to block patient!')
      }
    },
    
    async unblockPatient(patientId) {
      if (!confirm('Are you sure you want to unblock this patient?')) return
      
      try {
        await adminService.unblockPatient(patientId)
        await this.loadPatients()
        alert('Patient unblocked successfully!')
      } catch (error) {
        alert(error.response?.data?.message || 'Failed to unblock patient!')
      }
    },
    
    async deletePatient(patientId) {
      if (!confirm('Are you sure you want to PERMANENTLY DELETE this patient? This action cannot be undone!')) return
      
      try {
        await adminService.deletePatient(patientId)
        await this.loadPatients()
        alert('Patient deleted successfully!')
      } catch (error) {
        alert(error.response?.data?.message || 'Failed to delete patient!')
      }
    },
    
    closeModal() {
      this.showEditModal = false
      this.editingPatient = null
      this.patientForm = {
        first_name: '',
        last_name: '',
        phone: '',
        address: '',
        emergency_contact: '',
        blood_group: ''
      }
    }
  }
}
</script>

