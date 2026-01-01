<template>
  <div class="app-container">
    <div v-if="studentName" class="page-header">
      <h2>对学生「{{ studentName }}」的学习分析报告</h2>
      <p>由 AI 大模型生成，仅供教学参考</p>
      <el-button
        type="primary"
        icon="el-icon-refresh"
        :loading="loading"
        size="small"
        class="refresh-btn"
        @click="fetchAnalysis(true)"
      >
        重新生成分析报告
      </el-button>
      <span v-if="analysisResult && analysisResult.last_updated" class="update-time">
        上次更新于: {{ new Date(analysisResult.last_updated).toLocaleString() }}
      </span>
    </div>

    <div v-loading="loading" element-loading-text="AI 正在分析中，请稍候...">
      <analysis-report v-if="analysisResult" :report-data="analysisResult" />
      <div v-if="showEmpty" class="empty-container">
        <p>{{ emptyText }}</p>
      </div>
    </div>
  </div>
</template>
<script>
import { getStudentAnalysis } from '@/api/analysis'
import AnalysisReport from './components/AnalysisReport.vue'
export default {
  name: 'StudentAnalysisPage',
  components: { AnalysisReport },
  data() {
    return {
      loading: true, studentId: null, studentName: '',
      analysisResult: null, emptyText: '正在加载分析数据...'
    }
  },
  computed: { showEmpty() { return !this.loading && !this.analysisResult } },
  created() {
    this.studentId = this.$route.params.id
    this.studentName = this.$route.query.name || `学生ID: ${this.studentId}`
    if (this.studentId) { this.fetchAnalysis(false) } else { this.loading = false; this.emptyText = '无效的学生ID' }
  },
  methods: {
    fetchAnalysis(forceRefresh = false) {
      this.loading = true
      this.analysisResult = null // 重新分析时先清空，这样会有加载效果

      console.log(`准备请求AI分析，强制刷新: ${forceRefresh}`) // 添加调试日志

      // 确保 force_refresh 作为字符串 'true' 或 'false' 传递
      const params = {
    force_refresh: forceRefresh ? 'true' : 'false'
  }

      getStudentAnalysis(this.studentId, params).then(response => {
        console.log('成功从后端获取到AI分析数据')
        this.analysisResult = response.data
        this.loading = false
      }).catch(err => {
        console.error('获取AI分析失败:', err)
        this.emptyText = err.message || 'AI分析服务调用失败'
        this.loading = false
      })
    }
  }
}
</script>
<style scoped>
.page-header { position: relative; margin-bottom: 25px; padding-bottom: 15px; border-bottom: 1px solid #EBEEF5; }
.page-header h2 { margin: 0; font-size: 24px; }
.page-header p { margin-top: 8px; color: #909399; font-size: 14px; }
.refresh-btn { position: absolute; top: 0; right: 0; }
.update-time { position: absolute; top: 45px; right: 0; font-size: 12px; color: #909399; }
.empty-container { text-align: center; color: #909399; padding: 60px 0; font-size: 14px; }
</style>
