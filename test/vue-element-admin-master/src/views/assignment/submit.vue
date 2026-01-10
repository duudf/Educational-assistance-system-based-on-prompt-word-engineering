<template>
  <div class="app-container">
    <el-card v-if="assignment" v-loading="loading">
      <div slot="header" class="clearfix">
        <h3>{{ assignment.title }}</h3>
        <div>
          <span class="due-date">截止日期: {{ assignment.due_date }}</span>
          <el-tag v-if="isExpired" type="danger" size="small" style="margin-left: 10px;">已截止</el-tag>
        </div>
      </div>

      <div class="assignment-content">
        <h4>作业要求</h4>
        <div v-html="assignment.content" class="content-body" />
      </div>

      <el-divider />

      <div class="submission-section">
        <h4>我的提交</h4>
        <div v-if="submission && submission.status !== 'graded'" class="submission-info">
          <p>您已于 {{ submission.submission_date }} 提交，可以修改后重新提交。</p>
        </div>
        <div v-if="submission && submission.status === 'graded'" class="submission-info graded">
          <p>您的作业已被批改，得分: <el-tag type="success" size="medium">{{ submission.grade }}</el-tag></p>
        </div>

        <Tinymce
          ref="tinymceEditor"
          v-model="submissionContent"
          :height="300"
          :disabled="isSubmitDisabled"
        />
        <div style="margin-top: 20px; text-align: right;">
          <el-button @click="goBack">返回</el-button>
          <el-button
            type="primary"
            :loading="saving"
            :disabled="isSubmitDisabled"
            @click="handleSubmit"
          >
            {{ submission ? '更新提交' : '确认提交' }}
          </el-button>
        </div>
      </div>
    </el-card>
    <div v-else v-loading="loading" class="empty-placeholder" />
  </div>
</template>

<script>
import Tinymce from '@/components/Tinymce'
import { fetchStudentSubmissionDetail, postStudentSubmission } from '@/api/submission'

export default {
  name: 'SubmitAssignment',
  components: { Tinymce },
  data() {
    return {
      loading: true,
      saving: false,
      assignment: null,
      submission: null,
      submissionContent: '',
      isExpired: false // 新增：过期状态标志
    }
  },
  computed: {
    // 计算属性，用于统一控制提交按钮和编辑器的禁用状态
    isSubmitDisabled() {
      return this.saving || (this.submission && this.submission.status === 'graded') || this.isExpired;
    }
  },
  created() {
    const assignmentId = this.$route.params.id
    if (assignmentId) {
      this.fetchData(assignmentId)
    }
  },
  methods: {
    fetchData(id) {
      this.loading = true
      fetchStudentSubmissionDetail(id).then(response => {
        const { assignment, submission } = response.data
        this.assignment = assignment
        this.submission = submission
        if (submission) {
          this.submissionContent = submission.content
        }

        // --- ↓↓↓ 核心修改：根据截止日期判断是否过期 ↓↓↓ ---
        if (this.assignment.due_date && this.assignment.due_date !== 'N/A') {
          // 将后端返回的 'YYYY-MM-DD HH:MM' 格式字符串转换为 Date 对象
          // 注意 Safari/iOS 对 '-' 格式支持不佳，替换为 '/'
          const dueDate = new Date(this.assignment.due_date.replace(/-/g, '/'))
          if (new Date() > dueDate) {
            this.isExpired = true
            // 只有在学生还未提交的情况下才弹窗提示，避免打扰已提交的学生
            if (!this.submission) {
              this.$message({
                type: 'error',
                message: '该作业已超过截止日期，无法提交。',
                duration: 5000
              })
            }
          }
        }
        // --- ↑↑↑ 修改结束 ↑↑↑ ---

        this.loading = false
      }).catch(() => {
        this.loading = false;
      })
    },
    handleSubmit() {
      if (!this.submissionContent.trim()) {
        this.$message.warning('提交内容不能为空！')
        return
      }

      this.saving = true
      postStudentSubmission(this.assignment.id, { content: this.submissionContent })
        .then(() => {
          this.$notify({
            title: '成功',
            message: this.submission ? '作业更新成功！' : '作业提交成功！',
            type: 'success',
            duration: 2000
          })
          this.saving = false
          this.$router.push('/assignment/my-assignments')
        })
        .catch(() => {
          this.saving = false
        })
    },
    goBack() {
      this.$router.push('/assignment/my-assignments')
    }
  }
}
</script>

<style scoped>
.clearfix:before, .clearfix:after { display: table; content: ""; }
.clearfix:after { clear: both }
.due-date { color: #999; font-size: 14px; }
.assignment-content, .submission-section { margin-top: 20px; }
.content-body { padding: 15px; border: 1px solid #EBEEF5; border-radius: 4px; min-height: 100px; background-color: #FAFAFA; }
.submission-info { color: #606266; font-size: 14px; }
.submission-info.graded { color: #67C23A; font-weight: bold; }
.empty-placeholder { min-height: 50vh; }
</style>
