<template>
  <div :class="className" :style="{height:height,width:width}" />
</template>

<script>
import echarts from 'echarts'
require('echarts/theme/macarons') // 引入 ECharts 主题
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
  data() {
    return { chart: null }
  },
  watch: {
    chartData: {
      deep: true,
      handler(val) {
        if (val && val.submission_data) {
          this.setOptions(val)
        }
      }
    }
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
      if (this.chartData && this.chartData.submission_data) {
        this.setOptions(this.chartData)
      }
    },
    // --- ↓↓↓ 核心修改：改造 setOptions 函数以适应新数据 ↓↓↓ ---
    setOptions({xaxis_labels, submission_data} = {}) {
      this.chart.setOption({
        title: {
          text: '最近7天作业提交量',
          left: 'center'
        },
        xAxis: {
          data: xaxis_labels, // 使用后端返回的X轴标签 (e.g., ['01-01', '01-02'])
          boundaryGap: false,
          axisTick: {show: false}
        },
        grid: {left: '3%', right: '4%', bottom: '3%', top: '15%', containLabel: true},
        tooltip: {
          trigger: 'axis',
          axisPointer: {type: 'cross'},
          formatter: '{b}<br/>提交作业: {c} 份' // 自定义提示格式
        },
        yAxis: {
          axisTick: {show: false},
          name: '提交份数'
        },
        legend: {
          data: ['作业提交量'], // 修改图例名称
          top: '5%'
        },
        series: [{
          name: '作业提交量', // 修改系列名称
          smooth: true,
          type: 'line',
          itemStyle: {
            color: '#3888fa',
            lineStyle: {color: '#3888fa', width: 2},
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                {offset: 0, color: 'rgba(56, 136, 250, 0.3)'},
                {offset: 1, color: 'rgba(56, 136, 250, 0)'}
              ])
            }
          },
          data: submission_data, // 使用后端返回的提交量数据
          animationDuration: 2800,
          animationEasing: 'quadraticOut'
        }]
      })
    }
    // --- ↑↑↑ 修改结束 ↑↑↑ ---
  }
}
</script>
