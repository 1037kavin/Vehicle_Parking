<template>
  <div class="container py-4">
    <h2 class="mb-4">
      <i class="bi bi-person-circle me-2"></i>
      My Profile
    </h2>
    
    <LoadingSpinner v-if="loading" />
    
    <div v-else class="row g-4">
      <!-- Profile Information -->
      <div class="col-md-8">
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <h5 class="card-title mb-4">
              <i class="bi bi-person me-2"></i>
              Profile Information
            </h5>
            
            <div v-if="success" class="alert alert-success alert-dismissible fade show">
              {{ success }}
              <button type="button" class="btn-close" @click="success = ''"></button>
            </div>
            
            <div v-if="error" class="alert alert-danger alert-dismissible fade show">
              {{ error }}
              <button type="button" class="btn-close" @click="error = ''"></button>
            </div>
            
            <form @submit.prevent="updateProfile">
              <div class="mb-3">
                <label class="form-label">Username</label>
                <input 
                  type="text" 
                  class="form-control" 
                  v-model="profile.username"
                  disabled
                />
                <small class="text-muted">Username cannot be changed</small>
              </div>
              
              <div class="mb-3">
                <label class="form-label">Full Name *</label>
                <input 
                  type="text" 
                  class="form-control" 
                  v-model="profile.full_name"
                  required
                />
              </div>
              
              <div class="mb-3">
                <label class="form-label">Email Address *</label>
                <input 
                  type="email" 
                  class="form-control" 
                  v-model="profile.email"
                  required
                />
              </div>
              
              <div class="mb-3">
                <label class="form-label">Phone Number</label>
                <input 
                  type="tel" 
                  class="form-control" 
                  v-model="profile.phone"
                />
              </div>
              
              <button 
                type="submit" 
                class="btn btn-primary"
                :disabled="updating"
              >
                <span v-if="updating" class="spinner-border spinner-border-sm me-2"></span>
                {{ updating ? 'Updating...' : 'Update Profile' }}
              </button>
            </form>
          </div>
        </div>
        
        <!-- Change Password -->
        <div class="card border-0 shadow-sm mt-4">
          <div class="card-body">
            <h5 class="card-title mb-4">
              <i class="bi bi-lock me-2"></i>
              Change Password
            </h5>
            
            <form @submit.prevent="changePassword">
              <div class="mb-3">
                <label class="form-label">Current Password *</label>
                <input 
                  type="password" 
                  class="form-control" 
                  v-model="passwordForm.current_password"
                  required
                />
              </div>
              
              <div class="mb-3">
                <label class="form-label">New Password *</label>
                <input 
                  type="password" 
                  class="form-control" 
                  v-model="passwordForm.new_password"
                  required
                  minlength="6"
                />
                <small class="text-muted">Minimum 6 characters</small>
              </div>
              
              <div class="mb-3">
                <label class="form-label">Confirm New Password *</label>
                <input 
                  type="password" 
                  class="form-control" 
                  v-model="passwordForm.confirm_password"
                  required
                />
              </div>
              
              <button 
                type="submit" 
                class="btn btn-warning"
                :disabled="changingPassword"
              >
                <span v-if="changingPassword" class="spinner-border spinner-border-sm me-2"></span>
                {{ changingPassword ? 'Changing...' : 'Change Password' }}
              </button>
            </form>
          </div>
        </div>
      </div>
      
      <!-- Profile Stats -->
      <div class="col-md-4">
        <div class="card border-0 shadow-sm mb-3">
          <div class="card-body text-center">
            <div class="profile-avatar mb-3">
              <i class="bi bi-person-circle"></i>
            </div>
            <h5>{{ profile.full_name }}</h5>
            <p class="text-muted mb-2">@{{ profile.username }}</p>
            <span :class="['badge', profile.role === 'admin' ? 'bg-danger' : 'bg-primary']">
              {{ profile.role }}
            </span>
          </div>
        </div>
        
        <div class="card border-0 shadow-sm">
          <div class="card-body">
            <h6 class="card-title mb-3">Account Information</h6>
            
            <div class="info-item">
              <i class="bi bi-envelope me-2"></i>
              <span>{{ profile.email }}</span>
            </div>
            
            <div class="info-item">
              <i class="bi bi-phone me-2"></i>
              <span>{{ profile.phone || 'Not provided' }}</span>
            </div>
            
            <div class="info-item">
              <i class="bi bi-calendar me-2"></i>
              <span>Joined {{ formatDate(profile.created_at) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { userAPI } from '../../services/api'
import LoadingSpinner from '../../components/LoadingSpinner.vue'

export default {
  name: 'MyProfile',
  components: {
    LoadingSpinner
  },
  setup() {
    const loading = ref(true)
    const updating = ref(false)
    const changingPassword = ref(false)
    const success = ref('')
    const error = ref('')
    
    const profile = ref({
      username: '',
      full_name: '',
      email: '',
      phone: '',
      role: '',
      created_at: ''
    })
    
    const passwordForm = ref({
      current_password: '',
      new_password: '',
      confirm_password: ''
    })
    
    const loadProfile = async () => {
      try {
        const response = await userAPI.getProfile()
        profile.value = response.data
      } catch (error) {
        console.error('Error loading profile:', error)
      } finally {
        loading.value = false
      }
    }
    
    const updateProfile = async () => {
      try {
        updating.value = true
        error.value = ''
        success.value = ''
        
        await userAPI.updateProfile({
          full_name: profile.value.full_name,
          email: profile.value.email,
          phone: profile.value.phone
        })
        
        // Update local storage
        const user = JSON.parse(localStorage.getItem('user') || '{}')
        user.full_name = profile.value.full_name
        user.email = profile.value.email
        localStorage.setItem('user', JSON.stringify(user))
        
        success.value = 'Profile updated successfully!'
      } catch (err) {
        error.value = err.response?.data?.error || 'Failed to update profile'
      } finally {
        updating.value = false
      }
    }
    
    const changePassword = async () => {
      try {
        changingPassword.value = true
        error.value = ''
        success.value = ''
        
        // Validate passwords match
        if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
          error.value = 'New passwords do not match'
          changingPassword.value = false
          return
        }
        
        await userAPI.changePassword({
          current_password: passwordForm.value.current_password,
          new_password: passwordForm.value.new_password
        })
        
        success.value = 'Password changed successfully!'
        
        // Reset form
        passwordForm.value = {
          current_password: '',
          new_password: '',
          confirm_password: ''
        }
      } catch (err) {
        error.value = err.response?.data?.error || 'Failed to change password'
      } finally {
        changingPassword.value = false
      }
    }
    
    const formatDate = (date) => {
      if (!date) return 'N/A'
      return new Date(date).toLocaleDateString()
    }
    
    onMounted(() => {
      loadProfile()
    })
    
    return {
      loading,
      updating,
      changingPassword,
      success,
      error,
      profile,
      passwordForm,
      updateProfile,
      changePassword,
      formatDate
    }
  }
}
</script>

<style scoped>
.profile-avatar {
  font-size: 5rem;
  color: #667eea;
}

.info-item {
  padding: 10px 0;
  border-bottom: 1px solid #e9ecef;
}

.info-item:last-child {
  border-bottom: none;
}

.info-item i {
  color: #667eea;
}
</style>


