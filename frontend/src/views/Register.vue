<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-8 col-lg-6">
        <div class="card border-0 shadow-lg">
          <div class="card-body p-4 p-md-5">
            <form @submit.prevent="handleRegister">
              <h5 class="mb-4 text-secondary border-bottom pb-2">Account Information</h5>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="username" class="form-label">Username *</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    id="username"
                    v-model="formData.username"
                    required
                  >
                </div>
                
                <div class="col-md-6 mb-3">
                  <label for="email" class="form-label">Email *</label>
                  <input 
                    type="email" 
                    class="form-control" 
                    id="email"
                    v-model="formData.email"
                    required
                  >
                </div>
              </div>
              
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="password" class="form-label">Password *</label>
                  <input 
                    type="password" 
                    class="form-control" 
                    id="password"
                    v-model="formData.password"
                    required
                    minlength="8"
                  >
                </div>
                
                <div class="col-md-6 mb-3">
                  <label for="first_name" class="form-label">First Name *</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    id="first_name"
                    v-model="formData.first_name"
                    required
                  >
                </div>
              </div>

              <h5 class="mb-4 mt-4 text-secondary border-bottom pb-2">Personal Details</h5>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="last_name" class="form-label">Last Name *</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    id="last_name"
                    v-model="formData.last_name"
                    required
                  >
                </div>
                
                <div class="col-md-6 mb-3">
                  <label for="date_of_birth" class="form-label">Date of Birth *</label>
                  <input 
                    type="date" 
                    class="form-control" 
                    id="date_of_birth"
                    v-model="formData.date_of_birth"
                    required
                  >
                </div>
              </div>
              
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="gender" class="form-label">Gender *</label>
                  <select 
                    class="form-select" 
                    id="gender"
                    v-model="formData.gender"
                    required
                  >
                    <option value="">Select Gender</option>
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                  </select>
                </div>
                
                <div class="col-md-6 mb-3">
                  <label for="phone" class="form-label">Phone *</label>
                  <input 
                    type="tel" 
                    class="form-control" 
                    id="phone"
                    v-model="formData.phone"
                    required
                  >
                </div>
              </div>
              
              <div class="mb-3">
                <label for="address" class="form-label">Address</label>
                <textarea 
                  class="form-control" 
                  id="address"
                  v-model="formData.address"
                  rows="2"
                ></textarea>
              </div>
              
              <h5 class="mb-4 mt-4 text-secondary border-bottom pb-2">Medical Info (Optional)</h5>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="emergency_contact" class="form-label">Emergency Contact</label>
                  <input 
                    type="tel" 
                    class="form-control" 
                    id="emergency_contact"
                    v-model="formData.emergency_contact"
                  >
                </div>
                
                <div class="col-md-6 mb-3">
                  <label for="blood_group" class="form-label">Blood Group</label>
                  <select 
                    class="form-select" 
                    id="blood_group"
                    v-model="formData.blood_group"
                  >
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
              
              <div class="d-grid mt-4">
                <button type="submit" class="btn btn-primary btn-lg" :disabled="loading">
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                  {{ loading ? 'Creating Account...' : 'Register' }}
                </button>
              </div>
              
              <div class="text-center mt-4">
                <p class="mb-0 text-muted">
                  Already have an account? <router-link to="/login" class="text-decoration-none fw-medium">Login here</router-link>
                </p>
              </div>
            </form>
            
            <div v-if="error" class="alert alert-danger mt-4 text-center">
              {{ error }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex'

export default {
  name: 'Register',
  data() {
    return {
      formData: {
        username: '',
        email: '',
        password: '',
        first_name: '',
        last_name: '',
        date_of_birth: '',
        gender: '',
        phone: '',
        address: '',
        emergency_contact: '',
        blood_group: ''
      },
      loading: false,
      error: ''
    }
  },
  methods: {
    ...mapActions(['register']),
    
    async handleRegister() {
      this.loading = true
      this.error = ''
      
      try {
        await this.register(this.formData)
        this.$router.push('/dashboard')
      } catch (error) {
        this.error = error.response?.data?.message || error.message || 'Registration failed!'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.register-container {
  min-height: calc(100vh - 200px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 0;
}

.card {
  border-radius: 1rem;
}
</style>
