<template>
  <el-row :gutter="40" class="panel-group">
    <!-- 我的课程 面板 -->
    <el-col :xs="12" :sm="12" :lg="8" class="card-panel-col">
      <div class="card-panel" @click="handlePanelClick('my-courses')">
        <div class="card-panel-icon-wrapper icon-course">
          <svg-icon icon-class="education" class-name="card-panel-icon" />
        </div>
        <div class="card-panel-description">
          <div class="card-panel-text">
            我的课程
          </div>
          <count-to :start-val="0" :end-val="statsData.courseCount" :duration="2600" class="card-panel-num" />
        </div>
      </div>
    </el-col>

    <!-- 待完成作业 面板 -->
    <el-col :xs="12" :sm="12" :lg="8" class="card-panel-col">
      <div class="card-panel" @click="handlePanelClick('pending-assignments')">
        <div class="card-panel-icon-wrapper icon-pending">
          <svg-icon icon-class="list" class-name="card-panel-icon" />
        </div>
        <div class="card-panel-description">
          <div class="card-panel-text">
            待完成作业
          </div>
          <count-to :start-val="0" :end-val="statsData.pendingCount" :duration="3000" class="card-panel-num" />
        </div>
      </div>
    </el-col>

    <!-- 已提交作业 面板 -->
    <el-col :xs="12" :sm="12" :lg="8" class="card-panel-col">
      <div class="card-panel" @click="handlePanelClick('submitted-assignments')">
        <div class="card-panel-icon-wrapper icon-submitted">
          <svg-icon icon-class="skill" class-name="card-panel-icon" />
        </div>
        <div class="card-panel-description">
          <div class="card-panel-text">
            已提交作业
          </div>
          <count-to :start-val="0" :end-val="statsData.submittedCount" :duration="3200" class="card-panel-num" />
        </div>
      </div>
    </el-col>

  </el-row>
</template>

<script>
import CountTo from 'vue-count-to'
import { getDashboardData } from '@/api/dashboard' // 复用同一个API

export default {
  name: 'StudentPanelGroup', // 给学生版组件一个不同的名字
  components: {
    CountTo
  },
  data() {
    return {
      statsData: {
        courseCount: 0,
        pendingCount: 0,
        submittedCount: 0
      }
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    fetchData() {
      getDashboardData().then(response => {
        const data = response.data;
        // 使用后端为学生角色返回的数据
        this.statsData = {
          courseCount: data.courseCount,
          pendingCount: data.pendingCount,
          submittedCount: data.submittedCount
        };
      }).catch(err => {
        console.error("在学生面板中获取数据失败:", err);
      });
    },
    handlePanelClick(type) {
      // 触发事件，方便父组件进行页面跳转等操作
      this.$emit('panel-click', type)
    }
  }
}
</script>

<style lang="scss" scoped>
/* 样式大部分可以复用，只修改图标颜色部分 */
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
      .icon-course {
        background: #40c9c6;
      }
      .icon-pending {
        background: #f4516c;
      }
      .icon-submitted {
        background: #36a3f7;
      }
    }

    .icon-course {
      color: #40c9c6;
    }
    .icon-pending {
      color: #f4516c;
    }
    .icon-submitted {
      color: #36a3f7;
    }

    /* 以下是通用样式 */
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
