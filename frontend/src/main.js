import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import { initializeTheme } from './services/storage'


initializeTheme()


const app = createApp(App)


app.use(store)
app.use(router)


store.dispatch('initializeAuth')


app.config.errorHandler = (err, vm, info) => {
  console.error('Vue error:', err)
  console.info('Error info:', info)
  
  
  if (err && err.message) {
    const errorMsg = err.message.toLowerCase()
    
    if (errorMsg.includes('cannot read properties') || 
        errorMsg.includes('undefined') ||
        errorMsg.includes('network') ||
        errorMsg.includes('401') ||
        errorMsg.includes('403')) {
      
      return
    }
  }
  
  
  
}


app.config.globalProperties.$filters = {
  formatDate(dateString) {
    if (!dateString) return ''
    return new Date(dateString).toLocaleDateString()
  },
  
  formatTime(timeString) {
    if (!timeString) return ''
    const [hours, minutes] = timeString.split(':')
    const hour = parseInt(hours, 10)
    const ampm = hour >= 12 ? 'PM' : 'AM'
    const formattedHour = hour % 12 || 12
    return `${formattedHour}:${minutes} ${ampm}`
  },
  
  truncate(text, length = 50) {
    if (!text) return ''
    if (text.length <= length) return text
    return text.substring(0, length) + '...'
  }
}


window.__VUE_ROUTER__ = router


app.mount('#app')


window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason)
  event.preventDefault()
})