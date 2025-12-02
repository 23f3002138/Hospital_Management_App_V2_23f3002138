<template>
  <div class="fade-in">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="h3 fw-bold text-primary mb-1">Manage Departments</h2>
        <p class="text-muted mb-0">Add and view hospital departments</p>
      </div>
      <button class="btn btn-primary px-4" @click="showAddModal = true">
        Add Department
      </button>
    </div>
    
    <!-- Departments Table -->
    <div class="card border-0 shadow-sm">
      <div class="card-header bg-white border-bottom py-3">
        <h5 class="mb-0 fw-bold text-primary">Departments List</h5>
      </div>
      <div class="card-body p-0">
        <div class="table-responsive">
          <table class="table table-hover mb-0 align-middle">
            <thead class="bg-light">
              <tr>
                <th class="ps-4">ID</th>
                <th>Name</th>
                <th>Description</th>
                <th>Doctors Count</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="dept in departments" :key="dept.id">
                <td class="ps-4 text-muted">#{{ dept.id }}</td>
                <td class="fw-medium">{{ dept.name }}</td>
                <td class="text-muted small">{{ dept.description || 'N/A' }}</td>
                <td>
                  <span class="badge bg-info bg-opacity-10 text-info px-3 py-2 rounded-pill">
                    {{ dept.doctors_count }} Doctors
                  </span>
                </td>
              </tr>
              <tr v-if="departments.length === 0">
                <td colspan="4" class="text-center py-5 text-muted">
                  No departments found
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    
    <!-- Add Modal -->
    <BaseModal 
      :show="showAddModal" 
      title="Add Department" 
      @close="closeModal"
    >
      <template #title>
        <div>
          <h5 class="modal-title h4 fw-bold text-primary">Add Department</h5>
          <p class="text-muted small mb-0">Create a new medical department.</p>
        </div>
      </template>
      
      <form @submit.prevent="saveDepartment">
        <div class="mb-3">
          <label class="form-label fw-medium text-muted small text-uppercase">Name <span class="text-danger">*</span></label>
          <input type="text" class="form-control form-control-lg" v-model="departmentForm.name" required placeholder="e.g. Cardiology">
        </div>
        <div class="mb-3">
          <label class="form-label fw-medium text-muted small text-uppercase">Description</label>
          <textarea class="form-control form-control-lg" v-model="departmentForm.description" rows="3" placeholder="Department description..."></textarea>
        </div>
      </form>

      <template #footer>
        <button type="button" class="btn btn-light btn-lg px-4" @click="closeModal">Cancel</button>
        <button type="button" class="btn btn-primary btn-lg px-5 shadow-sm" @click="saveDepartment">
          Create Department
        </button>
      </template>
    </BaseModal>
  </div>
</template>

<script>
import { commonService, adminService } from '@/services/api'
import BaseModal from '@/components/BaseModal.vue'

export default {
  name: 'AdminDepartments',
  components: {
    BaseModal
  },
  data() {
    return {
      departments: [],
      showAddModal: false,
      departmentForm: {
        name: '',
        description: ''
      }
    }
  },
  async mounted() {
    await this.loadDepartments()
  },
  methods: {
    async loadDepartments() {
      try {
        const response = await commonService.getDepartments()
        this.departments = response.data.departments
      } catch (error) {
        console.error('Failed to load departments:', error)
      }
    },
    
    async saveDepartment() {
      if (!this.departmentForm.name) return
      
      try {
        await adminService.addDepartment(this.departmentForm)
        this.closeModal()
        await this.loadDepartments()
        alert('Department added successfully!')
      } catch (error) {
        alert(error.response?.data?.message || 'Failed to add department!')
      }
    },
    
    closeModal() {
      this.showAddModal = false
      this.departmentForm = {
        name: '',
        description: ''
      }
    }
  }
}
</script>
