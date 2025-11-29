<template>
  <div class="container-fluid py-4">
    <h2 class="mb-4">
      <i class="bi bi-people me-2"></i>
      Registered Users
    </h2>
    
    <LoadingSpinner v-if="loading" />
    
    <div v-else class="card border-0 shadow-sm">
      <div class="card-body">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <div>
            <h5 class="mb-0">Total Users: {{ users.length }}</h5>
          </div>
          <div class="input-group" style="max-width: 300px;">
            <span class="input-group-text">
              <i class="bi bi-search"></i>
            </span>
            <input 
              type="text" 
              class="form-control" 
              placeholder="Search users..."
              v-model="searchQuery"
            />
          </div>
        </div>
        
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
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in filteredUsers" :key="user.id">
                <td>{{ user.id }}</td>
                <td>
                  <i class="bi bi-person-circle me-2"></i>
                  {{ user.username }}
                </td>
                <td>{{ user.full_name }}</td>
                <td>{{ user.email }}</td>
                <td>{{ user.phone || 'N/A' }}</td>
                <td>
                  <span :class="['badge', user.role === 'admin' ? 'bg-danger' : 'bg-primary']">
                    {{ user.role }}
                  </span>
                </td>
                <td>
                  <span :class="['badge', user.active_reservations > 0 ? 'bg-warning' : 'bg-success']">
                    {{ user.active_reservations || 0 }}
                  </span>
                </td>
                <td>{{ formatDate(user.created_at) }}</td>
                <td>
                  <button 
                    class="btn btn-sm btn-outline-danger"
                    @click="deleteUser(user)"
                    :disabled="user.role === 'admin' || user.active_reservations > 0"
                    :title="user.active_reservations > 0 ? 'Cannot delete user with active bookings' : 'Delete user'"
                  >
                    <i class="bi bi-trash"></i>
                  </button>
                </td>
              </tr>
              <tr v-if="filteredUsers.length === 0">
                <td colspan="9" class="text-center text-muted py-4">
                  No users found
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { adminAPI } from '../../services/api'
import LoadingSpinner from '../../components/LoadingSpinner.vue'

export default {
  name: 'ViewUsers',
  components: {
    LoadingSpinner
  },
  setup() {
    const loading = ref(true)
    const users = ref([])
    const searchQuery = ref('')
    
    const filteredUsers = computed(() => {
      if (!searchQuery.value) return users.value
      
      const query = searchQuery.value.toLowerCase()
      return users.value.filter(user =>
        user.username.toLowerCase().includes(query) ||
        user.full_name.toLowerCase().includes(query) ||
        user.email.toLowerCase().includes(query)
      )
    })
    
    const loadUsers = async () => {
      try {
        const response = await adminAPI.getAllUsers()
        users.value = response.data
      } catch (error) {
        console.error('Error loading users:', error)
      } finally {
        loading.value = false
      }
    }
    
    const deleteUser = async (user) => {
      // Check for active reservations first
      if (user.active_reservations && user.active_reservations > 0) {
        alert(`Cannot delete user "${user.username}" with ${user.active_reservations} active booking(s). Please ask them to check out first.`)
        return
      }
      
      if (!confirm(`Are you sure you want to delete user "${user.username}"? This action cannot be undone.`)) return
      
      try {
        await adminAPI.deleteUser(user.id)
        users.value = users.value.filter(u => u.id !== user.id)
        alert('User deleted successfully')
      } catch (error) {
        alert('Failed to delete user: ' + (error.response?.data?.error || 'Unknown error'))
      }
    }
    
    const formatDate = (date) => {
      if (!date) return 'N/A'
      return new Date(date).toLocaleDateString()
    }
    
    onMounted(() => {
      loadUsers()
    })
    
    return {
      loading,
      users,
      searchQuery,
      filteredUsers,
      deleteUser,
      formatDate
    }
  }
}
</script>


