<template>
  <el-table :data="list" v-loading="loading" class="modern-table">
    <!-- 角色名称 -->
    <el-table-column label="角色信息" width="240">
      <template slot-scope="{row}">
        <div class="role-cell">
          <div class="role-avatar">{{ row.name.charAt(0) }}</div>
          <div class="role-meta">
            <div class="role-name">{{ row.name }}</div>
            <div class="role-desc">{{ row.description }}</div>
          </div>
        </div>
      </template>
    </el-table-column>

    <!-- 提示词预览：设计成代码块风格 -->
    <el-table-column label="核心提示词 (System Prompt)">
      <template slot-scope="{row}">
        <div class="prompt-preview-box">
          <code>{{ row.content }}</code>
        </div>
      </template>
    </el-table-column>

    <!-- 统计 -->
    <el-table-column label="使用频率" width="120" align="center">
      <template slot-scope="{row}">
        <span class="use-count"><i class="el-icon-data-line"></i> {{ row.useCount || 0 }}次</span>
      </template>
    </el-table-column>

    <!-- 操作 -->
    <el-table-column label="管理" width="150" align="center">
      <template slot-scope="{row}">
        <el-button-group>
          <el-button size="mini" icon="el-icon-edit" @click="$emit('edit', row)"></el-button>
          <el-button size="mini" type="danger" icon="el-icon-delete" @click="handleDelete(row.id)"></el-button>
        </el-button-group>
      </template>
    </el-table-column>
  </el-table>
</template>

<style lang="scss" scoped>
.modern-table {
  .role-cell {
    display: flex;
    align-items: center;
    .role-avatar {
      width: 36px;
      height: 36px;
      background: #ecf5ff;
      color: #409EFF;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: bold;
      margin-right: 12px;
    }
    .role-name {
      font-weight: bold;
      color: #303133;
    }
    .role-desc {
      font-size: 12px;
      color: #909399;
      margin-top: 4px;
    }
  }

  .prompt-preview-box {
    background: #f8f9fa;
    padding: 8px 12px;
    border-radius: 4px;
    border: 1px solid #e9ecef;
    code {
      font-family: 'Monaco', 'Menlo', monospace;
      font-size: 12px;
      color: #666;
      display: -webkit-box;
      -webkit-box-orient: vertical;
      -webkit-line-clamp: 2;
      overflow: hidden;
    }
  }

  .use-count {
    font-size: 13px;
    color: #67C23A;
  }
}
</style>
