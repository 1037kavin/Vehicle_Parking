<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary fixed-top shadow">
    <div class="container-fluid">
      <a class="navbar-brand" href="#">
        <i class="bi bi-car-front-fill me-2"></i>
        Parking Manager
      </a>
      
      <button 
        class="navbar-toggler" 
        type="button" 
        data-bs-toggle="collapse" 
        data-bs-target="#navbarNav"
      >
        <span class="navbar-toggler-icon"></span>
      </button>
      
      <div class="collapse navbar-collapse" id="navbarNav">
        <!-- Admin Menu -->
        <ul class="navbar-nav me-auto" v-if="isAdmin">
          <li class="nav-item">
            <router-link class="nav-link" to="/admin">
              Home
            </router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/admin/users">
              Users
            </router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/admin/search">
              Search
            </router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/admin/summary">
              Summary
            </router-link>
          </li>
        </ul>
        
        <!-- User Menu -->
        <ul class="navbar-nav me-auto" v-if="!isAdmin">
          <li class="nav-item">
            <router-link class="nav-link" to="/dashboard">
              <i class="bi bi-speedometer2 me-1"></i>
              Dashboard
            </router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/book-parking">
              <i class="bi bi-calendar-plus me-1"></i>
              Book Parking
            </router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/my-reservations">
              <i class="bi bi-list-check me-1"></i>
              My Reservations
            </router-link>
          </li>
        </ul>
        
        <!-- User Profile & Logout -->
        <ul class="navbar-nav">
          <li class="nav-item">
            <span class="nav-link text-white">
              <i class="bi bi-person-circle me-1"></i>{{ username }}
            </span>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/profile">
              <i class="bi bi-person me-1"></i>Edit Profile
            </router-link>
          </li>
          <li class="nav-item">
            <a class="nav-link text-warning" href="#" @click.prevent="logout">
              <i class="bi bi-box-arrow-right me-1"></i>Logout
            </a>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'Navbar',
  setup() {
    const router = useRouter()
    
    const isAdmin = computed(() => {
      return localStorage.getItem('role') === 'admin'
    })
    
    const username = computed(() => {
      const user = JSON.parse(localStorage.getItem('user') || '{}')
      return user.username || 'User'
    })
    
    const logout = () => {
      console.log('Logout clicked')
      try {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        localStorage.removeItem('role')
        console.log('LocalStorage cleared, redirecting to login...')
        router.push('/login')
      } catch (error) {
        console.error('Logout error:', error)
        alert('Error logging out: ' + error.message)
      }
    }
    
    return {
      isAdmin,
      username,
      logout
    }
  }
}
</script>

<style scoped>
.navbar {
  padding: 12px 0;
}

.navbar-brand {
  font-size: 1.5rem;
  font-weight: 700;
}

.nav-link {
  font-weight: 500;
  transition: all 0.3s ease;
}

.nav-link:hover {
  transform: translateY(-2px);
}

.router-link-active {
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
}
</style>


