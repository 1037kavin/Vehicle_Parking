import axios from 'axios'

// Create axios instance
const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor to add token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
      console.log('Request:', config.method.toUpperCase(), config.url, 'Token:', token.substring(0, 20) + '...')
    } else {
      console.warn('No token found in localStorage!')
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => {
    console.log('Response:', response.status, response.config.method.toUpperCase(), response.config.url)
    return response
  },
  (error) => {
    console.error('API Error:', error.response?.status, error.response?.data)
    if (error.response?.status === 401) {
      // Token expired or invalid
      console.error('Token expired or invalid - redirecting to login')
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      localStorage.removeItem('role')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth APIs
export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  logout: () => api.post('/auth/logout'),
  getCurrentUser: () => api.get('/auth/me'),
  getAllUsers: () => api.get('/admin/users')
}

// Parking Lot APIs
export const parkingLotAPI = {
  getAll: () => api.get('/parking-lots'),
  getById: (id) => api.get(`/parking-lots/${id}`),
  create: (data) => api.post('/parking-lots', data),
  update: (id, data) => api.put(`/parking-lots/${id}`, data),
  delete: (id) => api.delete(`/parking-lots/${id}`),
  getSpots: (id) => api.get(`/parking-lots/${id}/spots`)
}

// Parking Spot APIs
export const parkingSpotAPI = {
  getAll: () => api.get('/parking-spots'),
  getById: (id) => api.get(`/parking-spots/${id}`),
  getAvailable: () => api.get('/parking-spots/available'),
  getByLot: (lotId) => api.get(`/parking-spots/lot/${lotId}`),
  updateStatus: (id, data) => api.put(`/parking-spots/${id}/status`, data)
}

// Reservation APIs
export const reservationAPI = {
  getAll: () => api.get('/reservations'),
  getMyReservations: () => api.get('/reservations/my'),
  getById: (id) => api.get(`/reservations/${id}`),
  create: (data) => api.post('/reservations', data),
  checkIn: (id) => api.put(`/reservations/${id}/checkin`),
  checkOut: (id) => api.put(`/reservations/${id}/checkout`),
  cancel: (id) => api.delete(`/reservations/${id}`),
  exportCSV: () => api.get('/reservations/export', { responseType: 'blob' })
}

// Admin APIs
export const adminAPI = {
  getDashboardStats: () => api.get('/admin/dashboard-stats'),
  getAllUsers: () => api.get('/admin/users'),
  getUserById: (id) => api.get(`/admin/users/${id}`),
  deleteUser: (id) => api.delete(`/admin/users/${id}`),
  getAllReservations: () => api.get('/admin/reservations'),
  getSpotDetails: (spotId) => api.get(`/admin/spots/${spotId}`)
}

// User APIs
export const userAPI = {
  getProfile: () => api.get('/user/profile'),
  updateProfile: (data) => api.put('/user/profile', data),
  getStats: () => api.get('/user/stats'),
  changePassword: (data) => api.put('/user/change-password', data)
}

export default api


