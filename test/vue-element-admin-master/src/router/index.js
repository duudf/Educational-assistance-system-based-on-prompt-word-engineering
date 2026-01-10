import Vue from 'vue'
import Router from 'vue-router'

Vue.use(Router)

/* Layout */
import Layout from '@/layout'

/* Router Modules */
// 引入拆分出去的路由模块
import componentsRouter from './modules/components'
import chartsRouter from './modules/charts'
import studentRouter from './modules/student'
import assignmentRouter from './modules/assignment'
import analysisRouter from './modules/analysis' // <-- 导入
import submissionRouter from './modules/submission'
import aiRouter from './modules/ai'

/**
 * 注意：子菜单只会在 route children.length >= 1 时出现
 * 详情见: https://panjiachen.github.io/vue-element-teacher-site/zh/guide/essentials/router-and-nav.html
 *
 * hidden: true                   如果设置为 true，该项路由不会在侧边栏显示 (默认 false)
 * alwaysShow: true               如果设置为 true，将始终显示根菜单
 *                                如果不设置 alwaysShow，当 item 有多个子路由时，
 *                                它将变为嵌套模式，否则不显示根菜单
 * redirect: noRedirect           如果设置 noRedirect，则在面包屑中不会被重定向
 * name:'router-name'             路由名称，由 <keep-alive> 使用 (必须设置!!!)
 * meta : {
    roles: ['teacher','editor']    控制页面角色 (可以设置多个角色)
    title: 'title'               在侧边栏和面包屑中显示的名称 (推荐设置)
    icon: 'svg-name'/'el-icon-x' 侧边栏图标
    noCache: true                如果设置为 true，页面将不会被缓存 (默认 false)
    affix: true                  如果设置为 true，标签将固定在 tags-view 中
    breadcrumb: false            如果设置为 false，该项将隐藏在面包屑中 (默认 true)
    activeMenu: '/example/list'  如果设置了路径，侧边栏将高亮显示你设置的路径
  }
 */

/**
 * constantRoutes
 * 没有权限要求的基础页面
 * 所有角色都可以访问
 */

export const constantRoutes = [
  {
    path: '/redirect',
    component: Layout,
    hidden: true,
    children: [
      {
        path: '/redirect/:path(.*)',
        component: () => import('@/views/redirect/index')
      }
    ]
  },
  {
    path: '/login',
    component: () => import('@/views/login/index'),
    hidden: true
  },
  {
    path: '/register',
    component: () => import('@/views/register/index'),
    hidden: true
  },
  {
    path: '/auth-redirect',
    component: () => import('@/views/login/auth-redirect'),
    hidden: true
  },
  {
    path: '/404',
    component: () => import('@/views/error-page/404'),
    hidden: true
  },
  {
    path: '/401',
    component: () => import('@/views/error-page/401'),
    hidden: true
  },
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        component: () => import('@/views/dashboard/index'),
        name: 'Dashboard',
        meta: { title: '首页', icon: 'dashboard', affix: true }
      }
    ]
  },
  // {
  //   path: '/documentation',
  //   component: Layout,
  //   children: [
  //     {
  //       path: 'index',
  //       component: () => import('@/views/documentation/index'),
  //       name: 'Documentation',
  //       meta: { title: '文档', icon: 'documentation', affix: true }
  //     }
  //   ]
  // },
  // {
  //   path: '/guide',
  //   component: Layout,
  //   redirect: '/guide/index',
  //   children: [
  //     {
  //       path: 'index',
  //       component: () => import('@/views/guide/index'),
  //       name: 'Guide',
  //       meta: { title: '引导页', icon: 'guide', noCache: true }
  //     }
  //   ]
  // },
  {
    path: '/profile',
    component: Layout,
    redirect: '/profile/index',
    hidden: true,
    children: [
      {
        path: 'index',
        component: () => import('@/views/profile/index'),
        name: 'Profile',
        meta: { title: '个人中心', icon: 'user', noCache: true }
      }
    ]
  }
]

/**
 * asyncRoutes
 * 需要根据用户角色动态加载的路由
 */

export const asyncRoutes = [
  {
    path: '/permission',
    component: Layout,
    redirect: '/permission/page',
    alwaysShow: true, // will always show the root menu
    name: 'Permission',
    meta: {
      title: '教师菜单',
      icon: 'lock',
      roles: ['admin'] // 可见角色
    },
    children: [
      {
        path: 'page',
        component: () => import('@/views/permission/page'),
        name: 'PagePermission',
        meta: {
          title: '页面权限',
          roles: ['teacher', 'admin'] // 或者只在子导航中设置角色
        }
      },
      {
        path: 'directive',
        component: () => import('@/views/permission/directive'),
        name: 'DirectivePermission',
        meta: {
          title: '指令权限'
          // 如果不设置角色，则表示此页面不需要权限
        }
      },
      {
        path: 'role',
        component: () => import('@/views/permission/role'),
        name: 'RolePermission',
        meta: {
          title: '角色权限',
          roles: ['teacher', 'admin']
        }
      }
    ]
  },

  {
    path: '/icon',
    component: Layout,
    children: [
      {
        path: 'index',
        component: () => import('@/views/icons/index'),
        name: 'Icons',
        meta: { title: '图标', icon: 'icon', noCache: true, roles: [] }
      }
    ]
  },

  /** 当你的路由表太长时，你可以把它分割成小模块 **/
  componentsRouter,
  chartsRouter,
  assignmentRouter,
  studentRouter,
  analysisRouter, // <-- 注册
  submissionRouter,
  aiRouter,

  {
    path: '/example', // (强烈推荐) 将 /example 改为 /course
    component: Layout,
    redirect: '/example/list',
    name: 'CourseManagement',
    meta: {
      title: '课程中心', // 1. 将标题改为更中性的“课程中心”
      icon: 'education',
      roles: ['teacher', 'student'] // 2. 允许学生也看到这个顶级菜单
    },
    children: [
    // --- 教师专属路由 ---
      {
        path: 'list',
        component: () => import('@/views/example/list'),
        name: 'TeacherCourseList', // 3. 给教师列表页一个唯一的 name
        meta: { title: '我的教学', roles: ['teacher'] } // 4. 设为只有教师可见
      },
      {
        path: 'create',
        component: () => import('@/views/example/create'),
        name: 'CreateCourse',
        meta: { title: '创建新课程', roles: ['teacher'] } // 4. 设为只有教师可见
      },
      {
        path: 'edit/:id(\\d+)',
        component: () => import('@/views/example/edit'),
        name: 'EditCourse',
        meta: { title: '编辑课程', noCache: true, activeMenu: '/course/list', roles: ['teacher'] },
        hidden: true
      },

      // --- ↓↓↓ 为学生新增的路由 ↓↓↓ ---
      {
        path: 'select',
        component: () => import('@/views/course/select'), // 指向我们新创建的选课页面
        name: 'CourseSelection',
        meta: { title: '选课广场', roles: ['student'] } // 5. 设为只有学生可见
      },
      {
        path: 'my-courses',
        component: () => import('@/views/example/list'), // 6. 复用现有的 list.vue 页面
        name: 'MyCourses',
        meta: { title: '我的课程', roles: ['student'] } // 5. 设为只有学生可见
      }
    // --- ↑↑↑ 新增结束 ↑↑↑ ---
    ]
  },

  {
    path: '/error',
    component: Layout,
    redirect: 'noRedirect',
    name: 'ErrorPages',
    meta: {
      title: '错误页面',
      icon: '404',
      roles: ['admin']
    },
    children: [
      {
        path: '401',
        component: () => import('@/views/error-page/401'),
        name: 'Page401',
        meta: { title: '401', noCache: true }
      },
      {
        path: '404',
        component: () => import('@/views/error-page/404'),
        name: 'Page404',
        meta: { title: '404', noCache: true }
      }
    ]
  },

  {
    path: '/error-log',
    component: Layout,
    children: [
      {
        path: 'log',
        component: () => import('@/views/error-log/index'),
        name: 'ErrorLog',
        meta: { title: '错误日志', icon: 'bug', roles: ['admin'] }
      }
    ]
  },

  {
    path: '/excel',
    component: Layout,
    redirect: '/excel/export-excel',
    name: 'Excel',
    meta: {
      title: 'Excel',
      icon: 'excel',
      roles: ['admin']
    },
    children: [
      {
        path: 'export-excel',
        component: () => import('@/views/excel/export-excel'),
        name: 'ExportExcel',
        meta: { title: '导出 Excel' }
      },
      {
        path: 'export-selected-excel',
        component: () => import('@/views/excel/select-excel'),
        name: 'SelectExcel',
        meta: { title: '导出已选择项' }
      },
      {
        path: 'export-merge-header',
        component: () => import('@/views/excel/merge-header'),
        name: 'MergeHeader',
        meta: { title: '合并表头' }
      },
      {
        path: 'upload-excel',
        component: () => import('@/views/excel/upload-excel'),
        name: 'UploadExcel',
        meta: { title: '上传 Excel' }
      }
    ]
  },

  {
    path: '/theme',
    component: Layout,
    children: [
      {
        path: 'index',
        component: () => import('@/views/theme/index'),
        name: 'Theme',
        meta: { title: '主题', icon: 'theme', roles: ['admin'] }
      }
    ]
  },

  {
    path: '/clipboard',
    component: Layout,
    children: [
      {
        path: 'index',
        component: () => import('@/views/clipboard/index'),
        name: 'ClipboardDemo',
        meta: { title: '剪贴板', icon: 'clipboard', roles: ['admin'] }
      }
    ]
  },

  {
    path: 'external-link',
    component: Layout,
    children: [
      {
        path: 'https://github.com/PanJiaChen/vue-element-teacher',
        meta: { title: '外部链接', icon: 'link', roles: ['admin'] }
      }
    ]
  },

  // 404 页面必须放在路由最后 !!!
  { path: '*', redirect: '/404', hidden: true }
]

const createRouter = () => new Router({
  // mode: 'history', // 需要后端支持
  scrollBehavior: () => ({ y: 0 }),
  routes: constantRoutes
})

const router = createRouter()

// 详情见: https://github.com/vuejs/vue-router/issues/1234#issuecomment-357941465
export function resetRouter() {
  const newRouter = createRouter()
  router.matcher = newRouter.matcher // 重置路由
}

export default router
