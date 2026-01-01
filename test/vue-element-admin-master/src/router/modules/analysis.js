import Layout from '@/layout'

const analysisRouter = {
  path: '/analysis',
  component: Layout,
  hidden: true, // 在菜单中隐藏，因为它通常是从其他页面跳转过来的
  meta: {
    roles: ['teacher'] // 只有教师可以访问
  },
  children: [
    {
      path: 'student/:id(\\d+)',
      component: () => import('@/views/analysis/index'),
      name: 'StudentAnalysis',
      meta: { title: '学生学习分析报告', noCache: true, activeMenu: '/course/list' }
    }
  ]
}

export default analysisRouter
