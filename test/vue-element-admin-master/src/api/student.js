// src/api/student.js
import request from '@/utils/request'

export function fetchStudentList(query) {
  return request({
    url: '/students',
    method: 'get',
    params: query
  })
}
