<template>
  <div class="dashboard-editor-container">

    <!-- 1. 顶部数据卡片 -->
    <panel-group
      :stats-data="panelData"
      @handleSetLineChartData="handleSetLineChartData"
    />

    <!-- 2. 折线图区域 -->
    <el-row style="background:#fff;padding:16px 16px 0;margin-bottom:32px;">
      <div style="padding-bottom: 15px; font-weight: bold; color: #555; padding-left: 10px;">
        学习趋势对比 (AI练习 vs 作业提交)
      </div>
      <line-chart :chart-data="lineChartData" />
    </el-row>

    <!-- 3. 底部图表区域 -->
    <el-row :gutter="32">
      <el-col :xs="24" :sm="24" :lg="8">
        <div class="chart-wrapper">
          <!-- 雷达图：能力画像 -->
          <radar-chart :chart-data="radarData" />
        </div>
      </el-col>
      <el-col :xs="24" :sm="24" :lg="8">
        <div class="chart-wrapper">
          <!-- 饼图：练习类型分布 -->
          <pie-chart :chart-data="pieData" />
        </div>
      </el-col>
      <el-col :xs="24" :sm="24" :lg="8">
        <div class="chart-wrapper">
          <!-- 柱状图：成绩分布 -->
          <bar-chart :chart-data="barData" />
        </div>
      </el-col>
    </el-row>

  </div>
</template>

<script>
import PanelGroup from './components/PanelGroup'
import LineChart from './components/LineChart'
import RadarChart from './components/RaddarChart' // 确保文件名大小写一致
import PieChart from './components/PieChart'
import BarChart from './components/BarChart'
import request from '@/utils/request'

export default {
  name: 'StudentDashboard',
  components: {
    PanelGroup,
    LineChart,
    RadarChart,
    PieChart,
    BarChart
  },
  data() {
    return {
      // 卡片数据
      panelData: {
        courseCount: 0,
        pendingCount: 0,
        submittedCount: 0,
        total_practices: 0,
        avg_score: 0,
        total_favorites: 0
      },
      // 折线图数据
      lineChartData: {
        aiData: [],
        homeworkData: [],
        xAxisData: []
      },
      // 雷达图数据
      radarData: [],
      // 饼图数据
      pieData: [],
      // 柱状图数据
      barData: {
        x_axis: [],
        y_axis: []
      }
    }
  },
  created() {
    this.fetchDashboardData()
  },
  methods: {
    fetchDashboardData() {
      request({
        url: '/ai/dashboard/analysis',
        method: 'get'
      }).then(response => {
        // 注意：这里的键名必须与后端 Python 中的 data 字典键名完全对应
        const { card_data, line_data, radar_data, pie_data, bar_data } = response.data

        // 1. 填充卡片
        if (card_data) {
          this.panelData = card_data
        }

        // 2. 填充折线图 (对应后端 line_data)
        if (line_data) {
          this.lineChartData = {
            aiData: line_data.ai_practices || [],
            homeworkData: line_data.homework_submissions || [],
            xAxisData: line_data.dates || []
          }
        }

        // 3. 填充雷达图
        this.radarData = radar_data || []

        // 4. 填充饼图
        this.pieData = pie_data || []

        // 5. 填充柱状图
        if (bar_data) {
          this.barData = bar_data
        }
      }).catch(error => {
        console.error('获取仪表盘数据失败:', error)
      })
    },
    handleSetLineChartData(type) {
      console.log('点击了卡片:', type)
    }
  }
}
</script>

<style lang="scss" scoped>
.dashboard-editor-container {
  padding: 32px;
  background-color: rgb(240, 242, 245);
  position: relative;
  min-height: 100vh;

  .chart-wrapper {
    background: #fff;
    padding: 16px 16px 0;
    margin-bottom: 32px;
    border-radius: 4px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, .1);
  }
}
</style>
