<template>
  <div id="app">
    <Navbar v-if="isAuthenticated" />
    <div :class="{ 'content-wrapper': isAuthenticated }">
      <router-view />
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import Navbar from './components/Navbar.vue'

export default {
  name: 'App',
  components: {
    Navbar
  },
  setup() {
    const router = useRouter()
    
    const isAuthenticated = computed(() => {
      return !!localStorage.getItem('token')
    })

    return {
      isAuthenticated
    }
  }
}
</script>

<style>
#app {
  min-height: 100vh;
  background-color: #f8f9fa;
}

.content-wrapper {
  padding-top: 70px;
  min-height: 100vh;
}
</style>


