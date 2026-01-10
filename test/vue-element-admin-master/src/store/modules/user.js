import { login, logout, getInfo } from '@/api/user'
import { getToken, setToken, removeToken } from '@/utils/auth'
import router, { resetRouter } from '@/router'

// 定义一个函数来获取初始 state，便于重置
const getDefaultState = () => {
  return {
    token: getToken(),
    name: '',
    avatar: '',
    introduction: '',
    roles: []
  }
}

const state = getDefaultState()

// Mutations: 用于同步修改 state 的唯一方法
const mutations = {
  // 重置 state 为初始状态
  RESET_STATE: (state) => {
    Object.assign(state, getDefaultState())
  },
  SET_TOKEN: (state, token) => {
    state.token = token
  },
  SET_INTRODUCTION: (state, introduction) => {
    state.introduction = introduction
  },
  SET_NAME: (state, name) => {
    state.name = name
  },
  SET_AVATAR: (state, avatar) => {
    state.avatar = avatar
  },
  SET_ROLES: (state, roles) => {
    state.roles = roles
  }
}

// Actions: 用于处理异步操作和业务逻辑
const actions = {
  // 用户登录
  login({ commit }, userInfo) {
    const { username, password } = userInfo
    return new Promise((resolve, reject) => {
      login({ username: username.trim(), password: password }).then(response => {
        const { data } = response
        commit('SET_TOKEN', data.token) // 保存 token 到 Vuex
        setToken(data.token) // 保存 token 到 Cookie
        resolve()
      }).catch(error => {
        reject(error)
      })
    })
  },

  // 获取用户信息
  getInfo({ commit, state }) {
    return new Promise((resolve, reject) => {
      getInfo(state.token).then(response => {
        const { data } = response

        if (!data) {
          return reject('验证失败，请重新登录。')
        }

        const { roles, name, avatar, introduction } = data

        // 验证 roles 是否为有效数组
        if (!roles || roles.length <= 0) {
          return reject('getInfo: 角色信息不能为空！')
        }

        commit('SET_ROLES', roles)
        commit('SET_NAME', name)
        commit('SET_AVATAR', avatar)
        commit('SET_INTRODUCTION', introduction)
        resolve(data) // 将 data 返回，供 permission.js 使用
      }).catch(error => {
        reject(error)
      })
    })
  },

  // 用户登出
  logout({ commit, state }) {
    return new Promise((resolve, reject) => {
      logout(state.token).then(() => {
        // ✅ 核心登出逻辑
        removeToken() // 1. 从 Cookie 中移除 token
        resetRouter() // 2. 重置路由
        commit('RESET_STATE') // 3. 重置 Vuex 中的 state
        resolve()
      }).catch(error => {
        // 即使后端接口出错，前端也应强制执行登出清理
        removeToken()
        resetRouter()
        commit('RESET_STATE')
        reject(error)
      })
    })
  },

  // 移除 token (通常用于 token 失效时被动登出)
  resetToken({ commit }) {
    return new Promise(resolve => {
      removeToken()
      commit('RESET_STATE')
      resolve()
    })
  },

  // 动态修改权限 (用于 DEMO 或特殊场景)
  async changeRoles({ commit, dispatch }, role) {
    // 模拟根据新角色获取新 token
    const token = role + '-token'

    commit('SET_TOKEN', token)
    setToken(token)

    // 使用新 token 获取对应的用户信息 (包括 roles)
    const { roles } = await dispatch('getInfo')

    // 重置路由，清空旧的路由
    resetRouter()

    // 根据新的 roles 生成可访问的路由表
    const accessRoutes = await dispatch('permission/generateRoutes', roles, { root: true })

    // 动态添加新的路由
    router.addRoutes(accessRoutes)

    // 重置所有已访问的视图和缓存的视图
    await dispatch('tagsView/delAllViews', null, { root: true })
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions
}
