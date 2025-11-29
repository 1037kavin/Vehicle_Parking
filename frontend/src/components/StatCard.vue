<template>
  <div class="stat-card" :class="cardClass">
    <div class="d-flex justify-content-between align-items-center">
      <div>
        <h6 class="text-muted mb-2">{{ title }}</h6>
        <h2 class="mb-0 fw-bold">{{ value }}</h2>
        <small v-if="subtitle" class="text-muted">{{ subtitle }}</small>
      </div>
      <div :class="`stat-icon text-${color}`">
        <i :class="`bi bi-${icon}`"></i>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StatCard',
  props: {
    title: {
      type: String,
      required: true
    },
    value: {
      type: [String, Number],
      required: true
    },
    subtitle: {
      type: String,
      default: ''
    },
    icon: {
      type: String,
      required: true
    },
    color: {
      type: String,
      default: 'primary'
    },
    cardClass: {
      type: String,
      default: ''
    }
  }
}
</script>

<style scoped>
.stat-card {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  height: 100%;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.stat-icon {
  font-size: 2.5rem;
  opacity: 0.8;
}
</style>


