<template>
  <div
    :class="className"
    :style="{height: height, width: width}"
    v-loading="loading"
    element-loading-text="正在加载数据..."
    class="raddar-chart-container"
  >
    <!-- [修改] 头部布局优化，使用 flex-wrap -->
    <div class="chart-header">
      <el-radio-group v-model="scope" size="mini" @change="handleScopeChange" class="scope-selector">
        <el-radio-button label="self">只看我的</el-radio-button>
        <el-radio-button label="all">查看全部</el-radio-button>
      </el-radio-group>

      <el-select
        v-model="selectedIndicators"
        multiple
        collapse-tags
        size="mini"
        placeholder="请选择要对比的课程 (最多5项)"
        class="course-selector"
        :multiple-limit="5"
        @change="handleSelectionChange"
      >
        <el-option
          v-for="item in fullIndicatorData"
          :key="item.name"
          :label="item.name"
          :value="item.name"
        />
      </el-select>
    </div>

    <!-- ECharts 容器 -->
    <div ref="chart" :style="{height: `calc(100% - ${headerHeight}px)`, width: '100%'}" />

    <!-- 空状态提示 -->
    <div v-if="isEmpty" class="empty-chart-text">暂无课程数据或未选择对比课程</div>
  </div>
</template>

<script>
// ... <script> 部分与我们之前确认的交互式选择方案完全一致，无需修改 ...
import echarts from 'echarts'
require('echarts/theme/macarons')
import resize from './mixins/resize'
import { getCourseRadarData } from '@/api/analysis'

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
      scope: 'self',
      isEmpty: false,
      fullIndicatorData: [],
      fullSeriesData: [],
      selectedIndicators: [],
      headerHeight: 40 // [新增] 用于动态计算图表高度
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
      this.isEmpty = false
      getCourseRadarData({ scope: this.scope }).then(response => {
        const { indicator, series_data } = response.data
        this.fullIndicatorData = indicator || []
        this.fullSeriesData = series_data || []
        if (this.fullIndicatorData.length > 0) {
          this.selectedIndicators = this.fullIndicatorData.slice(0, 5).map(ind => ind.name)
          this.updateChart()
        } else {
          this.showEmptyState()
        }
        this.loading = false
      }).catch(() => {
        this.loading = false
        this.showEmptyState()
      })
    },
    handleSelectionChange() { this.updateChart() },
    handleScopeChange() { this.fetchData() },
    updateChart() {
      const filteredIndicator = this.fullIndicatorData.filter(ind => this.selectedIndicators.includes(ind.name))
      const filteredSeriesData = this.fullSeriesData.map(series => {
        const newData = []
        filteredIndicator.forEach(indicatorItem => {
          const originalIndex = this.fullIndicatorData.findIndex(origInd => origInd.name === indicatorItem.name)
          if (originalIndex !== -1) { newData.push(series.value[originalIndex]) }
        })
        return { ...series, value: newData }
      })

      if (filteredIndicator.length === 0) {
        this.showEmptyState()
        return
      }
      this.isEmpty = false
      this.initChart(filteredIndicator, filteredSeriesData)
    },
    initChart(indicator, seriesData) {
      this.$nextTick(() => {
        if (!this.$refs.chart) return
        this.chart = echarts.getInstanceByDom(this.$refs.chart) || echarts.init(this.$refs.chart, 'macarons')
        this.chart.setOption({
          tooltip: { trigger: 'item' },
          legend: {
            left: 'center', bottom: '5px', data: seriesData.map(s => s.name)
          },
          radar: {
            radius: '55%', center: ['50%', '50%'], splitNumber: 4,
            axisName: {
              formatter: (value) => value.length > 5 ? value.slice(0, 5) + '...' : value,
              color: '#666', fontSize: 12
            },
            indicator: indicator
          },
          series: [{
            type: 'radar', symbolSize: 0, areaStyle: {opacity: 0.6},
            data: seriesData, lineStyle: {width: 1}
          }]
        })
      })
    },
    showEmptyState() {
      if (this.chart) {
        this.chart.clear()
      }
      this.isEmpty = true
    }
  }
}
</script>

<style lang="scss" scoped>
.raddar-chart-container {
  position: relative;
}

/* --- ↓↓↓ 核心修改：优化头部布局样式 ↓↓↓ --- */
.chart-header {
  padding: 5px 15px;
  display: flex;
  align-items: center;
  flex-wrap: wrap; /* 1. 允许换行！这是关键 */
  gap: 15px; /* 2. 在元素之间增加间距 */
  min-height: 40px; /* 3. 保证最小高度，即使换行也能适应 */
  box-sizing: border-box;
}

.scope-selector {
  flex-shrink: 0; /* 4. 不允许这个元素被压缩 */
}

.course-selector {
  flex-grow: 1; /* 5. 允许这个元素占据剩余空间 */
  min-width: 220px; /* 6. 保证它有一个合理的最小宽度 */
}

/* --- ↑↑↑ 修改结束 ↑↑↑ --- */

.empty-chart-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #909399;
  font-size: 14px;
}
</style>
