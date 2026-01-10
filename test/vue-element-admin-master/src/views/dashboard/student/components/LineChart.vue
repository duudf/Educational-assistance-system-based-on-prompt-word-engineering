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
    height: { type: String, default: '350px' },
    autoResize: { type: Boolean, default: true },
    chartData: { type: Object, required: true }
  },
  data() { return { chart: null } },
  watch: {
    chartData: { deep: true, handler(val) { this.setOptions(val) } }
  },
  mounted() {
    this.$nextTick(() => { this.initChart() })
  },
  beforeDestroy() {
    if (!this.chart) { return }
    this.chart.dispose()
    this.chart = null
  },
  methods: {
    initChart() {
      this.chart = echarts.init(this.$el, 'macarons')
      this.setOptions(this.chartData)
    },
    // ✅ 修改参数命名，更清晰：aiData 和 homeworkData
    setOptions({ aiData, homeworkData, xAxisData } = {}) {
      this.chart.setOption({
        xAxis: {
          data: xAxisData || [],
          boundaryGap: false,
          axisTick: { show: false }
        },
        grid: {
          left: 10, right: 10, bottom: 20, top: 30, containLabel: true
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'cross' },
          padding: [5, 10]
        },
        yAxis: { axisTick: { show: false } },
        legend: {
          // ✅ 修改图例名称
          data: ['AI练习数', '作业提交数']
        },
        series: [{
          name: 'AI练习数',
          itemStyle: {
            normal: {
              color: '#3888fa', // 蓝色
              lineStyle: { color: '#3888fa', width: 2 },
              areaStyle: { color: '#f3f8ff' }
            }
          },
          smooth: true,
          type: 'line',
          data: aiData, // 接收 AI 数据
          animationDuration: 2800,
          animationEasing: 'cubicInOut'
        },
        {
          name: '作业提交数',
          smooth: true,
          type: 'line',
          itemStyle: {
            normal: {
              color: '#FF005A', // 红色
              lineStyle: { color: '#FF005A', width: 2 }
            }
          },
          data: homeworkData, // 接收 作业 数据
          animationDuration: 2800,
          animationEasing: 'quadraticOut'
        }]
      })
    }
  }
}
</script>
