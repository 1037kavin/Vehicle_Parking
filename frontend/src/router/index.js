import { createRouter, createWebHistory } from 'vue-router'

// Auth Views
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'

// Admin Views
import AdminHome from '../views/admin/AdminHome.vue'
import AdminSummary from '../views/admin/AdminSummary.vue'
import AdminSearch from '../views/admin/AdminSearch.vue'
import ViewUsers from '../views/admin/ViewUsers.vue'
import ViewAllSpots from '../views/admin/ViewAllSpots.vue'

// User Views
import UserDashboard from '../views/UserDashboard.vue'
import BookParking from '../views/user/BookParking.vue'
import MyReservations from '../views/user/MyReservations.vue'
import MyProfile from '../views/user/MyProfile.vue'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresGuest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { requiresGuest: true }
  },
  {
    path: '/admin',
    name: 'AdminHome',
    component: AdminHome,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/summary',
    name: 'AdminSummary',
    component: AdminSummary,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/search',
    name: 'AdminSearch',
    component: AdminSearch,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/users',
    name: 'ViewUsers',
    component: ViewUsers,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/dashboard',
    name: 'UserDashboard',
    component: UserDashboard,
    meta: { requiresAuth: true, requiresUser: true }
  },
  {
    path: '/book-parking',
    name: 'BookParking',
    component: BookParking,
    meta: { requiresAuth: true, requiresUser: true }
  },
  {
    path: '/my-reservations',
    name: 'MyReservations',
    component: MyReservations,
    meta: { requiresAuth: true, requiresUser: true }
  },
  {
    path: '/profile',
    name: 'MyProfile',
    component: MyProfile,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guards
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const userRole = localStorage.getItem('role')
  
  // Check if route requires authentication
  if (to.meta.requiresAuth && !token) {
    next('/login')
    return
  }
  
  // Check if route requires guest (not authenticated)
  if (to.meta.requiresGuest && token) {
    if (userRole === 'admin') {
      next('/admin')
    } else {
      next('/dashboard')
    }
    return
  }
  
  // Check if route requires admin role
  if (to.meta.requiresAdmin && userRole !== 'admin') {
    next('/dashboard')
    return
  }
  
  // Check if route requires user role
  if (to.meta.requiresUser && userRole === 'admin') {
    next('/admin')
    return
  }
  
  next()
})

export default router


