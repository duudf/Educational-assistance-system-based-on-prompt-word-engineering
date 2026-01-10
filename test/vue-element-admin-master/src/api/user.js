// src/api/user.js

import request from '@/utils/request'

export function login(data) { // <--- 加上 export
  return request({
    url: '/user/login',
    method: 'post',
    data
  })
}

export function register(data) { // <--- 加上 export
  return request({
    url: '/user/register',
    method: 'post',
    data
  })
}

export function getInfo(token) { // <--- 加上 export
  return request({
    url: '/user/info',
    method: 'get'
  })
}

export function logout() { // <--- 加上 export
  return request({
    url: '/user/logout',
    method: 'post'
  })
}
