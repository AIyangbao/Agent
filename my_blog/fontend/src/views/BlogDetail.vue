<template>
  <div class="page" v-if="post">
    <div class="article-wrap">
      <div class="article-back" @click="$router.push('/posts')">← 返回列表</div>
      <div class="article-hero">
        <div class="article-tags">
          <span v-for="tag in post.tags" :key="tag" class="card-tag" :class="tagClass(tag)">{{ tag }}</span>
        </div>
        <h1 class="article-title">{{ post.title }}</h1>
        <div class="article-meta">
          <span>📅 {{ post.date }}</span>
          <span>👁 {{ post.views }} 次阅读</span>
        </div>
        <div class="article-actions" v-if="user.isLoggedIn">
          <button class="btn-action btn-delete" @click.stop="confirmDelete">🗑 删除</button>
        </div>
      </div>
      <div class="article-divider"></div>
      <div class="article-body" v-html="post.content"></div>

    </div>

    <!-- 删除确认弹窗 -->
    <div class="modal-overlay" v-if="showDeleteConfirm" @click.self="cancelDelete">
      <div class="modal-box">
        <p class="modal-text">确定要删除 <strong>《{{ post.title }}》</strong> 吗？</p>
        <p class="modal-hint">此操作不可撤销</p>
        <div class="modal-btns">
          <button class="btn-cancel" @click="cancelDelete" :disabled="deleting">取消</button>
          <button class="btn-danger" @click="handleDelete" :disabled="deleting">
            {{ deleting ? '删除中...' : '确认删除' }}
          </button>
        </div>
      </div>
    </div>
  </div>
  <div class="page empty-page" v-else-if="!loading">
    <p>文章不存在或已删除</p>
    <button class="btn-outline" @click="$router.push('/posts')">返回列表</button>
  </div>
  <div class="page empty-page" v-else>
    <p>加载中...</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchPostById, deletePost } from '../api/posts'
import { useUserStore } from '../store'
import { inject } from 'vue'

const route = useRoute()
const router = useRouter()
const toast = inject('toast')
const user = useUserStore()
const post = ref(null)
const loading = ref(true)
const showDeleteConfirm = ref(false)
const deleting = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    const data = await fetchPostById(route.params.id)
    // 后端返回 { blog: {...}, tags: [...] }
    const blog = data.blog || data
    const tags = data.tags || []
    post.value = {
      id: blog.id,
      title: blog.title,
      content: blog.content,
      tags: tags,
      date: blog.create_time ? blog.create_time.slice(0, 10) : '',
      views: blog.views || 0
    }
  } catch (e) {
    console.error('加载文章失败', e)
    post.value = null
  } finally {
    loading.value = false
  }
})

function tagClass(tag) {
  const map = { Python: 'python', AI: 'ai', Vue: 'vue', Docker: 'docker', FastAPI: 'fastapi' }
  return (map[tag] || '').toLowerCase()
}

function confirmDelete() {
  showDeleteConfirm.value = true
}

async function handleDelete() {
  deleting.value = true
  try {
    await deletePost(post.value.id)
    if (toast) toast.success('删除成功')
    router.push('/posts')
  } catch (e) {
    if (toast) toast.error(e.message || '删除失败')
  } finally {
    deleting.value = false
    showDeleteConfirm.value = false
  }
}

function cancelDelete() {
  showDeleteConfirm.value = false
}
</script>

<style scoped>
/* 原有样式保持不变 */
.page { padding: 80px 1rem 4rem; }
.article-wrap { max-width: 780px; margin: 0 auto; }
.article-back {
  display: inline-flex; align-items: center; gap: 6px;
  font-size: 14px; color: var(--text-muted); cursor: pointer; margin-bottom: 1.5rem;
  transition: color 0.25s;
}
.article-back:hover { color: var(--primary); }
.article-hero { margin-bottom: 2rem; }
.article-tags { display: flex; gap: 0.4rem; flex-wrap: wrap; margin-bottom: 1rem; }
.card-tag {
  font-size: 11px; padding: 0.2rem 0.6rem; border-radius: 10px;
  border: 1px solid var(--border); color: var(--primary);
}
.card-tag.python { color: #60a5fa; border-color: rgba(96,165,250,0.3); }
.card-tag.ai { color: var(--accent); border-color: rgba(244,114,182,0.3); }
.card-tag.vue { color: #4ade80; border-color: rgba(74,222,128,0.3); }
.card-tag.docker { color: #38bdf8; border-color: rgba(56,189,248,0.3); }
.card-tag.fastapi { color: #a78bfa; border-color: rgba(167,139,250,0.3); }
.article-title {
  font-size: clamp(1.6rem, 3.5vw, 2.2rem); font-weight: 700; line-height: 1.3; margin-bottom: 1rem;
  background: linear-gradient(90deg, #fff 40%, var(--primary) 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.article-meta { display: flex; align-items: center; gap: 1.2rem; font-size: 13px; color: var(--text-dim); flex-wrap: wrap; }
.article-divider { height: 1px; background: var(--border); margin: 1.5rem 0; }
.article-body {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 2rem;
  backdrop-filter: blur(12px); line-height: 1.85;
}
.article-body :deep(h2) {
  font-size: 1.35rem; font-weight: 600; color: var(--primary);
  margin: 1.8rem 0 0.8rem; padding-left: 0.75rem; border-left: 3px solid var(--primary);
}
.article-body :deep(h3) { font-size: 1.1rem; font-weight: 600; margin: 1.4rem 0 0.6rem; color: var(--text); }
.article-body :deep(p) { margin-bottom: 1rem; color: var(--text-muted); font-size: 15px; }
.article-body :deep(code) {
  font-family: 'Fira Code', monospace; background: rgba(167,139,250,0.12);
  padding: 0.15em 0.4em; border-radius: 4px; font-size: 0.9em; color: var(--primary);
}
.article-body :deep(pre) {
  background: rgba(5, 3, 15, 0.8); border: 1px solid var(--border);
  border-radius: 8px; padding: 1.2rem; overflow-x: auto; margin: 1.2rem 0;
}
.article-body :deep(pre code) { background: none; padding: 0; color: #c8d3f5; font-size: 14px; line-height: 1.7; }
.article-body :deep(ul), .article-body :deep(ol) { padding-left: 1.5rem; margin-bottom: 1rem; color: var(--text-muted); }
.article-body :deep(li) { margin-bottom: 0.4rem; font-size: 15px; }
.article-body :deep(blockquote) {
  border-left: 3px solid var(--accent); padding-left: 1rem;
  color: var(--text-muted); font-style: italic; margin: 1.2rem 0;
}
.article-body :deep(hr) { border: none; border-top: 1px solid var(--border); margin: 1.5rem 0; }
.empty-page { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; gap: 1rem; height: 60vh; }
.empty-page p { color: var(--text-dim); font-size: 16px; }
.btn-outline {
  padding: 0.55rem 1.5rem; border-radius: 24px;
  border: 1px solid var(--border-accent); background: transparent;
  color: var(--text); font-size: 14px; cursor: pointer; transition: all 0.25s;
}
.btn-outline:hover { background: rgba(167,139,250,0.1); border-color: var(--primary); }

/* 操作按钮 */
.article-actions { display: flex; gap: 0.6rem; margin-top: 0.6rem; }
.btn-action {
  padding: 0.35rem 0.9rem; border-radius: 6px; border: 1px solid var(--border);
  background: transparent; color: var(--text-muted); font-size: 12px; cursor: pointer;
  transition: all 0.25s;
}
.btn-delete:hover { border-color: #f87171; color: #f87171; background: rgba(248,113,113,0.08); }

/* 确认弹窗 */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.55);
  display: flex; align-items: center; justify-content: center; z-index: 1000;
  backdrop-filter: blur(4px);
}
.modal-box {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 1.8rem; max-width: 400px; width: 90%;
  text-align: center;
}
.modal-text { font-size: 15px; color: var(--text); margin-bottom: 0.4rem; }
.modal-text strong { color: var(--primary); }
.modal-hint { font-size: 12px; color: var(--text-dim); margin-bottom: 1.2rem; }
.modal-btns { display: flex; gap: 0.8rem; justify-content: center; }
.btn-cancel {
  padding: 0.45rem 1.4rem; border-radius: 6px; border: 1px solid var(--border);
  background: transparent; color: var(--text-muted); font-size: 13px; cursor: pointer;
}
.btn-danger {
  padding: 0.45rem 1.4rem; border-radius: 6px; border: none;
  background: #f87171; color: #fff; font-size: 13px; cursor: pointer;
  transition: opacity 0.25s;
}
.btn-danger:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-danger:not(:disabled):hover { opacity: 0.85; }
@media (max-width: 640px) { .article-body { padding: 1.25rem; } }
</style>
