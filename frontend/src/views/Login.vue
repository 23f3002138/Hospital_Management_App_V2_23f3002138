<template>
  <div class="login-container fade-in">
    <div class="row justify-content-center w-100">
      <div class="col-md-6 col-lg-4">
        <div class="text-center mb-4">
          <h1 class="h3 fw-bold text-primary">Welcome Back</h1>
          <p class="text-muted">Sign in to your account to continue</p>
        </div>
        
        <div class="card border-0 shadow-lg">
          <div class="card-body p-4 p-md-5">
            <form @submit.prevent="handleLogin">
              <div class="mb-4">
                <label for="username" class="form-label">Username</label>
                <input 
                  type="text" 
                  class="form-control form-control-lg" 
                  id="username"
                  v-model="credentials.username"
                  placeholder="Enter your username"
                  required
                >
              </div>
              
              <div class="mb-4">
                <label for="password" class="form-label">Password</label>
                <input 
                  type="password" 
                  class="form-control form-control-lg" 
                  id="password"
                  v-model="credentials.password"
                  placeholder="Enter your password"
                  required
                >
              </div>
                
              <div class="d-grid gap-2 mt-5">
                <button type="submit" class="btn btn-primary btn-lg" :disabled="loading">
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                  {{ loading ? 'Signing in...' : 'Sign In' }}
                </button>
              </div>
              
              <div class="text-center mt-4">
                <p class="mb-0 text-muted">
                  New to HospitalOS? 
                  <router-link to="/register" class="text-decoration-none fw-medium">Create an account</router-link>
                </p>
              </div>
            </form>
            
            <div v-if="error" class="alert alert-danger mt-4 mb-0 text-center">
              {{ error }}
            </div>
          </div>
        </div>
        
        <!--  -->
        <div class="mt-4 text-center">
          <p class="text-muted small mb-2"></p>
          <div class="d-flex justify-content-center gap-3 flex-wrap">
            <span class="badge bg-white text-dark border fw-normal py-2 px-3"></span>
            <span class="badge bg-white text-dark border fw-normal py-2 px-3"></span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex'

export default {
  name: 'Login',
  data() {
    return {
      credentials: {
        username: '',
        password: ''
      },
      loading: false,
      error: ''
    }
  },
  methods: {
    ...mapActions(['login']),
    
    async handleLogin() {
      this.loading = true
      this.error = ''
      
      try {
        const result = await this.login(this.credentials)
        
        await new Promise(resolve => setTimeout(resolve, 200))
        
        const token = localStorage.getItem('token')
        if (!token) {
          this.error = 'Token not stored. Please try again.'
          return
        }
        
        if (this.$store.state.user && this.$store.state.isAuthenticated) {
          this.$router.push('/dashboard')
        } else {
          this.error = 'Login successful but user data not loaded. Please try again.'
        }
      } catch (error) {
        this.error = error.message || error.msg || 'Login failed!'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.login-container {
  min-height: calc(100vh - 200px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 0;
}

.form-control-lg {
  font-size: 1rem;
  padding: 0.8rem 1.2rem;
}

.card {
  border-radius: 1rem;
}
</style>
