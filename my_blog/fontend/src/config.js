/**
 * 前端环境配置 —— 本地开发 / 线上云 隔离
 *
 * 核心思路：所有后端接口统一经过 apiUrl() 拼地址。
 *   - 默认（不设置 VITE_API_BASE_URL）：走同源相对路径 /api
 *       · 本地开发：vite dev server 把 /api 代理到 http://localhost:8000（见 vite.config.js）
 *       · 线上云：nginx 把 /api 反代到后端
 *     => 两套环境都不用改代码，天然隔离。
 *   - 想从本地直连线上云后端：在 .env.development 设
 *       VITE_API_BASE_URL=https://blog.fireflyai.site/api
 *     （注意：跨域需后端 CORS 允许该来源）
 */
export const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

/** 拼接接口地址，path 以 / 开头，如 '/comments/list' */
export function apiUrl(path) {
  return API_BASE ? `${API_BASE}${path}` : `/api${path}`
}
