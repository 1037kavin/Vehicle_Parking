<template>
  <div class="container-fluid py-4">
    <div class="dashboard-header fade-in">
      <h1 class="mb-2">
        <i class="bi bi-speedometer2 me-2"></i>
        My Dashboard
      </h1>
      <p class="mb-0">Welcome back, {{ userName }}! Here's your parking summary.</p>
    </div>
    
    <LoadingSpinner v-if="loading" />
    
    <div v-else>
      <!-- Statistics Cards -->
      <div class="row g-4 mb-4">
        <div class="col-md-3">
          <StatCard
            title="Active Reservations"
            :value="stats.active_reservations || 0"
            icon="calendar-check"
            color="primary"
          />
        </div>
        <div class="col-md-3">
          <StatCard
            title="Total Bookings"
            :value="stats.total_bookings || 0"
            subtitle="All time"
            icon="list-check"
            color="info"
          />
        </div>
        <div class="col-md-3">
          <StatCard
            title="Total Spent"
            :value="`₹${stats.total_spent || 0}`"
            subtitle="Lifetime"
            icon="currency-rupee"
            color="success"
          />
        </div>
        <div class="col-md-3">
          <StatCard
            title="This Month"
            :value="`₹${stats.monthly_spent || 0}`"
            subtitle="Current month"
            icon="calendar-month"
            color="warning"
          />
        </div>
      </div>
      
      <!-- Quick Actions -->
      <div class="row g-4 mb-4">
        <div class="col-md-12">
          <div class="card border-0 shadow-sm">
            <div class="card-body">
              <h5 class="card-title mb-3">
                <i class="bi bi-lightning-charge me-2"></i>
                Quick Actions
              </h5>
              <div class="d-flex gap-3 flex-wrap">
                <router-link to="/book-parking" class="btn btn-primary">
                  <i class="bi bi-calendar-plus me-2"></i>
                  Book New Parking
                </router-link>
                <router-link to="/my-reservations" class="btn btn-outline-primary">
                  <i class="bi bi-list-check me-2"></i>
                  View My Reservations
                </router-link>
                <button class="btn btn-outline-success" @click="exportCSV" :disabled="exporting">
                  <span v-if="exporting" class="spinner-border spinner-border-sm me-2"></span>
                  <i v-else class="bi bi-file-earmark-spreadsheet me-2"></i>
                  Export History
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Charts -->
      <div class="row g-4 mb-4">
        <div class="col-md-6">
          <div class="card border-0 shadow-sm">
            <div class="card-body">
              <h5 class="card-title mb-3">
                <i class="bi bi-bar-chart me-2"></i>
                Most Used Parking Lots
              </h5>
              <ChartComponent
                chartId="mostUsedLotsChart"
                type="bar"
                :data="mostUsedLotsChartData"
              />
            </div>
          </div>
        </div>
        
        <div class="col-md-6">
          <div class="card border-0 shadow-sm">
            <div class="card-body">
              <h5 class="card-title mb-3">
                <i class="bi bi-pie-chart me-2"></i>
                Monthly Spending
              </h5>
              <ChartComponent
                chartId="monthlySpendingChart"
                type="line"
                :data="monthlySpendingChartData"
              />
            </div>
          </div>
        </div>
      </div>
      
      <!-- Current Active Reservations -->
      <div class="card border-0 shadow-sm">
        <div class="card-body">
          <h5 class="card-title mb-3">
            <i class="bi bi-clock-history me-2"></i>
            Current Active Reservations
          </h5>
          
          <div v-if="activeReservations.length === 0" class="text-center py-5">
            <i class="bi bi-calendar-x" style="font-size: 3rem; opacity: 0.3;"></i>
            <p class="text-muted mt-3">No active reservations</p>
            <router-link to="/book-parking" class="btn btn-primary">
              <i class="bi bi-calendar-plus me-2"></i>
              Book Now
            </router-link>
          </div>
          
          <div v-else class="row g-3">
            <div v-for="reservation in activeReservations" :key="reservation.id" class="col-md-6">
              <div class="card h-100 border-primary">
                <div class="card-body">
                  <div class="d-flex justify-content-between align-items-start mb-3">
                    <h6 class="card-title mb-0">
                      <i class="bi bi-geo-alt me-2"></i>
                      {{ reservation.lot_name }}
                    </h6>
                    <span class="badge bg-success">Active</span>
                  </div>
                  
                  <p class="mb-2">
                    <strong>Spot:</strong> {{ reservation.spot_number }}
                  </p>
                  <p class="mb-2">
                    <strong>Check In:</strong> {{ formatDateTime(reservation.parking_timestamp) }}
                  </p>
                  <p class="mb-2">
                    <strong>Duration:</strong> {{ calculateDuration(reservation.parking_timestamp) }}
                  </p>
                  <p class="mb-3">
                    <strong>Current Cost:</strong> ₹{{ reservation.parking_cost || 0 }}
                  </p>
                  
                  <button 
                    class="btn btn-danger btn-sm w-100"
                    @click="checkOut(reservation.id)"
                  >
                    <i class="bi bi-box-arrow-right me-2"></i>
                    Check Out
                  </button>
                </div>
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
import { useRouter } from 'vue-router'
import { userAPI, reservationAPI } from '../services/api'
import StatCard from '../components/StatCard.vue'
import ChartComponent from '../components/ChartComponent.vue'
import LoadingSpinner from '../components/LoadingSpinner.vue'

export default {
  name: 'UserDashboard',
  components: {
    StatCard,
    ChartComponent,
    LoadingSpinner
  },
  setup() {
    const router = useRouter()
    const loading = ref(true)
    const exporting = ref(false)
    const stats = ref({})
    const activeReservations = ref([])
    
    const userName = computed(() => {
      const user = JSON.parse(localStorage.getItem('user') || '{}')
      return user.full_name || user.username || 'User'
    })
    
    const mostUsedLotsChartData = computed(() => ({
      labels: stats.value.most_used_lots?.map(l => l.name) || [],
      datasets: [{
        label: 'Bookings',
        data: stats.value.most_used_lots?.map(l => l.count) || [],
        backgroundColor: '#0d6efd'
      }]
    }))
    
    const monthlySpendingChartData = computed(() => ({
      labels: stats.value.monthly_spending?.map(m => m.month) || [],
      datasets: [{
        label: 'Spending (₹)',
        data: stats.value.monthly_spending?.map(m => m.amount) || [],
        borderColor: '#198754',
        backgroundColor: 'rgba(25, 135, 84, 0.1)',
        tension: 0.4
      }]
    }))
    
    const loadStats = async () => {
      try {
        const response = await userAPI.getStats()
        stats.value = response.data
      } catch (error) {
        console.error('Error loading stats:', error)
      }
    }
    
    const loadActiveReservations = async () => {
      try {
        const response = await reservationAPI.getMyReservations()
        activeReservations.value = response.data.filter(r => r.status === 'active')
      } catch (error) {
        console.error('Error loading reservations:', error)
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
        link.setAttribute('download', `parking_history_${new Date().getTime()}.csv`)
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
    
    const checkOut = async (reservationId) => {
      if (!confirm('Are you sure you want to check out?')) return
      
      try {
        await reservationAPI.checkOut(reservationId)
        alert('Checked out successfully!')
        await loadActiveReservations()
        await loadStats()
      } catch (error) {
        alert('Check out failed: ' + (error.response?.data?.error || 'Unknown error'))
      }
    }
    
    const formatDateTime = (datetime) => {
      if (!datetime) return 'N/A'
      return new Date(datetime).toLocaleString()
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
    
    onMounted(async () => {
      loading.value = true
      await Promise.all([loadStats(), loadActiveReservations()])
      loading.value = false
    })
    
    return {
      loading,
      exporting,
      stats,
      activeReservations,
      userName,
      mostUsedLotsChartData,
      monthlySpendingChartData,
      exportCSV,
      checkOut,
      formatDateTime,
      calculateDuration
    }
  }
}
</script>

<style scoped>
.dashboard-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 30px;
  border-radius: 15px;
  margin-bottom: 30px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}
</style>


