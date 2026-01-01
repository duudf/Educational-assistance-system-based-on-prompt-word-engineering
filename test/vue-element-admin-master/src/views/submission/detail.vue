<template>
  <div class="app-container">
    <el-card v-if="submission" v-loading="loading">
      <div slot="header" class="clearfix">
        <h3>作业提交详情</h3>
        <el-button style="float: right; padding: 3px 0" type="text" @click="goBack">返回列表</el-button>
      </div>

      <el-descriptions :column="2" border>
        <el-descriptions-item>
          <template slot="label"><i class="el-icon-user" /> 学生姓名</template>
          {{ submission.student_name }}
        </el-descriptions-item>
        <el-descriptions-item>
          <template slot="label"><i class="el-icon-tickets" /> 作业标题</template>
          {{ submission.assignment_title }}
        </el-descriptions-item>
      </el-descriptions>

      <div class="submission-content-wrapper">
        <h4>提交内容</h4>
        <div v-html="submission.content" class="submission-content" />
      </div>

      <div class="grading-section">
        <h4>批改打分</h4>
        <el-form :inline="true">
          <el-form-item label="分数 (0-100)">
            <el-input-number v-model="grade" :precision="1" :step="5" :min="0" :max="100" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="saving" @click="handleSaveGrade">保存成绩</el-button>
          </el-form-item>
        </el-form>
      </div>

    </el-card>
    <div v-else v-loading="loading" class="empty-placeholder" />
  </div>
</template>

<script>
// --- ↓↓↓ 导入所有需要的 API 函数 ↓↓↓ ---
import { fetchSubmissionDetail, gradeSubmission } from '@/api/submission'

export default {
  name: 'SubmissionDetail',
  data() {
    return {
      loading: true,
      saving: false, // 新增：用于保存按钮的加载状态
      submission: null,
      grade: 0 // 新增：用于打分的临时变量
    }
  },
  created() {
    const id = this.$route.params.id
    if (id) {
      this.fetchData(id)
    }
  },
  methods: {
    fetchData(id) {
      this.loading = true
      fetchSubmissionDetail(id).then(response => {
        this.submission = response.data
        // 将获取到的分数赋值给 grade 变量
        this.grade = this.submission.grade || 0
        this.loading = false
      }).catch(() => {
        this.loading = false
      })
    },
    // --- ↓↓↓ 完善 handleSaveGrade 方法 ↓↓↓ ---
    handleSaveGrade() {
      this.saving = true
      // 调用后端 API 来更新成绩
      gradeSubmission(this.submission.submission_id, { grade: this.grade }).then(() => {
        this.$message({
          message: '成绩已成功保存！',
          type: 'success'
        })
        // 在前端同步更新状态，以便用户立即看到反馈
        this.submission.status = 'graded'
        this.submission.grade = this.grade
        this.saving = false
      }).catch(() => {
        this.$message.error('保存成绩失败')
        this.saving = false
      })
    },
    // --- ↓↓↓ 新增返回方法 ↓↓↓ ---
    goBack() {
      // 智能返回，如果上一页是提交列表，就返回那里
      const lastView = this.$store.getters.visitedViews.slice(-2)[0]
      if (lastView && lastView.name === 'SubmissionList') {
        this.$router.push(lastView.fullPath)
      } else {
        // 否则返回默认的作业列表页
        this.$router.push('/assignment/list')
      }
    }
  }
}
</script>

<style scoped>
/* 样式优化 */
.clearfix:before,
.clearfix:after {
  display: table;
  content: "";
}
.clearfix:after {
  clear: both
}
.submission-content-wrapper {
  margin-top: 20px;
}
.submission-content {
  padding: 15px;
  border: 1px solid #EBEEF5;
  border-radius: 4px;
  background-color: #FAFAFA;
  min-height: 200px;
}
.grading-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #EBEEF5;
}
.empty-placeholder {
  min-height: 50vh;
}
</style>
