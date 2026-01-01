<template>
  <div class="app-container">
    <el-table v-loading="listLoading" :data="list" border fit highlight-current-row style="width: 100%">

      <!-- 作业ID 列 -->
      <el-table-column align="center" label="作业ID" width="80">
        <template slot-scope="scope"><span>{{ scope.row.id }}</span></template>
      </el-table-column>

      <!-- 作业标题 列 -->
      <el-table-column min-width="200px" label="作业标题">
        <template slot-scope="{row}">
          <router-link :to="'/assignment/edit/'+row.id" class="link-type"><span>{{ row.title }}</span></router-link>
        </template>
      </el-table-column>

      <!-- 所属课程 列 -->
      <el-table-column width="180px" align="center" label="所属课程">
        <template slot-scope="scope"><span>{{ scope.row.course_name }}</span></template>
      </el-table-column>

      <!-- 截止日期 列 -->
      <el-table-column width="180px" align="center" label="截止日期">
        <template slot-scope="scope"><span>{{ scope.row.due_date }}</span></template>
      </el-table-column>

      <!-- 提交人数 列 -->
      <el-table-column width="110px" align="center" label="提交人数">
        <template slot-scope="scope">
          <!-- --- ↓↓↓ 核心修改：将 el-button 的 @click 改为 router-link 跳转 ↓↓↓ --- -->
          <router-link
            v-if="scope.row.submission_count > 0"
            :to="{ path: `/assignment/${scope.row.id}/submissions`, query: { title: scope.row.title } }"
          >
            <el-button type="text" size="small">
              {{ scope.row.submission_count }} 人
            </el-button>
          </router-link>
          <span v-else>{{ scope.row.submission_count }} 人</span>
          <!-- --- ↑↑↑ 修改结束 ↑↑↑ --- -->
        </template>
      </el-table-column>

      <!-- 操作 列 -->
      <el-table-column align="center" label="操作" width="120">
        <template slot-scope="scope">
          <router-link :to="'/assignment/edit/'+scope.row.id">
            <el-button type="primary" size="small" icon="el-icon-edit">编辑</el-button>
          </router-link>
        </template>
      </el-table-column>

    </el-table>

    <!-- 分页 -->
    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" @pagination="getList" />

    <!-- 对话框部分已被删除 -->
  </div>
</template>

<script>
import { fetchAssignmentList } from '@/api/assignment'
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
        this.list = [] // 失败时确保 list 是空数组
        this.$message.error('加载作业列表失败')
      })
    }
  }
}
</script>
