import Layout from '@/layout'

const studentRouter = {
  path: '/student',
  component: Layout,
  redirect: '/student/list',
  name: 'StudentManagement',
  meta: {
    title: '学生管理',
    icon: 'user',
    roles: ['teacher'] // 仅教师可见
  },
  children: [
    {
      path: 'list',
      component: () => import('@/views/student/list'),
      name: 'StudentList',
      meta: { title: '学生列表' }
    },
    // --- ↓↓↓ 新增：学生详情页路由 ↓↓↓ ---
    {
      path: 'profile/:id(\\d+)', // 匹配 /student/profile/123 这样的路径
      component: () => import('@/views/student/profile'), // 指向我们新创建的详情页组件
      name: 'StudentProfile',
      meta: {
        title: '学生详情',
        activeMenu: '/student/list' // 确保侧边栏在“学生管理”菜单上保持高亮
      },
      hidden: true // 在侧边栏菜单中隐藏此项，因为它总是从列表页进入
    }
    // --- ↑↑↑ 新增结束 ↑↑↑ ---
  ]
}

export default studentRouter
