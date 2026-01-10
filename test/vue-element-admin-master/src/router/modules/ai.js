// src/router/modules/ai.js (最终修正版)

import Layout from '@/layout'

const aiRouter = {
  path: '/ai-practice',
  component: Layout,
  redirect: '/ai-practice/practice', // [修正] 指向更明确的 'practice' 路径
  name: 'AILab',
  alwaysShow: true, // [关键] 强制显示父菜单
  meta: {
    title: 'AI 实验室',
    icon: 'el-icon-magic-stick',
    roles: ['teacher', 'student']
  },
  children: [
    {
      // [修正] 将 path 从 'index' 改为 'practice'，语义更清晰
      path: 'practice',
      component: () => import('@/views/ai-practice/index'),
      name: 'AIPractice',
      meta: { title: '智能出题练习' }
    },
    {
      path: 'favorites',
      component: () => import('@/views/ai-practice/favorites'),
      name: 'AIFavorites', // [修正] 统一命名风格
      meta: { title: '我的收藏' }
    },
    {
      path: 'discovery',
      component: () => import('@/views/ai-practice/Discovery'),
      name: 'AIDiscovery', // [修正] 统一命名风格
      meta: { title: 'AI 导师广场' }
    },
    {
      path: 'role-manager',
      component: () => import('@/views/ai-practice/role-manager'),
      name: 'AIRoleManager', // [修正] 统一命名风格
      meta: { title: '提示词管理', roles: ['teacher', 'admin'] }
    }
  ]
}

export default aiRouter
