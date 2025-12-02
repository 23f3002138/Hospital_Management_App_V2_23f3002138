import { createRouter, createWebHistory } from 'vue-router'
import store from '../store'

const Login = () => import('../views/Login.vue')
const Register = () => import('../views/Register.vue')
const Dashboard = () => import('../views/Dashboard.vue')
const AdminDoctors = () => import('../views/admin/Doctors.vue')
const AdminPatients = () => import('../views/admin/Patients.vue')
const AdminAppointments = () => import('../views/admin/Appointments.vue')
const AdminDepartments = () => import('../views/admin/Departments.vue')
const DoctorAppointments = () => import('../views/doctor/Appointments.vue')
const DoctorPatients = () => import('../views/doctor/Patients.vue')
const DoctorAvailability = () => import('../views/doctor/Availability.vue')
const CompleteTreatment = () => import('../views/doctor/CompleteTreatment.vue')
const PatientAppointments = () => import('../views/patient/Appointments.vue')
const FindDoctors = () => import('../views/patient/FindDoctors.vue')
const ExportHistory = () => import('../views/patient/ExportHistory.vue')
const PatientProfile = () => import('../views/patient/Profile.vue')

const routes = [
  { path: '/', redirect: '/dashboard' },
  {
    path: '/login',
    component: Login,
    meta: { requiresGuest: true }
  },
  {
    path: '/register',
    component: Register,
    meta: { requiresGuest: true }
  },
  {
    path: '/dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },

  // Admin Routes
  {
    path: '/admin/doctors',
    component: AdminDoctors,
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/admin/patients',
    component: AdminPatients,
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/admin/appointments',
    component: AdminAppointments,
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/admin/departments',
    component: AdminDepartments,
    meta: { requiresAuth: true, role: 'admin' }
  },

  // Doctor Routes
  {
    path: '/doctor/appointments',
    component: DoctorAppointments,
    meta: { requiresAuth: true, role: 'doctor' }
  },
  {
    path: '/doctor/patients',
    component: DoctorPatients,
    meta: { requiresAuth: true, role: 'doctor' }
  },
  {
    path: '/doctor/availability',
    component: DoctorAvailability,
    meta: { requiresAuth: true, role: 'doctor' }
  },
  {
    path: '/doctor/appointments/:id/complete',
    component: CompleteTreatment,
    meta: { requiresAuth: true, role: 'doctor' }
  },

  // Patient Routes
  {
    path: '/patient/appointments',
    component: PatientAppointments,
    meta: { requiresAuth: true, role: 'patient' }
  },
  {
    path: '/patient/doctors',
    component: FindDoctors,
    meta: { requiresAuth: true, role: 'patient' }
  },
  {
    path: '/patient/export-history',
    component: ExportHistory,
    meta: { requiresAuth: true, role: 'patient' }
  },
  {
    path: '/patient/profile',
    component: PatientProfile,
    meta: { requiresAuth: true, role: 'patient' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const isAuthenticated = store.state.isAuthenticated
  const userRole = store.state.user?.role

  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login')
  } else if (to.meta.requiresGuest && isAuthenticated) {
    next('/dashboard')
  } else if (to.meta.role && userRole !== to.meta.role) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router