<template>
  <div class="app-container">
    <!-- 筛选和排序区域 -->
    <div class="filter-container">
      <el-select v-model="listQuery.course_id" placeholder="按课程筛选" clearable style="width: 200px" class="filter-item" @change="handleFilter">
        <el-option v-for="item in courseOptions" :key="item.id" :label="item.name" :value="item.id" />
      </el-select>

      <el-select v-model="listQuery.sort" style="width: 180px" class="filter-item" @change="handleFilter">
        <el-option v-for="item in sortOptions" :key="item.key" :label="item.label" :value="item.key" />
      </el-select>
    </div>

    <!-- 表格 -->
    <el-table v-loading="listLoading" :data="list" border fit highlight-current-row style="width: 100%">
      <el-table-column label="作业标题" min-width="200px">
        <template slot-scope="{row}">
          <router-link :to="'/assignment/submit/'+row.id" class="link-type">
            <span>{{ row.title }}</span>
          </router-link>
        </template>
      </el-table-column>
      <el-table-column label="所属课程" prop="course_name" width="180px" align="center" />
      <el-table-column label="截止日期" prop="due_date" width="180px" align="center" />
      <el-table-column label="状态" width="120px" align="center">
        <template slot-scope="{row}">
          <el-tag :type="row.status | statusFilter">
            {{ row.status | statusTranslator }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150px" align="center">
        <template slot-scope="{row}">
          <!-- --- ↓↓↓ 核心修改：增加对 'expired' 状态的处理 ↓↓↓ --- -->
          <el-button v-if="row.status==='pending'" type="success" size="mini" @click="goToSubmit(row.id)">
            去完成
          </el-button>
          <el-button v-else-if="row.status==='expired'" type="danger" size="mini" disabled>
            已截止
          </el-button>
          <el-button v-else type="primary" size="mini" @click="viewSubmission(row.id)">
            查看提交
          </el-button>
          <!-- --- ↑↑↑ 修改结束 ↑↑↑ --- -->
        </template>
      </el-table-column>
    </el-table>
    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" @pagination="getList" />
  </div>
</template>

<script>
import { fetchStudentAssignments } from '@/api/assignment'
import { fetchCourseOptions } from '@/api/course'
import Pagination from '@/components/Pagination'

export default {
  name: 'MyAssignments',
  components: {Pagination},
  filters: {
    statusFilter(status) {
      const statusMap = {
        graded: 'success',
        submitted: 'warning',
        pending: 'info',
        expired: 'danger' // 已过期 -> 红色
      }
      return statusMap[status] || ''
    },
    statusTranslator(status) {
      const statusMap = {
        graded: '已批改',
        submitted: '已提交',
        pending: '待完成',
        expired: '已过期' // 已过期 -> 文本
      }
      return statusMap[status] || status
    }
  },
  data() {
    return {
      list: [],
      total: 0,
      listLoading: true,
      listQuery: {
        page: 1,
        limit: 20,
        course_id: undefined,
        sort: '+due_date'
      },
      sortOptions: [
        {label: '按截止日期升序', key: '+due_date'},
        {label: '按截止日期降序', key: '-due_date'},
        {label: '按课程名称升序', key: '+course'},
        {label: '按课程名称降序', key: '-course'}
      ],
      courseOptions: []
    }
  },
  created() {
    this.getList()
    this.getCourseOptions()
  },
  methods: {
    getList() {
      this.listLoading = true
      fetchStudentAssignments(this.listQuery).then(response => {
        this.list = response.data.items
        this.total = response.data.total
        this.listLoading = false
      }).catch(err => {
        console.error("获取作业列表失败:", err);
        this.listLoading = false;
        this.list = [];
        this.$message.error("加载作业列表失败");
      })
    },
    getCourseOptions() {
      fetchCourseOptions().then(response => {
        this.courseOptions = response.data.items
      }).catch(err => {
        console.error("获取课程选项失败:", err);
      })
    },
    handleFilter() {
      this.listQuery.page = 1
      this.getList()
    },
    goToSubmit(id) {
      this.$router.push(`/assignment/submit/${id}`)
    },
    viewSubmission(id) {
      this.$router.push(`/assignment/submit/${id}`)
    }
  }
}
</script>

<style lang="scss" scoped>
@import "~@/styles/mixin.scss";

.filter-container {
  padding-bottom: 20px;
}

.filter-item {
  margin-right: 10px;
}
</style>
