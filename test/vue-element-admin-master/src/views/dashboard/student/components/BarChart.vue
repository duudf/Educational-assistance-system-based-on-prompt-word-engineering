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
    className: {type: String, default: 'chart'},
    width: {type: String, default: '100%'},
    height: {type: String, default: '300px'},
    chartData: {type: Object, default: () => ({x_axis: [], y_axis: []})}
  },
  watch: {
    chartData: {
      deep: true,
      handler(val) {
        this.setOptions(val)
      }
    }
  },
  data() {
    return {chart: null}
  },
  mounted() {
    this.$nextTick(() => {
      this.initChart()
    })
  },
  methods: {
    initChart() {
      this.chart = echarts.init(this.$el, 'macarons')
      this.setOptions(this.chartData)
    },
    setOptions({x_axis, y_axis} = {}) {
      if (!this.chart) return
      this.chart.setOption({
        title: {text: 'AI练习成绩分布', textStyle: {fontSize: 14}},
        tooltip: {trigger: 'axis'},
        xAxis: {type: 'category', data: x_axis},
        yAxis: {type: 'value'},
        series: [{
          name: '次数',
          type: 'bar',
          data: y_axis,
          barWidth: '40%'
        }]
      })
    }
  }
}
</script>
