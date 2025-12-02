<template>
  <div class="fade-in">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="h3 fw-bold text-primary mb-1">Manage Availability</h2>
        <p class="text-muted mb-0">Set your working hours for appointments</p>
      </div>
    </div>
    
    <div class="card border-0 shadow-sm mb-4">
      <div class="card-header bg-white border-bottom py-3">
        <h5 class="mb-0 fw-bold text-primary">Set Availability for Next 7 Days</h5>
      </div>
      <div class="card-body p-4">
        <form @submit.prevent="setAvailability">
          <div class="row g-3 align-items-end mb-4">
            <div class="col-md-4">
              <label class="form-label fw-medium text-muted small text-uppercase">Date</label>
              <input type="date" class="form-control form-control-lg" v-model="availability.date" required>
            </div>
            <div class="col-md-3">
              <label class="form-label fw-medium text-muted small text-uppercase">Start Time</label>
              <input type="time" class="form-control form-control-lg" v-model="availability.startTime" required>
            </div>
            <div class="col-md-3">
              <label class="form-label fw-medium text-muted small text-uppercase">End Time</label>
              <input type="time" class="form-control form-control-lg" v-model="availability.endTime" required>
            </div>
            <div class="col-md-2">
              <button type="submit" class="btn btn-primary btn-lg w-100">Add Slot</button>
            </div>
          </div>
        </form>
        
        <!-- Quick Set for Week -->
        <div class="mb-4 p-3 bg-light rounded-3">
          <h6 class="fw-bold text-muted mb-3 small text-uppercase">Quick Set for Week (Mon-Fri)</h6>
          <div class="d-flex gap-2">
            <button v-for="timeSlot in commonTimeSlots" :key="timeSlot.label" 
                    class="btn btn-outline-primary bg-white"
                    @click="setWeekAvailability(timeSlot)">
              {{ timeSlot.label }}
            </button>
          </div>
        </div>
        
        <!-- Current Availability -->
        <h5 class="fw-bold text-primary mb-3">Current Availability</h5>
        <div v-if="availabilities.length === 0" class="alert alert-light border text-center py-4 text-muted">
          No availability set for the next 7 days
        </div>
        <div v-else class="table-responsive">
          <table class="table table-hover mb-0 align-middle">
            <thead class="bg-light">
              <tr>
                <th class="ps-4">Date</th>
                <th>Start Time</th>
                <th>End Time</th>
                <th>Status</th>
                <th class="text-end pe-4">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="slot in availabilities" :key="slot.id">
                <td class="ps-4 fw-medium">{{ formatDate(slot.date) }}</td>
                <td>{{ slot.start_time }}</td>
                <td>{{ slot.end_time }}</td>
                <td>
                  <span class="badge px-3 py-2 rounded-pill" :class="slot.is_available ? 'bg-success bg-opacity-10 text-success' : 'bg-danger bg-opacity-10 text-danger'">
                    {{ slot.is_available ? 'Available' : 'Unavailable' }}
                  </span>
                </td>
                <td class="text-end pe-4">
                  <button class="btn btn-sm btn-outline-danger px-3" @click="removeAvailability(slot.id)">
                    Remove
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { doctorService } from '@/services/api'

export default {
  name: 'DoctorAvailability',
  data() {
    return {
      availability: {
        date: '',
        startTime: '09:00',
        endTime: '17:00'
      },
      availabilities: [],
      commonTimeSlots: [
        { label: '9AM-5PM', start: '09:00', end: '17:00' },
        { label: '10AM-6PM', start: '10:00', end: '18:00' },
        { label: '8AM-4PM', start: '08:00', end: '16:00' }
      ]
    }
  },
  async mounted() {
    await this.loadAvailability()
    
    this.availability.date = new Date().toISOString().split('T')[0]
  },
  methods: {
    async loadAvailability() {
      try {
        const response = await doctorService.getAvailability()
        this.availabilities = response.data.availabilities || []
      } catch (error) {
        console.error('Failed to load availability:', error)
        alert('Failed to load availability')
      }
    },
    
    async setAvailability() {
      try {
        const slot = {
          date: this.availability.date,
          start_time: this.availability.startTime,
          end_time: this.availability.endTime,
          is_available: true
        }
        
        await doctorService.setAvailabilityBatch([slot])
        
        alert('Availability set successfully!')
        this.availability.startTime = '09:00'
        this.availability.endTime = '17:00'
        await this.loadAvailability()
      } catch (error) {
        console.error('Failed to set availability:', error)
        alert(error.response?.data?.message || 'Failed to set availability')
      }
    },
    
    async setWeekAvailability(timeSlot) {
      try {
        const slots = []
        const today = new Date()
        
        for (let i = 0; i < 7; i++) {
          const date = new Date(today)
          date.setDate(today.getDate() + i)
          const dateStr = date.toISOString().split('T')[0]
          
          
          if (date.getDay() === 0 || date.getDay() === 6) continue
          
          slots.push({
            date: dateStr,
            start_time: timeSlot.start,
            end_time: timeSlot.end,
            is_available: true
          })
        }
        
        await doctorService.setAvailabilityBatch(slots)
        alert(`Availability set for week (${timeSlot.label})!`)
        await this.loadAvailability()
      } catch (error) {
        console.error('Failed to set week availability:', error)
        alert(error.response?.data?.message || 'Failed to set week availability')
      }
    },
    
    async removeAvailability(availabilityId) {
      if (confirm('Are you sure you want to remove this availability slot?')) {
        try {
          await doctorService.deleteAvailability(availabilityId)
          await this.loadAvailability()
        } catch (error) {
          console.error('Failed to remove availability:', error)
          alert(error.response?.data?.message || 'Failed to remove availability')
        }
      }
    },
    
    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString('en-US', {
        weekday: 'short',
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }
  }
}
</script>