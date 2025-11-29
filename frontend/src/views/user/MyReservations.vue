<template>
  <div class="container-fluid py-4">
    <h2 class="mb-4">
      <i class="bi bi-list-check me-2"></i>
      My Reservations
    </h2>
    
    <div class="card border-0 shadow-sm mb-4">
      <div class="card-body">
        <div class="d-flex justify-content-between align-items-center flex-wrap gap-3">
          <div class="btn-group" role="group">
            <button 
              :class="['btn', filter === 'all' ? 'btn-primary' : 'btn-outline-primary']"
              @click="filter = 'all'"
            >
              All
            </button>
            <button 
              :class="['btn', filter === 'active' ? 'btn-primary' : 'btn-outline-primary']"
              @click="filter = 'active'"
            >
              Active
            </button>
            <button 
              :class="['btn', filter === 'completed' ? 'btn-primary' : 'btn-outline-primary']"
              @click="filter = 'completed'"
            >
              Completed
            </button>
            <button 
              :class="['btn', filter === 'cancelled' ? 'btn-primary' : 'btn-outline-primary']"
              @click="filter = 'cancelled'"
            >
              Cancelled
            </button>
          </div>
          
          <button class="btn btn-success" @click="exportCSV" :disabled="exporting">
            <span v-if="exporting" class="spinner-border spinner-border-sm me-2"></span>
            <i v-else class="bi bi-file-earmark-spreadsheet me-2"></i>
            Export as CSV
          </button>
        </div>
      </div>
    </div>
    
    <LoadingSpinner v-if="loading" />
    
    <div v-else>
      <div v-if="filteredReservations.length === 0" class="text-center py-5">
        <i class="bi bi-calendar-x" style="font-size: 4rem; opacity: 0.3;"></i>
        <h4 class="mt-3 text-muted">No reservations found</h4>
        <p class="text-muted">Start by booking your first parking spot!</p>
        <router-link to="/book-parking" class="btn btn-primary">
          <i class="bi bi-calendar-plus me-2"></i>
          Book Now
        </router-link>
      </div>
      
      <div v-else class="row g-4">
        <div v-for="reservation in filteredReservations" :key="reservation.id" class="col-md-6">
          <div class="card h-100 reservation-card" :class="getCardClass(reservation.status)">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-start mb-3">
                <h5 class="card-title mb-0">
                  <i class="bi bi-geo-alt me-2"></i>
                  {{ reservation.lot_name }}
                </h5>
                <span :class="['badge', getStatusClass(reservation.status)]">
                  {{ reservation.status }}
                </span>
              </div>
              
              <div class="reservation-details">
                <p class="mb-2">
                  <i class="bi bi-pin-map me-2"></i>
                  <strong>Spot:</strong> {{ reservation.spot_number }}
                </p>
                
                <p class="mb-2">
                  <i class="bi bi-calendar-check me-2"></i>
                  <strong>Check In:</strong> {{ formatDateTime(reservation.parking_timestamp) }}
                </p>
                
                <p class="mb-2">
                  <i class="bi bi-calendar-x me-2"></i>
                  <strong>Check Out:</strong> 
                  {{ reservation.leaving_timestamp ? formatDateTime(reservation.leaving_timestamp) : 'Still parked' }}
                </p>
                
                <p v-if="reservation.status === 'active'" class="mb-2">
                  <i class="bi bi-clock me-2"></i>
                  <strong>Duration:</strong> {{ calculateDuration(reservation.parking_timestamp) }}
                </p>
                
                <p v-else-if="reservation.leaving_timestamp" class="mb-2">
                  <i class="bi bi-clock-history me-2"></i>
                  <strong>Total Duration:</strong> {{ calculateTotalDuration(reservation.parking_timestamp, reservation.leaving_timestamp) }}
                </p>
                
                <p class="mb-0">
                  <i class="bi bi-currency-rupee me-2"></i>
                  <strong>Cost:</strong> ₹{{ reservation.parking_cost || 0 }}
                </p>
              </div>
              
              <div class="mt-3" v-if="reservation.status === 'active'">
                <button 
                  class="btn btn-danger w-100"
                  @click="checkOut(reservation.id)"
                >
                  <i class="bi bi-box-arrow-right me-2"></i>
                  Check Out
                </button>
              </div>
              
              <div class="mt-3" v-if="reservation.status === 'completed'">
                <small class="text-muted">
                  <i class="bi bi-check-circle me-1"></i>
                  Completed on {{ formatDate(reservation.leaving_timestamp) }}
                </small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { reservationAPI } from '../../services/api'
import LoadingSpinner from '../../components/LoadingSpinner.vue'

export default {
  name: 'MyReservations',
  components: {
    LoadingSpinner
  },
  setup() {
    const loading = ref(true)
    const exporting = ref(false)
    const reservations = ref([])
    const filter = ref('all')
    
    const filteredReservations = computed(() => {
      if (filter.value === 'all') return reservations.value
      return reservations.value.filter(r => r.status === filter.value)
    })
    
    const loadReservations = async () => {
      try {
        const response = await reservationAPI.getMyReservations()
        reservations.value = response.data
      } catch (error) {
        console.error('Error loading reservations:', error)
      } finally {
        loading.value = false
      }
    }
    
    const checkOut = async (reservationId) => {
      if (!confirm('Are you sure you want to check out?')) return
      
      try {
        await reservationAPI.checkOut(reservationId)
        alert('Checked out successfully!')
        await loadReservations()
      } catch (error) {
        alert('Check out failed: ' + (error.response?.data?.error || 'Unknown error'))
      }
    }
    
    const exportCSV = async () => {
      try {
        exporting.value = true
        const response = await reservationAPI.exportCSV()
        
        // Create download link
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `my_parking_history_${new Date().getTime()}.csv`)
        document.body.appendChild(link)
        link.click()
        link.remove()
        
        alert('Export completed successfully!')
      } catch (error) {
        alert('Export failed: ' + (error.response?.data?.error || 'Unknown error'))
      } finally {
        exporting.value = false
      }
    }
    
    const formatDateTime = (datetime) => {
      if (!datetime) return 'N/A'
      return new Date(datetime).toLocaleString()
    }
    
    const formatDate = (datetime) => {
      if (!datetime) return 'N/A'
      return new Date(datetime).toLocaleDateString()
    }
    
    const calculateDuration = (startTime) => {
      if (!startTime) return 'N/A'
      
      const start = new Date(startTime)
      const now = new Date()
      const diff = now - start
      
      const hours = Math.floor(diff / (1000 * 60 * 60))
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
      
      return `${hours}h ${minutes}m`
    }
    
    const calculateTotalDuration = (startTime, endTime) => {
      if (!startTime || !endTime) return 'N/A'
      
      const start = new Date(startTime)
      const end = new Date(endTime)
      const diff = end - start
      
      const hours = Math.floor(diff / (1000 * 60 * 60))
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
      
      return `${hours}h ${minutes}m`
    }
    
    const getStatusClass = (status) => {
      const statusMap = {
        'active': 'bg-success',
        'completed': 'bg-secondary',
        'cancelled': 'bg-danger'
      }
      return statusMap[status] || 'bg-secondary'
    }
    
    const getCardClass = (status) => {
      const classMap = {
        'active': 'border-success',
        'completed': 'border-secondary',
        'cancelled': 'border-danger'
      }
      return classMap[status] || ''
    }
    
    onMounted(() => {
      loadReservations()
    })
    
    return {
      loading,
      exporting,
      reservations,
      filter,
      filteredReservations,
      checkOut,
      exportCSV,
      formatDateTime,
      formatDate,
      calculateDuration,
      calculateTotalDuration,
      getStatusClass,
      getCardClass
    }
  }
}
</script>

<style scoped>
.reservation-card {
  border: none;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.reservation-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.reservation-details {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
}
</style>


