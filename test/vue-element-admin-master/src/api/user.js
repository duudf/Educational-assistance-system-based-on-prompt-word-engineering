import request from '@/utils/request'

export function login(data) {
  return request({
    url: '/user/login', // URL保持不变，代理会转发
    method: 'post',
    data
  })
}

// 新增注册函数
export function register(data) {
  return request({
    url: '/user/register',
    method: 'post',
    data
  })
}

export function getInfo(token) {
  return request({
    url: '/user/info', // URL保持不变
    method: 'get'
    // 注意：这里的 params 是错的，vue-element-admin 的请求拦截器
    // 会自动从 Vuex 中获取 token 并放入请求头 X-Token
    // 所以 params 是不需要的
    // params: { token }
  })
}

export function logout() {
  return request({
    url: '/user/logout',
    method: 'post'
  })
}
