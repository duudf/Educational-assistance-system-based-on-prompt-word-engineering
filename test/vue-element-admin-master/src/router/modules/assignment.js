// src/router/modules/assignment.js
import Layout from '@/layout'

const assignmentRouter = {
  path: '/assignment',
  component: Layout,
  redirect: '/assignment/list',
  name: 'AssignmentManagement',
  meta: { title: '作业管理', icon: 'form' ,roles: ['teacher', 'admin']},
  children: [
    {
      path: 'list',
      component: () => import('@/views/assignment/list'),
      name: 'AssignmentList',
      meta: { title: '作业列表' }
    },
    {
      path: 'create',
      component: () => import('@/views/assignment/create'),
      name: 'CreateAssignment',
      meta: { title: '发布新作业' }
    },
    {
      path: 'edit/:id(\\d+)',
      component: () => import('@/views/assignment/edit'),
      name: 'EditAssignment',
      meta: { title: '编辑作业', noCache: true }, // <-- 删除了 activeMenu
      hidden: true
    },
    {
      path: ':id(\\d+)/submissions',
      component: () => import('@/views/assignment/submissionList'),
      name: 'SubmissionList',
      meta: { title: '作业提交列表' }, // <-- 删除了 activeMenu
      hidden: true
    }
  ]
}

export default assignmentRouter
