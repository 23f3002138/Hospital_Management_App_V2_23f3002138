<template>
  <div class="fade-in">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="h3 fw-bold text-primary mb-1">Manage Doctors</h2>
        <p class="text-muted mb-0">Add, edit, or remove medical staff</p>
      </div>
      <button class="btn btn-primary px-4" @click="showAddModal = true">
        Add Doctor
      </button>
    </div>
    
    <!-- Search -->
    <div class="card border-0 shadow-sm mb-4">
      <div class="card-body p-4">
        <div class="row align-items-end g-3">
          <div class="col-md-9">
            <label class="form-label fw-medium text-muted small text-uppercase">Search Query</label>
            <input 
              type="text" 
              class="form-control form-control-lg" 
              placeholder="Search by name or specialization..."
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
    
    <!-- Doctors Table -->
    <div class="card border-0 shadow-sm">
      <div class="card-header bg-white border-bottom py-3">
        <h5 class="mb-0 fw-bold text-primary">Doctors List</h5>
      </div>
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-hover mb-0 align-middle">
            <thead class="bg-light">
              <tr>
                <th class="ps-4">ID</th>
                <th>Name</th>
                <th>Specialization</th>
                <th>Department</th>
                <th>Phone</th>
                <th>Status</th>
                <th>Account</th>
                <th class="text-end pe-4">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="doctor in doctors" :key="doctor.id">
                <td class="ps-4 text-muted">#{{ doctor.id }}</td>
                <td class="fw-medium">{{ doctor.full_name }}</td>
                <td>{{ doctor.specialization }}</td>
                <td>
                  <span class="badge bg-light text-dark border">{{ doctor.department }}</span>
                </td>
                <td>{{ doctor.phone }}</td>
                <td>
                  <span :class="`badge bg-${doctor.is_available ? 'success' : 'danger'} bg-opacity-10 text-${doctor.is_available ? 'success' : 'danger'} px-3 py-2 rounded-pill`">
                    {{ doctor.is_available ? 'Available' : 'Unavailable' }}
                  </span>
                </td>
                <td>
                  <span v-if="doctor.is_blocked" class="badge bg-danger bg-opacity-10 text-danger px-3 py-2 rounded-pill">
                    Blocked
                  </span>
                  <span v-else class="badge bg-success bg-opacity-10 text-success px-3 py-2 rounded-pill">
                    Active
                  </span>
                </td>
                <td class="text-end pe-4">
                  <div class="d-flex flex-column gap-1" style="min-width: 90px;">
                    <button class="btn btn-xs btn-outline-primary px-2 py-1" @click="editDoctor(doctor)" style="font-size: 0.75rem;">
                      Edit
                    </button>
                    <button 
                      v-if="doctor.is_blocked" 
                      class="btn btn-xs btn-outline-success px-2 py-1" 
                      @click="unblockDoctor(doctor.id)"
                      style="font-size: 0.75rem;"
                    >
                      Unblock
                    </button>
                    <button 
                      v-else 
                      class="btn btn-xs btn-outline-warning px-2 py-1" 
                      @click="blockDoctor(doctor.id)"
                      style="font-size: 0.75rem;"
                    >
                      Block
                    </button>
                    <button class="btn btn-xs btn-outline-danger px-2 py-1" @click="deleteDoctor(doctor.id)" style="font-size: 0.75rem;">
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="doctors.length === 0">
                <td colspan="8" class="text-center py-5 text-muted">
                  No doctors found
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    
    <!-- Add/Edit Modal -->
    <BaseModal 
      :show="showAddModal || showEditModal" 
      :title="editingDoctor ? 'Edit Doctor' : 'Add Doctor'" 
      @close="closeModal"
    >
      <template #title>
        <div>
          <h5 class="modal-title h4 fw-bold text-primary">{{ editingDoctor ? 'Edit Doctor' : 'Add Doctor' }}</h5>
          <p class="text-muted small mb-0">Fill in the details below to {{ editingDoctor ? 'update the' : 'add a new' }} doctor.</p>
        </div>
      </template>
      
      <form @submit.prevent="saveDoctor">
        <h6 class="text-primary text-uppercase small fw-bold mb-3 border-bottom pb-2">Account Information</h6>
        <div class="row g-3 mb-4">
          <div class="col-md-6">
            <label class="form-label fw-medium text-muted small text-uppercase">Username <span class="text-danger">*</span></label>
            <input type="text" class="form-control form-control-lg" v-model="doctorForm.username" required placeholder="e.g. dr.smith">
          </div>
          <div class="col-md-6">
            <label class="form-label fw-medium text-muted small text-uppercase">Email <span class="text-danger">*</span></label>
            <input type="email" class="form-control form-control-lg" v-model="doctorForm.email" required placeholder="name@hospital.com">
          </div>
          <div class="col-md-12" v-if="!editingDoctor">
            <label class="form-label fw-medium text-muted small text-uppercase">Password <span class="text-danger">*</span></label>
            <input type="password" class="form-control form-control-lg" v-model="doctorForm.password" required placeholder="Create a strong password">
          </div>
        </div>

        <h6 class="text-primary text-uppercase small fw-bold mb-3 border-bottom pb-2">Personal Details</h6>
        <div class="row g-3 mb-4">
          <div class="col-md-6">
            <label class="form-label fw-medium text-muted small text-uppercase">First Name <span class="text-danger">*</span></label>
            <input type="text" class="form-control form-control-lg" v-model="doctorForm.first_name" required placeholder="John">
          </div>
          <div class="col-md-6">
            <label class="form-label fw-medium text-muted small text-uppercase">Last Name <span class="text-danger">*</span></label>
            <input type="text" class="form-control form-control-lg" v-model="doctorForm.last_name" required placeholder="Doe">
          </div>
          <div class="col-md-6">
            <label class="form-label fw-medium text-muted small text-uppercase">Phone <span class="text-danger">*</span></label>
            <input type="tel" class="form-control form-control-lg" v-model="doctorForm.phone" required placeholder="+1 (555) 000-0000">
          </div>
          <div class="col-12">
            <label class="form-label fw-medium text-muted small text-uppercase">Address <span class="text-danger">*</span></label>
            <textarea class="form-control form-control-lg" v-model="doctorForm.address" required rows="2" placeholder="Full address"></textarea>
          </div>
        </div>

        <h6 class="text-primary text-uppercase small fw-bold mb-3 border-bottom pb-2">Professional Information</h6>
        <div class="row g-3 mb-3">
          <div class="col-md-6">
            <label class="form-label fw-medium text-muted small text-uppercase">Department <span class="text-danger">*</span></label>
            <select class="form-select form-select-lg" v-model="doctorForm.department_id" required>
              <option value="">Select Department</option>
              <option v-for="dept in departments" :key="dept.id" :value="dept.id">
                {{ dept.name }}
              </option>
            </select>
          </div>
          <div class="col-md-6">
            <label class="form-label fw-medium text-muted small text-uppercase">Specialization <span class="text-danger">*</span></label>
            <input type="text" class="form-control form-control-lg" v-model="doctorForm.specialization" required placeholder="e.g. Cardiology">
          </div>
          <div class="col-md-6">
            <label class="form-label fw-medium text-muted small text-uppercase">Experience (years) <span class="text-danger">*</span></label>
            <input type="number" class="form-control form-control-lg" v-model="doctorForm.experience" required placeholder="0">
          </div>
          <div class="col-md-6">
            <label class="form-label fw-medium text-muted small text-uppercase">License Number <span class="text-danger">*</span></label>
            <input type="text" class="form-control form-control-lg" v-model="doctorForm.license_number" required placeholder="LIC-12345">
          </div>
          <div class="col-md-6">
            <label class="form-label fw-medium text-muted small text-uppercase">Consultation Fee <span class="text-danger">*</span></label>
            <div class="input-group input-group-lg">
              <span class="input-group-text bg-light border-end-0">$</span>
              <input type="number" step="0.01" class="form-control border-start-0 ps-0" v-model="doctorForm.consultation_fee" required placeholder="0.00">
            </div>
          </div>
          <div class="col-md-6 d-flex align-items-center">
            <div class="form-check form-switch form-switch-lg">
              <input class="form-check-input" type="checkbox" v-model="doctorForm.is_available" id="is_available">
              <label class="form-check-label fw-medium ms-2" for="is_available">
                Available for appointments
              </label>
            </div>
          </div>
        </div>
      </form>

      <template #footer>
        <button type="button" class="btn btn-light btn-lg px-4" @click="closeModal">Cancel</button>
        <button type="button" class="btn btn-primary btn-lg px-5 shadow-sm" @click="saveDoctor">
          {{ editingDoctor ? 'Update Doctor' : 'Create Account' }}
        </button>
      </template>
    </BaseModal>
  </div>
</template>

<script>
import { adminService, commonService } from '@/services/api'
import BaseModal from '@/components/BaseModal.vue'

export default {
  name: 'AdminDoctors',
  components: {
    BaseModal
  },
  data() {
    return {
      doctors: [],
      departments: [],
      searchQuery: '',
      showAddModal: false,
      showEditModal: false,
      editingDoctor: null,
      doctorForm: {
        username: '',
        email: '',
        password: '',
        first_name: '',
        last_name: '',
        department_id: '',
        specialization: '',
        phone: '',
        address: '',
        license_number: '',
        experience: 0,
        consultation_fee: 0,
        is_available: true
      }
    }
  },
  async mounted() {
    await this.loadDoctors()
    await this.loadDepartments()
  },
  methods: {
    async loadDoctors() {
      try {
        console.log('Loading doctors...')
        const response = await adminService.getDoctors({ _t: Date.now() })
        console.log('Doctors loaded:', response.data.doctors.length)
        this.doctors = response.data.doctors
      } catch (error) {
        console.error('Failed to load doctors:', error)
      }
    },
    
    async loadDepartments() {
      try {
        const response = await commonService.getDepartments()
        this.departments = response.data.departments
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
        const response = await adminService.advancedSearch({
          type: 'doctors',
          q: this.searchQuery.trim(),
          field: 'name'
        })
        this.doctors = response.data.doctors || []
      } catch (error) {
        console.error('Search failed:', error)
        alert('Search failed. Please try again.')
      }
    },
    
    editDoctor(doctor) {
      this.editingDoctor = doctor
      this.doctorForm = {
        username: doctor.user?.username || '',
        email: doctor.user?.email || '',
        first_name: doctor.first_name,
        last_name: doctor.last_name,
        department_id: doctor.department_id,
        specialization: doctor.specialization,
        phone: doctor.phone,
        address: doctor.address || '',
        license_number: doctor.license_number || '',
        experience: doctor.experience || 0,
        consultation_fee: doctor.consultation_fee || 0,
        is_available: doctor.is_available
      }
      this.showEditModal = true
    },
    
    async saveDoctor() {
      try {
        if (this.editingDoctor) {
          await adminService.updateDoctor(this.editingDoctor.id, this.doctorForm)
        } else {
          await adminService.addDoctor(this.doctorForm)
        }
        await this.loadDoctors()
        alert('Doctor saved successfully!')
        this.closeModal()

      } catch (error) {
        console.error('saveDoctor error:', error)
        alert(error.response?.data?.message || 'Failed to save doctor!')
      }
    },

    async blockDoctor(doctorId) {
      if (!confirm('Are you sure you want to block this doctor? They will not be able to log in.')) return
      
      try {
        console.log('Blocking doctor:', doctorId)
        await adminService.blockDoctor(doctorId)
        console.log('Block API success')
        await this.loadDoctors()
        console.log('List refreshed')
        alert('Doctor blocked successfully!')
        window.location.reload()
      } catch (error) {
        console.error('Block failed:', error)
        alert(error.response?.data?.message || 'Failed to block doctor!')
      }
    },

    async unblockDoctor(doctorId) {
      if (!confirm('Are you sure you want to unblock this doctor?')) return
      
      try {
        await adminService.unblockDoctor(doctorId)
        await this.loadDoctors()
        alert('Doctor unblocked successfully!')
      } catch (error) {
        alert(error.response?.data?.message || 'Failed to unblock doctor!')
      }
    },

    async deleteDoctor(doctorId) {
      if (!confirm('Are you sure you want to PERMANENTLY DELETE this doctor? This action cannot be undone!')) return
      
      try {
        console.log('Deleting doctor:', doctorId)
        await adminService.deleteDoctor(doctorId)
        console.log('Delete API success')
        await this.loadDoctors()
        console.log('List refreshed')
        alert('Doctor deleted successfully!')
        window.location.reload()
      } catch (error) {
        console.error('Delete failed:', error)
        alert(error.response?.data?.message || 'Failed to delete doctor!')
      }
    },
    
    closeModal() {
      this.showAddModal = false
      this.showEditModal = false
      this.editingDoctor = null
      this.doctorForm = {
        username: '',
        email: '',
        password: '',
        first_name: '',
        last_name: '',
        department_id: '',
        specialization: '',
        phone: '',
        address: '',
        license_number: '',
        experience: 0,
        consultation_fee: 0,
        is_available: true
      }
    }
  }
}
</script>
