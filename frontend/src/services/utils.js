
export const dateUtils = {
  formatDate(dateString, format = 'standard') {
    if (!dateString) return ''
    
    const date = new Date(dateString)
    
    switch (format) {
      case 'short':
        return date.toLocaleDateString('en-US', {
          month: 'short',
          day: 'numeric',
          year: 'numeric'
        })
      case 'long':
        return date.toLocaleDateString('en-US', {
          weekday: 'long',
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        })
      case 'time':
        return date.toLocaleTimeString('en-US', {
          hour: '2-digit',
          minute: '2-digit'
        })
      case 'datetime':
        return date.toLocaleString('en-US', {
          year: 'numeric',
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        })
      default:
        return date.toLocaleDateString('en-US', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit'
        })
    }
  },
  
  formatTime(timeString) {
    if (!timeString) return ''
    
    const [hours, minutes] = timeString.split(':')
    const hour = parseInt(hours, 10)
    const ampm = hour >= 12 ? 'PM' : 'AM'
    const formattedHour = hour % 12 || 12
    
    return `${formattedHour}:${minutes} ${ampm}`
  },
  
  isToday(dateString) {
    const today = new Date().toDateString()
    const date = new Date(dateString).toDateString()
    return today === date
  },
  
  isFutureDate(dateString) {
    const today = new Date()
    const date = new Date(dateString)
    return date > today
  },
  
  addDays(dateString, days) {
    const date = new Date(dateString)
    date.setDate(date.getDate() + days)
    return date.toISOString().split('T')[0]
  },
  
  getTimeSlots(startTime, endTime, interval = 30) {
    const slots = []
    const start = new Date(`2000-01-01T${startTime}`)
    const end = new Date(`2000-01-01T${endTime}`)
    
    while (start < end) {
      slots.push(start.toTimeString().slice(0, 5))
      start.setMinutes(start.getMinutes() + interval)
    }
    
    return slots
  }
}


export const validationUtils = {
  validateEmail(email) {
    const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return pattern.test(email)
  },
  
  validatePhone(phone) {
    const pattern = /^\+?[\d\s-()]{10,}$/
    return pattern.test(phone.replace(/\s/g, ''))
  },
  
  validatePassword(password) {
    const minLength = 8
    const hasUpperCase = /[A-Z]/.test(password)
    const hasLowerCase = /[a-z]/.test(password)
    const hasNumbers = /\d/.test(password)
    
    return {
      isValid: password.length >= minLength && hasUpperCase && hasLowerCase && hasNumbers,
      requirements: {
        minLength: password.length >= minLength,
        hasUpperCase,
        hasLowerCase,
        hasNumbers
      }
    }
  },
  
  validateRequired(fields, data) {
    const errors = {}
    
    fields.forEach(field => {
      if (!data[field] || data[field].toString().trim() === '') {
        errors[field] = `${field.replace(/_/g, ' ')} is required`
      }
    })
    
    return {
      isValid: Object.keys(errors).length === 0,
      errors
    }
  }
}


export const uiUtils = {
  showToast(message, type = 'info') {
    
    const toastContainer = document.getElementById('toast-container') || createToastContainer()
    const toastId = 'toast-' + Date.now()
    
    const toastHtml = `
      <div id="${toastId}" class="toast align-items-center text-bg-${type} border-0" role="alert">
        <div class="d-flex">
          <div class="toast-body">
            ${message}
          </div>
          <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
      </div>
    `
    
    toastContainer.insertAdjacentHTML('beforeend', toastHtml)
    
    
    const toastElement = document.getElementById(toastId)
    const toast = new bootstrap.Toast(toastElement, { delay: 5000 })
    toast.show()
    
    
    toastElement.addEventListener('hidden.bs.toast', () => {
      toastElement.remove()
    })
  },
  
  showLoading() {
    const spinner = document.getElementById('loading-spinner')
    if (spinner) {
      spinner.style.display = 'block'
    }
  },
  
  hideLoading() {
    const spinner = document.getElementById('loading-spinner')
    if (spinner) {
      spinner.style.display = 'none'
    }
  },
  
  confirmDialog(message, title = 'Confirmation') {
    return new Promise((resolve) => {
      
      const confirmed = window.confirm(`${title}\n\n${message}`)
      resolve(confirmed)
    })
  }
}


function createToastContainer() {
  const container = document.createElement('div')
  container.id = 'toast-container'
  container.className = 'toast-container position-fixed top-0 end-0 p-3'
  container.style.zIndex = '9999'
  document.body.appendChild(container)
  return container
}


export const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}

export const truncateText = (text, maxLength = 100) => {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

export const generateId = () => {
  return Date.now().toString(36) + Math.random().toString(36).substr(2)
}




export const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('en-US')
}

export const formatTime = (timeString) => {
  if (!timeString) return ''
  const [hours, minutes] = timeString.split(':')
  const hour = parseInt(hours, 10)
  const ampm = hour >= 12 ? 'PM' : 'AM'
  const formattedHour = hour % 12 || 12
  return `${formattedHour}:${minutes} ${ampm}`
}

export const showToast = (message, type = 'info') => {
  
  const toastContainer = document.getElementById('toast-container') || createToastContainer()
  const toastId = 'toast-' + Date.now()
  
  const toastHtml = `
    <div id="${toastId}" class="toast align-items-center text-bg-${type} border-0" role="alert">
      <div class="d-flex">
        <div class="toast-body">
          ${message}
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
      </div>
    </div>
  `
  
  toastContainer.insertAdjacentHTML('beforeend', toastHtml)
  
  const toastElement = document.getElementById(toastId)
  const toast = new bootstrap.Toast(toastElement, { delay: 3000 })
  toast.show()
  
  toastElement.addEventListener('hidden.bs.toast', () => {
    toastElement.remove()
  })
}

function createToastContainer() {
  const container = document.createElement('div')
  container.id = 'toast-container'
  container.className = 'toast-container position-fixed top-0 end-0 p-3'
  container.style.zIndex = '9999'
  document.body.appendChild(container)
  return container
}

export const validateEmail = (email) => {
  const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return pattern.test(email)
}

export const validatePhone = (phone) => {
  const pattern = /^\+?[\d\s-()]{10,}$/
  return pattern.test(phone.replace(/\s/g, ''))
}