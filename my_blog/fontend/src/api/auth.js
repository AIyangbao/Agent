/**
 * 用户相关 API
 * 对接 FastAPI 后端：blog_backend/routers/users.py
 */
import { get, post, put } from './request'

export function login(username, password) {
  return post('/user/login', { username, password })
}

export function register(username, password) {
  return post('/user/register', { username, password })
}

// 手机号 + 验证码注册（对接 routers/users.py 的 /api/user/register/phone）
export function registerByPhone(phone, code) {
  return post('/user/register/phone', { phone, code })
}

// 短信验证码登录（对接 routers/sms.py 的 /api/sms/send 与 /api/sms/login）
export function smsSend(phone) {
  return post('/sms/send', { phone })
}
export function smsLogin(phone, code) {
  return post('/sms/login', { phone, code })
}

// 获取当前登录用户资料（GET /api/user/me）
export function getMe() {
  return get('/user/me')
}

// 更新个人资料：昵称 / 头像 / 简介（PUT /api/user/profile）
export function updateProfile(data) {
  return put('/user/profile', data)
}

// 修改密码（PUT /api/user/password，需先校验旧密码）
export function updatePassword(old_password, new_password) {
  return put('/user/password', { old_password, new_password })
}
