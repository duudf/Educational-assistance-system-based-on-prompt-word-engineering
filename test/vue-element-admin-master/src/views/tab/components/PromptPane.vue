<template>
  <el-table :data="promptList" v-loading="loading" border fit highlight-current-row style="width: 100%">

    <!-- ID 列 -->
    <el-table-column align="center" label="编号" width="65">
      <template slot-scope="scope">
        <span>{{ scope.row.id }}</span>
      </template>
    </el-table-column>

    <!-- 角色名称 -->
    <el-table-column width="180px" align="center" label="AI 角色名称">
      <template slot-scope="{row}">
        <span style="font-weight:bold;color:#409EFF">{{ row.role_name }}</span>
        <!-- 如果是系统角色，加一个精美小标签 -->
        <el-tag v-if="row.is_system" size="mini" type="danger" effect="dark" style="margin-left:5px">官方</el-tag>
      </template>
    </el-table-column>

    <!-- 核心提示词预览 -->
    <el-table-column min-width="300px" label="提示词预览 (Prompt)">
      <template slot-scope="{row}">
        <span class="prompt-text">{{ row.content }}</span>
        <el-tag size="mini" type="info" style="margin-left:10px">{{ row.category_name }}</el-tag>
      </template>
    </el-table-column>

    <!-- 创建教师 -->
    <el-table-column width="130px" align="center" label="归属/创建者">
      <template slot-scope="{row}">
        <el-tag :type="row.is_system ? 'warning' : 'plain'" size="small">
          <i class="el-icon-user"></i> {{ row.teacher_name }}
        </el-tag>
      </template>
    </el-table-column>

    <!-- 推荐指数 -->
    <el-table-column width="120px" label="推荐指数">
      <template slot-scope="scope">
        <i v-for="n in +scope.row.importance" :key="n" class="el-icon-star-on" style="color:#F7BA2A" />
      </template>
    </el-table-column>

    <!-- 状态 -->
    <el-table-column class-name="status-col" label="状态" width="110">
      <template slot-scope="{row}">
        <el-tag :type="row.status | statusFilter">
          {{ row.status === 'active' ? '服务中' : '已禁用' }}
        </el-tag>
      </template>
    </el-table-column>

    <!-- 操作按钮 -->
    <el-table-column align="center" label="操作" width="150">
      <template slot-scope="{row}">
        <el-button
          type="primary"
          size="mini"
          round
          icon="el-icon-monitor"
          @click="handleSelect(row)"
        >
          开启练习
        </el-button>
      </template>
    </el-table-column>
  </el-table>
</template>

<script>
import { fetchRoleList } from '@/api/ai'

export default {
  filters: {
    statusFilter(status) {
      const statusMap = {
        active: 'success',
        disabled: 'info'
      }
      return statusMap[status]
    }
  },
  props: {
    category: {
      type: String,
      default: 'ALL'
    }
  },
  data() {
    return {
      promptList: [],
      loading: false
    }
  },
  // 监听分类切换，自动刷新列表
  watch: {
    category() {
      this.getPrompts()
    }
  },
  created() {
    this.getPrompts()
  },
  methods: {
    getPrompts() {
      this.loading = true
      // 调用后端真实接口
      fetchRoleList({ category: this.category }).then(response => {
        this.promptList = response.data
        this.loading = false
      }).catch(err => {
        console.error(err)
        this.loading = false
      })
    },
    handleSelect(row) {
      this.$confirm(`确认进入 [${row.role_name}] 的出题实验室吗？`, '进入练习', {
        confirmButtonText: '立即开启',
        cancelButtonText: '再看看',
        type: 'success'
      }).then(() => {
        this.$message.success(`已加载 ${row.teacher_name} 预设的 AI 环境！`)
        // 跳转到之前的 index.vue (出题练习页) 并传递角色 ID
        this.$router.push({ path: '/ai-practice/index', query: { roleId: row.id }})
      })
    }
  }
}
</script>

<style scoped>
.prompt-text {
  display: inline-block;
  max-width: 250px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  vertical-align: middle;
  color: #666;
}
/* 美化表格行高 */
.el-table .cell {
  line-height: 30px;
}
</style>
