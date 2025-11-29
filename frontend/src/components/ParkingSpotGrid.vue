<template>
  <div class="parking-spots-container">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h5 class="mb-0">Parking Spots</h5>
      <div class="legend d-flex gap-3">
        <span>
          <span class="legend-box available"></span>
          Available
        </span>
        <span>
          <span class="legend-box occupied"></span>
          Occupied
        </span>
      </div>
    </div>
    
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
    
    <div v-else class="parking-grid">
      <div 
        v-for="spot in spots" 
        :key="spot.id"
        :class="['parking-spot', spot.status === 'A' ? 'available' : 'occupied']"
        @click="handleSpotClick(spot)"
        :title="getSpotTitle(spot)"
      >
        <i :class="['bi', spot.status === 'A' ? 'bi-car-front' : 'bi-car-front-fill']"></i>
        <small class="fw-bold">{{ spot.spot_number }}</small>
        <small class="text-muted" style="font-size: 0.7rem">Floor {{ spot.floor_number }}</small>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ParkingSpotGrid',
  props: {
    spots: {
      type: Array,
      required: true
    },
    loading: {
      type: Boolean,
      default: false
    },
    clickable: {
      type: Boolean,
      default: false
    }
  },
  emits: ['spot-clicked'],
  methods: {
    handleSpotClick(spot) {
      console.log('Spot clicked in grid:', spot)
      console.log('Clickable prop:', this.clickable)
      console.log('Spot status:', spot.status)
      
      if (this.clickable && spot.status === 'A') {
        console.log('Emitting spot-clicked event')
        this.$emit('spot-clicked', spot)
      } else {
        console.log('Click not processed. Clickable:', this.clickable, 'Status:', spot.status)
      }
    },
    getSpotTitle(spot) {
      if (spot.status === 'A') {
        return `Spot ${spot.spot_number} - Available`
      } else {
        return `Spot ${spot.spot_number} - Occupied`
      }
    }
  }
}
</script>

<style scoped>
.parking-spots-container {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.legend {
  font-size: 0.9rem;
}

.legend-box {
  display: inline-block;
  width: 20px;
  height: 20px;
  border-radius: 4px;
  margin-right: 5px;
  vertical-align: middle;
}

.legend-box.available {
  background: #d4edda;
  border: 2px solid #198754;
}

.legend-box.occupied {
  background: #f8d7da;
  border: 2px solid #dc3545;
}

.parking-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 15px;
  margin-top: 20px;
}

.parking-spot {
  aspect-ratio: 1;
  border: 2px solid #dee2e6;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  background: white;
  padding: 10px;
}

.parking-spot i {
  font-size: 1.5rem;
  margin-bottom: 5px;
}

.parking-spot.available {
  border-color: #198754;
  background: #d4edda;
  cursor: pointer;
}

.parking-spot.available:hover {
  background: #198754;
  color: white;
  transform: scale(1.05);
}

.parking-spot.occupied {
  border-color: #dc3545;
  background: #f8d7da;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .parking-grid {
    grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
    gap: 10px;
  }
}
</style>


