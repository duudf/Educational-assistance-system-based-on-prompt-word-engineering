// src/api/course.js
import request from '@/utils/request'

// 获取课程列表（分页）
export function fetchCourseList(query) {
  return request({
    url: '/courses',
    method: 'get',
    params: query
  })
}
// --- ↓↓↓ [新增] 删除课程的请求函数 ↓↓↓ ---
export function deleteCourse(id) {
  return request({
    url: `/courses/${id}`,
    method: 'delete'
  })
}
// --- ↓↓↓ 在这里添加缺失的函数 ↓↓↓ ---
// 获取教师自己的课程列表（用于下拉菜单）
export function fetchCourseOptions() {
  return request({
    url: '/courses/list', // 指向我们后端专门为下拉列表创建的API
    method: 'get'
  })
}
// --- ↑↑↑ 添加结束 ↑↑↑ ---

// 根据ID获取单个课程的详情
export function fetchCourseDetail(id) {
  return request({
    url: `/courses/${id}`,
    method: 'get'
  })
}

// 创建新课程
export function createCourse(data) {
  return request({
    url: '/courses',
    method: 'post',
    data
  })
}

// 更新课程
export function updateCourse(id, data) {
  return request({
    url: `/courses/${id}`,
    method: 'put',
    data
  })
}
// 学生选课/退课
export function enrollCourse(data) {
  return request({
    url: '/courses/enroll',
    method: 'post',
    data
  })
}
