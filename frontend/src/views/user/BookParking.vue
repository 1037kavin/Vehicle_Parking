<template>
  <div class="container-fluid py-4">
    <h2 class="mb-4">
      <i class="bi bi-calendar-plus me-2"></i>
      Book Parking Spot
    </h2>
    
    <div class="row g-4">
      <!-- Step 1: Select Parking Lot -->
      <div class="col-md-4">
        <div class="card border-0 shadow-sm sticky-top" style="top: 80px;">
          <div class="card-body">
            <h5 class="card-title">
              <span class="badge bg-primary me-2">1</span>
              Select Parking Lot
            </h5>
            <p class="text-muted small">Choose your preferred parking location</p>
            
            <LoadingSpinner v-if="loadingLots" :showMessage="false" />
            
            <div v-else class="lot-list">
              <div 
                v-for="lot in parkingLots" 
                :key="lot.id"
                :class="['lot-item', { 'active': selectedLot?.id === lot.id }]"
                @click="selectLot(lot)"
              >
                <div class="d-flex justify-content-between align-items-start">
                  <div>
                    <h6 class="mb-1">{{ lot.prime_location_name }}</h6>
                    <small class="text-muted">{{ lot.address }}</small>
                  </div>
                  <span class="badge bg-success">
                    {{ lot.available_spots }} available
                  </span>
                </div>
                <div class="mt-2">
                  <strong class="text-primary">₹{{ lot.price_per_hour }}/hour</strong>
                </div>
              </div>
              
              <div v-if="parkingLots.length === 0" class="text-center py-3">
                <p class="text-muted">No parking lots available</p>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Step 2 & 3: Select Spot and Confirm -->
      <div class="col-md-8">
        <div v-if="!selectedLot" class="card border-0 shadow-sm">
          <div class="card-body text-center py-5">
            <i class="bi bi-arrow-left-circle" style="font-size: 4rem; opacity: 0.3;"></i>
            <h4 class="mt-3 text-muted">Select a parking lot to continue</h4>
          </div>
        </div>
        
        <div v-else>
          <!-- Parking Lot Details -->
          <div class="card border-0 shadow-sm mb-4">
            <div class="card-body">
              <h5 class="card-title">
                <span class="badge bg-primary me-2">2</span>
                Selected Parking Lot
              </h5>
              <div class="row mt-3">
                <div class="col-md-8">
                  <h4>{{ selectedLot.prime_location_name }}</h4>
                  <p class="text-muted mb-2">
                    <i class="bi bi-geo-alt me-2"></i>
                    {{ selectedLot.address }}, {{ selectedLot.pin_code }}
                  </p>
                  <p class="mb-0">
                    <i class="bi bi-currency-rupee me-2"></i>
                    <strong class="text-success">₹{{ selectedLot.price_per_hour }} per hour</strong>
                  </p>
                </div>
                <div class="col-md-4 text-end">
                  <div class="availability-badge">
                    <h3 class="mb-0 text-success">{{ selectedLot.available_spots }}</h3>
                    <small class="text-muted">spots available</small>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Available Spots -->
          <div class="card border-0 shadow-sm">
            <div class="card-body">
              <h5 class="card-title mb-3">
                <span class="badge bg-primary me-2">3</span>
                Available Parking Spots
              </h5>
              
              <LoadingSpinner v-if="loadingSpots" :showMessage="false" />
              
              <div v-else>
                <div v-if="selectedLot.available_spots === 0" class="text-center py-5">
                  <i class="bi bi-x-circle" style="font-size: 4rem; opacity: 0.3; color: #dc3545;"></i>
                  <h4 class="mt-3 text-muted">No spots available</h4>
                  <p class="text-muted">Please select another parking lot</p>
                </div>
                
                <div v-else>
                  <p class="text-muted">Click on an available spot to book</p>
                  
                  <ParkingSpotGrid 
                    :spots="spots" 
                    :loading="loadingSpots"
                    :clickable="true"
                    @spot-clicked="bookSpot"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Booking Confirmation Modal -->
    <div class="modal fade" id="bookingModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Confirm Booking</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="booking-summary">
              <h6 class="border-bottom pb-2 mb-3">Booking Details</h6>
              
              <div class="mb-3">
                <label class="form-label"><strong>Spot ID:</strong></label>
                <input 
                  type="text" 
                  class="form-control" 
                  :value="selectedSpot?.spot_number" 
                  disabled
                  style="background-color: #f0f0f0;"
                />
              </div>
              
              <div class="mb-3">
                <label class="form-label"><strong>Lot ID:</strong></label>
                <input 
                  type="text" 
                  class="form-control" 
                  :value="selectedLot?.prime_location_name" 
                  disabled
                  style="background-color: #f0f0f0;"
                />
              </div>
              
              <div class="mb-3">
                <label class="form-label"><strong>User ID:</strong></label>
                <input 
                  type="text" 
                  class="form-control" 
                  :value="userInfo" 
                  disabled
                  style="background-color: #f0f0f0;"
                />
              </div>
              
              <div class="mb-3">
                <label class="form-label"><strong>Vehicle Number: *</strong></label>
                <input 
                  type="text" 
                  class="form-control" 
                  v-model="vehicleNumber"
                  placeholder="Enter vehicle number (e.g., KA01AB1234)"
                  required
                  style="text-transform: uppercase;"
                />
                <small class="text-muted">Enter your vehicle registration number</small>
              </div>
              
              <div class="mb-2">
                <strong>Floor:</strong> {{ selectedSpot?.floor_number }}
              </div>
              <div class="mb-3">
                <strong>Rate:</strong> ₹{{ selectedLot?.price_per_hour }}/hour
              </div>
              
              <div class="alert alert-info">
                <i class="bi bi-info-circle me-2"></i>
                You will be charged based on actual parking duration
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button 
              type="button" 
              class="btn btn-primary" 
              @click="confirmBooking"
              :disabled="booking"
            >
              <span v-if="booking" class="spinner-border spinner-border-sm me-2"></span>
              {{ booking ? 'Booking...' : 'Confirm Booking' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { parkingLotAPI, parkingSpotAPI, reservationAPI } from '../../services/api'
import ParkingSpotGrid from '../../components/ParkingSpotGrid.vue'
import LoadingSpinner from '../../components/LoadingSpinner.vue'
import { Modal } from 'bootstrap'

export default {
  name: 'BookParking',
  components: {
    ParkingSpotGrid,
    LoadingSpinner
  },
  setup() {
    const router = useRouter()
    const loadingLots = ref(true)
    const loadingSpots = ref(false)
    const booking = ref(false)
    const parkingLots = ref([])
    const spots = ref([])
    const selectedLot = ref(null)
    const selectedSpot = ref(null)
    const vehicleNumber = ref('')
    const userInfo = ref(localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')).username : 'Current User')
    
    const loadParkingLots = async () => {
      try {
        const response = await parkingLotAPI.getAll()
        parkingLots.value = response.data.filter(lot => lot.available_spots > 0)
      } catch (error) {
        console.error('Error loading parking lots:', error)
      } finally {
        loadingLots.value = false
      }
    }
    
    const selectLot = async (lot) => {
      selectedLot.value = lot
      selectedSpot.value = null
      await loadSpots()
    }
    
    const loadSpots = async () => {
      if (!selectedLot.value) return
      
      try {
        loadingSpots.value = true
        const response = await parkingLotAPI.getSpots(selectedLot.value.id)
        spots.value = response.data
      } catch (error) {
        console.error('Error loading spots:', error)
      } finally {
        loadingSpots.value = false
      }
    }
    
    const bookSpot = (spot) => {
      console.log('Spot clicked:', spot)
      
      if (spot.status !== 'A') {
        alert('This spot is not available')
        return
      }
      
      selectedSpot.value = spot
      vehicleNumber.value = '' // Reset vehicle number
      
      // Show confirmation modal
      try {
        const modalElement = document.getElementById('bookingModal')
        if (!modalElement) {
          console.error('Modal element not found')
          alert('Error: Modal not found')
          return
        }
        const modal = new Modal(modalElement)
        modal.show()
      } catch (error) {
        console.error('Error showing modal:', error)
        alert('Error showing booking modal: ' + error.message)
      }
    }
    
    const confirmBooking = async () => {
      // Validate vehicle number
      if (!vehicleNumber.value || vehicleNumber.value.trim() === '') {
        alert('Please enter a vehicle number')
        return
      }
      
      try {
        booking.value = true
        
        await reservationAPI.create({
          spot_id: selectedSpot.value.id,
          vehicle_number: vehicleNumber.value.toUpperCase()
        })
        
        // Close modal
        const modalElement = document.getElementById('bookingModal')
        const modal = Modal.getInstance(modalElement)
        if (modal) {
          modal.hide()
        }
        
        // Refresh spots to show the booked spot as occupied
        await loadSpots()
        await loadParkingLots() // Refresh lots to update available count
        
        alert('Booking successful! Redirecting to your reservations...')
        router.push('/my-reservations')
        
      } catch (error) {
        alert('Booking failed: ' + (error.response?.data?.error || 'Unknown error'))
      } finally {
        booking.value = false
      }
    }
    
    onMounted(() => {
      loadParkingLots()
    })
    
    return {
      loadingLots,
      loadingSpots,
      booking,
      parkingLots,
      spots,
      selectedLot,
      selectedSpot,
      vehicleNumber,
      userInfo,
      selectLot,
      bookSpot,
      confirmBooking
    }
  }
}
</script>

<style scoped>
.lot-list {
  max-height: 500px;
  overflow-y: auto;
}

.lot-item {
  padding: 15px;
  border: 2px solid #e9ecef;
  border-radius: 10px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.lot-item:hover {
  border-color: #0d6efd;
  background-color: #f8f9fa;
  transform: translateX(5px);
}

.lot-item.active {
  border-color: #0d6efd;
  background-color: #e7f1ff;
}

.availability-badge {
  background: #d4edda;
  border-radius: 10px;
  padding: 15px;
  text-align: center;
}

.booking-summary {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 10px;
}
</style>


