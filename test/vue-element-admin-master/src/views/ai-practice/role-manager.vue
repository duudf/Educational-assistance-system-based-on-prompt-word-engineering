<template>
  <div class="role-manager-container">
    <!-- 顶部卡片 -->
    <div class="header-card">
      <div class="header-content">
        <div class="title-group">
          <h2 class="main-title">AI 角色提示词实验室</h2>
          <p class="sub-title">设计并部署您的个性化 AI 导师，Prompt 的质量决定了 AI 的批改深度。</p>
        </div>
        <div class="action-group">
          <el-button type="primary" icon="el-icon-plus" round @click="handleCreate">新建 AI 角色</el-button>
        </div>
      </div>
      <div class="stats-row">
        <div class="stat-item">
          <span class="label">我的角色</span>
          <span class="value">{{ roleList.length }}</span>
        </div>
        <div class="divider" />
        <div class="stat-item">
          <!-- [修改] 标签和值都改为动态的累计总次数 -->
          <span class="label">累计调用总次数</span>
          <span class="value">{{ stats.total_all_time_calls }}</span>
        </div>
      </div>
    </div>

    <!-- 表格区域 -->
    <div class="table-section">
      <el-table v-loading="loading" :data="roleList" border style="width: 100%" class="custom-table">
        <el-table-column type="expand">
          <template slot-scope="{row}">
            <div class="prompt-detail-box">
              <div class="detail-header"><i class="el-icon-document" /> 完整提示词指令</div>
              <pre class="prompt-content">{{ row.content }}</pre>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="AI 角色名称" width="220">
          <template slot-scope="{row}">
            <div class="role-name-cell">
              <span class="name-text">{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="角色定位描述" min-width="200" prop="description" />

        <!-- [修改] 新增“累计调用次数”列 -->
        <el-table-column label="累计调用次数" width="140" align="center">
          <template slot-scope="{row}">
            <span style="font-weight: bold; font-size: 16px; color: #303133;">
              {{ stats.calls_by_role[row.id] || 0 }}
            </span>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="180" align="center">
          <template slot-scope="{row}">
            <el-button type="text" icon="el-icon-edit" @click="handleEdit(row)">编辑</el-button>
            <el-button type="text" icon="el-icon-delete" style="color:#F56C6C" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 弹窗部分 (无变化) -->
    <el-dialog :title="dialogTitle" :visible.sync="dialogVisible" width="650px" append-to-body>
      <el-form ref="form" :model="form" :rules="rules" label-position="top">
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="form.name" placeholder="如：Python 资深导师" />
        </el-form-item>
        <el-form-item label="性格描述" prop="description">
          <el-input v-model="form.description" placeholder="例如：性格严谨，注重代码规范" />
        </el-form-item>
        <el-form-item label="核心 Prompt (System Role)" prop="content">
          <div slot="label" class="prompt-label-header">
            <span>核心 Prompt (System Role)</span>
            <el-popover placement="bottom-end" width="220" trigger="click">
              <div class="template-list">
                <div class="template-item" @click="handleFillTemplate('code')">💻 编程/算法批改模板</div>
                <div class="template-item" @click="handleFillTemplate('general')">📚 通用知识评分模板</div>
                <div class="template-item" @click="handleFillTemplate('language')">🗣️ 语言对练/考官模板</div>
              </div>
              <span slot="reference" class="magic-link" style="color: rgba(0,123,255,0.78);">
                <i class="el-icon-magic-stick" /> 使用专业模板填充 <i class="el-icon-arrow-down" />
              </span>
            </el-popover>
          </div>
          <el-input v-model="form.content" type="textarea" :rows="14" placeholder="请输入 AI 的指令..." />
        </el-form-item>
      </el-form>
      <div slot="footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitSave">保 存</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import request from '@/utils/request'

export default {
  data() {
    return {
      loading: false,
      roleList: [],
      dialogVisible: false,
      dialogTitle: '',
      form: { id: null, name: '', description: '', content: '' },
      // [修改] 更新 stats 数据结构以匹配新接口
      stats: {
        total_all_time_calls: 0,
        calls_by_role: {}
      },
      rules: {
        name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
        description: [{ required: true, message: '请输入性格描述', trigger: 'blur' }],
        content: [{ required: true, message: '请输入核心Prompt', trigger: 'blur' }]
      },
      templates: {
        code: `# Role: 资深技术架构师\n\n# Scoring Criteria:\n1. 逻辑实现(40分)\n2. 代码规范(30分)\n3. 性能优化(30分)\n\n# Output Format:\n请严格按照以下JSON格式返回，不要包含任何额外的解释或\`\`\`json标记:\n{\n  "grade": <0-100的整数>,\n  "feedback": "<评语文本>"\n}`,
        general: `# Role: 知识渊博的导师\n\n# Task:\n根据用户的问题和回答，进行评分和点评。\n\n# Output Format:\n请严格按照以下JSON格式返回:\n{\n  "grade": <0-100的整数>,\n  "feedback": "<评语文本>"\n}`,
        language: `# Role: 雅思考官\n\n# Task:\n模拟雅思口语考试，对用户的回答进行评估。\n\n# Scoring Criteria:\n1. Fluency and Coherence (流利度与连贯性)\n2. Lexical Resource (词汇资源)\n3. Grammatical Range and Accuracy (语法范围与准确性)\n4. Pronunciation (发音)\n\n# Output Format:\n请严格按照以下JSON格式返回:\n{\n  "grade": <1-9的小数，例如8.5>,\n  "feedback": "<综合评语和改进建议>"\n}`
      }
    }
  },
  created() {
    this.loadPageData()
  },
  methods: {
    async loadPageData() {
      this.loading = true
      try {
        // [修改] 并行请求角色列表和新的统计数据接口
        const [rolesRes, statsRes] = await Promise.all([
          request({ url: '/ai/teacher/roles', method: 'get' }),
          request({ url: '/ai/teacher/roles/stats', method: 'get' }) // 调用新接口
        ])
        this.roleList = rolesRes.data
        this.stats = statsRes.data
      } catch (error) {
        console.error('Failed to load page data:', error)
        this.$message.error('数据加载失败，请刷新页面重试')
      } finally {
        this.loading = false
      }
    },
    handleFillTemplate(type) {
      this.form.content = this.templates[type]
      document.body.click()
    },
    handleCreate() {
      this.form = { id: null, name: '', description: '', content: '' }
      this.dialogTitle = '创建新角色'
      this.dialogVisible = true
      this.$nextTick(() => { this.$refs.form.clearValidate() })
    },
    handleEdit(row) {
      this.form = { ...row }
      this.dialogTitle = '编辑角色'
      this.dialogVisible = true
      this.$nextTick(() => { this.$refs.form.clearValidate() })
    },
    submitSave() {
      this.$refs.form.validate(async(valid) => {
        if (valid) {
          const method = this.form.id ? 'put' : 'post'
          const url = this.form.id ? `/ai/teacher/roles/${this.form.id}` : '/ai/teacher/roles'
          await request({url, method, data: this.form})
          this.$message.success('保存成功')
          this.dialogVisible = false
          await this.loadPageData() // 保存后刷新所有数据
        } else {
          return false
        }
      })
    },
    async handleDelete(id) {
      try {
        await this.$confirm('删除后，使用该角色的历史批改记录将不受影响，但无法再使用此角色进行新的批改。确定要删除吗？', '警告', {type: 'warning'})
        await request({url: `/ai/teacher/roles/${id}`, method: 'delete'})
        this.$message.success('删除成功')
        await this.loadPageData() // 删除后刷新所有数据
      } catch (error) {
        if (error !== 'cancel') {
          console.error('删除失败:', error)
        }
      }
    }
  }
}
</script>

<style lang="scss" scoped>
/* 样式部分无需修改 */
.role-manager-container {
  padding: 24px;
  background-color: #f6f8fb;
  min-height: 100vh;
}

.header-card {
  background: linear-gradient(135deg, #2b32b2 0%, #1488cc 100%);
  border-radius: 12px;
  padding: 30px;
  color: #fff;
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.main-title {
  margin: 0;
  font-size: 26px;
}

.sub-title {
  margin-top: 10px;
  opacity: 0.8;
  font-size: 14px;
}

.stats-row {
  margin-top: 30px;
  display: flex;
  align-items: center;
}

.stat-item {
  .label {
    display: block;
    font-size: 12px;
    opacity: 0.7;
    margin-bottom: 4px;
  }

  .value {
    font-size: 24px;
    font-weight: bold;
  }
}

.divider {
  width: 1px;
  height: 30px;
  background: rgba(255, 255, 255, 0.2);
  margin: 0 40px;
}

.table-section {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.prompt-label-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.magic-link {
  color: #409EFF;
  cursor: pointer;
  font-size: 13px;
  font-weight: normal;
}

.role-name-cell {
  display: flex;
  align-items: center;

  .name-text {
    font-weight: 600;
    color: #303133;
  }
}

.prompt-detail-box {
  padding: 20px;
  background: #fcfcfd;
  border: 1px solid #ebf0f5;
  border-radius: 8px;
  margin: 10px;
}

.detail-header {
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 15px;
  font-size: 14px;
}

.prompt-content {
  background: #2d3436;
  color: #dfe6e9;
  padding: 15px;
  border-radius: 6px;
  font-family: monospace;
  font-size: 13px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-all;
  margin: 0;
}

.template-list {
  padding: 5px 0;
}

.template-item {
  padding: 10px 15px;
  font-size: 14px;
  cursor: pointer;
  color: #606266;

  &:hover {
    background: #f5f7fa;
    color: #409EFF;
  }
}
</style>
