<template>
  <div class="dashboard-container">
    <!--
      动态组件 <component> 会根据 is 绑定的值来渲染对应的组件。
      如果 currentDashboardComponent 是 'TeacherDashboard'，则渲染 <teacher-dashboard />
      如果 currentDashboardComponent 是 'StudentDashboard'，则渲染 <student-dashboard />
    -->
    <component :is="currentDashboardComponent" />
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
// 1. 导入我们新的、路径正确的教师和学生仪表盘组件
import TeacherDashboard from './teacher/index.vue'
import StudentDashboard from './student/index.vue'

export default {
  name: 'Dashboard',
  // 2. 注册组件，使用清晰的组件名
  components: {
    TeacherDashboard,
    StudentDashboard
  },
  data() {
    return {
      // 用于控制当前显示哪个仪表盘组件的变量
      currentDashboardComponent: '' // 初始为空，由 created() 钩子决定
    }
  },
  computed: {
    // 从 Vuex store 中获取用户的角色信息
    ...mapGetters([
      'roles'
    ])
  },
  // 3. 在组件创建时，使用正确的逻辑来判断和切换组件
  created() {
    // 检查用户的角色数组中是否包含 'teacher'
    if (this.roles.includes('teacher')) {
      // 如果是教师，设置要显示的组件为 'TeacherDashboard'
      this.currentDashboardComponent = 'TeacherDashboard'
    } else {
      // 否则 (角色为 'student' 或其他)，设置要显示的组件为 'StudentDashboard'
      this.currentDashboardComponent = 'StudentDashboard'
    }
  }
}
</script>
