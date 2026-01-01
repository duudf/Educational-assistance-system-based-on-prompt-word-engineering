<template>
  <div class="app-container">
    <div class="page-header">
      <h3>作业 "{{ assignmentTitle }}" 的提交情况</h3>
      <el-button icon="el-icon-back" size="small" @click="goBack">返回作业列表</el-button>
    </div>

    <el-table v-loading="loading" :data="submissionList" border fit highlight-current-row style="width: 100%">

      <!-- 序号列 -->
      <el-table-column label="序号" type="index" width="80" align="center" />

      <!-- 学生姓名列 -->
      <el-table-column prop="student_name" label="学生姓名" width="180" />

      <!-- 提交状态列 -->
      <el-table-column prop="status" label="提交状态" width="120" align="center">
        <template slot-scope="{row}">
          <el-tag :type="row.status | statusFilter">
            {{ row.status | statusTranslator }}
          </el-tag>
        </template>
      </el-table-column>

      <!-- 提交时间列 -->
      <el-table-column prop="submission_date" label="提交时间" width="200" align="center" />

      <!-- 成绩列 -->
      <el-table-column prop="grade" label="成绩" width="100" align="center" />

      <!-- 操作列 -->
      <el-table-column label="操作" align="center" min-width="150">
        <template slot-scope="scope">
          <router-link v-if="scope.row.submission_id" :to="'/submission/detail/' + scope.row.submission_id">
            <el-button type="primary" size="mini">
              {{ scope.row.status === 'graded' ? '查看/修改' : '查看并批改' }}
            </el-button>
          </router-link>
          <el-button v-else type="warning" size="mini" @click="remindStudent(scope.row)">
            提醒提交
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
import { fetchSubmissionsByAssignment } from '@/api/submission'

export default {
  name: 'SubmissionList',
  filters: {
    statusFilter(status) {
      const statusMap = {
        graded: 'success',    // 已批改 -> 成功 (绿色)
        submitted: 'warning', // 待批改 -> 警告 (黄色)
        unsubmitted: 'info'   // 未提交 -> 信息 (灰色)
      }
      return statusMap[status] || ''
    },
    statusTranslator(status) {
      const statusMap = {
        graded: '已批改',
        submitted: '待批改',
        unsubmitted: '未提交'
      }
      return statusMap[status] || status
    }
  },
  data() {
    return {
      loading: true,
      submissionList: [],
      assignmentTitle: ''
    }
  },
  created() {
    const assignmentId = this.$route.params.id

    if (this.$route.query.title) {
      this.assignmentTitle = this.$route.query.title
    } else {
      this.assignmentTitle = `ID: ${assignmentId}`
    }

    if (assignmentId) {
      this.fetchData(assignmentId)
    } else {
      this.$message.error('无效的作业ID')
      this.loading = false
    }
  },
  methods: {
    fetchData(assignmentId) {
      this.loading = true
      fetchSubmissionsByAssignment(assignmentId).then(response => {
        this.submissionList = response.data.items
        this.loading = false
      }).catch(err => {
        console.error('获取提交列表失败:', err)
        this.$message.error('加载提交列表失败')
        this.loading = false
      })
    },
    goBack() {
      this.$router.push('/assignment/list')
    },
    remindStudent(row) {
      this.$message({
        message: `已提醒学生 ${row.student_name} 提交作业（此功能待后端实现）。`,
        type: 'info'
      })
    }
  }
}
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
</style>
