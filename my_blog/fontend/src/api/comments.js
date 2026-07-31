/**
 * 评论相关 API —— 对接后端 /api/comments/*
 * 后端统一响应：{ code, msg, data }，request.js 已自动取出 data 字段
 */
import { get, post, del } from './request'

// 获取某篇文章的评论列表（返回扁平数组，前端自行转成楼中楼树）
export function fetchComments(blogId) {
  return get(`/comments/list?blogId=${blogId}`)
}

// 发表评论 / 回复。parentId 为 null 或不传时，作为一级评论
export function createComment({ blogId, content, parentId = null }) {
  return post('/comments/add', {
    blog_id: Number(blogId),
    content,
    parent_id: parentId,
  })
}

// 删除评论（鉴权由后端 get_current_user + 评论归属判断完成）
export function deleteComment(id) {
  return del(`/comments/delete?id=${id}`)
}

// 把后端返回的扁平列表转成楼中楼树状结构
export function buildCommentTree(flat = []) {
  const map = {}
  const roots = []
  flat.forEach((c) => {
    map[c.id] = { ...c, replies: [] }
  })
  flat.forEach((c) => {
    if (c.parent_id != null && map[c.parent_id]) {
      map[c.parent_id].replies.push(map[c.id])
    } else {
      roots.push(map[c.id])
    }
  })
  return roots
}
