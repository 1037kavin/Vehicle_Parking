<template>
  <div class="container-fluid py-4">
    <h2 class="mb-4">
      <i class="bi bi-grid-3x3 me-2"></i>
      All Parking Spots
    </h2>
    
    <div class="card border-0 shadow-sm mb-4">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-4">
            <label class="form-label">Filter by Parking Lot</label>
            <select class="form-select" v-model="selectedLotId" @change="loadSpots">
              <option value="">All Parking Lots</option>
              <option v-for="lot in parkingLots" :key="lot.id" :value="lot.id">
                {{ lot.prime_location_name }}
              </option>
            </select>
          </div>
          
          <div class="col-md-4">
            <label class="form-label">Filter by Status</label>
            <select class="form-select" v-model="selectedStatus">
              <option value="">All Statuses</option>
              <option value="A">Available</option>
              <option value="O">Occupied</option>
            </select>
          </div>
          
          <div class="col-md-4">
            <label class="form-label">Search Spot Number</label>
            <input 
              type="text" 
              class="form-control" 
              v-model="searchQuery"
              placeholder="e.g., S001"
            />
          </div>
        </div>
      </div>
    </div>
    
    <LoadingSpinner v-if="loading" />
    
    <div v-else>
      <div class="card border-0 shadow-sm">
        <div class="card-body">
          <h5 class="mb-3">
            Showing {{ filteredSpots.length }} spots
          </h5>
          
          <ParkingSpotGrid 
            :spots="filteredSpots" 
            :loading="loading"
            :clickable="true"
            @spot-clicked="viewSpotDetails"
          />
        </div>
      </div>
    </div>
    
    <!-- Spot Details Modal -->
    <div class="modal fade" id="spotDetailsModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Spot Details - {{ selectedSpot.spot_number }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <strong>Spot Number:</strong> {{ selectedSpot.spot_number }}
            </div>
            <div class="mb-3">
              <strong>Floor:</strong> {{ selectedSpot.floor_number }}
            </div>
            <div class="mb-3">
              <strong>Status:</strong> 
              <span :class="['badge ms-2', selectedSpot.status === 'A' ? 'bg-success' : 'bg-danger']">
                {{ selectedSpot.status === 'A' ? 'Available' : 'Occupied' }}
              </span>
            </div>
            <div class="mb-3">
              <strong>Parking Lot:</strong> {{ selectedSpot.lot_name }}
            </div>
            <div v-if="selectedSpot.status === 'O' && selectedSpot.current_reservation" class="mt-4">
              <h6 class="border-bottom pb-2">Current Reservation</h6>
              <p><strong>User:</strong> {{ selectedSpot.current_reservation.user_name }}</p>
              <p><strong>Check In:</strong> {{ formatDateTime(selectedSpot.current_reservation.parking_timestamp) }}</p>
              <p><strong>Duration:</strong> {{ calculateDuration(selectedSpot.current_reservation.parking_timestamp) }}</p>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { parkingLotAPI, parkingSpotAPI, adminAPI } from '../../services/api'
import ParkingSpotGrid from '../../components/ParkingSpotGrid.vue'
import LoadingSpinner from '../../components/LoadingSpinner.vue'
import { Modal } from 'bootstrap'

export default {
  name: 'ViewAllSpots',
  components: {
    ParkingSpotGrid,
    LoadingSpinner
  },
  setup() {
    const route = useRoute()
    const loading = ref(true)
    const parkingLots = ref([])
    const spots = ref([])
    const selectedLotId = ref(route.query.lotId || '')
    const selectedStatus = ref('')
    const searchQuery = ref('')
    const selectedSpot = ref({})
    
    const filteredSpots = computed(() => {
      let filtered = spots.value
      
      if (selectedStatus.value) {
        filtered = filtered.filter(spot => spot.status === selectedStatus.value)
      }
      
      if (searchQuery.value) {
        filtered = filtered.filter(spot =>
          spot.spot_number.toLowerCase().includes(searchQuery.value.toLowerCase())
        )
      }
      
      return filtered
    })
    
    const loadParkingLots = async () => {
      try {
        const response = await parkingLotAPI.getAll()
        parkingLots.value = response.data
      } catch (error) {
        console.error('Error loading parking lots:', error)
      }
    }
    
    const loadSpots = async () => {
      try {
        loading.value = true
        let response
        
        if (selectedLotId.value) {
          response = await parkingSpotAPI.getByLot(selectedLotId.value)
        } else {
          response = await parkingSpotAPI.getAll()
        }
        
        spots.value = response.data
      } catch (error) {
        console.error('Error loading spots:', error)
      } finally {
        loading.value = false
      }
    }
    
    const viewSpotDetails = async (spot) => {
      try {
        const response = await adminAPI.getSpotDetails(spot.id)
        selectedSpot.value = response.data
        
        // Show modal
        const modalElement = document.getElementById('spotDetailsModal')
        const modal = new Modal(modalElement)
        modal.show()
      } catch (error) {
        console.error('Error loading spot details:', error)
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
      await loadParkingLots()
      await loadSpots()
    })
    
    return {
      loading,
      parkingLots,
      spots,
      selectedLotId,
      selectedStatus,
      searchQuery,
      filteredSpots,
      selectedSpot,
      loadSpots,
      viewSpotDetails,
      formatDateTime,
      calculateDuration
    }
  }
}
</script>


