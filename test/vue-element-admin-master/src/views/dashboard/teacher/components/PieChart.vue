<template>
  <!-- 新增父容器拆分：独立标题 + 图表/占位符区域 -->
  <div :class="className" :style="{height:height,width:width}">
    <!-- 独立标题：和柱状图样式统一 -->
    <div class="chart-title">各课程学生人数分布</div>

    <!-- 图表/无数据区域：包含loading和显示逻辑 -->
    <div
      v-loading="loading"
      class="chart-content"
      style="height: calc(100% - 30px); width: 100%;"
    >
      <!-- 有数据时显示图表 -->
      <div v-if="hasData" ref="chart" style="height: 100%; width: 100%;" />
      <!-- 无数据时显示占位提示 -->
      <div v-else class="no-data-placeholder">
        暂无数据
      </div>
    </div>
  </div>
</template>

<script>
import echarts from 'echarts'
require('echarts/theme/macarons')
import resize from './mixins/resize'
import { getCourseStudentPieData } from '@/api/analysis'

export default {
  mixins: [resize],
  props: {
    className: { type: String, default: 'chart' },
    width: { type: String, default: '100%' },
    height: { type: String, default: '300px' }
  },
  data() {
    return {
      chart: null,
      loading: true,
      hasData: false // 新增：控制数据有无的显示状态
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
    fetchData() {
      this.loading = true
      this.hasData = false // 重置数据状态
      getCourseStudentPieData().then(response => {
        const pieData = response.data
        // 判定有数据：数组存在且长度大于0
        if (pieData && pieData.length > 0) {
          this.hasData = true
          this.$nextTick(() => {
            this.initChart(pieData)
          })
        } else {
          this.hasData = false
          // 清空可能存在的旧图表
          if (this.chart) {
            this.chart.clear()
          }
        }
        this.loading = false
      }).catch(error => {
        console.error('获取饼图数据失败:', error)
        this.hasData = false
        this.loading = false
      })
    },
    initChart(pieData) {
      // 绑定到ref元素，而非直接绑定$el
      this.chart = echarts.init(this.$refs.chart, 'macarons')

      this.chart.setOption({
        // 移除ECharts内部title，改用外部独立标题
        tooltip: {
          trigger: 'item',
          formatter: '{a} <br/>{b} : {c} 人 ({d}%)'
        },
        legend: {
          orient: 'horizontal',
          left: 'center',
          bottom: '5',
          data: pieData.map(item => item.name)
        },
        series: [
          {
            name: '选课人数',
            type: 'pie',
            roseType: 'radius',
            radius: ['10%', '40%'],
            center: ['45%', '45%'],
            data: pieData,
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            },
            label: {
              show: true,
              position: 'outside',
              formatter: function (params) {
                const maxCharsPerLine = 7
                let name = params.name
                if (name.length > maxCharsPerLine) {
                  name = name.substring(0, maxCharsPerLine) + '\n' + name.substring(maxCharsPerLine)
                }
                return `${name}\n${params.value}人`
              }
            },
            labelLine: {
              show: true,
              length: 10,
              length2: 15
            }
          }
        ]
      })
    }
  }
}
</script>

<!-- 新增样式：和柱状图保持完全一致 -->
<style scoped>
/* 标题样式：统一字体、大小、位置 */
.chart-title {
  color: #2198cb;
  text-align: center;
  font-size: 18px;
  font-weight: normal;
  height: 30px;
  line-height: 30px;
}

/* 无数据占位样式：和柱状图统一 */
.no-data-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  width: 100%;
  color: #909399;
  font-size: 14px;
}
</style>
