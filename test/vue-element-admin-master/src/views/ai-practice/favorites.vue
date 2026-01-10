<template>
  <div class="app-container">
    <el-card>
      <div slot="header">
        <h3>我的收藏夹</h3>
      </div>

      <div v-loading="loading" class="quiz-container">
        <div v-if="!loading && favoriteList.length === 0" class="empty-state">
          <p>你的收藏夹是空的。</p>
          <p>快去“智能出题练习”页面，点击题目旁边的星星 ☆ 收藏你喜欢的题目吧！</p>
        </div>

        <div v-for="(quiz, index) in favoriteList" :key="index" class="quiz-item">
          <h4>{{ index + 1 }}. <el-tag size="small">{{ quiz.type }}</el-tag> {{ quiz.question }}</h4>

          <!-- 选择题选项 -->
          <el-radio-group v-if="quiz.type === '选择题' && quiz.options" v-model="userAnswers[index]" class="options-group" disabled>
            <el-radio v-for="(optionText, key) in quiz.options" :key="key" :label="key">{{ key }}. {{ optionText }}</el-radio>
          </el-radio-group>

          <!-- 简答题/编程题输入框 -->
          <el-input v-else v-model="userAnswers[index]" type="textarea" :rows="4" placeholder="在此输入你的答案" disabled />

          <!-- 答案 -->
          <div class="answer-section">
            <div class="answer-content">
              <p><strong>参考答案:</strong> <span class="correct-answer">{{ quiz.answer }}</span></p>
              <p><strong>解析:</strong> {{ quiz.explanation }}</p>
            </div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
import { fetchFavorites } from '@/api/ai'

export default {
  name: 'MyFavorites',
  data() {
    return {
      loading: true,
      favoriteList: [],
      userAnswers: {} // 在收藏夹页面，这个只是为了展示，可以保持为空
    }
  },
  created() {
    this.fetchList()
  },
  methods: {
    fetchList() {
      this.loading = true
      fetchFavorites().then(response => {
        this.favoriteList = response.data.items
        this.loading = false
      }).catch(() => {
        this.loading = false
        this.$message.error('加载收藏列表失败')
      })
    }
  }
}
</script>

<style scoped>
/* 复用 ai-practice/index.vue 的样式 */
.empty-state { text-align: center; color: #909399; padding: 40px 0; line-height: 1.8; font-size: 14px; }
.quiz-item { margin-bottom: 30px; padding-bottom: 20px; border-bottom: 1px solid #EBEEF5; }
.options-group { display: block; margin-top: 10px; }
.el-radio { display: block; margin: 10px 0; }
.answer-section { margin-top: 15px; }
.answer-content { margin-top: 10px; padding: 15px; background-color: #f9f9f9; border-radius: 4px; font-size: 14px; border-left: 4px solid #67C23A; }
.answer-content p { margin: 8px 0; }
.correct-answer { color: #67C23A; font-weight: bold; }
</style>
