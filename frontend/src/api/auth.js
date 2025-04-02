import axios from 'axios'

// 用户登录
export function login(account, password) {
  return axios.post('/admin/login', { account, password })
}

// 用户注册
export function signup(account, password) {
  return axios.post('/admin/signup', { account, password })
}