// 引入 Mock.js、深拷贝工具函数以及路由配置
const Mock = require('mockjs')
const { deepClone } = require('../utils')
const { asyncRoutes, constantRoutes } = require('./routes.js')

// 对路由配置进行深拷贝，合并常量路由和异步路由
const routes = deepClone([...constantRoutes, ...asyncRoutes])

// 定义角色列表数据
const roles = [
  {
    key: 'admin',
    name: '管理员', // 角色显示名称
    description: '超级管理员。可以访问所有页面。', // 角色描述
    routes: routes
  },
  {
    key: 'editor',
    name: '编辑', // 角色显示名称
    description: '普通编辑。可以查看除权限管理页面之外的所有页面。', // 角色描述
    routes: routes.filter(i => i.path !== '/permission')// 只是一个模拟，过滤掉权限测试页面
  },
  {
    key: 'visitor',
    name: '访客', // 角色显示名称
    description: '只是一个访客。只能查看首页和文档页面。', // 角色描述
    routes: [{
      path: '',
      redirect: 'dashboard',
      children: [
        {
          path: 'dashboard',
          name: 'Dashboard',
          // meta.title 通常用于在菜单和面包屑中显示
          meta: { title: '首页', icon: 'dashboard' }
        }
      ]
    }]
  }
]

module.exports = [
  // 模拟: 从服务器获取所有路由
  {
    url: '/vue-element-admin/routes',
    type: 'get',
    response: _ => {
      return {
        code: 20000,
        data: routes
      }
    }
  },

  // 模拟: 从服务器获取所有角色
  {
    url: '/vue-element-admin/roles',
    type: 'get',
    response: _ => {
      return {
        code: 20000,
        data: roles
      }
    }
  },

  // 模拟: 添加角色
  {
    url: '/vue-element-admin/role',
    type: 'post',
    response: {
      code: 20000,
      data: {
        key: Mock.mock('@integer(300, 5000)')
      }
    }
  },

  // 模拟: 更新角色
  {
    url: '/vue-element-admin/role/[A-Za-z0-9]',
    type: 'put',
    response: {
      code: 20000,
      data: {
        status: 'success'
      }
    }
  },

  // 模拟: 删除角色
  {
    url: '/vue-element-admin/role/[A-Za-z0-9]',
    type: 'delete',
    response: {
      code: 20000,
      data: {
        status: 'success'
      }
    }
  }
]
