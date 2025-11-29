<template>
  <div class="auth-container">
    <div class="container">
      <div class="row justify-content-center align-items-center min-vh-100 py-5">
        <div class="col-md-6">
          <div class="auth-card">
            <div class="text-center mb-4">
              <i class="bi bi-person-plus-fill auth-icon"></i>
              <h2 class="fw-bold mt-3">Create Account</h2>
              <p class="text-muted">Sign up for a new account</p>
            </div>
            
            <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
              {{ error }}
              <button type="button" class="btn-close" @click="error = ''"></button>
            </div>
            
            <div v-if="success" class="alert alert-success alert-dismissible fade show" role="alert">
              {{ success }}
              <button type="button" class="btn-close" @click="success = ''"></button>
            </div>
            
            <form @submit.prevent="handleRegister">
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="username" class="form-label">Username *</label>
                  <input
                    type="text"
                    class="form-control"
                    id="username"
                    v-model="formData.username"
                    required
                    minlength="3"
                    placeholder="Choose a username"
                  />
                </div>
                
                <div class="col-md-6 mb-3">
                  <label for="fullName" class="form-label">Full Name *</label>
                  <input
                    type="text"
                    class="form-control"
                    id="fullName"
                    v-model="formData.full_name"
                    required
                    placeholder="Your full name"
                  />
                </div>
              </div>
              
              <div class="mb-3">
                <label for="email" class="form-label">Email Address *</label>
                <input
                  type="email"
                  class="form-control"
                  id="email"
                  v-model="formData.email"
                  required
                  placeholder="your.email@example.com"
                />
              </div>
              
              <div class="mb-3">
                <label for="phone" class="form-label">Phone Number</label>
                <input
                  type="tel"
                  class="form-control"
                  id="phone"
                  v-model="formData.phone"
                  placeholder="Optional"
                />
              </div>
              
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="password" class="form-label">Password *</label>
                  <div class="input-group">
                    <input
                      :type="showPassword ? 'text' : 'password'"
                      class="form-control"
                      id="password"
                      v-model="formData.password"
                      required
                      minlength="6"
                      placeholder="Minimum 6 characters"
                    />
                    <button 
                      class="btn btn-outline-secondary" 
                      type="button"
                      @click="showPassword = !showPassword"
                    >
                      <i :class="['bi', showPassword ? 'bi-eye-slash' : 'bi-eye']"></i>
                    </button>
                  </div>
                </div>
                
                <div class="col-md-6 mb-3">
                  <label for="confirmPassword" class="form-label">Confirm Password *</label>
                  <input
                    type="password"
                    class="form-control"
                    id="confirmPassword"
                    v-model="confirmPassword"
                    required
                    placeholder="Re-enter password"
                  />
                </div>
              </div>
              
              <div class="mb-3">
                <small class="text-muted">
                  Password must be at least 6 characters long
                </small>
              </div>
              
              <button 
                type="submit" 
                class="btn btn-primary w-100 py-2 fw-bold"
                :disabled="loading"
              >
                <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                {{ loading ? 'Creating Account...' : 'Create Account' }}
              </button>
            </form>
            
            <div class="mt-4 text-center">
              <p class="text-muted">
                Already have an account? 
                <router-link to="/login" class="text-primary fw-bold">Sign in here</router-link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authAPI } from '../services/api'

export default {
  name: 'Register',
  setup() {
    const router = useRouter()
    const formData = ref({
      username: '',
      full_name: '',
      email: '',
      phone: '',
      password: ''
    })
    const confirmPassword = ref('')
    const error = ref('')
    const success = ref('')
    const loading = ref(false)
    const showPassword = ref(false)
    
    const handleRegister = async () => {
      try {
        loading.value = true
        error.value = ''
        success.value = ''
        
        // Validate passwords match
        if (formData.value.password !== confirmPassword.value) {
          error.value = 'Passwords do not match'
          loading.value = false
          return
        }
        
        // Validate password length
        if (formData.value.password.length < 6) {
          error.value = 'Password must be at least 6 characters long'
          loading.value = false
          return
        }
        
        await authAPI.register(formData.value)
        
        success.value = 'Account created successfully! Redirecting to login...'
        
        setTimeout(() => {
          router.push('/login')
        }, 2000)
        
      } catch (err) {
        error.value = err.response?.data?.error || 'Registration failed. Please try again.'
      } finally {
        loading.value = false
      }
    }
    
    return {
      formData,
      confirmPassword,
      error,
      success,
      loading,
      showPassword,
      handleRegister
    }
  }
}
</script>

<style scoped>
.auth-container {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

.auth-card {
  background: white;
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.auth-icon {
  font-size: 4rem;
  color: #667eea;
}

.form-label {
  font-weight: 600;
  color: #495057;
}
</style>


