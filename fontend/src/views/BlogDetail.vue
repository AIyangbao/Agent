<template>
  <div class="detail-page" v-if="post">
    <!-- Hero -->
    <section class="hero-area">
      <div class="hero-content">
        <h1 class="hero-title">{{ post.title }}</h1>
        <p class="hero-subtitle">记录学习与项目心得 · In Code We Trust</p>
      </div>
    </section>

    <!-- 三栏内容区 -->
    <main class="content-area">
      <!-- 左栏 -->
      <aside class="sidebar-left">
        <div class="card profile-card">
          <div class="profile-avatar">
            <img src="/avatar-firefly.jpg" alt="流月" draggable="false" />
          </div>
          <h3 class="profile-name">流月</h3>
          <p class="profile-bio">Hello, I'm <span class="bio-accent">流月.</span></p>
          <p class="profile-desc">广州华商学院 · AI专业 · Python / Vue / FastAPI</p>
        </div>
      </aside>

      <!-- 中间正文 -->
      <section class="main-content">
        <article class="detail-article card">
          <header class="da-header">
            <h1 class="da-title">{{ post.title }}</h1>
            <div class="da-meta">
              <span class="da-meta-item">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                {{ post.date || '未知日期' }}
              </span>
              <span v-for="tag in (post.tags || [])" :key="tag" class="da-tag">#{{ tag }}</span>
              <span v-if="post.author" class="da-author">/ {{ post.author }}</span>
            </div>
          </header>
          <div class="da-body" v-html="renderedContent"></div>

          <footer class="da-footer" v-if="isLoggedIn">
            <button class="btn-delete" @click="handleDelete">删除此文章</button>
          </footer>
        </article>

        <CommentSection :blogId="id" :list="[]" />
      </section>

      <!-- 右栏 -->
      <aside class="sidebar-right">
        <div class="card info-card">
          <h4 class="card-title-sm">站点信息</h4>
          <p style="font-size:13px;color:var(--text-secondary);margin:0;">FastAPI + Vue3 + Docker · v2.0</p>
        </div>
      </aside>
    </main>
  </div>

  <div v-else class="detail-loading">
    <div class="loading-spinner"></div>
    <p>正在加载文章...</p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchPostById, deletePost } from '../api/posts'
import { useUserStore } from '../store'
import CommentSection from '../components/CommentSection.vue'
import { renderMarkdown } from '../utils/markdown.js'

const route = useRoute()
const router = useRouter()
const user = useUserStore()
const id = route.params.id
const isLoggedIn = computed(() => user.isLoggedIn)
const post = ref(null)
const renderedContent = ref('')

async function loadDetail() {
  try {
    const data = await fetchPostById(id)
    const blog = data.Blog || data
    post.value = {
      id: blog.id,
      title: blog.title,
      date: blog.create_time ? blog.create_time.slice(0, 10) : '',
      tags: data.tags_name || [],
      author: 'Firefly',
    }
    renderedContent.value = renderMarkdown(blog.content || '')
  } catch (e) {
    console.error('[BlogDetail] 加载失败', e)
  }
}

function handleDelete() {
  if (!confirm('确定要删除这篇文章吗？')) return
  deletePost(id).then(() => router.push('/')).catch(() => alert('删除失败'))
}

onMounted(loadDetail)
</script>

<style scoped>
.detail-page { min-height: 100vh; }

/* Hero */
.hero-area {
  position: relative; width: 100%; height: 30vh; min-height: 200px;
  overflow: hidden;
  background: url('/bg-firefly.webp') center 25% / cover no-repeat;
  display: flex; align-items: center; justify-content: center;
}
.hero-area::after {
  content: ''; position: absolute; inset: 0;
  background: linear-gradient(180deg, rgba(0,0,0,0) 40%, var(--bg-body) 100%);
}
.hero-content { position: relative; z-index: 2; text-align: center; color: #fff; }
.hero-title { font-size: 2rem; font-weight: 700; letter-spacing: 2px; text-shadow: 0 2px 8px rgba(0,0,0,0.4); margin-bottom: 0.5rem; }
.hero-subtitle { font-size: 0.9rem; opacity: 0.85; letter-spacing: 1px; }

/* 三栏 */
.content-area {
  max-width: 1100px; margin: -40px auto 0; padding: 0 1.5rem 3rem;
  display: grid; grid-template-columns: 220px 1fr 240px; gap: 1.2rem;
  position: relative; z-index: 2;
}
.sidebar-left, .sidebar-right { display: flex; flex-direction: column; gap: 1rem; }
.main-content { display: flex; flex-direction: column; gap: 1rem; min-width: 0; }

/* Card */
.card {
  background: var(--bg-card); backdrop-filter: blur(12px);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-lg); box-shadow: var(--shadow-sm); overflow: hidden;
}
.card-title-sm {
  font-size: 13px; font-weight: 600; color: var(--text-secondary);
  margin-bottom: 0.85rem; padding-left: 0.75rem;
  border-left: 3px solid var(--primary);
}

/* 左栏个人信息 */
.profile-card { padding: 1.5rem 1.2rem; text-align: center; }
.profile-avatar { width: 90px; height: 90px; margin: 0 auto 0.85rem; border-radius: 14px; overflow: hidden; border: 2px solid var(--primary-light); }
.profile-avatar img { width: 100%; height: 100%; object-fit: cover; }
.profile-name { font-size: 18px; font-weight: 700; color: var(--text); margin-bottom: 0.3rem; }
.profile-bio { font-size: 13px; color: var(--text-secondary); margin-bottom: 0.2rem; }
.bio-accent { color: var(--primary); font-weight: 600; }
.profile-desc { font-size: 12px; color: var(--text-dim); line-height: 1.5; }

/* 文章主体 */
.detail-article { padding: 0; }
.da-header { padding: 1.8rem 2rem 1rem; }
.da-title {
  font-size: clamp(1.5rem, 3vw, 2rem); font-weight: 800; color: var(--text);
  line-height: 1.3; margin-bottom: 0.85rem;
  padding-left: 1rem; border-left: 4px solid var(--primary);
}
.da-meta { display: flex; align-items: center; gap: 1rem; flex-wrap: wrap; font-size: 13px; color: var(--text-dim); }
.da-meta-item { display: inline-flex; align-items: center; gap: 0.3rem; }
.da-meta-item svg { width: 14px; height: 14px; flex-shrink: 0; }
.da-tag { color: var(--primary); font-weight: 500; }
.da-author { color: var(--text-dim); }

.da-body {
  padding: 1.5rem 2rem 2.5rem; font-size: 15px; line-height: 1.85;
  color: var(--text-secondary); word-break: break-word;
}

/* Markdown */
.da-body :deep(h2), .da-body :deep(h3) { margin: 1.6em 0 0.7em; color: var(--text); font-weight: 700; }
.da-body :deep(h2) { font-size: 1.45rem; padding-bottom: 0.35rem; border-bottom: 2px solid var(--primary-bg); }
.da-body :deep(h3) { font-size: 1.22rem; }
.da-body :deep(p) { margin: 0 0 1em; }
.da-body :deep(code) { background: #f1f5f9; color: #be123c; padding: 0.15em 0.4em; border-radius: 5px; font-size: 13px; }
.da-body :deep(pre) { background: #1e293b; border-radius: var(--radius); padding: 1rem; overflow-x: auto; margin: 1em 0; }
.da-body :deep(pre code) { background: none; padding: 0; color: #e2e8f0; }
.da-body :deep(strong) { color: var(--text); font-weight: 700; }
.da-body :deep(blockquote) { border-left: 4px solid var(--primary); padding: 0.6rem 1rem; margin: 1em 0; background: var(--primary-bg); border-radius: 0 var(--radius) var(--radius) 0; color: var(--text-dim); }
.da-body :deep(li) { margin-left: 1.5rem; margin-bottom: 0.3rem; }
.da-body :deep(img) { max-width: 100%; border-radius: var(--radius); margin: 1em 0; }
.da-body :deep(a) { color: var(--primary); text-decoration: none; }
.da-body :deep(a:hover) { text-decoration: underline; }

.da-footer { padding: 1.2rem 2rem; border-top: 1px solid var(--border-strong); display: flex; justify-content: flex-end; }
.btn-delete {
  padding: 0.5rem 1.3rem; border-radius: 10px;
  background: #fef2f2; color: #dc2626; border: 1px solid #fecaca;
  font-size: 13px; cursor: pointer; transition: all 0.2s;
}
.btn-delete:hover { background: #dc2626; color: #fff; }

/* 右栏 */
.info-card { padding: 1.2rem; }

/* 加载状态 */
.detail-loading { display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 60vh; gap: 1rem; color: var(--text-dim); }
.loading-spinner {
  width: 36px; height: 36px; border: 3px solid var(--border-strong);
  border-top-color: var(--primary); border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* 暗色 */
html[data-theme='dark'] .da-body code { background: rgba(51,65,85,0.5); color: #fca5a5; }
html[data-theme='dark'] .btn-delete { background: rgba(127,29,29,0.3); border-color: rgba(220,38,38,0.3); }
html[data-theme='dark'] .btn-delete:hover { background: #dc2626; color: #fff; }
html[data-theme='dark'] .da-body pre { border-color: rgba(255,255,255,0.06); }

/* 响应式 */
@media (max-width: 1024px) {
  .content-area { grid-template-columns: 1fr 240px; }
  .sidebar-left { display: none; }
}
@media (max-width: 640px) {
  .content-area { grid-template-columns: 1fr; padding: 0 1rem 2rem; margin-top: -30px; }
  .sidebar-right { display: none; }
  .hero-area { height: 25vh; min-height: 180px; }
  .da-header { padding: 1.3rem 1.3rem 0.8rem; }
  .da-body { padding: 1.2rem 1.3rem 2rem; }
}
</style>
