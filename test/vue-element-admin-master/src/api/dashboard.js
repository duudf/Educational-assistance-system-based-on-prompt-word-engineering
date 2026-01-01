// src/api/dashboard.js
import request from '@/utils/request' // 项目通用的axios封装，vue项目标配

// 获取看板统计数据，和后端接口地址完全对应
export function getDashboardData() {
  return request({
    url: '/dashboard/data', // 后端接口路径，完整地址是 baseURL + /dashboard/data
    method: 'GET' // 后端是GET请求，必须对应
  })
}
