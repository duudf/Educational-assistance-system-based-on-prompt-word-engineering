<template>
  <div v-if="reportData && reportData.current" class="analysis-report-container">
    <el-row :gutter="32">
      <el-col :xs="24" :sm="24" :lg="10">
        <el-card class="box-card" shadow="never">
          <div slot="header" class="clearfix"><span>学生能力六维对比图</span></div>
          <div ref="radarChart" style="height: 350px; width: 100%;" />
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="24" :lg="14">
        <el-card class="box-card" shadow="never">
          <div slot="header" class="clearfix"><span>AI 综合评价</span></div>
          <p class="summary-text">{{ reportData.current.summary }}</p>
          <div v-if="reportData.previous" class="comparison-block">
            <strong>上次评价：</strong><p class="summary-text old-summary">{{ reportData.previous.summary }}</p>
          </div>
        </el-card>
        <el-card class="box-card" shadow="never" style="margin-top: 32px;">
          <div slot="header" class="clearfix"><span>潜在强项</span></div>
          <div><el-tag
                 v-for="item in reportData.current.strengths"
                 v-if="reportData.current.strengths && reportData.current.strengths.length > 0"
                 :key="item"
                 type="success"
                 effect="dark"
                 class="tag-item"
               >{{ item }}
               </el-tag>
            <div v-else class="empty-text">暂未发现明显强项</div>
          </div>
        </el-card>
        <el-card class="box-card" shadow="never" style="margin-top: 32px;">
          <div slot="header" class="clearfix"><span>学习改进建议</span></div>
          <ul
            v-if="reportData.current.suggestions && reportData.current.suggestions.length > 0"
            class="suggestion-list"
          >
            <li v-for="item in reportData.current.suggestions" :key="item"><i class="el-icon-s-opportunity" /> {{ item }}
            </li>
          </ul>
          <div v-else class="empty-text">暂无特别建议</div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>
<script>
import * as echarts from 'echarts'

export default {
  name: 'AnalysisReport', props: { reportData: { type: Object, required: true }},
  data() {
    return { chart: null }
  }, watch: {
    reportData: {
      deep: true, handler(val) {
        if (val) {
          this.$nextTick(() => {
            this.initChart()
          })
        }
      }
    }
  },
  mounted() {
    this.$nextTick(() => {
      this.initChart()
    })
  }, beforeDestroy() {
    if (!this.chart) {
      return
    }
    this.chart.dispose()
    this.chart = null
  },
  methods: {
    initChart() {
      if (!this.reportData || !this.reportData.current || !this.$refs.radarChart) return
      this.chart = echarts.init(this.$refs.radarChart, 'macarons')
      const currentData = this.reportData.current
      const previousData = this.reportData.previous
      const seriesData = [{
        value: [currentData.activity_score, currentData.performance_score, currentData.knowledge_mastery_score, currentData.innovation_score, currentData.consistency_score, currentData.potential_score],
        name: '本次评分',
        areaStyle: { color: 'rgba(64, 201, 198, 0.6)' },
        lineStyle: { color: 'rgba(64, 201, 198, 1)' },
        itemStyle: { color: 'rgba(64, 201, 198, 1)' }
      }]
      if (previousData) {
        seriesData.push({
          value: [previousData.activity_score, previousData.performance_score, previousData.knowledge_mastery_score, previousData.innovation_score, previousData.consistency_score, previousData.potential_score],
          name: '上次评分',
          areaStyle: { color: 'rgba(144, 147, 153, 0.4)' },
          lineStyle: { color: 'rgba(144, 147, 153, 1)' },
          itemStyle: { color: 'rgba(144, 147, 153, 1)' }
        })
      }
      const option = {
        tooltip: { trigger: 'item' },
        legend: { data: previousData ? ['本次评分', '上次评分'] : ['本次评分'], bottom: 5 },
        radar: {
          indicator: [{ name: '学习积极性', max: 5 }, { name: '成绩表现', max: 5 }, {
            name: '知识掌握度',
            max: 5
          }, { name: '探索创新性', max: 5 }, { name: '稳定性与毅力', max: 5 }, { name: '发展潜力', max: 5 }],
          shape: 'polygon',
          radius: '60%',
          center: ['50%', '50%'],
          axisName: { color: '#666', fontSize: 14 }
        },
        series: [{ name: '学生能力分析', type: 'radar', data: seriesData }]
      }
      this.chart.setOption(option)
    }
  }
}
</script>
<style lang="scss" scoped>
.analysis-report-container {
  padding-top: 20px;
}

.box-card {
  border: 1px solid #EBEEF5;
}

.summary-text {
  font-size: 15px;
  line-height: 1.8;
  color: #303133;
  text-indent: 2em;
  margin: 0;
}

.suggestion-list {
  list-style: none;
  padding: 0;
  margin: 0;

  li {
    font-size: 14px;
    line-height: 1.7;
    margin-bottom: 12px;
    color: #606266;
    display: flex;
    align-items: flex-start;

    .el-icon-s-opportunity {
      color: #E6A23C;
      margin-right: 8px;
      margin-top: 4px;
    }
  }
}

.empty-text {
  color: #909399;
  font-size: 14px;
  text-align: center;
  padding: 20px 0;
}

.tag-item {
  font-size: 14px;
  margin-right: 10px;
  margin-bottom: 10px;
}

.comparison-block {
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px dashed #DCDFE6;

  strong {
    color: #909399;
    font-size: 14px;
  }

  .old-summary {
    color: #909399;
    font-style: italic;
  }
}
</style>
