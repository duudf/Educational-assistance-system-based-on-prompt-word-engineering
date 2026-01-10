<template>
  <div class="app-container ai-practice-container">
    <el-card>
      <div slot="header" class="header-container">
        <div class="header-left">
          <h3>AI 智能出题练习</h3>
          <!-- ✅ 修改点1：将角色选择移到这里，作为全局设置 -->
          <!-- ✅ 修改点：在当前AI助教后面增加跳转广场的入口 -->
<div class="global-role-selector">
  <span class="role-label"><i class="el-icon-user"></i> 当前AI助教：</span>
  <el-select v-model="currentRoleId" placeholder="选择考官/助教" size="small" style="width: 180px;">
    <el-option
      v-for="role in aiRoles"
      :key="role.id"
      :label="role.name"
      :value="role.id"
    >
      <span style="float: left">{{ role.name }}</span>
    </el-option>
  </el-select>

  <el-tooltip v-if="currentRoleDesc" :content="currentRoleDesc" placement="bottom">
    <i class="el-icon-info role-info-icon"></i>
  </el-tooltip>

  <!-- 🌟 新增：垂直分隔线和跳转链接 -->
  <el-divider direction="vertical"></el-divider>
  <router-link to="/ai-practice/discovery" class="go-discovery-link">
    <i class="el-icon-discover"></i> 导师广场
  </router-link>
</div>
        </div>

        <div>
          <router-link to="/ai-practice/favorites">
            <el-button icon="el-icon-star-on" style="margin-right: 10px;">我的收藏夹</el-button>
          </router-link>
          <el-button type="primary" icon="el-icon-magic-stick" @click="openGenerateDialog">
            生成新练习
          </el-button>
        </div>
      </div>

      <!-- 练习列表区域 -->
      <div v-loading="loading" element-loading-text="AI 正在努力出题中..." class="quiz-container">
        <div v-if="!loading && quizList.length === 0" class="empty-state">
          <p>你还没有练习记录，点击右上角的“生成新练习”按钮开始吧！</p>
        </div>

        <div v-for="(quiz, index) in quizList" :key="quiz.record_id || index" class="quiz-item">
          <h4>
            {{ index + 1 }}. <el-tag size="small" style="margin-right: 8px;">{{ quiz.type }}</el-tag> {{ quiz.question }}
            <el-tooltip :content="quiz.isFavorited ? '取消收藏' : '收藏此题'" placement="top">
              <el-button
                type="text"
                :icon="quiz.isFavorited ? 'el-icon-star-on' : 'el-icon-star-off'"
                class="favorite-btn"
                :class="{ 'is-favorited': quiz.isFavorited }"
                @click="toggleFavorite(quiz, index)"
              />
            </el-tooltip>
          </h4>

          <!-- 选项或输入框 -->
          <el-radio-group v-if="quiz.type === '选择题' && quiz.options" v-model="quiz.user_answer" class="options-group" @change="handleAnswerChange(quiz)">
            <el-radio v-for="(optionText, key) in quiz.options" :key="key" :label="key">{{ key }}. {{ optionText }}</el-radio>
          </el-radio-group>

          <el-input v-else v-model="quiz.user_answer" type="textarea" :rows="5" placeholder="在此输入你的答案" @input="handleAnswerChange(quiz)" />

          <!-- AI 批改区域 -->
          <div v-if="quiz.type !== '选择题'" class="ai-grading-section">
            <div class="grade-actions">
              <!-- ✅ 修改点2：按钮文案动态化，提示用户当前是谁在改卷 -->
              <el-button size="mini" type="primary" icon="el-icon-s-check" :loading="quiz.isGrading" @click="handleAiGrade(quiz)">
                让 {{ currentRoleName }} 批改
              </el-button>
              <span v-if="quiz.lastGradedBy" class="graded-by-tip"> (上次批改: {{ quiz.lastGradedBy }})</span>
            </div>

            <transition name="el-fade-in">
              <div v-if="quiz.ai_feedback" class="ai-feedback-box">
                <p>
                  <strong>{{ quiz.graderName || 'AI' }} 点评
                    (得分: <el-tag size="mini" :type="quiz.ai_grade > 80 ? 'success' : 'warning'">{{ quiz.ai_grade }}</el-tag>)
                  </strong>
                </p>
                <div class="feedback-content">{{ quiz.ai_feedback }}</div>
              </div>
            </transition>
          </div>

          <!-- 参考答案区域 -->
          <div class="answer-section">
            <el-button size="mini" @click="toggleAnswer(quiz)">{{ quiz.showAnswer ? '隐藏参考答案' : '查看参考答案' }}</el-button>
            <transition name="el-fade-in">
              <div v-if="quiz.showAnswer" class="answer-content">
                <p><strong>参考答案:</strong> <span :class="{'correct-answer': isCorrect(quiz)}">{{ quiz.answer }}</span></p>
                <p><strong>解析:</strong> {{ quiz.explanation }}</p>
              </div>
            </transition>
          </div>
        </div>
      </div>
    </el-card>

    <!-- AI 出题设置弹窗 (移除了角色选择，只保留课程和要求) -->
    <el-dialog title="AI 出题设置" :visible.sync="dialogVisible" width="600px" append-to-body>
      <el-form :model="form" label-width="100px">
        <el-form-item label="选择课程">
          <el-select v-model="form.course_id" placeholder="请选择一门你的课程" style="width: 100%;">
            <el-option v-for="course in courseOptions" :key="course.id" :label="course.name" :value="course.id" />
          </el-select>
        </el-form-item>

        <el-form-item label="出题要求">
          <el-input
            v-model="form.topic"
            type="textarea"
            :rows="5"
            placeholder="请输入详细的出题要求（如：考察重点、难度等级等）..."
          />
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取 消</el-button>
        <el-button type="primary" :loading="loading" @click="handleGenerate">出题</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { debounce } from 'lodash'
import request from '@/utils/request'
import { generateQuiz, favoriteQuiz, fetchPracticeHistory, gradePractice, savePracticeAnswer } from '@/api/ai'
import { fetchCourseOptions } from '@/api/course'

export default {
  name: 'AIPractice',
  data() {
    return {
      loading: false,
      dialogVisible: false,
      form: {
        course_id: null,
        topic: ''
      },
      currentRoleId: null, // ✅ 全局当前选中的角色ID
      courseOptions: [],
      aiRoles: [],
      quizList: [],
      debouncedSaveAnswer: null
    }
  },
  computed: {
    // 当前角色对象
    currentRole() {
      return this.aiRoles.find(r => r.id === this.currentRoleId) || {}
    },
    // 当前角色名称
    currentRoleName() {
      return this.currentRole.name || 'AI'
    },
    // 当前角色描述
    currentRoleDesc() {
      return this.currentRole.description || ''
    }
  },
  created() {
    this.getCourseOptions()
    this.loadLastPractice()
    this.fetchAiRoles()

    this.debouncedSaveAnswer = debounce((quiz) => {
      if (quiz && quiz.record_id && quiz.user_answer !== undefined) {
        savePracticeAnswer(quiz.record_id, { user_answer: quiz.user_answer })
          .then(() => { this.$message({ message: '答案已自动保存', type: 'success', duration: 1500 }) })
          .catch(() => { /* 忽略静默保存失败 */ })
      }
    }, 2000)
  },
  beforeDestroy() { if (this.debouncedSaveAnswer) { this.debouncedSaveAnswer.cancel() } },
  methods: {
    getCourseOptions() { fetchCourseOptions().then(response => { this.courseOptions = response.data.items }) },

    fetchAiRoles() {
      request({ url: '/ai/roles', method: 'get' }).then(res => {
        this.aiRoles = res.data
        if (this.aiRoles.length > 0) {
          this.currentRoleId = this.aiRoles[0].id // 默认选中第一个
        }
      })
    },

    loadLastPractice() {
      this.loading = true
      fetchPracticeHistory().then(response => {
        // 加载历史记录时，并没有保存当时是谁批改的，这里只展示数据
        this.quizList = response.data.map(q => ({
          ...q,
          showAnswer: false,
          isGrading: false,
          isFavorited: false,
          graderName: '历史记录' // 标记这是以前改的
        }))
        this.loading = false
      }).catch(() => { this.loading = false })
    },

    openGenerateDialog() {
      this.dialogVisible = true
    },

    handleGenerate() {
      if (!this.form.course_id || !this.form.topic.trim()) {
        this.$message.warning('请先选择课程并输入出题要求！')
        return
      }

      this.loading = true
      this.dialogVisible = false
      this.quizList = []

      const selectedCourse = this.courseOptions.find(c => c.id === this.form.course_id)

      // ✅ 生成题目时，也可以传入当前角色，让 AI 模仿该角色出题
      generateQuiz({
        course_name: selectedCourse.name,
        topic: this.form.topic,
        role_id: this.currentRoleId
      }).then(response => {
        this.quizList = response.data.map(q => ({
          ...q,
          showAnswer: false,
          isGrading: false,
          isFavorited: false,
          user_answer: ''
        }))
        this.loading = false
      }).catch(() => {
        this.loading = false
        this.$message.error('AI出题失败，请稍后重试')
      })
    },

    handleAnswerChange(quiz) { if (this.debouncedSaveAnswer) { this.debouncedSaveAnswer(quiz) } },

    handleAiGrade(quiz) {
      if (!quiz.user_answer || !quiz.user_answer.trim()) {
        this.$message.warning('请先作答，再请求批改！')
        return
      }

      if (this.debouncedSaveAnswer) { this.debouncedSaveAnswer.flush() }

      this.$set(quiz, 'isGrading', true)

      // 1. 先保存答案
      this.saveAnswerToBackend(quiz, quiz.user_answer).then(() => {
        // 2. ✅ 调用批改接口，传入当前全局选中的 role_id
        // 这样即使题目没变，只要切换了下拉框，评分结果就会变
        gradePractice(quiz.record_id, {
          user_answer: quiz.user_answer,
          role_id: this.currentRoleId // 关键：使用当前选中的角色
        }).then(response => {
          const { grade, feedback } = response.data

          this.$set(quiz, 'ai_grade', grade)
          this.$set(quiz, 'ai_feedback', feedback)
          this.$set(quiz, 'isGrading', false)

          // 记录这次是被谁批改的，方便UI展示
          this.$set(quiz, 'graderName', this.currentRoleName)
          this.$set(quiz, 'lastGradedBy', this.currentRoleName)

          this.$message.success(`${this.currentRoleName} 已完成批改！`)
        }).catch(() => { this.$set(quiz, 'isGrading', false) })
      })
    },

    saveAnswerToBackend(quiz, answer) { return savePracticeAnswer(quiz.record_id, { user_answer: answer }) },

    toggleFavorite(quiz, index) {
      const isNowFavorited = !quiz.isFavorited
      const action = isNowFavorited ? 'add' : 'remove'
      const quizDataForApi = { ...quiz }

      delete quizDataForApi.showAnswer; delete quizDataForApi.isFavorited; delete quizDataForApi.isGrading
      delete quizDataForApi.user_answer; delete quizDataForApi.ai_grade; delete quizDataForApi.ai_feedback
      delete quizDataForApi.graderName; delete quizDataForApi.lastGradedBy

      favoriteQuiz({
        action,
        quiz_data: quizDataForApi,
        user_answer: quiz.user_answer
      }).then((response) => {
        this.$set(this.quizList[index], 'isFavorited', isNowFavorited)
        this.$message.success(response.message || (isNowFavorited ? '收藏成功！' : '已取消收藏。'))
      }).catch(() => { this.$message.error('操作失败，请稍后重试') })
    },

    toggleAnswer(quiz) { this.$set(quiz, 'showAnswer', !quiz.showAnswer) },

    isCorrect(quiz) {
      if (quiz.type === '选择题' && quiz.showAnswer) {
        return String(quiz.answer).trim().toLowerCase() === String(quiz.user_answer).trim().toLowerCase()
      }
      return false
    }
  }
}
</script>

<style scoped>
.ai-practice-container { position: relative; }

.header-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.header-left {
  display: flex;
  align-items: center;
}
.header-left h3 {
  margin-right: 20px;
  margin-bottom: 0;
}
/* 角色选择器样式优化 */
.global-role-selector {
  display: flex;
  align-items: center;
  background-color: #f5f7fa;
  padding: 5px 12px;
  border-radius: 20px;
  border: 1px solid #e4e7ed;
}

.role-label {
  font-size: 13px;
  color: #606266;
  margin-right: 8px;
  font-weight: 500;
}

.role-info-icon {
  margin-left: 8px;
  color: #909399;
  cursor: pointer;
  font-size: 16px;
}

.role-info-icon:hover {
  color: #409EFF;
}

/* 🌟 新增：跳转广场链接的样式 */
.go-discovery-link {
  font-size: 13px;
  color: #409EFF;
  text-decoration: none;
  margin-left: 5px;
  display: flex;
  align-items: center;
  transition: all 0.3s;
  padding: 2px 5px;
  border-radius: 4px;
}

.go-discovery-link i {
  margin-right: 4px;
  font-size: 15px;
}

.go-discovery-link:hover {
  background-color: #ecf5ff;
  color: #66b1ff;
}

/* 调整分割线间距 */
.el-divider--vertical {
  margin: 0 10px;
  background-color: #dcdfe6;
}
/* 角色选择器样式 */
.global-role-selector {
  display: flex;
  align-items: center;
  background-color: #f5f7fa;
  padding: 5px 15px;
  border-radius: 20px;
  border: 1px solid #e4e7ed;
}
.role-label {
  font-size: 14px;
  color: #606266;
  margin-right: 10px;
  font-weight: 500;
}
.role-info-icon {
  margin-left: 8px;
  color: #909399;
  cursor: pointer;
}

.quiz-container { min-height: 300px; margin-top: 20px; }
.empty-state { text-align: center; color: #909399; padding: 40px 0; line-height: 1.8; font-size: 14px; }
.quiz-item { margin-bottom: 30px; padding-bottom: 20px; border-bottom: 1px solid #EBEEF5; }
.quiz-item h4 { display: flex; align-items: center; margin-bottom: 15px; line-height: 1.5; }

.favorite-btn { margin-left: auto; font-size: 20px; color: #c0c4cc; padding: 0 10px; }
.favorite-btn.is-favorited { color: #E6A23C; }

.options-group { display: block; margin-top: 10px; }
.el-radio { display: block; margin: 10px 0; }

.ai-grading-section { margin-top: 15px; }
.grade-actions { display: flex; align-items: center; }
.graded-by-tip { margin-left: 10px; font-size: 12px; color: #909399; }

.ai-feedback-box { margin-top: 10px; padding: 15px; background-color: #f0f9eb; border-radius: 4px; border-left: 4px solid #67C23A; }
.ai-feedback-box .feedback-content { white-space: pre-wrap; word-break: break-all; margin-top: 5px; }

.answer-section { margin-top: 15px; }
.answer-content { margin-top: 10px; padding: 15px; background-color: #f9f9f9; border-radius: 4px; font-size: 14px; border-left: 4px solid #409EFF; line-height: 1.6; }
.answer-content p { margin: 8px 0; }
.correct-answer { color: #67C23A; font-weight: bold; }
</style>
