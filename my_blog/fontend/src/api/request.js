/**
 * 基础请求封装
 * 对接后端 FastAPI 统一响应格式：{ code, msg, data }
 */
import { apiUrl } from '../config'

async function request(url, options = {}) {
  // 从 localStorage 读取 token，加到请求头
  const token = localStorage.getItem('blog_token')
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers
  }
  const config = {
    ...options,
    headers
  }
  if (config.body && typeof config.body === 'object') {
    config.body = JSON.stringify(config.body)
  }
  const res = await fetch(apiUrl(url), config)
  const json = await res.json()
  if (!res.ok || json.code !== 200) {
    throw new Error(json.detail || json.message || '请求失败')
  }
  return json.data ?? json
}

export const get = (url) => request(url)
export const post = (url, body) => request(url, { method: 'POST', body })
export const put = (url, body) => request(url, { method: 'PUT', body })
export const del = (url) => request(url, { method: 'DELETE' })
