<template>
  <div class="admin-search">
    <div class="page-header">
      <h2>Search</h2>
    </div>

    <!-- Search Controls -->
    <div class="search-container">
      <div class="row g-3 align-items-end">
        <div class="col-md-4">
          <label for="searchBy" class="form-label">Search By</label>
          <select 
            id="searchBy" 
            class="form-select" 
            v-model="searchBy"
            @change="clearResults"
          >
            <option value="location">Parking Lot by Location</option>
            <option value="user_name">User Name</option>
            <option value="vehicle_number">Vehicle Number</option>
          </select>
        </div>
        
        <div class="col-md-6">
          <label for="searchString" class="form-label">Search String</label>
          <input
            id="searchString"
            type="text"
            class="form-control"
            v-model="searchString"
            :placeholder="getPlaceholder()"
            @input="handleSearchInput"
            @keyup.enter="performSearch"
          />
        </div>
        
        <div class="col-md-2">
          <button 
            class="btn btn-primary w-100" 
            @click="performSearch"
            :disabled="!searchString || loading"
          >
            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
            Search
          </button>
        </div>
      </div>
    </div>

    <!-- Search Example -->
    <div class="search-example mt-3">
      <small class="text-muted">
        <i class="bi bi-info-circle"></i>
        Example: Type "Velachery" to search parking lots at that location (results appear as you type)
      </small>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- No Results -->
    <div v-if="searched && !loading && results.length === 0 && matchedUsers.length === 0 && matchedReservations.length === 0" class="alert alert-info mt-4">
      <i class="bi bi-search"></i> No results found for "{{ searchString }}"
    </div>

    <!-- Search Results -->
    <div v-if="!loading && (results.length > 0 || matchedUsers.length > 0 || matchedReservations.length > 0)" class="results-section mt-4">
      
      <!-- User Details (for User Name search) -->
      <div v-if="searchBy === 'user_name' && matchedUsers.length > 0" class="user-results mb-4">
        <h5 class="mb-3">Search Results - Matching Users ({{ matchedUsers.length }} found)</h5>
        <div class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>ID</th>
                <th>Username</th>
                <th>Full Name</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Role</th>
                <th>Active Bookings</th>
                <th>Registered On</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in matchedUsers" :key="user.id">
                <td>{{ user.id }}</td>
                <td>
                  <i class="bi bi-person-circle me-2"></i>
                  {{ user.username }}
                </td>
                <td>{{ user.full_name || 'N/A' }}</td>
                <td>{{ user.email }}</td>
                <td>{{ user.phone || 'N/A' }}</td>
                <td>
                  <span class="badge" :class="user.role === 'admin' ? 'bg-danger' : 'bg-primary'">
                    {{ user.role }}
                  </span>
                </td>
                <td>
                  <span class="badge bg-warning text-dark">{{ user.active_reservations || 0 }}</span>
                </td>
                <td>{{ formatDate(user.created_at) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Vehicle Details (for Vehicle Number search) -->
      <div v-if="searchBy === 'vehicle_number' && matchedReservations.length > 0" class="vehicle-results mb-4">
        <h5 class="mb-3">Search Results - Matching Vehicles ({{ matchedReservations.length }} found)</h5>
        <div class="row g-3">
          <div v-for="reservation in matchedReservations" :key="reservation.id" class="col-md-6 col-lg-4">
            <div class="card vehicle-card">
              <div class="card-header bg-warning">
                <h6 class="mb-0">Occupied Parking Spot Details</h6>
              </div>
              <div class="card-body">
                <div class="detail-row">
                  <label>ID:</label>
                  <span>{{ reservation.id }}</span>
                </div>
                <div class="detail-row">
                  <label>Customer ID:</label>
                  <span>{{ reservation.user_id }}</span>
                </div>
                <div class="detail-row">
                  <label>Customer Name:</label>
                  <span>{{ reservation.user_name }}</span>
                </div>
                <div class="detail-row">
                  <label>Vehicle Number:</label>
                  <span class="badge bg-info">{{ reservation.vehicle_number }}</span>
                </div>
                <div class="detail-row">
                  <label>Parking Lot:</label>
                  <span>{{ reservation.lot_name }}</span>
                </div>
                <div class="detail-row">
                  <label>Spot Number:</label>
                  <span class="badge bg-danger">{{ reservation.spot_number }}</span>
                </div>
                <div class="detail-row">
                  <label>Date/Time of Parking:</label>
                  <span>{{ formatDateTime(reservation.parking_timestamp) }}</span>
                </div>
                <div class="detail-row">
                  <label>Est. Parking Cost:</label>
                  <span>₹{{ reservation.parking_cost || '0.00' }}</span>
                </div>
                <div class="detail-row">
                  <label>Payment Status:</label>
                  <span class="badge" :class="getPaymentBadge(reservation.payment_status)">
                    {{ reservation.payment_status }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Parking Lots Grid (only for Location search) -->
      <div v-if="searchBy === 'location' && results.length > 0">
        <h5 class="mb-3">Search Results - Parking Lots ({{ results.length }} found)</h5>
        <div class="row g-4">
          <div v-for="lot in results" :key="lot.id" class="col-md-6 col-lg-4">
            <div class="parking-lot-card">
              <div class="card-header">
                <h6 class="mb-0">{{ lot.prime_location_name }}</h6>
                <div class="badge bg-secondary">Parking #{{ lot.id }}</div>
              </div>
              
              <div class="card-body">
                <div class="lot-info mb-3">
                  <p class="mb-1"><strong>Address:</strong> {{ lot.address }}</p>
                  <p class="mb-1"><strong>Pin Code:</strong> {{ lot.pin_code }}</p>
                  <p class="mb-1"><strong>Price:</strong> ₹{{ lot.price_per_hour }}/hour</p>
                </div>

                <div class="occupancy-info mb-3">
                  <strong>Occupied: {{ lot.occupied_spots }}/{{ lot.number_of_spots }}</strong>
                </div>

                <!-- Parking Spots Grid -->
                <div class="spots-grid">
                  <div
                    v-for="(spot, index) in getLotsSpots(lot.id)"
                    :key="spot.id"
                    class="spot-box"
                    :class="getSpotClass(spot)"
                    :title="`Spot ${spot.spot_number} - ${spot.status}`"
                  >
                    {{ spot.spot_number }}
                  </div>
                  <div v-if="getLotsSpots(lot.id).length < lot.number_of_spots" class="spot-box-placeholder">
                    ...
                  </div>
                </div>

                <!-- Actions -->
                <div class="card-actions mt-3">
                  <button 
                    class="btn btn-sm btn-outline-primary"
                    @click="viewLotDetails(lot.id)"
                  >
                    View Details
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
import { ref, onMounted } from 'vue';
import { parkingLotAPI, adminAPI } from '../../services/api';

export default {
  name: 'AdminSearch',
  setup() {
    const searchBy = ref('location');
    const searchString = ref('');
    const loading = ref(false);
    const searched = ref(false);
    const results = ref([]);
    const allSpots = ref({});
    const searchTimeout = ref(null);
    const allUsers = ref([]);
    const allReservations = ref([]);
    const matchedUsers = ref([]);
    const matchedReservations = ref([]);

    const getPlaceholder = () => {
      const placeholders = {
        location: 'Enter location name (e.g., Velachery)',
        user_name: 'Enter user name (e.g., kavin)',
        vehicle_number: 'Enter vehicle number (e.g., TN01AB1234)'
      };
      return placeholders[searchBy.value] || 'Enter search term';
    };

    const clearResults = () => {
      results.value = [];
      searchString.value = '';
      searched.value = false;
      matchedUsers.value = [];
      matchedReservations.value = [];
    };

    const handleSearchInput = () => {
      // Clear previous timeout
      if (searchTimeout.value) {
        clearTimeout(searchTimeout.value);
      }

      // If search string is empty, clear results
      if (!searchString.value.trim()) {
        results.value = [];
        searched.value = false;
        return;
      }

      // Set new timeout for debounced search (500ms delay)
      searchTimeout.value = setTimeout(() => {
        performSearch();
      }, 500);
    };

    const loadAllUsers = async () => {
      try {
        const response = await adminAPI.getAllUsers();
        allUsers.value = response.data;
      } catch (error) {
        console.error('Error loading users:', error);
        allUsers.value = [];
      }
    };

    const loadAllReservations = async () => {
      try {
        const response = await adminAPI.getAllReservations();
        allReservations.value = response.data;
      } catch (error) {
        console.error('Error loading reservations:', error);
        allReservations.value = [];
      }
    };

    const performSearch = async () => {
      if (!searchString.value.trim()) return;

      loading.value = true;
      searched.value = true;
      results.value = [];
      allSpots.value = {};
      matchedUsers.value = [];
      matchedReservations.value = [];

      try {
        const searchTerm = searchString.value.toLowerCase();

        if (searchBy.value === 'location') {
          // Search by location - filter parking lots
          const allLots = await parkingLotAPI.getAll();
          results.value = allLots.data.filter(lot => 
            lot.prime_location_name.toLowerCase().includes(searchTerm) ||
            lot.address.toLowerCase().includes(searchTerm) ||
            lot.pin_code.toString().includes(searchTerm)
          );

          // Load spots for each result
          for (const lot of results.value) {
            await loadSpotsForLot(lot.id);
          }
        } 
        else if (searchBy.value === 'user_name') {
          // Load data if not already loaded
          if (allUsers.value.length === 0) await loadAllUsers();

          // Find matching users by name - ONLY show user table
          matchedUsers.value = allUsers.value.filter(user => 
            user.username.toLowerCase().includes(searchTerm) ||
            (user.full_name && user.full_name.toLowerCase().includes(searchTerm))
          );
        }
        else if (searchBy.value === 'vehicle_number') {
          // Load reservations if not already loaded
          if (allReservations.value.length === 0) await loadAllReservations();

          // Find active reservations with matching vehicle numbers - ONLY show vehicle cards
          matchedReservations.value = allReservations.value.filter(res => 
            res.status === 'active' &&
            res.vehicle_number &&
            res.vehicle_number.toLowerCase().includes(searchTerm)
          );
        }
      } catch (error) {
        console.error('Search error:', error);
        // Don't show alert for live search, just log error
        if (error.response && error.response.status !== 404) {
          console.error('Search failed:', error.message);
        }
      } finally {
        loading.value = false;
      }
    };

    const loadSpotsForLot = async (lotId) => {
      try {
        const response = await parkingLotAPI.getSpots(lotId);
        allSpots.value[lotId] = response.data;
      } catch (error) {
        console.error(`Error loading spots for lot ${lotId}:`, error);
        allSpots.value[lotId] = [];
      }
    };

    const getLotsSpots = (lotId) => {
      return allSpots.value[lotId] || [];
    };

    const getSpotClass = (spot) => {
      if (spot.is_blocked) return 'spot-blocked';
      if (spot.status === 'occupied') return 'spot-occupied';
      return 'spot-available';
    };

    const viewLotDetails = (lotId) => {
      // Navigate to home page
      window.location.href = `/#/admin`;
    };

    const formatDate = (dateString) => {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-GB').replace(/\//g, '/');
    };

    const formatDateTime = (dateString) => {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      return date.toLocaleString('en-GB', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
    };

    const getPaymentBadge = (status) => {
      if (status === 'paid') return 'bg-success';
      if (status === 'pending') return 'bg-warning text-dark';
      return 'bg-secondary';
    };

    // Load data on mount for faster search
    onMounted(() => {
      loadAllUsers();
      loadAllReservations();
    });

    return {
      searchBy,
      searchString,
      loading,
      searched,
      results,
      matchedUsers,
      matchedReservations,
      getPlaceholder,
      clearResults,
      handleSearchInput,
      performSearch,
      getLotsSpots,
      getSpotClass,
      viewLotDetails,
      formatDate,
      formatDateTime,
      getPaymentBadge
    };
  }
};
</script>

<style scoped>
.admin-search {
  padding: 20px;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h2 {
  color: #2c3e50;
  font-weight: 600;
}

.search-container {
  background: #f8f9fa;
  padding: 25px;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.search-example {
  padding-left: 10px;
}

.results-section h5 {
  color: #2c3e50;
  font-weight: 600;
}

.parking-lot-card {
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 10px;
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
}

.parking-lot-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.parking-lot-card .card-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.parking-lot-card .card-body {
  padding: 15px;
}

.lot-info p {
  font-size: 0.9rem;
  color: #6c757d;
}

.occupancy-info {
  padding: 10px;
  background: #f8f9fa;
  border-radius: 5px;
  text-align: center;
}

.spots-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 5px;
  margin-top: 10px;
}

.spot-box {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid;
  border-radius: 5px;
  font-weight: bold;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
}

.spot-available {
  background: #d4edda;
  border-color: #28a745;
  color: #155724;
}

.spot-occupied {
  background: #f8d7da;
  border-color: #dc3545;
  color: #721c24;
}

.spot-blocked {
  background: #e2e3e5;
  border-color: #6c757d;
  color: #383d41;
}

.spot-box-placeholder {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  color: #6c757d;
}

.card-actions {
  display: flex;
  justify-content: center;
  gap: 10px;
}

@media (max-width: 768px) {
  .spots-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

/* User Results Table */
.user-results .table {
  background: white;
  border-radius: 10px;
  overflow: hidden;
}

.user-results th {
  background: #f8f9fa;
  font-weight: 600;
  color: #2c3e50;
  border-bottom: 2px solid #dee2e6;
}

.user-results td {
  vertical-align: middle;
}

/* Vehicle Results Card */
.vehicle-card {
  border: 1px solid #dee2e6;
  border-radius: 10px;
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
}

.vehicle-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.vehicle-card .card-header {
  padding: 12px 15px;
}

.vehicle-card .card-header h6 {
  margin: 0;
  font-weight: 600;
}

.vehicle-card .card-body {
  padding: 15px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-row label {
  font-weight: 600;
  color: #495057;
  margin: 0;
}

.detail-row span {
  color: #212529;
}

</style>
