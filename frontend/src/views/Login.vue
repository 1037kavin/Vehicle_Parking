<template>
  <div class="auth-container">
    <div class="container">
      <div class="row justify-content-center align-items-center min-vh-100">
        <div class="col-md-5">
          <div class="auth-card">
            <div class="text-center mb-4">
              <i class="bi bi-car-front-fill auth-icon"></i>
              <h2 class="fw-bold mt-3">Welcome Back</h2>
              <p class="text-muted">Sign in to your account</p>
            </div>
            
            <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
              {{ error }}
              <button type="button" class="btn-close" @click="error = ''"></button>
            </div>
            
            <form @submit.prevent="handleLogin">
              <div class="mb-3">
                <label for="username" class="form-label">Username</label>
                <div class="input-group">
                  <span class="input-group-text">
                    <i class="bi bi-person"></i>
                  </span>
                  <input
                    type="text"
                    class="form-control"
                    id="username"
                    v-model="credentials.username"
                    required
                    placeholder="Enter your username"
                  />
                </div>
              </div>
              
              <div class="mb-3">
                <label for="password" class="form-label">Password</label>
                <div class="input-group">
                  <span class="input-group-text">
                    <i class="bi bi-lock"></i>
                  </span>
                  <input
                    :type="showPassword ? 'text' : 'password'"
                    class="form-control"
                    id="password"
                    v-model="credentials.password"
                    required
                    placeholder="Enter your password"
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
              
              <button 
                type="submit" 
                class="btn btn-primary w-100 py-2 fw-bold"
                :disabled="loading"
              >
                <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                {{ loading ? 'Signing in...' : 'Sign In' }}
              </button>
            </form>
            
            <div class="mt-4 text-center">
              <p class="text-muted">
                Don't have an account? 
                <router-link to="/register" class="text-primary fw-bold">Register here</router-link>
              </p>
            </div>
            
            <div class="mt-3 p-3 bg-light rounded">
              <small class="text-muted">
                <strong>Demo Credentials:</strong><br>
                Admin: admin / admin123<br>
                User: user1 / user123
              </small>
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
  name: 'Login',
  setup() {
    const router = useRouter()
    const credentials = ref({
      username: '',
      password: ''
    })
    const error = ref('')
    const loading = ref(false)
    const showPassword = ref(false)
    
    const handleLogin = async () => {
      try {
        loading.value = true
        error.value = ''
        
        const response = await authAPI.login(credentials.value)
        
        // Store auth data
        localStorage.setItem('token', response.data.access_token)
        localStorage.setItem('user', JSON.stringify(response.data.user))
        localStorage.setItem('role', response.data.user.role)
        
        // Redirect based on role
        if (response.data.user.role === 'admin') {
          router.push('/admin')
        } else {
          router.push('/dashboard')
        }
      } catch (err) {
        error.value = err.response?.data?.error || 'Login failed. Please check your credentials.'
      } finally {
        loading.value = false
      }
    }
    
    return {
      credentials,
      error,
      loading,
      showPassword,
      handleLogin
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

.input-group-text {
  background-color: #f8f9fa;
  border-right: none;
}

.form-control {
  border-left: none;
}

.form-control:focus {
  border-color: #667eea;
  box-shadow: none;
}

.input-group:focus-within .input-group-text {
  border-color: #667eea;
}
</style>


