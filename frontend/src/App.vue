<template>
  <div id="app">
    <nav class="navbar navbar-expand-lg fixed-top custom-navbar">
      <div class="container">
        <router-link class="navbar-brand" to="/">
          <span class="brand-text">HospitalOS</span>
        </router-link>
        
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>
        
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav ms-auto align-items-center" v-if="isAuthenticated">
            <li class="nav-item">
              <router-link class="nav-link" to="/dashboard">Dashboard</router-link>
            </li>
            
            <!-- Admin Links -->
            <template v-if="user && user.role === 'admin'">
              <li class="nav-item"><router-link class="nav-link" to="/admin/doctors">Doctors</router-link></li>
              <li class="nav-item"><router-link class="nav-link" to="/admin/patients">Patients</router-link></li>
              <li class="nav-item"><router-link class="nav-link" to="/admin/appointments">Appointments</router-link></li>
            </template>

            <!-- Doctor Links -->
            <template v-if="user && user.role === 'doctor'">
              <li class="nav-item"><router-link class="nav-link" to="/doctor/appointments">My Appointments</router-link></li>
              <li class="nav-item"><router-link class="nav-link" to="/doctor/patients">My Patients</router-link></li>
              <li class="nav-item"><router-link class="nav-link" to="/doctor/availability">Availability</router-link></li>
            </template>

            <!-- Patient Links -->
            <template v-if="user && user.role === 'patient'">
              <li class="nav-item"><router-link class="nav-link" to="/patient/appointments">My Appointments</router-link></li>
              <li class="nav-item"><router-link class="nav-link" to="/patient/doctors">Find Doctors</router-link></li>
            </template>

            <li class="nav-item ms-lg-3">
              <div class="user-profile-badge">
                <span class="user-name">{{ user?.username }}</span>
                <span class="user-role">{{ user?.role }}</span>
              </div>
            </li>
            <li class="nav-item ms-2">
              <button class="btn btn-outline-danger btn-sm logout-btn" @click="logout">
                Logout
              </button>
            </li>
          </ul>
          
          <ul class="navbar-nav ms-auto" v-if="!isAuthenticated">
            <li class="nav-item">
              <router-link class="nav-link" to="/login">Login</router-link>
            </li>
            <li class="nav-item">
              <router-link class="btn btn-primary ms-2 px-4" to="/register">Register</router-link>
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <div class="container main-content">
      <router-view />
    </div>

    <footer class="footer mt-auto py-3 bg-white border-top">
      <div class="container text-center">
        <span class="text-muted small">&copy; 2025 HospitalOS. All rights reserved.</span>
        <div class="mt-2">
          <a href="#" class="footer-link me-3">Privacy Policy</a>
          <a href="#" class="footer-link">Terms of Service</a>
        </div>
      </div>
    </footer>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'

export default {
  name: 'App',
  computed: {
    ...mapState(['user', 'isAuthenticated'])
  },
  methods: {
    ...mapActions(['logout'])
  }
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

:root {
  --primary: #0f172a;
  --secondary: #334155;
  --accent: #0ea5e9;
  --background: #f8fafc;
  --surface: #ffffff;
  --text-main: #1e293b;
  --text-muted: #64748b;
  --border: #e2e8f0;
  --radius-sm: 0.5rem;
  --radius-md: 0.75rem;
  --radius-lg: 1rem;
}

body, html {
  font-family: 'Poppins', sans-serif;
  background-color: var(--background);
  color: var(--text-main);
  -webkit-font-smoothing: antialiased;
  height: 100%;
}

/* Custom Scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  padding-top: 100px;
  padding-bottom: 3rem;
}

/* Navbar */
.custom-navbar {
  background-color: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--border);
  padding: 1rem 0;
}

.navbar-brand {
  font-weight: 700;
  color: var(--primary) !important;
  font-size: 1.5rem;
  letter-spacing: -0.5px;
}

.nav-link {
  color: var(--text-muted) !important;
  font-weight: 500;
  margin: 0 0.5rem;
  transition: color 0.2s;
}

.nav-link:hover, .nav-link.router-link-active {
  color: var(--accent) !important;
}

.user-profile-badge {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  line-height: 1.2;
  padding-right: 1rem;
  border-right: 1px solid var(--border);
}

.user-name {
  font-weight: 600;
  font-size: 0.9rem;
  color: var(--primary);
}

.user-role {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Buttons */
.btn {
  border-radius: var(--radius-sm);
  font-weight: 500;
  padding: 0.6rem 1.5rem;
  transition: all 0.2s;
  font-size: 0.95rem;
}

.btn-primary {
  background-color: var(--accent);
  border-color: var(--accent);
}

.btn-primary:hover {
  background-color: #0284c7;
  border-color: #0284c7;
  transform: translateY(-1px);
}

.btn-lg {
  padding: 0.8rem 2rem;
  font-size: 1.1rem;
}

.btn-sm {
  padding: 0.4rem 1rem;
  font-size: 0.85rem;
}

.btn-xs {
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
  line-height: 1.2;
}

/* Cards */
.card {
  border-radius: var(--radius-md);
  border: 1px solid var(--border);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s, box-shadow 0.2s;
  margin-bottom: 1.5rem;
}

.hover-shadow:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

/* Forms */
.form-control, .form-select {
  border-radius: var(--radius-sm);
  border-color: var(--border);
  padding: 0.75rem 1rem;
}

.form-control:focus, .form-select:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.15);
}

/* Footer */
.footer {
  background-color: var(--surface);
  color: var(--text-muted);
  font-size: 0.9rem;
}

.footer-link {
  color: var(--text-muted);
  text-decoration: none;
  font-size: 0.9rem;
  transition: color 0.2s;
}

.footer-link:hover {
  color: var(--accent);
}

/* Utilities */
.text-primary { color: var(--accent) !important; }
.bg-light { background-color: #f1f5f9 !important; }

/* Animations */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.fade-in {
  animation: fadeIn 0.4s ease-out forwards;
}
</style>