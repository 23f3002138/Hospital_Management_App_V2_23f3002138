import axios from 'axios'

const API_BASE = process.env.NODE_ENV === 'production'
  ? 'http://localhost:5000/api'
  : '/api'

const axiosInstance = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json'
  }
})

axiosInstance.interceptors.request.use(
  (config) => {
    let token = localStorage.getItem('token')

    if (!token) {
      const defaultAuth = axiosInstance.defaults.headers.common['Authorization']
      if (defaultAuth && defaultAuth.startsWith('Bearer ')) {
        token = defaultAuth.substring(7)
      }
    }

    if (token) {
      config.headers.Authorization = `Bearer ${token}`
      console.log(`[API] ✓ Token added to ${config.method?.toUpperCase()} ${config.url}`)
    } else {
      console.error(`[API] ✗ NO TOKEN for ${config.method?.toUpperCase()} ${config.url}`)
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

axiosInstance.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      const errorMsg = error.response?.data?.message || ''
      if (errorMsg.includes('expired') || errorMsg.includes('invalid') || errorMsg.includes('Token')) {
        console.error('[API] Token is invalid, clearing...')
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        delete axiosInstance.defaults.headers.common['Authorization']

        const currentPath = window.location.pathname
        if (currentPath !== '/login' && currentPath !== '/register') {
          if (window.__VUE_ROUTER__) {
            window.__VUE_ROUTER__.push('/login')
          } else {
            window.location.href = '/login'
          }
        }
      }
    }
    return Promise.reject(error)
  }
)

export const authService = {
  login(credentials) {
    return axiosInstance.post('/login', credentials)
  },

  register(userData) {
    return axiosInstance.post('/register', userData)
  }
}

export const adminService = {
  getDashboard() {
    return axiosInstance.get('/admin/dashboard')
  },

  advancedSearch(params) {
    return axiosInstance.get('/admin/search/advanced', { params })
  },

  getDoctors() {
    return axiosInstance.get('/admin/doctors')
  },

  addDoctor(doctorData) {
    return axiosInstance.post('/admin/doctors', doctorData)
  },

  updateDoctor(doctorId, doctorData) {
    return axiosInstance.put(`/admin/doctors/${doctorId}`, doctorData)
  },

  blockDoctor(doctorId) {
    return axiosInstance.post(`/admin/doctors/${doctorId}/block`)
  },

  unblockDoctor(doctorId) {
    return axiosInstance.post(`/admin/doctors/${doctorId}/unblock`)
  },

  deleteDoctor(doctorId) {
    return axiosInstance.delete(`/admin/doctors/${doctorId}`)
  },

  getPatients() {
    return axiosInstance.get('/admin/patients')
  },

  updatePatient(patientId, patientData) {
    return axiosInstance.put(`/admin/patients/${patientId}`, patientData)
  },

  blockPatient(patientId) {
    return axiosInstance.post(`/admin/patients/${patientId}/block`)
  },

  unblockPatient(patientId) {
    return axiosInstance.post(`/admin/patients/${patientId}/unblock`)
  },

  deletePatient(patientId) {
    return axiosInstance.delete(`/admin/patients/${patientId}`)
  },

  getAppointments(params) {
    return axiosInstance.get('/admin/appointments', { params })
  },

  triggerDailyReminders() {
    return axiosInstance.post('/admin/jobs/daily-reminders')
  },

  triggerMonthlyReports() {
    return axiosInstance.post('/admin/jobs/monthly-reports')
  },

  exportAppointments(month, year) {
    return axiosInstance.get('/admin/export/appointments', {
      params: { month, year },
      responseType: 'blob'
    })
  },

  exportMonthlyReportPdf(month, year) {
    return axiosInstance.get('/admin/export/monthly-report-pdf', {
      params: { month, year },
      responseType: 'blob'
    })
  },

  addDepartment(departmentData) {
    return axiosInstance.post('/admin/departments', departmentData)
  }
}

export const doctorService = {
  getDashboard() {
    return axiosInstance.get('/doctor/dashboard')
  },

  getAppointments(params = {}) {
    return axiosInstance.get('/doctor/appointments', { params })
  },

  getAvailability(params = {}) {
    return axiosInstance.get('/doctor/availability', { params })
  },

  setAvailabilityBatch(slots) {
    return axiosInstance.post('/doctor/availability/batch', { slots })
  },

  deleteAvailability(availabilityId) {
    return axiosInstance.delete(`/doctor/availability/${availabilityId}`)
  },

  completeAppointment(appointmentId, treatmentData) {
    return axiosInstance.post(`/doctor/appointments/${appointmentId}/treatment`, treatmentData)
  },

  getPatients() {
    return axiosInstance.get('/doctor/patients')
  },

  getPatientHistory(patientId) {
    return axiosInstance.get(`/doctor/patients/${patientId}/history`)
  },

  getPatientFullHistory(patientId) {
    return axiosInstance.get(`/doctor/patients/${patientId}/full-history`)
  },

  cancelAppointment(appointmentId) {
    return axiosInstance.post(`/doctor/appointments/${appointmentId}/cancel`)
  }
}

export const patientService = {
  getDashboard() {
    return axiosInstance.get('/patient/dashboard')
  },

  getAppointments(params = {}) {
    return axiosInstance.get('/patient/appointments', { params })
  },

  bookAppointment(appointmentData) {
    return axiosInstance.post('/patient/appointments', appointmentData)
  },

  cancelAppointment(appointmentId) {
    return axiosInstance.post(`/patient/appointments/${appointmentId}/cancel`)
  },

  updateProfile(profileData) {
    return axiosInstance.put('/patient/profile', profileData)
  },

  getTreatmentHistory() {
    return axiosInstance.get('/patient/treatment-history')
  },

  exportTreatmentHistory(email) {
    return axiosInstance.post('/patient/export-treatment-history', { email })
  },

  getDoctorAvailability(doctorId, date = null) {
    const params = { doctor_id: doctorId }
    if (date) params.date = date
    return axiosInstance.get('/patient/doctors/availability', { params })
  },

  searchDoctors(params) {
    return axiosInstance.get('/patient/search/doctors', { params })
  }
}

export const commonService = {
  getDepartments() {
    return axiosInstance.get('/departments')
  },

  getDoctors(params = {}) {
    return axiosInstance.get('/doctors', { params })
  },

  search(query, type = 'all') {
    return axiosInstance.get('/search', { params: { q: query, type } })
  }
}

export default axiosInstance