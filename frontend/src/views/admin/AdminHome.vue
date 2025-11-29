<template>
  <div class="container-fluid py-4">
    <!-- Parking Lots Section -->
    <div class="parking-lots-section">
      <h3 class="section-title mb-4">Welcome Admin</h3>
      
      <LoadingSpinner v-if="loading" />
      
      <div v-else>
        <!-- Parking Lots Grid -->
        <div class="row g-4 mb-4">
          <div v-for="lot in parkingLots" :key="lot.id" class="col-md-6 col-lg-4">
            <div class="parking-lot-box">
              <!-- Lot Header -->
              <div class="lot-header">
                <h5 class="lot-name">{{ lot.prime_location_name }}</h5>
                <div class="lot-actions">
                  <button 
                    class="btn-action edit" 
                    @click="editLot(lot)"
                    data-bs-toggle="modal" 
                    data-bs-target="#editLotModal"
                  >
                    Edit
                  </button>
                  <span class="separator">|</span>
                  <button 
                    class="btn-action delete" 
                    @click="deleteLot(lot.id)"
                    :disabled="lot.occupied_spots > 0"
                  >
                    Delete
                  </button>
                </div>
              </div>
              
              <!-- Occupancy Status -->
              <div class="occupancy-status">
                (Occupied: {{ lot.occupied_spots }}/{{ lot.number_of_spots }})
              </div>
              
              <!-- Parking Spots Grid -->
              <div class="spots-grid">
                <div 
                  v-for="spot in getLotSpots(lot.id)" 
                  :key="spot.id"
                  :class="['spot-box', getSpotClass(spot.status)]"
                  @click="handleSpotClick(spot, lot)"
                  style="cursor: pointer;"
                  :title="`${spot.spot_number} - ${getSpotStatusText(spot.status)}`"
                >
                  {{ spot.status }}
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Add Lot Button (only when lots exist) -->
        <div v-if="parkingLots.length > 0" class="text-center mt-4">
          <button 
            class="btn btn-add-lot"
            data-bs-toggle="modal" 
            data-bs-target="#addLotModal"
          >
            + Add Lot
          </button>
        </div>
        
        <!-- No Lots Message -->
        <div v-if="parkingLots.length === 0" class="text-center py-5">
          <i class="bi bi-building" style="font-size: 4rem; opacity: 0.3;"></i>
          <h4 class="mt-3 text-muted">No Parking Lots Available</h4>
          <button 
            class="btn btn-primary mt-3"
            data-bs-toggle="modal" 
            data-bs-target="#addLotModal"
          >
            <i class="bi bi-plus-circle me-2"></i>
            Add Your First Parking Lot
          </button>
        </div>
      </div>
    </div>
    
    <!-- Add Parking Lot Modal -->
    <div class="modal fade" id="addLotModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Add New Parking Lot</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <form @submit.prevent="addParkingLot">
            <div class="modal-body">
              <div class="mb-3">
                <label class="form-label">Location Name *</label>
                <input 
                  type="text" 
                  class="form-control" 
                  v-model="newLot.prime_location_name"
                  required
                  placeholder="e.g., Downtown Parking"
                />
              </div>
              
              <div class="mb-3">
                <label class="form-label">Address *</label>
                <textarea 
                  class="form-control" 
                  v-model="newLot.address"
                  rows="2"
                  required
                  placeholder="Full address"
                ></textarea>
              </div>
              
              <div class="mb-3">
                <label class="form-label">Pin Code *</label>
                <input 
                  type="text" 
                  class="form-control" 
                  v-model="newLot.pin_code"
                  required
                  placeholder="123456"
                />
              </div>
              
              <div class="mb-3">
                <label class="form-label">Price per Hour (₹) *</label>
                <input 
                  type="number" 
                  class="form-control" 
                  v-model="newLot.price_per_hour"
                  min="0"
                  step="0.01"
                  required
                  placeholder="50"
                />
              </div>
              
              <div class="mb-3">
                <label class="form-label">Number of Spots *</label>
                <input 
                  type="number" 
                  class="form-control" 
                  v-model="newLot.number_of_spots"
                  min="1"
                  required
                  placeholder="15"
                />
              </div>
              
              <div class="mb-3">
                <label class="form-label">Description</label>
                <textarea 
                  class="form-control" 
                  v-model="newLot.description"
                  rows="2"
                  placeholder="Optional description"
                ></textarea>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
              <button type="submit" class="btn btn-primary" :disabled="submitting">
                <span v-if="submitting" class="spinner-border spinner-border-sm me-2"></span>
                {{ submitting ? 'Adding...' : 'Add Parking Lot' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
    
    <!-- Edit Parking Lot Modal -->
    <div class="modal fade" id="editLotModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Edit Parking Lot</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <form @submit.prevent="updateParkingLot">
            <div class="modal-body">
              <div class="mb-3">
                <label class="form-label">Location Name *</label>
                <input 
                  type="text" 
                  class="form-control" 
                  v-model="editingLot.prime_location_name"
                  required
                />
              </div>
              
              <div class="mb-3">
                <label class="form-label">Address *</label>
                <textarea 
                  class="form-control" 
                  v-model="editingLot.address"
                  rows="2"
                  required
                ></textarea>
              </div>
              
              <div class="mb-3">
                <label class="form-label">Pin Code *</label>
                <input 
                  type="text" 
                  class="form-control" 
                  v-model="editingLot.pin_code"
                  required
                />
              </div>
              
              <div class="mb-3">
                <label class="form-label">Price per Hour (₹) *</label>
                <input 
                  type="number" 
                  class="form-control" 
                  v-model="editingLot.price_per_hour"
                  min="0"
                  step="0.01"
                  required
                />
              </div>
              
              <div class="mb-3">
                <label class="form-label">Number of Spots *</label>
                <input 
                  type="number" 
                  class="form-control" 
                  v-model="editingLot.number_of_spots"
                  min="1"
                  required
                />
                <small class="text-muted">Increasing will add spots, decreasing will remove available spots</small>
              </div>
              
              <div class="mb-3">
                <label class="form-label">Description</label>
                <textarea 
                  class="form-control" 
                  v-model="editingLot.description"
                  rows="2"
                ></textarea>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
              <button type="submit" class="btn btn-primary" :disabled="submitting">
                <span v-if="submitting" class="spinner-border spinner-border-sm me-2"></span>
                {{ submitting ? 'Updating...' : 'Update Parking Lot' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
    
    <!-- Block/Unblock Spot Modal (for Available spots) -->
    <div class="modal fade" id="blockSpotModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Manage Parking Spot</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <strong>Spot Number:</strong> {{ selectedSpot?.spot_number }}
            </div>
            <div class="mb-3">
              <strong>Floor:</strong> {{ selectedSpot?.floor_number }}
            </div>
            <div class="mb-3">
              <strong>Current Status:</strong> 
              <span :class="selectedSpot?.status === 'A' ? 'badge bg-success' : 'badge bg-secondary'">
                {{ getSpotStatusText(selectedSpot?.status) }}
              </span>
            </div>
            <div class="alert alert-info">
              <i class="bi bi-info-circle me-2"></i>
              {{ selectedSpot?.status === 'A' ? 'Block this spot to prevent bookings' : 'Unblock this spot to allow bookings' }}
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button 
              type="button" 
              :class="selectedSpot?.status === 'A' ? 'btn btn-warning' : 'btn btn-success'"
              @click="toggleSpotBlock"
              :disabled="submitting"
            >
              <span v-if="submitting" class="spinner-border spinner-border-sm me-2"></span>
              {{ selectedSpot?.status === 'A' ? 'Block Spot' : 'Unblock Spot' }}
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Occupied Spot Details Modal -->
    <div class="modal fade" id="spotDetailsModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header bg-warning">
            <h5 class="modal-title">Occupied Parking Spot Details</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="detail-item">
              <label>ID:</label>
              <input type="text" class="form-control" :value="spotDetails?.reservation?.id" disabled>
            </div>
            <div class="detail-item">
              <label>Customer ID:</label>
              <input type="text" class="form-control" :value="spotDetails?.reservation?.user_id" disabled>
            </div>
            <div class="detail-item">
              <label>Vehicle Number:</label>
              <input type="text" class="form-control" :value="spotDetails?.reservation?.vehicle_number" disabled>
            </div>
            <div class="detail-item">
              <label>Date/Time of Parking:</label>
              <input type="text" class="form-control" :value="formatDateTime(spotDetails?.reservation?.parking_timestamp)" disabled>
            </div>
            <div class="detail-item">
              <label>Est. Parking Cost:</label>
              <input type="text" class="form-control" :value="`₹${spotDetails?.reservation?.parking_cost || calculateCurrentCost()}`" disabled>
            </div>
            <div class="detail-item">
              <label>Duration:</label>
              <input type="text" class="form-control" :value="`${spotDetails?.reservation?.duration_hours || 0} hours`" disabled>
            </div>
            <div class="detail-item">
              <label>Payment Status:</label>
              <input type="text" class="form-control" :value="spotDetails?.reservation?.payment_status || 'Pending'" disabled>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-primary" data-bs-dismiss="modal">Close</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { parkingLotAPI, parkingSpotAPI, adminAPI, reservationAPI } from '../../services/api'
import LoadingSpinner from '../../components/LoadingSpinner.vue'
import { Modal } from 'bootstrap'

export default {
  name: 'AdminHome',
  components: {
    LoadingSpinner
  },
  setup() {
    const loading = ref(true)
    const submitting = ref(false)
    const parkingLots = ref([])
    const allSpots = ref({}) // Organized by lot_id
    const selectedSpot = ref(null)
    const selectedLot = ref(null)
    const spotDetails = ref(null)
    
    const newLot = ref({
      prime_location_name: '',
      address: '',
      pin_code: '',
      price_per_hour: '',
      number_of_spots: '',
      description: ''
    })
    
    const editingLot = ref({})
    
    const loadParkingLots = async () => {
      try {
        const response = await parkingLotAPI.getAll()
        parkingLots.value = response.data
        
        // Load spots for each lot
        for (const lot of parkingLots.value) {
          await loadSpotsForLot(lot.id)
        }
      } catch (error) {
        console.error('Error loading parking lots:', error)
      } finally {
        loading.value = false
      }
    }
    
    const loadSpotsForLot = async (lotId) => {
      try {
        const response = await parkingLotAPI.getSpots(lotId)
        // Store all spots for grid display
        allSpots.value[lotId] = response.data
      } catch (error) {
        console.error(`Error loading spots for lot ${lotId}:`, error)
        allSpots.value[lotId] = []
      }
    }
    
    const getLotSpots = (lotId) => {
      return allSpots.value[lotId] || []
    }
    
    const getSpotClass = (status) => {
      if (status === 'A') return 'available'
      if (status === 'B') return 'blocked'
      if (status === 'O') return 'occupied'
      return ''
    }
    
    const getSpotStatusText = (status) => {
      if (status === 'A') return 'Available'
      if (status === 'B') return 'Blocked'
      if (status === 'O') return 'Occupied'
      return status
    }
    
    const handleSpotClick = async (spot, lot) => {
      selectedSpot.value = spot
      selectedLot.value = lot
      
      if (spot.status === 'O') {
        // Show occupied spot details
        await loadSpotDetails(spot.id)
        const modalElement = document.getElementById('spotDetailsModal')
        const modal = new Modal(modalElement)
        modal.show()
      } else {
        // Show block/unblock modal
        const modalElement = document.getElementById('blockSpotModal')
        const modal = new Modal(modalElement)
        modal.show()
      }
    }
    
    const loadSpotDetails = async (spotId) => {
      try {
        console.log('Loading spot details for spot ID:', spotId)
        const response = await adminAPI.getSpotDetails(spotId)
        console.log('Spot details response:', response.data)
        spotDetails.value = response.data
      } catch (error) {
        console.error('Error loading spot details:', error)
        alert('Error loading spot details: ' + (error.response?.data?.error || error.message))
      }
    }
    
    const toggleSpotBlock = async () => {
      try {
        submitting.value = true
        const newStatus = selectedSpot.value.status === 'A' ? 'B' : 'A'
        
        await parkingSpotAPI.updateStatus(selectedSpot.value.id, { status: newStatus })
        
        // Close modal
        const modalElement = document.getElementById('blockSpotModal')
        const modal = Modal.getInstance(modalElement)
        if (modal) {
          modal.hide()
        }
        
        // Refresh spots
        await loadSpotsForLot(selectedLot.value.id)
        alert(`Spot ${selectedSpot.value.spot_number} ${newStatus === 'B' ? 'blocked' : 'unblocked'} successfully!`)
        
      } catch (error) {
        console.error('Error toggling spot block:', error)
        alert('Error: ' + (error.response?.data?.error || 'Failed to update spot'))
      } finally {
        submitting.value = false
      }
    }
    
    const formatDateTime = (timestamp) => {
      if (!timestamp) return 'N/A'
      const date = new Date(timestamp)
      return date.toLocaleString()
    }
    
    const calculateCurrentCost = () => {
      if (!spotDetails.value?.reservation) return 0
      const hours = spotDetails.value.reservation.duration_hours || 0
      const rate = selectedLot.value?.price_per_hour || 0
      return (hours * rate).toFixed(2)
    }
    
    const addParkingLot = async () => {
      try {
        submitting.value = true
        await parkingLotAPI.create(newLot.value)
        
        // Reset form
        newLot.value = {
          prime_location_name: '',
          address: '',
          pin_code: '',
          price_per_hour: '',
          number_of_spots: '',
          description: ''
        }
        
        // Close modal
        try {
          const modalElement = document.getElementById('addLotModal')
          const modal = Modal.getInstance(modalElement)
          if (modal) {
            modal.hide()
          }
        } catch (modalError) {
          console.log('Modal close error (non-critical):', modalError)
        }
        
        alert('Parking lot added successfully!')
        await loadParkingLots()
      } catch (error) {
        console.error('Add error:', error)
        alert('Error: ' + (error.response?.data?.error || 'Failed to add parking lot'))
      } finally {
        submitting.value = false
      }
    }
    
    const editLot = (lot) => {
      editingLot.value = { ...lot }
    }
    
    const updateParkingLot = async () => {
      try {
        submitting.value = true
        await parkingLotAPI.update(editingLot.value.id, editingLot.value)
        
        // Close modal
        try {
          const modalElement = document.getElementById('editLotModal')
          const modal = Modal.getInstance(modalElement)
          if (modal) {
            modal.hide()
          }
        } catch (modalError) {
          console.log('Modal close error (non-critical):', modalError)
        }
        
        alert('Parking lot updated successfully!')
        await loadParkingLots()
      } catch (error) {
        console.error('Update error:', error)
        alert('Error: ' + (error.response?.data?.error || 'Failed to update parking lot'))
      } finally {
        submitting.value = false
      }
    }
    
    const deleteLot = async (lotId) => {
      if (!confirm('Are you sure you want to delete this parking lot?')) return
      
      try {
        await parkingLotAPI.delete(lotId)
        alert('Parking lot deleted successfully!')
        await loadParkingLots()
      } catch (error) {
        alert('Error: ' + (error.response?.data?.error || 'Failed to delete parking lot'))
      }
    }
    
    onMounted(() => {
      loadParkingLots()
    })
    
    return {
      loading,
      submitting,
      parkingLots,
      newLot,
      editingLot,
      selectedSpot,
      selectedLot,
      spotDetails,
      getLotSpots,
      getSpotClass,
      getSpotStatusText,
      handleSpotClick,
      toggleSpotBlock,
      formatDateTime,
      calculateCurrentCost,
      addParkingLot,
      editLot,
      updateParkingLot,
      deleteLot
    }
  }
}
</script>

<style scoped>
.section-title {
  color: #0d6efd;
  font-weight: 700;
  text-align: center;
  font-size: 1.8rem;
}

.parking-lot-box {
  background: white;
  border: 2px solid #0d6efd;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.parking-lot-box:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.lot-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 2px solid #e9ecef;
}

.lot-name {
  font-size: 1.1rem;
  font-weight: 700;
  color: #212529;
  margin: 0;
}

.lot-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-action {
  background: none;
  border: none;
  padding: 0;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-action.edit {
  color: #ff8800;
}

.btn-action.edit:hover {
  color: #ff6600;
  text-decoration: underline;
}

.btn-action.delete {
  color: #dc3545;
}

.btn-action.delete:hover:not(:disabled) {
  color: #bb2d3b;
  text-decoration: underline;
}

.btn-action:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.separator {
  color: #6c757d;
}

.occupancy-status {
  color: #198754;
  font-weight: 600;
  margin-bottom: 15px;
  font-size: 0.95rem;
}

.spots-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 8px;
  margin-top: 10px;
}

.spot-box {
  aspect-ratio: 1;
  border: 2px solid;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.2s;
}

.spot-box.available {
  background-color: #90ee90;
  border-color: #198754;
  color: #155724;
}

.spot-box.occupied {
  background-color: #ffb3ba;
  border-color: #dc3545;
  color: #721c24;
}

.spot-box.blocked {
  background-color: #d3d3d3;
  border-color: #6c757d;
  color: #495057;
  cursor: pointer !important;
}

.spot-box.blocked:hover {
  background-color: #b0b0b0;
  transform: translateY(-2px);
}

.detail-item {
  margin-bottom: 15px;
}

.detail-item label {
  font-weight: 600;
  margin-bottom: 5px;
  display: block;
  color: #495057;
}

.detail-item input {
  background-color: #f8f9fa !important;
  border: 1px solid #dee2e6;
}

.spot-box:hover {
  transform: scale(1.05);
}

.btn-add-lot {
  background-color: #0d6efd;
  color: #ffffff;
  border: none;
  border-radius: 8px;
  padding: 12px 40px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 8px rgba(13, 110, 253, 0.3);
}

.btn-add-lot:hover {
  background-color: #0b5ed7;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(13, 110, 253, 0.4);
}

@media (max-width: 768px) {
  .spots-grid {
    grid-template-columns: repeat(5, 1fr);
    gap: 6px;
  }
  
  .spot-box {
    font-size: 0.9rem;
  }
}
</style>

