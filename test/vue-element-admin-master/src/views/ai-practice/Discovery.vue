<template>
  <div class="prompt-pane-container">
    <el-table
      v-loading="loading"
      :data="promptList"
      border
      fit
      highlight-current-row
      style="width: 100%"
      :header-cell-style="{background:'#f5f7fa', color:'#606266', textAlign:'center'}"
    >
      <!-- 1. 编号 (居中) -->
      <el-table-column align="center" label="编号" width="80">
        <template slot-scope="scope">
          <span>{{ scope.row.id }}</span>
        </template>
      </el-table-column>

      <!-- 2. AI 角色名称 (左对齐) -->
      <el-table-column label="AI 角色名称" width="220">
        <template slot-scope="{row}">
          <span style="font-weight:bold; color:#409EFF">{{ row.name }}</span>
        </template>
      </el-table-column>

      <!-- 3. 角色描述 (左对齐) -->
      <el-table-column label="角色描述预览" min-width="200">
        <template slot-scope="{row}">
          <span class="description-text">{{ row.description }}</span>
        </template>
      </el-table-column>

      <!-- 4. 提示词预览 (核心修改：增加 popper-class 并在下方 slot 定义内容) -->
      <el-table-column label="提示词预览 (Prompt Content)" min-width="300">
        <template slot-scope="{row}">
          <!-- 增加 popper-class，并将内容放到 slot="content" 里以支持复杂样式 -->
          <el-tooltip placement="top" effect="dark" popper-class="at-prompt-tooltip">
            <div slot="content" class="tooltip-inner-content">
              {{ row.content }}
            </div>
            <span class="prompt-preview">{{ row.content }}</span>
          </el-tooltip>
        </template>
      </el-table-column>

      <!-- 5. 归属/创建者 (居中) -->
      <el-table-column align="center" label="归属/创建者" width="160">
        <template slot-scope="{row}">
          <el-tag :type="row.is_system ? 'warning' : 'info'" size="small" plain>
            <i class="el-icon-user"></i> {{ row.creator }}
          </el-tag>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
import { fetchRoleList } from '@/api/ai'

export default {
  name: 'PromptPane',
  data() {
    return {
      promptList: [],
      loading: false
    }
  },
  created() {
    this.getPrompts()
  },
  methods: {
    getPrompts() {
      this.loading = true
      fetchRoleList().then(response => {
        this.promptList = response.data
        this.loading = false
      }).catch(() => {
        this.loading = false
      })
    }
  }
}
</script>

<style scoped>
/* 限制描述文本，防止撑开表格 */
.description-text {
  color: #606266;
  font-size: 13px;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 1;
  overflow: hidden;
}

/* 限制 Prompt 预览，超出显示省略号 */
.prompt-preview {
  display: inline-block;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #909399;
  font-family: monospace;
  cursor: help;
}

.prompt-pane-container {
  padding: 10px 0;
}
</style>

<!-- 注意：这里新开一个 style，且不要加 scoped，否则样式无法作用到 body 下的 tooltip -->
<style lang="css">
.at-prompt-tooltip {
  max-width: 600px !important; /* 限制最大宽度，防止飞出屏幕 */
}
.tooltip-inner-content {
  line-height: 1.6;
  word-break: break-all;     /* 强制长文本换行 */
  white-space: pre-wrap;     /* 保留换行符 */
  font-size: 13px;
}
</style>
