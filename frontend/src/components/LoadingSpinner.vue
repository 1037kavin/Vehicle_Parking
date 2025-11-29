<template>
  <div class="spinner-wrapper">
    <div class="spinner-border text-primary" role="status" :style="{ width: size, height: size }">
      <span class="visually-hidden">{{ message }}</span>
    </div>
    <p v-if="showMessage" class="mt-3 text-muted">{{ message }}</p>
  </div>
</template>

<script>
export default {
  name: 'LoadingSpinner',
  props: {
    message: {
      type: String,
      default: 'Loading...'
    },
    showMessage: {
      type: Boolean,
      default: true
    },
    size: {
      type: String,
      default: '3rem'
    }
  }
}
</script>

<style scoped>
.spinner-wrapper {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}
</style>


