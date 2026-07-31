<template>
  <div class="comments-section">
    <div class="comments-title">
      💬 评论 <span class="count" v-if="total">({{ total }})</span>
    </div>

    <div v-if="!tree.length && !sending" class="empty">暂无评论，来说第一句话吧 ✨</div>

    <!-- 评论列表（在发表框上方） -->
    <CommentItem
      v-for="c in tree"
      :key="c.id"
      :comment="c"
      :current-user="user.username"
      @reply="handleReply"
      @delete="handleDelete"
    />

    <!-- 一级评论发表框（在列表下方） -->
    <div class="comment-form">
      <textarea
        class="form-input"
        v-model="text"
        rows="3"
        placeholder="留下你的想法..."
        :disabled="!user.isLoggedIn"
      ></textarea>
      <button
        class="btn-primary"
        :disabled="!user.isLoggedIn || sending"
        @click="submitRoot"
      >
        {{ user.isLoggedIn ? (sending ? '发送中...' : '发表评论') : '请先登录' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, inject } from 'vue'
import { useUserStore } from '../store'
import CommentItem from './CommentItem.vue'
import { fetchComments, createComment, deleteComment, buildCommentTree } from '../api/comments'

const props = defineProps({
  blogId: { type: [Number, String], required: true },
})

const user = useUserStore()
const toast = inject('toast', (msg) => console.warn('[toast]', msg))

const flat = ref([])
const tree = computed(() => buildCommentTree(flat.value))
const total = computed(() => flat.value.length)
const text = ref('')
const sending = ref(false)

async function load() {
  try {
    const data = await fetchComments(Number(props.blogId))
    flat.value = Array.isArray(data) ? data : []
  } catch (e) {
    console.error('[评论] 加载失败', e)
    flat.value = []
  }
}

async function submitRoot() {
  const t = text.value.trim()
  if (!t) {
    toast('评论不能为空', 'error')
    return
  }
  sending.value = true
  try {
    // 乐观更新：先在本地插入，用户立即看到
    const optimistic = {
      id: Date.now(),           // 临时 id，reload 后会被真实 id 替换
      blog_id: Number(props.blogId),
      user_id: 0,
      username: user.username || '我',
      content: t,
      parent_id: null,
      create_time: new Date().toISOString(),
      _optimistic: true,        // 标记，用于 UI 区分
    }
    flat.value = [...flat.value, optimistic]
    text.value = ''

    // 后台真正提交 + reload 校验
    await createComment({ blogId: Number(props.blogId), content: t, parentId: null })
    toast('评论成功 ✨', 'success')
    await load()                // 用服务端数据覆盖临时数据
  } catch (e) {
    toast(e.message || '评论失败', 'error')
    await load()                // 失败也 reload，回滚乐观状态
  } finally {
    sending.value = false
  }
}

async function handleReply({ parentId, content }) {
  try {
    // 乐观插入回复
    const optimistic = {
      id: Date.now(),
      blog_id: Number(props.blogId),
      user_id: 0,
      username: user.username || '我',
      content,
      parent_id: parentId,
      create_time: new Date().toISOString(),
      _optimistic: true,
    }
    flat.value = [...flat.value, optimistic]

    await createComment({ blogId: Number(props.blogId), content, parentId })
    toast('回复成功 ✨', 'success')
    await load()
  } catch (e) {
    toast(e.message || '回复失败', 'error')
    await load()
  }
}

async function handleDelete(id) {
  try {
    await deleteComment(id)
    toast('已删除', 'success')
    await load()
  } catch (e) {
    toast(e.message || '删除失败', 'error')
  }
}

onMounted(load)
// 文章切换（blogId 变化，如 HomePage 弹窗切换）时重新拉取评论
watch(
  () => props.blogId,
  (n, o) => {
    if (n !== o) load()
  }
)
</script>

<style scoped>
.comments-section {
  margin-top: 2.5rem;
}
.comments-title {
  font-size: 1.15rem;
  font-weight: 600;
  margin-bottom: 1.25rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text);
}
.count {
  font-size: 14px;
  color: var(--text-dim);
}
.comment-form {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.25rem;
  margin-bottom: 1.5rem;
  backdrop-filter: blur(12px);
}
.form-input {
  width: 100%;
  padding: 0.65rem 0.9rem;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: rgba(10, 6, 25, 0.6);
  color: var(--text);
  font-size: 14px;
  font-family: inherit;
  outline: none;
  resize: vertical;
  margin-bottom: 0.75rem;
  transition: border-color 0.25s;
}
.form-input:focus {
  border-color: var(--border-accent);
}
.form-input::placeholder {
  color: var(--text-dim);
}
.btn-primary {
  padding: 0.5rem 1.2rem;
  border-radius: 24px;
  border: none;
  background: linear-gradient(90deg, var(--primary-dark), #9333ea);
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s;
}
.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  filter: brightness(1.1);
}
.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.empty {
  color: var(--text-dim);
  font-size: 14px;
  text-align: center;
  padding: 1.5rem 0;
}
</style>
