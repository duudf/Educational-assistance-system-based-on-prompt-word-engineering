<template>
  <div class="app-container">
    <div v-if="profile" v-loading="loading">
      <el-card>
        <div slot="header" class="clearfix">
          <h3>学生档案：{{ profile.name }}</h3>
        </div>

        <el-row :gutter="20">
          <el-col :span="12">
            <h4>已选课程 ({{ profile.enrolled_courses.length }}门)</h4>
            <el-table :data="profile.enrolled_courses" border size="mini">
              <el-table-column prop="name" label="课程名称" />
              <el-table-column prop="teacher_name" label="授课教师" width="120" />
            </el-table>
          </el-col>

          <el-col :span="12">
            <h4>作业提交记录 ({{ profile.submissions.length }}条)</h4>
            <el-table :data="profile.submissions" border size="mini">
              <el-table-column prop="assignment_title" label="作业标题" />
              <el-table-column prop="course_name" label="所属课程" />
              <el-table-column prop="grade" label="成绩" width="80" />
            </el-table>
          </el-col>
        </el-row>
      </el-card>
    </div>
  </div>
</template>

<script>
import { fetchStudentProfile } from '@/api/student'

export default {
  name: 'StudentProfile',
  data() {
    return {
      loading: true,
      profile: null
    }
  },
  created() {
    const studentId = this.$route.params.id
    if (studentId) {
      this.fetchData(studentId)
    }

  },
  methods: {
    fetchData(id) {
      this.loading = true
      fetchStudentProfile(id).then(response => {
        this.profile = response.data
        this.loading = false
      })
    }
  }
}
</script>

<style scoped>
.clearfix:before, .clearfix:after { display: table; content: ""; }
.clearfix:after { clear: both }
h4 {
  margin-top: 0;
  margin-bottom: 10px;
}
</style>
