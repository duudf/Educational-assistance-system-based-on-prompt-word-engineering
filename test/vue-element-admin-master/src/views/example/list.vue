<template>
  <div class="app-container">
    <!-- 创建课程按钮：只在当前用户是教师时显示 -->
    <div class="filter-container" v-if="isTeacher">
      <router-link to="/example/create">
        <el-button class="filter-item" type="primary" icon="el-icon-edit">
          创建新课程
        </el-button>
      </router-link>
    </div>

    <!-- 课程表格 -->
    <el-table v-loading="listLoading" :data="list" border fit highlight-current-row style="width: 100%">
      <el-table-column label="课程ID" prop="id" sortable width="100" align="center" >
        <template slot-scope="scope"><span>{{ scope.row.id }}</span></template>
      </el-table-column>

      <el-table-column min-width="200px" label="课程名称">
        <template slot-scope="{row}">
          <router-link v-if="isTeacher" :to="'/example/edit/'+row.id" class="link-type">
            <span>{{ row.name }}</span>
          </router-link>
          <span v-else>{{ row.name }}</span>
        </template>
      </el-table-column>

      <el-table-column width="120px" align="center" label="授课教师">
        <template slot-scope="scope"><span>{{ scope.row.teacher_name }}</span></template>
      </el-table-column>

      <el-table-column width="120px" align="center" label="选课人数">
        <template slot-scope="scope">
          <router-link v-if="isTeacher" :to="{ path: '/student/list', query: { course_id: scope.row.id }}">
            <el-button type="text" size="small">{{ scope.row.student_count }} 人</el-button>
          </router-link>
          <span v-else>{{ scope.row.student_count }} 人</span>
        </template>
      </el-table-column>

      <el-table-column class-name="status-col" label="课程描述" min-width="300">
        <template slot-scope="{row}"><span>{{ row.description }}</span></template>
      </el-table-column>

      <!-- [修改] 操作列：宽度增加，并添加删除按钮 -->
      <el-table-column v-if="isTeacher" align="center" label="操作" width="200">
        <template slot-scope="scope">
          <router-link :to="'/example/edit/'+scope.row.id" style="margin-right: 10px;">
            <el-button type="primary" size="small" icon="el-icon-edit">编辑</el-button>
          </router-link>
          <!-- [新增] 删除按钮 -->
          <el-button type="danger" size="small" icon="el-icon-delete" @click="handleDelete(scope.row)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页组件 -->
    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" @pagination="getList" />
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
// [修改] 导入新增的 deleteCourse API
import { fetchCourseList, deleteCourse } from '@/api/course'
import Pagination from '@/components/Pagination'

export default {
  name: 'CourseList',
  components: {Pagination},
  data() {
    return {
      list: [],
      total: 0,
      listLoading: true,
      listQuery: {
        page: 1,
        limit: 20
      }
    }
  },
  computed: {
    ...mapGetters([
      'roles'
    ]),
    isTeacher() {
      return this.roles.includes('teacher')
    }
  },
  created() {
    this.getList()
  },
  methods: {
    getList() {
      this.listLoading = true
      fetchCourseList(this.listQuery).then(response => {
        this.list = response.data.items
        this.total = response.data.total
        this.listLoading = false
      }).catch(() => {
        this.listLoading = false
        this.list = []
      })
    },
    // [新增] 处理删除按钮点击事件的方法
    handleDelete(row) {
      // 弹出确认框，防止误操作
      this.$confirm(`确定要删除课程 "${row.name}" 吗？此操作将无法撤销。`, '警告', {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        // 用户点击了“确定”
        try {
          await deleteCourse(row.id)
          this.$message({
            type: 'success',
            message: '删除成功!'
          })
          // 删除成功后，重新加载列表
          this.getList()
        } catch (error) {
          // API请求失败的处理已由请求拦截器完成，这里无需额外操作
          console.error('删除失败:', error)
        }
      }).catch(() => {
        // 用户点击了“取消”
        this.$message({
          type: 'info',
          message: '已取消删除'
        })
      })
    }
  }
}
</script>

<style scoped>
.filter-container {
  padding-bottom: 20px;
}
</style>
