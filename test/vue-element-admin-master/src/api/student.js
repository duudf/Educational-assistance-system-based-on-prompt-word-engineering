// src/api/student.js
import request from '@/utils/request'

export function fetchStudentList(query) {
  return request({
    url: '/students',
    method: 'get',
    params: query
  })
}
// --- ↓↓↓ 新增：获取学生详情 ↓↓↓ ---
export function fetchStudentProfile(studentId) {
  return request({
    url: `/students/${studentId}/profile`,
    method: 'get'
  })
}
