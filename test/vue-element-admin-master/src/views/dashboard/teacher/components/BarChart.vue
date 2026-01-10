<template>
  <div v-loading="loading" :class="className" :style="{height:height,width:width}">
    <!-- [新增] 独立的图表标题，无论有无数据都显示 -->
    <div class="chart-title">我创建的 AI 角色近7日调用次数</div>

    <!-- 图表容器，只有在有数据时显示 -->
    <div v-if="hasData" ref="chart" style="height: calc(100% - 30px); width: 100%;" />

    <!-- 暂无数据提示，在没有数据且加载完成后显示 -->
    <div v-else class="no-data-placeholder">
      暂无数据
    </div>
  </div>
</template>

<script>
import echarts from 'echarts'
require('echarts/theme/macarons')
import resize from './mixins/resize'
import { fetchTeacherRoleStats } from '@/api/dashboard'

const animationDuration = 2000

export default {
  props: {
    className: { type: String, default: 'chart' },
    width: { type: String, default: '100%' },
    height: { type: String, default: '300px' }
  },
  data() {
    return {
      chart: null,
      loading: true,
      hasData: false
    }
  },
  mounted() {
    this.fetchData()
  },
  beforeDestroy() {
    if (this.chart) {
      this.chart.dispose()
      this.chart = null
    }
  },
  methods: {
    async fetchData() {
      this.loading = true
      this.hasData = false
      try {
        const response = await fetchTeacherRoleStats()
        const chartData = response.data
        if (chartData && chartData.series && chartData.series.length > 0 && chartData.series.some(s => s.data.some(d => d > 0))) {
          this.hasData = true
          this.$nextTick(() => {
            this.initChart(chartData)
          })
        } else {
          this.hasData = false
        }
      } catch (error) {
        console.error('获取图表数据失败:', error)
        this.hasData = false
      } finally {
        this.loading = false
      }
    },
    initChart(chartData) {
      this.chart = echarts.init(this.$refs.chart, 'macarons')
      this.chart.setOption({
        // [删除] 原ECharts内部的title配置，改为外部独立显示
        tooltip: {
          trigger: 'axis',
          axisPointer: {type: 'shadow'}
        },
        legend: {
          bottom: 5,
          data: chartData.series.map(s => s.name)
        },
        grid: {
          top: 9, // 因为标题移到外部，这里顶部间距设为0
          left: '3%',
          right: '4%',
          bottom: '10%',
          containLabel: true
        },
        xAxis: [{
          type: 'category',
          data: chartData.dates,
          axisTick: {alignWithLabel: true}
        }],
        yAxis: [{
          type: 'value',
          axisTick: {show: false},
          minInterval: 1,
          max: value => value.max < 5 ? 5 : Math.ceil(value.max / 2) * 2
        }],
        series: chartData.series.map(item => ({
          ...item,
          animationDuration
        }))
      })
    }
  }
}
</script>

<style scoped>
/* [新增] 标题样式，和原ECharts标题样式保持一致 */
.chart-title {
  color: #2198cb;
  text-align: center;
  font-size: 18px;
  font-weight: normal;
  height: 30px;
  line-height: 30px;
}

.no-data-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: calc(100% - 40px); /* 减去标题高度 */
  width: 100%;
  color: #909399;
  font-size: 14px;
}
</style>
