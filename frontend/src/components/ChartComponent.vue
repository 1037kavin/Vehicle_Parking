<template>
  <div class="chart-container">
    <canvas :id="chartId"></canvas>
  </div>
</template>

<script>
import { onMounted, watch } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

export default {
  name: 'ChartComponent',
  props: {
    chartId: {
      type: String,
      required: true
    },
    type: {
      type: String,
      required: true
    },
    data: {
      type: Object,
      required: true
    },
    options: {
      type: Object,
      default: () => ({})
    }
  },
  setup(props) {
    let chartInstance = null
    
    const createChart = () => {
      const ctx = document.getElementById(props.chartId)
      if (!ctx) return
      
      if (chartInstance) {
        chartInstance.destroy()
      }
      
      chartInstance = new Chart(ctx, {
        type: props.type,
        data: props.data,
        options: {
          responsive: true,
          maintainAspectRatio: true,
          ...props.options
        }
      })
    }
    
    onMounted(() => {
      createChart()
    })
    
    watch(() => props.data, () => {
      createChart()
    }, { deep: true })
    
    return {}
  }
}
</script>

<style scoped>
.chart-container {
  position: relative;
  height: 300px;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
</style>


