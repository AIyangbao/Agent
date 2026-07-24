/**
 * 文章相关 API
 * 后端接口：GET /api/blogs/list_blogs、GET /api/blogs/detail、POST /api/blogs/add
 */
import { get, post, del, put } from './request'

export function fetchPosts(params = {}) {
  const qs = new URLSearchParams()
  if (params.tag) qs.set('tagId', params.tag)
  if (params.keyword) qs.set('keyword', params.keyword)
  if (params.page) qs.set('page', params.page)
  if (params.pageSize) qs.set('pageSize', params.pageSize)
  return get(`/blogs/list_blogs?${qs.toString()}`)
}

export function fetchPostById(id) {
  return get(`/blogs/detail?id=${id}`)
}

export function createPost(data) {
  return post('/blogs/add', data)
}

export function deletePost(id) {
  return del(`/blogs/delete?id=${id}`)
}

export function updatePost(id, data) {
  return put(`/blogs/update?id=${id}`, data)
}
