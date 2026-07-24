/**
 * 用户相关 API
 * 对接 FastAPI 后端：blog_backend/routers/users.py
 */
import { post } from './request'

export function login(username, password) {
  return post('/user/login', { username, password })
}

export function register(username, password) {
  return post('/user/register', { username, password })
}
