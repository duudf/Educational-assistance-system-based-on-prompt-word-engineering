// src/api/ai.js
import request from '@/utils/request'

export function generateQuiz(data) {
  return request({
    url: '/ai/generate-quiz',
    method: 'post',
    data
  })
}
export function favoriteQuiz(data) {
  return request({
    url: '/ai/favorite-quiz',
    method: 'post',
    data // data: { action: 'add'/'remove', quiz_data: {...} }
  })
}
export function fetchFavorites() {
  return request({
    url: '/ai/favorites',
    method: 'get'
  })
}

export function fetchPracticeHistory() {
  return request({
    url: '/ai/practice-history',
    method: 'get'
  })
}

export function gradePractice(recordId, data) {
  return request({
    url: `/ai/grade-practice/${recordId}`,
    method: 'post',
    data
  })
}
export function savePracticeAnswer(recordId, data) {
  return request({
    url: `/ai/practice-record/${recordId}`,
    method: 'put',
    data // data: { user_answer: '...' }
  })
}
export function fetchRoleList(query) {
  return request({
    url: '/ai/prompts/list',
    method: 'get',
    params: query // 包含 category
  })
}
export function fetchTeacherRoleStats() {
  return request({
    url: '/ai/teacher/roles/daily-stats',
    method: 'get'
  })
}
