/**
 * 标签相关 API
 * 后端接口：GET /api/tags/list
 */
import { get } from './request'

export function getTagList() {
  return get('/tags/list')
}
