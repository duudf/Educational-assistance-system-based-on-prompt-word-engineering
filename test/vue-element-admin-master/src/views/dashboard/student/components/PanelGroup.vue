<template>
  <el-row :gutter="40" class="panel-group">

    <!-- 1. 我的课程 (lg由8改为6) -->
    <el-col :xs="12" :sm="12" :lg="6" class="card-panel-col">
      <div class="card-panel" @click="handlePanelClick('my-courses')">
        <div class="card-panel-icon-wrapper icon-course">
          <svg-icon icon-class="education" class-name="card-panel-icon" />
        </div>
        <div class="card-panel-description">
          <div class="card-panel-text">我的课程</div>
          <count-to :start-val="0" :end-val="statsData.courseCount" :duration="2600" class="card-panel-num" />
        </div>
      </div>
    </el-col>

    <!-- 2. 待完成作业 (lg由8改为6) -->
    <el-col :xs="12" :sm="12" :lg="6" class="card-panel-col">
      <div class="card-panel" @click="handlePanelClick('pending-assignments')">
        <div class="card-panel-icon-wrapper icon-pending">
          <svg-icon icon-class="list" class-name="card-panel-icon" />
        </div>
        <div class="card-panel-description">
          <div class="card-panel-text">待完成作业</div>
          <count-to :start-val="0" :end-val="statsData.pendingCount" :duration="3000" class="card-panel-num" />
        </div>
      </div>
    </el-col>

    <!-- 3. 已提交作业 (lg由8改为6) -->
    <el-col :xs="12" :sm="12" :lg="6" class="card-panel-col">
      <div class="card-panel" @click="handlePanelClick('submitted-assignments')">
        <div class="card-panel-icon-wrapper icon-submitted">
          <svg-icon icon-class="skill" class-name="card-panel-icon" />
        </div>
        <div class="card-panel-description">
          <div class="card-panel-text">已提交作业</div>
          <count-to :start-val="0" :end-val="statsData.submittedCount" :duration="3200" class="card-panel-num" />
        </div>
      </div>
    </el-col>

    <!-- 4. 【新增】AI 练习 (新增卡片) -->
    <el-col :xs="12" :sm="12" :lg="6" class="card-panel-col">
      <div class="card-panel" @click="handlePanelClick('ai-practices')">
        <div class="card-panel-icon-wrapper icon-ai">
          <!-- 找个图标，比如 form 或 edit -->
          <svg-icon icon-class="form" class-name="card-panel-icon" />
        </div>
        <div class="card-panel-description">
          <div class="card-panel-text">AI 练习次数</div>
          <!-- 绑定新字段 aiPracticeCount -->
          <count-to :start-val="0" :end-val="statsData.aiPracticeCount" :duration="3600" class="card-panel-num" />
        </div>
      </div>
    </el-col>

  </el-row>
</template>

<script>
import CountTo from 'vue-count-to'
// import { getDashboardData } from '@/api/dashboard' // 暂时注释原API，防止路径不对
import request from '@/utils/request' // 直接引入request工具，确保能连上Python

export default {
  name: 'StudentPanelGroup',
  components: {
    CountTo
  },
  data() {
    return {
      statsData: {
        courseCount: 0,
        pendingCount: 0,
        submittedCount: 0,
        aiPracticeCount: 0 // 新增字段
      }
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    fetchData() {
      // 直接请求后端的 Python 接口，解决连不上的问题
      request({
        url: '/ai/dashboard/analysis',
        method: 'get'
      }).then(response => {
        const data = response.data.card_data; // 注意这里取 card_data

        this.statsData = {
          courseCount: data.courseCount,
          pendingCount: data.pendingCount,
          submittedCount: data.submittedCount,
          aiPracticeCount: data.total_practices // 把后端返回的AI数据赋值过来
        };
      }).catch(err => {
        console.error("获取面板数据失败:", err);
      });
    },
    handlePanelClick(type) {
      this.$emit('panel-click', type)
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
      .icon-course { background: #40c9c6; }
      .icon-pending { background: #f4516c; }
      .icon-submitted { background: #36a3f7; }
      .icon-ai { background: #8e44ad; } /* 新增悬停颜色 */
    }

    .icon-course { color: #40c9c6; }
    .icon-pending { color: #f4516c; }
    .icon-submitted { color: #36a3f7; }
    .icon-ai { color: #8e44ad; } /* 新增图标颜色 */

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
