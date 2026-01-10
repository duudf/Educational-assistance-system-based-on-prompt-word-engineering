<template>
  <div class="app-container">
    <div class="filter-container">
      <!-- --- ↓↓↓ 核心修改：v-model 绑定到 listQuery.search ↓↓↓ --- -->
      <el-input
        v-model="listQuery.search"
        placeholder="输入ID/课程名/教师名搜索"
        style="width: 250px;"
        class="filter-item"
        @keyup.enter.native="handleFilter"
      />
      <el-button class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">搜索</el-button>
      <el-button class="filter-item" icon="el-icon-refresh" @click="handleReset">重置</el-button>
    </div>

    <el-table v-loading="listLoading" :data="list" border fit highlight-current-row style="width: 100%">
      <el-table-column label="课程ID" prop="id" sortable width="100" align="center" />
      <el-table-column min-width="200px" label="课程名称">
        <template slot-scope="{row}"><span>{{ row.name }}</span></template>
      </el-table-column>
      <el-table-column width="150px" align="center" label="授课教师">
        <template slot-scope="scope"><span>{{ scope.row.teacher_name }}</span></template>
      </el-table-column>
      <el-table-column width="120px" align="center" label="当前人数">
        <template slot-scope="scope"><span>{{ scope.row.student_count }} 人</span></template>
      </el-table-column>
      <el-table-column label="课程描述" min-width="300">
        <template slot-scope="{row}"><span>{{ row.description }}</span></template>
      </el-table-column>
      <el-table-column align="center" label="操作" width="120">
        <template slot-scope="scope">
          <el-button :loading="scope.row.loading" :type="scope.row.is_enrolled ? 'danger' : 'primary'" size="small" @click="handleEnroll(scope.row)">
            {{ scope.row.is_enrolled ? '退选课程' : '选择课程' }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" @pagination="getList" />
  </div>
</template>

<script>
import { fetchCourseList, enrollCourse } from '@/api/course'
import Pagination from '@/components/Pagination'
export default {
  name: 'CourseSelection',
  components: { Pagination },
  data() {
    return {
      list: [],
      total: 0,
      listLoading: true,
      // --- ↓↓↓ 核心修改：将 name 改为 search ↓↓↓ ---
      listQuery: {
        page: 1,
        limit: 10,
        search: undefined
      }
    }
  },
  created() {
    this.getList()
  },
  methods: {
    getList() {
      this.listLoading = true
      const params = { ...this.listQuery, all: true }
      fetchCourseList(params).then(response => {
        this.list = response.data.items.map(v => {
          this.$set(v, 'loading', false); return v
        })
        this.total = response.data.total
        this.listLoading = false
      })
    },
    handleFilter() {
      this.listQuery.page = 1
      this.getList()
    },
    // --- ↓↓↓ 核心修改：重置 listQuery.search ↓↓↓ ---
    handleReset() {
      this.listQuery.search = undefined
      this.handleFilter()
    },
    handleEnroll(row) {
      row.loading = true
      const action = row.is_enrolled ? 'drop' : 'enroll'
      enrollCourse({ course_id: row.id, action: action }).then(() => {
        this.$message({ type: 'success', message: action === 'enroll' ? '选课成功!' : '退课成功!' })
        row.is_enrolled = !row.is_enrolled;
        action === 'enroll' ? row.student_count++ : row.student_count--;
        row.loading = false
      }).catch(() => {
        row.loading = false
      })
    }
  }
}
</script>

<style scoped>
.filter-container { padding-bottom: 20px; }
.filter-item { margin-right: 10px; }
</style>
