/**
 * 基础请求封装
 * 对接后端 FastAPI 统一响应格式：{ code, msg, data }
 */
const BASE = '/api'

async function request(url, options = {}) {
  const config = {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options
  }
  if (config.body && typeof config.body === 'object') {
    config.body = JSON.stringify(config.body)
  }
  const res = await fetch(`${BASE}${url}`, config)
  const json = await res.json()
  if (!res.ok || json.code !== 200) {
    throw new Error(json.detail || json.msg || '请求失败')
  }
  return json.data ?? json
}

export const get = (url) => request(url)
export const post = (url, body) => request(url, { method: 'POST', body })
export const put = (url, body) => request(url, { method: 'PUT', body })
export const del = (url) => request(url, { method: 'DELETE' })
