<template>
  <div class="search-component">
    <div class="card">
      <div class="card-body">
        <div class="row align-items-end">
          <div class="col-md-6">
            <label class="form-label">Search</label>
            <input 
              type="text" 
              class="form-control" 
              v-model="searchQuery" 
              placeholder="Search for doctors, specializations (case-insensitive)..." 
              @keyup.enter="performSearch"
            >
          </div>
          <div class="col-md-3">
            <label class="form-label">Type</label>
            <select class="form-control" v-model="searchType">
              <option value="all">All</option>
              <option value="doctors">Doctors</option>
              <option value="patients">Patients</option>
              <option value="specialization">Specialization</option>
            </select>
          </div>
          <div class="col-md-3">
            <button class="btn btn-primary w-100" @click="performSearch">
              <i class="fas fa-search me-2"></i>Search
            </button>
          </div>
        </div>
        
        <!-- Search Results -->
        <div v-if="searchResults.doctors && searchResults.doctors.length > 0" class="mt-3">
          <h6>Doctors ({{ searchResults.doctors.length }})</h6>
          <div class="list-group">
            <div v-for="doctor in searchResults.doctors" :key="doctor.id" 
                 class="list-group-item">
              <div class="d-flex justify-content-between">
                <div>
                  <h6 class="mb-1">Dr. {{ doctor.first_name }} {{ doctor.last_name }}</h6>
                  <p class="mb-1 text-muted">{{ doctor.specialization }}</p>
                  <small>Phone: {{ doctor.phone }}</small>
                </div>
                <div>
                  <span class="badge" :class="doctor.is_available ? 'bg-success' : 'bg-danger'">
                    {{ doctor.is_available ? 'Available' : 'Unavailable' }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div v-if="searchResults.patients && searchResults.patients.length > 0" class="mt-3">
          <h6>Patients ({{ searchResults.patients.length }})</h6>
          <div class="list-group">
            <div v-for="patient in searchResults.patients" :key="patient.id" 
                 class="list-group-item">
              <h6 class="mb-1">{{ patient.first_name }} {{ patient.last_name }}</h6>
              <p class="mb-1 text-muted">Phone: {{ patient.phone }}</p>
              <small>Blood Group: {{ patient.blood_group || 'Not specified' }}</small>
            </div>
          </div>
        </div>
        
        <div v-if="hasSearched && !hasResults" class="text-center text-muted mt-3">
          No results found for "{{ searchQuery }}"
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'SearchComponent',
  data() {
    return {
      searchQuery: '',
      searchType: 'all',
      searchResults: {},
      hasSearched: false
    }
  },
  computed: {
    hasResults() {
      return (this.searchResults.doctors && this.searchResults.doctors.length > 0) ||
             (this.searchResults.patients && this.searchResults.patients.length > 0)
    }
  },
  methods: {
    async performSearch() {
      if (!this.searchQuery || !this.searchQuery.trim()) {
        this.searchResults = {}
        this.hasSearched = false
        return
      }
      
      try {
        const response = await axios.get('/api/search', {
          params: {
            q: this.searchQuery.trim(),
            type: this.searchType
          }
        })
        this.searchResults = response.data
        this.hasSearched = true
      } catch (error) {
        console.error('Search failed:', error)
        this.searchResults = {}
        alert('Search failed. Please try again.')
      }
    }
  }
}
</script>