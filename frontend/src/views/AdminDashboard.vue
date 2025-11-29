<template>
  <div class="container-fluid py-4">
    <div class="dashboard-header fade-in">
      <h1 class="mb-2">
        <i class="bi bi-speedometer2 me-2"></i>
        Admin Dashboard
      </h1>
      <p class="mb-0">Welcome back, {{ adminName }}! Here's your parking management overview.</p>
    </div>
    
    <LoadingSpinner v-if="loading" />
    
    <div v-else>
      <!-- Statistics Cards -->
      <div class="row g-4 mb-4">
        <div class="col-md-3">
          <StatCard
            title="Total Parking Lots"
            :value="stats.total_parking_lots || 0"
            icon="building"
            color="primary"
          />
        </div>
        <div class="col-md-3">
          <StatCard
            title="Total Parking Spots"
            :value="stats.total_parking_spots || 0"
            icon="grid-3x3"
            color="info"
          />
        </div>
        <div class="col-md-3">
          <StatCard
            title="Available Spots"
            :value="stats.available_spots || 0"
            subtitle="Ready to book"
            icon="check-circle"
            color="success"
          />
        </div>
        <div class="col-md-3">
          <StatCard
            title="Occupied Spots"
            :value="stats.occupied_spots || 0"
            subtitle="Currently parked"
            icon="car-front-fill"
            color="danger"
          />
        </div>
      </div>
      
      <div class="row g-4 mb-4">
        <div class="col-md-3">
          <StatCard
            title="Total Users"
            :value="stats.total_users || 0"
            icon="people"
            color="warning"
          />
        </div>
        <div class="col-md-3">
          <StatCard
            title="Active Reservations"
            :value="stats.active_reservations || 0"
            icon="calendar-check"
            color="info"
          />
        </div>
        <div class="col-md-3">
          <StatCard
            title="Today's Revenue"
            :value="`₹${stats.today_revenue || 0}`"
            icon="currency-rupee"
            color="success"
          />
        </div>
        <div class="col-md-3">
          <StatCard
            title="Total Revenue"
            :value="`₹${stats.total_revenue || 0}`"
            icon="cash-stack"
            color="primary"
          />
        </div>
      </div>
      
      <!-- Charts -->
      <div class="row g-4 mb-4">
        <div class="col-md-6">
          <div class="card border-0 shadow-sm">
            <div class="card-body">
              <h5 class="card-title mb-3">
                <i class="bi bi-pie-chart me-2"></i>
                Parking Spot Status
              </h5>
              <ChartComponent
                chartId="spotStatusChart"
                type="doughnut"
                :data="spotStatusChartData"
              />
            </div>
          </div>
        </div>
        
        <div class="col-md-6">
          <div class="card border-0 shadow-sm">
            <div class="card-body">
              <h5 class="card-title mb-3">
                <i class="bi bi-bar-chart me-2"></i>
                Parking Lots Overview
              </h5>
              <ChartComponent
                chartId="lotOverviewChart"
                type="bar"
                :data="lotOverviewChartData"
              />
            </div>
          </div>
        </div>
      </div>
      
      <!-- Recent Reservations -->
      <div class="card border-0 shadow-sm">
        <div class="card-body">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <h5 class="card-title mb-0">
              <i class="bi bi-clock-history me-2"></i>
              Recent Reservations
            </h5>
            <button class="btn btn-sm btn-outline-primary" @click="loadRecentReservations">
              <i class="bi bi-arrow-clockwise me-1"></i>
              Refresh
            </button>
          </div>
          
          <div class="table-responsive">
            <table class="table table-hover">
              <thead>
                <tr>
                  <th>User</th>
                  <th>Parking Lot</th>
                  <th>Spot</th>
                  <th>Check In</th>
                  <th>Check Out</th>
                  <th>Status</th>
                  <th>Cost</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="reservation in recentReservations" :key="reservation.id">
                  <td>{{ reservation.user_name }}</td>
                  <td>{{ reservation.lot_name }}</td>
                  <td>{{ reservation.spot_number }}</td>
                  <td>{{ formatDateTime(reservation.parking_timestamp) }}</td>
                  <td>{{ reservation.leaving_timestamp ? formatDateTime(reservation.leaving_timestamp) : 'N/A' }}</td>
                  <td>
                    <span :class="['badge', getStatusClass(reservation.status)]">
                      {{ reservation.status }}
                    </span>
                  </td>
                  <td>₹{{ reservation.parking_cost || 0 }}</td>
                </tr>
                <tr v-if="recentReservations.length === 0">
                  <td colspan="7" class="text-center text-muted">No recent reservations</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { adminAPI, reservationAPI } from '../services/api'
import StatCard from '../components/StatCard.vue'
import ChartComponent from '../components/ChartComponent.vue'
import LoadingSpinner from '../components/LoadingSpinner.vue'

export default {
  name: 'AdminDashboard',
  components: {
    StatCard,
    ChartComponent,
    LoadingSpinner
  },
  setup() {
    const loading = ref(true)
    const stats = ref({})
    const recentReservations = ref([])
    
    const adminName = computed(() => {
      const user = JSON.parse(localStorage.getItem('user') || '{}')
      return user.full_name || user.username || 'Admin'
    })
    
    const spotStatusChartData = computed(() => ({
      labels: ['Available', 'Occupied'],
      datasets: [{
        data: [stats.value.available_spots || 0, stats.value.occupied_spots || 0],
        backgroundColor: ['#198754', '#dc3545'],
        borderWidth: 0
      }]
    }))
    
    const lotOverviewChartData = computed(() => ({
      labels: stats.value.lot_names || [],
      datasets: [{
        label: 'Total Spots',
        data: stats.value.lot_spot_counts || [],
        backgroundColor: '#0d6efd'
      }]
    }))
    
    const loadDashboardStats = async () => {
      try {
        const response = await adminAPI.getDashboardStats()
        stats.value = response.data
      } catch (error) {
        console.error('Error loading dashboard stats:', error)
      }
    }
    
    const loadRecentReservations = async () => {
      try {
        const response = await adminAPI.getAllReservations()
        recentReservations.value = response.data.slice(0, 10) // Get last 10
      } catch (error) {
        console.error('Error loading reservations:', error)
      }
    }
    
    const formatDateTime = (datetime) => {
      if (!datetime) return 'N/A'
      return new Date(datetime).toLocaleString()
    }
    
    const getStatusClass = (status) => {
      const statusMap = {
        'active': 'bg-success',
        'completed': 'bg-secondary',
        'cancelled': 'bg-danger'
      }
      return statusMap[status] || 'bg-secondary'
    }
    
    onMounted(async () => {
      loading.value = true
      await Promise.all([loadDashboardStats(), loadRecentReservations()])
      loading.value = false
    })
    
    return {
      loading,
      stats,
      recentReservations,
      adminName,
      spotStatusChartData,
      lotOverviewChartData,
      loadRecentReservations,
      formatDateTime,
      getStatusClass
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

.card {
  transition: transform 0.3s ease;
}

.card:hover {
  transform: translateY(-5px);
}
</style>


