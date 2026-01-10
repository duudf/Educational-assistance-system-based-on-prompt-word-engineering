import request from '@/utils/request'

export function getTeacherRoles(params) {
  return request({ url: '/ai/teacher/roles', method: 'get', params })
}

export function createRole(data) {
  return request({ url: '/ai/teacher/roles', method: 'post', data })
}

export function updateRole(id, data) {
  return request({ url: `/ai/teacher/roles/${id}`, method: 'put', data })
}

export function deleteRole(id) {
  return request({ url: `/ai/teacher/roles/${id}`, method: 'delete' })
}
