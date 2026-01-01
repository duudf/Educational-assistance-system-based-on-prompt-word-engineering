import request from '@/utils/request'

// --- ↓↓↓ 新增这个函数 ↓↓↓ ---
// 获取作业列表 (分页)
export function fetchAssignmentList(query) {
  return request({
    url: '/assignments',
    method: 'get',
    params: query
  })
}
// --- ↑↑↑ 新增结束 ↑↑↑ ---

// 根据ID获取作业详情
export function fetchAssignment(id) {
  return request({
    url: `/assignments/${id}`,
    method: 'get'
  })
}

// 创建新作业
export function createAssignment(data) {
  return request({
    url: '/assignments',
    method: 'post',
    data
  })
}

// 更新作业
export function updateAssignment(id, data) {
  return request({
    url: `/assignments/${id}`,
    method: 'put',
    data
  })
}
