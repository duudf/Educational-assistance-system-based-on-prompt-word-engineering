// src/api/submission.js
import request from '@/utils/request'

// 根据作业ID获取提交列表
export function fetchSubmissionsByAssignment(assignmentId) {
  return request({
    url: `/assignments/${assignmentId}/submissions`,
    method: 'get'
  })
}

// 根据提交ID获取提交详情
export function fetchSubmissionDetail(submissionId) {
  return request({
    url: `/submissions/${submissionId}`,
    method: 'get'
  })
}

export function gradeSubmission(submissionId, data) {
  return request({
    // 1. 确认 URL 是动态拼接的
    url: `/submissions/${submissionId}/grade`,
    // 2. 确认方法是 'post'
    method: 'post',
    // 3. 确认发送了 data
    data
  })
}
// --- ↓↓↓ 新增：获取学生作业提交详情（包含作业内容）↓↓↓ ---
export function fetchStudentSubmissionDetail(assignmentId) {
  return request({
    url: `/student/assignments/${assignmentId}/submission-detail`,
    method: 'get'
  })
}
export function postStudentSubmission(assignmentId, data) {
  return request({
    url: `/student/assignments/${assignmentId}/submit`,
    method: 'post',
    data
  })
}
