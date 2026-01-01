<template>
  <div class="app-container">
    <!-- 新增：创建课程按钮 -->
    <div class="filter-container">
      <!-- --- ↓↓↓ 跳转到创建页面，路径也要修改 ↓↓↓ --- -->
      <router-link to="/example/create">
        <el-button class="filter-item" type="primary" icon="el-icon-edit">
          创建新课程
        </el-button>
      </router-link>
    </div>

    <el-table v-loading="listLoading" :data="list" border fit highlight-current-row style="width: 100%">
      <el-table-column align="center" label="课程ID" width="80">
        <template slot-scope="scope"><span>{{ scope.row.id }}</span></template>
      </el-table-column>
      <el-table-column min-width="200px" label="课程名称">
        <template slot-scope="{row}">
          <!-- --- ↓↓↓ 核心修改：将 /course 改为 /example ↓↓↓ --- -->
          <router-link :to="'/example/edit/'+row.id" class="link-type">
            <span>{{ row.name }}</span>
          </router-link>
        </template>
      </el-table-column>
      <el-table-column width="120px" align="center" label="授课教师">
        <template slot-scope="scope"><span>{{ scope.row.teacher_name }}</span></template>
      </el-table-column>
      <el-table-column width="120px" align="center" label="选课人数">
        <template slot-scope="scope">
          <router-link :to="{ path: '/student/list', query: { course_id: scope.row.id }}">
            <el-button type="text" size="small">{{ scope.row.student_count }} 人</el-button>
          </router-link>
        </template>
      </el-table-column>
      <el-table-column class-name="status-col" label="课程描述" min-width="300">
        <template slot-scope="{row}"><span>{{ row.description }}</span></template>
      </el-table-column>
      <el-table-column align="center" label="操作" width="120">
        <template slot-scope="scope">
          <!-- --- ↓↓↓ 核心修改：将 /course 改为 /example ↓↓↓ --- -->
          <router-link :to="'/example/edit/'+scope.row.id">
            <el-button type="primary" size="small" icon="el-icon-edit">编辑</el-button>
          </router-link>
        </template>
      </el-table-column>
    </el-table>
    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" @pagination="getList" />
  </div>
</template>
<script>
// 导入课程列表的 API 函数
import { fetchCourseList } from '@/api/course'
import Pagination from '@/components/Pagination'

export default {
  name: 'CourseList', // 组件名修改为 CourseList
  components: { Pagination },
  data() {
    return {
      list: null,
      total: 0,
      listLoading: true,
      listQuery: {
        page: 1,
        limit: 20
      }
    }
  },
  created() {
    this.getList()
  },
  methods: {
    getList() {
      this.listLoading = true
      // 调用获取课程列表的 API
      fetchCourseList(this.listQuery).then(response => {
        this.list = response.data.items
        this.total = response.data.total
        this.listLoading = false
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
