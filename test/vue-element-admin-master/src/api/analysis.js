// @/api/analysis.js 修复后代码
import request from '@/utils/request'

export function getStudentAnalysis(studentId, params) {
  return request({
    url: `/students/${studentId}/analysis`,
    method: 'get',
    params: params // ✅ GET请求必须用 params 属性传参，axios会自动拼到URL后
    // 简写：params  （key和value同名可以简写）
  })
}

// 新增：获取每日作业提交量
export function getDailySubmissions() {
  return request({
    url: '/analysis/daily_submissions',
    method: 'get'
  })
}
