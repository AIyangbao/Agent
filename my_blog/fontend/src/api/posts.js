/**
 * 文章相关 API
 */
import { get, post } from './request'

export function fetchPosts(params = {}) {
  const qs = new URLSearchParams(params).toString()
  return get(`/posts${qs ? '?' + qs : ''}`)
}

export function fetchPostById(id) {
  return get(`/posts/${id}`)
}

export function createPost(data) {
  return post('/posts', data)
}
