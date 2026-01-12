<template>
  <div class="app-container">
    <el-card>
      <div slot="header">
        <h3>我的收藏夹</h3>
      </div>

      <div v-loading="loading" class="quiz-container">
        <!-- 空状态展示 -->
        <div v-if="!loading && favoriteList.length === 0" class="empty-state">
          <p>你的收藏夹是空的。</p>
          <p>快去“智能出题练习”页面，点击题目旁边的星星 ☆ 收藏你喜欢的题目吧！</p>
        </div>

        <!-- 收藏列表 -->
        <div v-for="(quiz, index) in favoriteList" :key="quiz.id || index" class="quiz-item">
          <div class="quiz-header">
            <!-- ✅ 核心修改点：去掉了 .quiz_data 前缀 -->
            <h4>
              {{ index + 1 }}.
              <el-tag size="small">{{ quiz.type }}</el-tag>
              {{ quiz.question }}
            </h4>
            <!-- 取消收藏按钮 -->
            <el-button
              type="danger"
              icon="el-icon-delete"
              size="mini"
              circle
              plain
              title="取消收藏"
              @click="handleRemoveFavorite(quiz, index)"
            />
          </div>

          <!-- 用户当时作答的答案 -->
          <!-- ✅ 核心修改点：去掉了 .quiz_data 前缀 -->
          <!-- 选择题 -->
          <el-radio-group v-if="quiz.type === '选择题' && quiz.options" v-model="quiz.user_answer" class="options-group" disabled>
            <el-radio v-for="(optionText, key) in quiz.options" :key="key" :label="key">{{ key }}. {{ optionText }}</el-radio>
          </el-radio-group>
          <!-- 简答/编程题 -->
          <el-input v-else v-model="quiz.user_answer" type="textarea" :rows="4" placeholder="你当时作答的答案" disabled />

          <!-- 标准答案与解析 -->
          <div class="answer-section">
            <div class="answer-content">
              <!-- ✅ 核心修改点：去掉了 .quiz_data 前缀 -->
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
import { fetchFavorites, favoriteQuiz } from '@/api/ai'

export default {
  name: 'MyFavorites',
  data() {
    return {
      loading: true,
      favoriteList: []
    }
  },
  created() {
    this.getFavoriteList()
  },
  methods: {
    // 获取收藏列表
    getFavoriteList() {
      this.loading = true
      fetchFavorites().then(response => {
        // 在这里打印数据，可以帮助你确认后端返回的真实结构
        console.log('Fetched favorites data:', response.data.items)
        this.favoriteList = response.data.items
        this.loading = false
      }).catch(() => {
        this.loading = false
        this.$message.error('加载收藏列表失败，请稍后重试')
      })
    },

    // 处理取消收藏的操作
    handleRemoveFavorite(quiz, index) {
      this.$confirm('确定要从收藏夹中移除这道题吗?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        // ✅ 核心修改点：为了与AIPractice.vue保持一致，将整个quiz对象作为quiz_data传递
        // 后端可以从这个对象中提取需要的字段
        const quizDataForApi = { ...quiz }
        // 清理掉不必要的前端状态字段
        delete quizDataForApi.isFavorited // 如果有的话

        const params = {
          action: 'remove',
          quiz_data: quizDataForApi
        }

        favoriteQuiz(params).then(() => {
          this.favoriteList.splice(index, 1)
          this.$message({
            type: 'success',
            message: '取消收藏成功!'
          })
        }).catch(() => {
          this.$message.error('操作失败，请稍后重试')
        })
      }).catch(() => {
        // 用户点击了“取消”
      })
    }
  }
}
</script>

<style scoped>
/* 样式部分无需修改 */
.empty-state {
  text-align: center;
  color: #909399;
  padding: 40px 0;
  line-height: 1.8;
  font-size: 14px;
}
.quiz-item {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #EBEEF5;
}
.quiz-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}
.quiz-header h4 {
  margin: 0;
  padding-right: 15px;
  line-height: 1.5;
  flex-grow: 1;
}
.options-group {
  display: block;
  margin-top: 10px;
}
.el-radio {
  display: block;
  margin: 10px 0;
}
.answer-section {
  margin-top: 15px;
}
.answer-content {
  margin-top: 10px;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 4px;
  font-size: 14px;
  border-left: 4px solid #67C23A;
}
.answer-content p {
  margin: 8px 0;
}
.correct-answer {
  color: #67C23A;
  font-weight: bold;
}
</style>
