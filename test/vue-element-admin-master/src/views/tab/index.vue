<template>
  <div class="prompt-container">
    <div class="header-section">
      <el-tag effect="dark" type="info">已加载提示词库</el-tag>
      <el-alert
        :closable="false"
        style="width:auto;display:inline-block;vertical-align: middle;margin-left:20px;"
        title="学生可以根据下方分类选择老师预设的 AI 角色进行对话"
        type="success"
      />
    </div>

    <el-tabs v-model="activeCategory" style="margin-top:15px;" type="border-card">
      <el-tab-pane v-for="item in categoryOptions" :key="item.key" :label="item.label" :name="item.key">
        <keep-alive>
          <!-- 只有激活的分类才会渲染 TablePane -->
          <prompt-pane v-if="activeCategory==item.key" :category="item.key" />
        </keep-alive>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
import PromptPane from './components/PromptPane'

export default {
  name: 'PromptLibrary',
  components: { PromptPane },
  data() {
    return {
      // 修改分类：让提示词按领域划分
      categoryOptions: [
        { label: '全部角色', key: 'ALL' },
        { label: '语言对练', key: 'LANGUAGE' },
        { label: '编程助手', key: 'CODE' },
        { label: '学科知识', key: 'SUBJECT' },
        { label: '创意写作', key: 'WRITING' }
      ],
      activeCategory: 'ALL'
    }
  },
  watch: {
    activeCategory(val) {
      // 保持刷新后 Tab 状态不丢失
      this.$router.push(`${this.$route.path}?category=${val}`)
    }
  },
  created() {
    const category = this.$route.query.category
    if (category) {
      this.activeCategory = category
    }
  }
}
</script>

<style scoped>
.prompt-container {
  margin: 30px;
}

.header-section {
  margin-bottom: 20px;
}
</style>
