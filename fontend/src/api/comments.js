/**
 * 评论相关 API
 */
import { get, post } from './request'

export function fetchComments(postId) {
  return get(`/posts/${postId}/comments`)
}

export function createComment(postId, text) {
  return post(`/posts/${postId}/comments`, { text })
}
