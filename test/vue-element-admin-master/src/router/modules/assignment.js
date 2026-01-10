// src/router/modules/assignment.js
import Layout from '@/layout'

const assignmentRouter = {
  path: '/assignment',
  component: Layout,
  redirect: '/assignment/list',
  name: 'AssignmentManagement',
  meta: { title: '作业管理', icon: 'form', roles: ['student', 'teacher', 'admin'] },
  children: [
    {
      path: 'list',
      component: () => import('@/views/assignment/list'),
      name: 'AssignmentList',
      meta: { title: '作业列表', roles: ['teacher', 'admin'] }
    },
    {
      path: 'create',
      component: () => import('@/views/assignment/create'),
      name: 'CreateAssignment',
      meta: { title: '发布新作业', roles: ['teacher', 'admin'] }
    },
    {
      path: 'edit/:id(\\d+)',
      component: () => import('@/views/assignment/edit'),
      name: 'EditAssignment',
      meta: { title: '编辑作业', noCache: true, roles: ['teacher', 'admin'] }, // <-- 删除了 activeMenu
      hidden: true
    },
    {
      path: ':id(\\d+)/submissions',
      component: () => import('@/views/assignment/submissionList'),
      name: 'SubmissionList',
      meta: { title: '作业提交列表', roles: ['teacher', 'admin'] },
      hidden: true
    },
    // --- ↓↓↓ 为学生新增的路由 ↓↓↓ ---
    {
      path: 'my-assignments',
      component: () => import('@/views/assignment/my-assignments'),
      name: 'MyAssignments',
      meta: { title: '我的作业', roles: ['student'], noCache: true }
    },

    {
      path: 'submit/:id(\\d+)',
      component: () => import('@/views/assignment/submit'),
      name: 'SubmitAssignment',
      meta: { title: '提交作业', roles: ['student'], activeMenu: '/assignment/my-assignments' },
      hidden: true
    }
  ]
}

export default assignmentRouter
