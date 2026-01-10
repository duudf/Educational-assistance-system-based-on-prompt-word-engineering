<template>
  <div class="app-container">
    <el-table v-loading="listLoading" :data="list" border fit highlight-current-row style="width: 100%">

      <el-table-column align="center" label="作业ID" width="80">
        <template slot-scope="scope"><span>{{ scope.row.id }}</span></template>
      </el-table-column>

      <el-table-column min-width="200px" label="作业标题">
        <template slot-scope="{row}">
          <router-link :to="'/assignment/edit/'+row.id" class="link-type"><span>{{ row.title }}</span></router-link>
        </template>
      </el-table-column>

      <el-table-column width="180px" align="center" label="所属课程">
        <template slot-scope="scope"><span>{{ scope.row.course_name }}</span></template>
      </el-table-column>

      <el-table-column width="180px" align="center" label="截止日期">
        <template slot-scope="scope"><span>{{ scope.row.due_date }}</span></template>
      </el-table-column>

      <el-table-column width="110px" align="center" label="提交人数">
        <template slot-scope="scope">
          <router-link
            v-if="scope.row.submission_count > 0"
            :to="{ path: `/assignment/${scope.row.id}/submissions`, query: { title: scope.row.title } }"
          >
            <el-button type="text" size="small">
              {{ scope.row.submission_count }} 人
            </el-button>
          </router-link>
          <span v-else>{{ scope.row.submission_count }} 人</span>
        </template>
      </el-table-column>

      <!-- [修改] 操作列：宽度增加，并添加删除按钮 -->
      <el-table-column align="center" label="操作" width="200">
        <template slot-scope="scope">
          <router-link :to="'/assignment/edit/'+scope.row.id" style="margin-right: 10px;">
            <el-button type="primary" size="small" icon="el-icon-edit">编辑</el-button>
          </router-link>
          <!-- [新增] 删除按钮 -->
          <el-button type="danger" size="small" icon="el-icon-delete" @click="handleDelete(scope.row)">
            删除
          </el-button>
        </template>
      </el-table-column>

    </el-table>

    <!-- 分页 -->
    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" @pagination="getList" />
  </div>
</template>

<script>
// [修改] 导入新增的 deleteAssignment API
import { fetchAssignmentList, deleteAssignment } from '@/api/assignment'
import Pagination from '@/components/Pagination'

export default {
  name: 'AssignmentList',
  components: { Pagination },
  data() {
    return {
      list: [],
      total: 0,
      listLoading: true,
      listQuery: { page: 1, limit: 20 }
    }
  },
  created() {
    this.getList()
  },
  methods: {
    getList() {
      this.listLoading = true
      fetchAssignmentList(this.listQuery).then(response => {
        this.list = response.data.items
        this.total = response.data.total
        this.listLoading = false
      }).catch(err => {
        console.error('获取作业列表失败:', err)
        this.listLoading = false
        this.list = []
        this.$message.error('加载作业列表失败')
      })
    },
    // [新增] 处理删除按钮点击事件的方法
    handleDelete(row) {
      this.$confirm(`确定要删除作业 "${row.title}" 吗？此操作将同时删除所有学生的提交记录，且无法撤销。`, '严重警告', {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async() => {
        try {
          await deleteAssignment(row.id)
          this.$message({
            type: 'success',
            message: '删除成功!'
          })
          // 如果删除的是当前页的最后一条数据，最好返回上一页
          if (this.list.length === 1 && this.listQuery.page > 1) {
            this.listQuery.page--
          }
          this.getList() // 重新加载列表
        } catch (error) {
          // API请求失败的处理已由请求拦截器完成
          console.error('删除失败:', error)
        }
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消删除'
        })
      })
    }
  }
}
</script>
