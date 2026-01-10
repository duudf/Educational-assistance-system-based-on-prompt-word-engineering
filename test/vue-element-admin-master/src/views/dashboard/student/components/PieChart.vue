<template>
  <div :class="className" :style="{height:height,width:width}" />
</template>

<script>
import echarts from 'echarts'
require('echarts/theme/macarons')
import resize from './mixins/resize'

export default {
  mixins: [resize],
  props: {
    className: { type: String, default: 'chart' },
    width: { type: String, default: '100%' },
    height: { type: String, default: '300px' },
    chartData: { type: Array, default: () => [] }
  },
  watch: {
    chartData: {
      deep: true,
      handler(val) { this.setOptions(val) }
    }
  },
  data() { return { chart: null } },
  mounted() { this.$nextTick(() => { this.initChart() }) },
  methods: {
    initChart() {
      this.chart = echarts.init(this.$el, 'macarons')
      this.setOptions(this.chartData)
    },
    setOptions(data) {
      if (!this.chart) return
      this.chart.setOption({
        title: { text: '题目类型占比', textStyle: { fontSize: 14 }, left: 'center' },
        tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
        legend: { bottom: 0 },
        series: [{
          type: 'pie',
          radius: ['30%', '50%'],
          data: data,
          animationDuration: 1500
        }]
      })
    }
  }
}
</script>
