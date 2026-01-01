// src/router/modules/student.js
import Layout from '@/layout'

const studentRouter = {
  path: '/student',
  component: Layout,
  redirect: '/student/list',
  name: 'StudentManagement',
  meta: {
    title: '学生管理',
    icon: 'user',
    roles: ['teacher']
  },
  children: [
    {
      path: 'list', // <-- 必须有这个 'list' 路径
      component: () => import('@/views/student/list'), // <-- 必须指向正确的学生列表文件
      name: 'StudentList',
      meta: { title: '学生列表' }
    }
  ]
}

export default studentRouter
