<template>
  <div class="teacher-dashboard-container">
    <!-- 数据面板组 (独立获取数据) -->
    <panel-group />

    <!-- 折线图容器：最近7天作业提交量 -->
    <el-row style="background:#fff;padding:16px 16px 0;margin-bottom:32px;">
      <!-- 使用 v-if 确保在数据加载后再渲染图表 -->
      <line-chart v-if="lineChartLoaded" :chart-data="lineChartData" />
    </el-row>

    <!-- 保留其他图表行，但移除会引起错误的信息行 -->
    <el-row :gutter="32">
      <el-col :xs="24" :sm="24" :lg="8">
        <div class="chart-wrapper"><raddar-chart /></div>
      </el-col>
      <el-col :xs="24" :sm="24" :lg="8">
        <div class="chart-wrapper"><pie-chart /></div>
      </el-col>
      <el-col :xs="24" :sm="24" :lg="8">
        <div class="chart-wrapper"><bar-chart /></div>
      </el-col>
    </el-row>
  </div>
</template>

<script>
// 1. 引入需要的组件和新的 API 函数
import PanelGroup from './components/PanelGroup'
import LineChart from './components/LineChart'
import RaddarChart from './components/RaddarChart'
import PieChart from './components/PieChart'
import BarChart from './components/BarChart'
import { getDailySubmissions } from '@/api/analysis'

export default {
  name: 'TeacherDashboard',
  // 2. 注册组件
  components: {
    PanelGroup,
    LineChart,
    RaddarChart,
    PieChart,
    BarChart
  },
  // 3. 定义 data
  data() {
    return {
      lineChartData: {},
      lineChartLoaded: false
    }
  },
  // 4. 在 created 钩子中获取数据
  created() {
    this.fetchLineChartData()
  },
  methods: {
    // 5. 定义获取数据的方法
    fetchLineChartData() {
      getDailySubmissions().then(response => {
        this.lineChartData = response.data
        this.lineChartLoaded = true
      }).catch(err => {
        console.error("获取折线图数据失败:", err);
      });
    }
  }
}
</script>

<style lang="scss" scoped>
/* 样式保持不变 */
.teacher-dashboard-container {
  padding: 32px;
  background-color: rgb(240, 242, 245);
  position: relative;
}
.chart-wrapper {
  background: #fff;
  padding: 16px 16px 0;
  margin-bottom: 32px;
}
</style>
