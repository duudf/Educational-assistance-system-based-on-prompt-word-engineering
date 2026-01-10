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

export function getCourseRadarData(params) { // 确保能接收参数
  return request({
    url: '/analysis/course_radar',
    method: 'get',
    params // 将参数传递给 axios
  })
}

export function getCourseStudentPieData() {
  return request({
    url: '/analysis/course_student_pie',
    method: 'get'
  })
}
