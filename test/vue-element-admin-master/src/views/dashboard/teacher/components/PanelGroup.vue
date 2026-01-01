<template>
  <el-row :gutter="40" class="panel-group">
    <!-- 学生总数 面板 -->
    <el-col :xs="12" :sm="12" :lg="6" class="card-panel-col">
      <div class="card-panel" @click="handlePanelClick('students')">
        <div class="card-panel-icon-wrapper icon-people">
          <svg-icon icon-class="peoples" class-name="card-panel-icon" />
        </div>
        <div class="card-panel-description">
          <div class="card-panel-text">
            学生总数
          </div>
          <count-to :start-val="0" :end-val="statsData.studentCount" :duration="2600" class="card-panel-num" />
        </div>
      </div>
    </el-col>

    <!-- 课程数量 面板 -->
    <el-col :xs="12" :sm="12" :lg="6" class="card-panel-col">
      <div class="card-panel" @click="handlePanelClick('courses')">
        <div class="card-panel-icon-wrapper icon-course">
          <svg-icon icon-class="education" class-name="card-panel-icon" />
        </div>
        <div class="card-panel-description">
          <div class="card-panel-text">
            课程数量
          </div>
          <count-to :start-val="0" :end-val="statsData.courseCount" :duration="3000" class="card-panel-num" />
        </div>
      </div>
    </el-col>

    <!-- 提示词库 面板 -->
    <el-col :xs="12" :sm="12" :lg="6" class="card-panel-col">
      <div class="card-panel" @click="handlePanelClick('prompts')">
        <div class="card-panel-icon-wrapper icon-prompt">
          <svg-icon icon-class="clipboard" class-name="card-panel-icon" />
        </div>
        <div class="card-panel-description">
          <div class="card-panel-text">
            提示词库
          </div>
          <count-to :start-val="0" :end-val="statsData.promptCount" :duration="3200" class="card-panel-num" />
        </div>
      </div>
    </el-col>

    <!-- 待批改作业 面板 -->
    <el-col :xs="12" :sm="12" :lg="6" class="card-panel-col">
      <div class="card-panel" @click="handlePanelClick('reviews')">
        <div class="card-panel-icon-wrapper icon-review">
          <svg-icon icon-class="form" class-name="card-panel-icon" />
        </div>
        <div class="card-panel-description">
          <div class="card-panel-text">
            待批改作业
          </div>
          <count-to :start-val="0" :end-val="statsData.reviewCount" :duration="3600" class="card-panel-num" />
        </div>
      </div>
    </el-col>
  </el-row>
</template>

<script>
import CountTo from 'vue-count-to'
// 导入封装好的后端请求方法
import { getDashboardData } from '@/api/dashboard'

export default {
  name: 'PanelGroup',
  components: {
    CountTo
  },
  data() {
    return {
      statsData: {
        studentCount: 0,
        courseCount: 0,
        promptCount: 0,
        reviewCount: 0
      },
      recentAssignments: [] // 接收后端返回的最近作业列表
    }
  },
  // ✅ 核心修改：全部场景都用 mounted，子组件必用这个钩子请求数据
  mounted() {
    this.fetchData() // 直接执行请求，父组件会兜底调用
  },
  methods: {
    // 获取看板数据，请求你的Flask后端 /dashboard/data
    async fetchData() {
      try {
        console.log('✅ 开始请求后端 /dashboard/data 接口')
        const res = await getDashboardData()
        const data = res.data
        // 赋值后端返回的真实数据
        this.statsData = {
          studentCount: data.studentCount,
          courseCount: data.courseCount,
          promptCount: data.promptCount,
          reviewCount: data.reviewCount
        }
        this.recentAssignments = data.recent_assignments || []
        console.log('✅ 后端数据请求成功：', this.statsData)
      } catch (err) {
        console.error('❌ 获取看板数据失败：', err)
        // 请求失败兜底，避免页面显示NaN
        this.statsData = {
          studentCount: 0,
          courseCount: 0,
          promptCount: 0,
          reviewCount: 0
        }
      }
    },
    // ✅ 修复事件名：和父组件监听的事件名完全一致，折线图切换生效
    handlePanelClick(type) {
      this.$emit('handleSetLineChartData', type)
    }
  }
}
</script>

<style lang="scss" scoped>
.panel-group {
  margin-top: 18px;

  .card-panel-col {
    margin-bottom: 32px;
  }

  .card-panel {
    height: 108px;
    cursor: pointer;
    font-size: 12px;
    position: relative;
    overflow: hidden;
    color: #666;
    background: #fff;
    box-shadow: 4px 4px 40px rgba(0, 0, 0, .05);
    border-color: rgba(0, 0, 0, .05);

    &:hover {
      .card-panel-icon-wrapper {
        color: #fff;
      }
      .icon-people {
        background: #40c9c6;
      }
      .icon-course {
        background: #36a3f7;
      }
      .icon-prompt {
        background: #f4516c;
      }
      .icon-review {
        background: #34bfa3
      }
    }

    .icon-people {
      color: #40c9c6;
    }
    .icon-course {
      color: #36a3f7;
    }
    .icon-prompt {
      color: #f4516c;
    }
    .icon-review {
      color: #34bfa3
    }

    .card-panel-icon-wrapper {
      float: left;
      margin: 14px 0 0 14px;
      padding: 16px;
      transition: all 0.38s ease-out;
      border-radius: 6px;
    }

    .card-panel-icon {
      float: left;
      font-size: 48px;
    }

    .card-panel-description {
      float: right;
      font-weight: bold;
      margin: 26px;
      margin-left: 0px;

      .card-panel-text {
        line-height: 18px;
        color: rgba(0, 0, 0, 0.45);
        font-size: 16px;
        margin-bottom: 12px;
      }

      .card-panel-num {
        font-size: 20px;
      }
    }
  }
}
</style>
