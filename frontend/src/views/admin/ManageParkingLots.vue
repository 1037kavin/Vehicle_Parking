<template>
  <div class="container-fluid py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>
        <i class="bi bi-building me-2"></i>
        Manage Parking Lots
      </h2>
      <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addLotModal">
        <i class="bi bi-plus-circle me-2"></i>
        Add New Parking Lot
      </button>
    </div>
    
    <LoadingSpinner v-if="loading" />
    
    <div v-else>
      <div v-if="error" class="alert alert-danger alert-dismissible fade show">
        {{ error }}
        <button type="button" class="btn-close" @click="error = ''"></button>
      </div>
      
      <div v-if="success" class="alert alert-success alert-dismissible fade show">
        {{ success }}
        <button type="button" class="btn-close" @click="success = ''"></button>
      </div>
      
      <div class="row g-4">
        <div v-for="lot in parkingLots" :key="lot.id" class="col-md-6 col-lg-4">
          <div class="card h-100 parking-lot-card">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-start mb-3">
                <h5 class="card-title">{{ lot.prime_location_name }}</h5>
                <span class="badge bg-primary">{{ lot.number_of_spots }} spots</span>
              </div>
              
              <p class="card-text text-muted">
                <i class="bi bi-geo-alt me-2"></i>
                {{ lot.address }}
              </p>
              
              <p class="card-text text-muted">
                <i class="bi bi-pin-map me-2"></i>
                Pin: {{ lot.pin_code }}
              </p>
              
              <p class="card-text">
                <i class="bi bi-currency-rupee me-2"></i>
                <strong>₹{{ lot.price_per_hour }}/hour</strong>
              </p>
              
              <div class="d-flex justify-content-between align-items-center mb-3">
                <div>
                  <small class="text-success">
                    <i class="bi bi-check-circle me-1"></i>
                    {{ lot.available_spots }} Available
                  </small>
                </div>
                <div>
                  <small class="text-danger">
                    <i class="bi bi-x-circle me-1"></i>
                    {{ lot.occupied_spots }} Occupied
                  </small>
                </div>
              </div>
              
              <div class="progress mb-3" style="height: 8px;">
                <div 
                  class="progress-bar bg-danger" 
                  :style="{ width: (lot.occupied_spots / lot.number_of_spots * 100) + '%' }"
                ></div>
              </div>
              
              <div class="btn-group w-100" role="group">
                <button 
                  class="btn btn-outline-primary btn-sm"
                  @click="editLot(lot)"
                  data-bs-toggle="modal" 
                  data-bs-target="#editLotModal"
                >
                  <i class="bi bi-pencil me-1"></i>
                  Edit
                </button>
                <button 
                  class="btn btn-outline-info btn-sm"
                  @click="viewLotSpots(lot)"
                >
                  <i class="bi bi-grid me-1"></i>
                  View Spots
                </button>
                <button 
                  class="btn btn-outline-danger btn-sm"
                  @click="deleteLot(lot.id)"
                  :disabled="lot.occupied_spots > 0"
                >
                  <i class="bi bi-trash me-1"></i>
                  Delete
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <div v-if="parkingLots.length === 0" class="col-12">
          <div class="text-center py-5">
            <i class="bi bi-building" style="font-size: 4rem; opacity: 0.3;"></i>
            <h4 class="mt-3 text-muted">No Parking Lots Available</h4>
            <p class="text-muted">Add your first parking lot to get started</p>
          </div>
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
                />
              </div>
              
              <div class="mb-3">
                <label class="form-label">Address *</label>
                <textarea 
                  class="form-control" 
                  v-model="newLot.address"
                  rows="2"
                  required
                ></textarea>
              </div>
              
              <div class="mb-3">
                <label class="form-label">Pin Code *</label>
                <input 
                  type="text" 
                  class="form-control" 
                  v-model="newLot.pin_code"
                  required
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
                />
              </div>
              
              <div class="mb-3">
                <label class="form-label">Description</label>
                <textarea 
                  class="form-control" 
                  v-model="newLot.description"
                  rows="2"
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
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { parkingLotAPI } from '../../services/api'
import LoadingSpinner from '../../components/LoadingSpinner.vue'
import { Modal } from 'bootstrap'

export default {
  name: 'ManageParkingLots',
  components: {
    LoadingSpinner
  },
  setup() {
    const router = useRouter()
    const loading = ref(true)
    const submitting = ref(false)
    const error = ref('')
    const success = ref('')
    const parkingLots = ref([])
    
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
      } catch (err) {
        error.value = 'Failed to load parking lots'
      } finally {
        loading.value = false
      }
    }
    
    const addParkingLot = async () => {
      try {
        submitting.value = true
        await parkingLotAPI.create(newLot.value)
        success.value = 'Parking lot added successfully'
        
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
        const modalElement = document.getElementById('addLotModal')
        const modal = Modal.getInstance(modalElement)
        if (modal) {
          modal.hide()
        }
        
        await loadParkingLots()
      } catch (err) {
        error.value = err.response?.data?.error || 'Failed to add parking lot'
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
        success.value = 'Parking lot updated successfully'
        
        // Close modal
        const modalElement = document.getElementById('editLotModal')
        const modal = Modal.getInstance(modalElement)
        if (modal) {
          modal.hide()
        }
        
        await loadParkingLots()
      } catch (err) {
        error.value = err.response?.data?.error || 'Failed to update parking lot'
      } finally {
        submitting.value = false
      }
    }
    
    const deleteLot = async (lotId) => {
      if (!confirm('Are you sure you want to delete this parking lot?')) return
      
      try {
        await parkingLotAPI.delete(lotId)
        success.value = 'Parking lot deleted successfully'
        await loadParkingLots()
      } catch (err) {
        error.value = err.response?.data?.error || 'Failed to delete parking lot'
      }
    }
    
    const viewLotSpots = (lot) => {
      router.push(`/admin/spots?lotId=${lot.id}`)
    }
    
    onMounted(() => {
      loadParkingLots()
    })
    
    return {
      loading,
      submitting,
      error,
      success,
      parkingLots,
      newLot,
      editingLot,
      addParkingLot,
      editLot,
      updateParkingLot,
      deleteLot,
      viewLotSpots
    }
  }
}
</script>

<style scoped>
.parking-lot-card {
  border: none;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.parking-lot-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}
</style>


