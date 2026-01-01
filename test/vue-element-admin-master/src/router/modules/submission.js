// src/router/modules/submission.js
import Layout from '@/layout'

const submissionRouter = {
  path: '/submission',
  component: Layout,
  hidden: true, // 在侧边栏菜单中隐藏
  meta: {
    roles: ['teacher'] // 假设只有教师可以查看
  },
  children: [
    {
      path: 'detail/:id(\\d+)', // 匹配 /submission/detail/123
      component: () => import('@/views/submission/detail'), // 指向你的详情页组件
      name: 'SubmissionDetail',
      meta: {
        title: '批改作业',
        activeMenu: '/assignment/list' // 关键！让侧边栏高亮在“作业管理”
      }
    }
  ]
}

export default submissionRouter
