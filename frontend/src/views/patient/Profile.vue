<template>
  <div class="fade-in">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="h3 fw-bold text-primary mb-1">My Profile</h2>
        <p class="text-muted mb-0">Manage your personal information</p>
      </div>
    </div>

    <div class="row justify-content-center">
      <div class="col-lg-8">
        <div class="card border-0 shadow-sm">
          <div class="card-body p-4">
            <form @submit.prevent="saveProfile">
              <h6 class="text-primary text-uppercase small fw-bold mb-3 border-bottom pb-2">Personal Details</h6>
              
              <div class="row g-3 mb-4">
                <div class="col-md-6">
                  <label class="form-label fw-medium text-muted small text-uppercase">First Name</label>
                  <input type="text" class="form-control form-control-lg" v-model="profileForm.first_name" required>
                </div>
                <div class="col-md-6">
                  <label class="form-label fw-medium text-muted small text-uppercase">Last Name</label>
                  <input type="text" class="form-control form-control-lg" v-model="profileForm.last_name" required>
                </div>
                <div class="col-md-6">
                  <label class="form-label fw-medium text-muted small text-uppercase">Date of Birth</label>
                  <input type="text" class="form-control form-control-lg bg-light" :value="formatDate(profile.date_of_birth)" readonly>
                  <small class="text-muted">Contact admin to change DOB</small>
                </div>
                <div class="col-md-6">
                  <label class="form-label fw-medium text-muted small text-uppercase">Gender</label>
                  <input type="text" class="form-control form-control-lg bg-light" :value="profile.gender" readonly>
                </div>
              </div>

              <h6 class="text-primary text-uppercase small fw-bold mb-3 border-bottom pb-2">Contact Information</h6>
              
              <div class="row g-3 mb-4">
                <div class="col-md-6">
                  <label class="form-label fw-medium text-muted small text-uppercase">Phone <span class="text-danger">*</span></label>
                  <input type="tel" class="form-control form-control-lg" v-model="profileForm.phone" required>
                </div>
                <div class="col-md-6">
                  <label class="form-label fw-medium text-muted small text-uppercase">Emergency Contact</label>
                  <input type="tel" class="form-control form-control-lg" v-model="profileForm.emergency_contact">
                </div>
                <div class="col-12">
                  <label class="form-label fw-medium text-muted small text-uppercase">Address</label>
                  <textarea class="form-control form-control-lg" v-model="profileForm.address" rows="2"></textarea>
                </div>
              </div>

              <h6 class="text-primary text-uppercase small fw-bold mb-3 border-bottom pb-2">Medical Information</h6>
              
              <div class="row g-3 mb-4">
                <div class="col-md-6">
                  <label class="form-label fw-medium text-muted small text-uppercase">Blood Group</label>
                  <select class="form-select form-select-lg" v-model="profileForm.blood_group">
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

              <div class="d-flex justify-content-end gap-3 mt-5">
                <button type="button" class="btn btn-light btn-lg px-4" @click="$router.push('/dashboard')">Cancel</button>
                <button type="submit" class="btn btn-primary btn-lg px-5 shadow-sm" :disabled="saving">
                  {{ saving ? 'Saving...' : 'Save Changes' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { patientService } from '@/services/api'

export default {
  name: 'PatientProfile',
  data() {
    return {
      profile: {},
      profileForm: {
        first_name: '',
        last_name: '',
        phone: '',
        address: '',
        emergency_contact: '',
        blood_group: ''
      },
      saving: false
    }
  },
  async mounted() {
    await this.loadProfile()
  },
  methods: {
    async loadProfile() {
      try {
        const response = await patientService.getDashboard()
        this.profile = response.data.patient
        
        // Initialize form
        this.profileForm = {
          first_name: this.profile.first_name,
          last_name: this.profile.last_name,
          phone: this.profile.phone,
          address: this.profile.address || '',
          emergency_contact: this.profile.emergency_contact || '',
          blood_group: this.profile.blood_group || ''
        }
      } catch (error) {
        console.error('Failed to load profile:', error)
        alert('Failed to load profile data.')
      }
    },
    
    async saveProfile() {
      this.saving = true
      try {
        await patientService.updateProfile(this.profileForm)
        alert('Profile updated successfully!')
        await this.loadProfile()
      } catch (error) {
        console.error('Failed to update profile:', error)
        alert(error.response?.data?.message || 'Failed to update profile!')
      } finally {
        this.saving = false
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString()
    }
  }
}
</script>
