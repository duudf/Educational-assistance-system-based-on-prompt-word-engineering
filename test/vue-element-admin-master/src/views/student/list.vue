<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input v-model="listQuery.course_id" placeholder="按课程ID筛选" style="width: 200px;" class="filter-item" @keyup.enter.native="handleFilter" />
      <el-button class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">
        搜索
      </el-button>
    </div>

    <el-table
      v-loading="listLoading"
      :data="list"
      border
      fit
      highlight-current-row
      style="width: 100%;"
    >
      <el-table-column label="学生ID" prop="id" align="center" width="80" />
      <el-table-column label="用户名" prop="name" min-width="150px" />
      <el-table-column label="已选课程数" prop="enrolled_course_count" align="center" width="120" />
      <el-table-column label="已提交作业数" prop="submission_count" align="center" width="140" />
      <el-table-column label="操作" align="center" width="230" class-name="small-padding fixed-width">
        <template slot-scope="{row}">
          <router-link :to="{ path: `/analysis/student/${row.id}`, query: { name: row.name }}">
            <el-button type="primary" size="mini">
              AI 分析
            </el-button>
          </router-link>
          <el-button type="info" size="mini" @click="handleViewDetails(row)">
            查看详情
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" @pagination="getList" />
  </div>
</template>

<script>
import { fetchStudentList } from '@/api/student'
import Pagination from '@/components/Pagination'

export default {
  name: 'StudentList',
  components: { Pagination },
  data() {
    return {
      list: null,
      total: 0,
      listLoading: true,
      listQuery: {
        page: 1,
        limit: 20,
        course_id: undefined
      }
    }
  },
  created() {
    // 检查路由参数中是否带有 course_id
    const courseId = this.$route.query.course_id
    if (courseId) {
      this.listQuery.course_id = courseId
    }
    this.getList()
  },
  methods: {
    getList() {
      this.listLoading = true
      fetchStudentList(this.listQuery).then(response => {
        this.list = response.data.items
        this.total = response.data.total
        this.listLoading = false
      })
    },
    handleFilter() {
      this.listQuery.page = 1
      this.getList()
    },
    handleViewDetails(row) {
      // 可以在这里实现跳转到学生个人主页等功能
      this.$message(`查看学生 ${row.name} 的详细信息`)
    }
  }
}
</script>

<style scoped>
.filter-container {
  padding-bottom: 20px;
}
</style>
