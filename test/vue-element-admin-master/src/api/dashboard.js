// src/api/dashboard.js

import request from '@/utils/request'

// 这是您文件里已有的函数，我们保留它
export function getDashboardData() {
  return request({
    url: '/dashboard/data',
    method: 'GET'
  })
}

// --- ↓↓↓ [新增] 把我们为图表新写的 API 函数添加到这个文件里 ↓↓↓ ---
export function fetchTeacherRoleStats() {
  return request({
    url: '/ai/teacher/roles/daily-stats', // 这是我们新创建的后端接口
    method: 'get'
  })
}
// --- ↑↑↑ 新增结束 ↑↑↑ ---
