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
  data() {
    return { chart: null }
  },
  watch: {
    chartData: {
      deep: true,
      handler(val) {
        this.setOptions(val)
      }
    }
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
    setOptions(data) {
      if (!this.chart || !data || data.length === 0) return
      this.chart.setOption({
        // --- 完全同步你提供的标题样式 ---
        title: {
          text: '个人综合能力画像',
          left: 'center',
          textStyle: { fontSize: 14 }
        },
        // ----------------------------
        tooltip: { trigger: 'item' },
        radar: {
          radius: '50%', // 缩小图表半径，确保文字指标有足够的显示空间
          center: ['50%', '55%'], // 中心点稍微下移，避开左上角的标题
          splitNumber: 5,
          indicator: [
            { name: '任务完成率', max: 100 },
            { name: 'AI评分', max: 100 },
            { name: '学习活跃度', max: 100 },
            { name: '课程覆盖', max: 100 },
            { name: '收藏偏好', max: 100 }
          ],
          name: {
            textStyle: { color: '#999' }
          }
        },
        series: [{
          type: 'radar',
          symbol: 'circle',
          symbolSize: 4,
          // 中间填充颜色
          areaStyle: {
            normal: {
              color: 'rgba(90, 177, 239, 0.5)',
              opacity: 0.6
            }
          },
          itemStyle: { normal: { color: '#5ab1ef' }},
          lineStyle: { normal: { width: 2 }},
          data: [{
            value: data,
            name: '综合评分'
          }],
          animationDuration: 2000
        }]
      })
    }
  }
}
</script>
