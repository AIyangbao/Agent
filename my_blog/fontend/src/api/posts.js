/**
 * 文章相关 API
 * 后端接口：GET /api/blogs/list_blogs、GET /api/blogs/detail、POST /api/blogs/add
 */
import { get, post, del, put } from './request'
import { apiUrl } from '../config'

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

/**
 * 上传图片（multipart/form-data），返回后端给的访问 URL。
 * onProgress 回调可接收 0~100 的上传进度（仅浏览器 fetch 支持 upload.onprogress）。
 */
export function uploadImage(file, onProgress) {
  const token = localStorage.getItem('blog_token')
  const form = new FormData()
  form.append('file', file)

  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()
    xhr.open('POST', apiUrl('/blogs/upload_image'))
    if (token) xhr.setRequestHeader('Authorization', `Bearer ${token}`)
    xhr.upload.onprogress = (e) => {
      if (onProgress && e.lengthComputable) onProgress(Math.round((e.loaded / e.total) * 100))
    }
    xhr.onload = () => {
      try {
        const json = JSON.parse(xhr.responseText)
        if (xhr.status >= 200 && xhr.status < 300 && json.code === 200) {
          resolve(json.data?.url || json.data)
        } else {
          reject(new Error(json.detail || json.message || '上传失败'))
        }
      } catch (e) {
        reject(new Error('上传响应解析失败'))
      }
    }
    xhr.onerror = () => reject(new Error('网络错误，上传失败'))
    xhr.send(form)
  })
}
