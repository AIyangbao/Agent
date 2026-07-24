<template>
  <div class="page">
    <div class="page-header">
      <h2>全部文章</h2>
      <p>在这里你能找到 Python、AI、Vue、Docker 等各种话题</p>
    </div>

    <div class="list-controls">
      <div class="search-wrap">
        <span class="search-icon">🔍</span>
        <input v-model="keyword" placeholder="搜索文章标题或内容..." />
        <span v-if="keyword" class="search-clear" @click="clearSearch">✕</span>
      </div>
      <div class="tag-filters">
        <button
          v-for="tag in allTags"
          :key="tag"
          class="tag-btn"
          :class="{ active: currentTag === tag }"
          @click="setTag(tag)"
        >{{ tag === 'all' ? '全部' : tag }}</button>
      </div>
    </div>

    <div class="search-info" v-if="keyword.trim()">
      搜索「<strong>{{ keyword }}</strong>」找到 {{ total }} 篇文章
    </div>

    <div class="cards-grid">
      <template v-for="(post, i) in filteredPosts" :key="post.id">
        <BlogCard
          :post="post"
          :style="{ animationDelay: i * 0.05 + 's' }"
          class="card-enter"
          @click="$router.push('/posts/' + post.id)"
        />
      </template>
      <div v-if="!filteredPosts.length && !loading" class="empty">没有找到相关文章 ∅</div>
      <div v-if="loading" class="empty">加载中...</div>
    </div>

    <div class="pagination" v-if="totalPages > 1">
      <span
        v-for="p in totalPages"
        :key="p"
        class="page-num"
        :class="{ active: p === page }"
        @click="goPage(p)"
      >{{ p }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { fetchPosts } from '../api/posts'
import BlogCard from '../components/BlogCard.vue'

const keyword = ref('')
const currentTag = ref('all')
const page = ref(1)
const pageSize = 10
const loading = ref(false)
const total = ref(0)
const posts = ref([])

let searchTimer = null

const allTags = computed(() => {
  const set = new Set()
  posts.value.forEach(p => (p.tags || []).forEach(t => set.add(t)))
  return ['all', ...set]
})

// 关键词搜索交给后端，前端只做标签过滤
const filteredPosts = computed(() => {
  if (currentTag.value === 'all') return posts.value
  return posts.value.filter(p => (p.tags || []).includes(currentTag.value))
})

const totalPages = computed(() => Math.ceil(total.value / pageSize) || 1)

// 防抖 300ms：输入停顿后才调后端，避免每次按键都发请求
watch(keyword, () => {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    page.value = 1
    loadPosts()
  }, 300)
})

function setTag(tag) {
  currentTag.value = tag
}

function goPage(p) {
  page.value = p
  loadPosts()
}

function clearSearch() {
  keyword.value = ''
  page.value = 1
  loadPosts()
}

async function loadPosts() {
  loading.value = true
  try {
    const params = { page: page.value, pageSize }
    if (keyword.value.trim()) {
      params.keyword = keyword.value.trim()
    }
    const data = await fetchPosts(params)
    posts.value = formatPosts(data.list || [])
    total.value = data.total || 0
  } catch (e) {
    console.error('加载文章失败', e)
    posts.value = []
  } finally {
    loading.value = false
  }
}

function formatPosts(rows) {
  const map = new Map()
  for (const row of rows) {
    const blog = row.Blog || row
    if (!map.has(blog.id)) {
      map.set(blog.id, {
        id: blog.id,
        title: blog.title,
        content: blog.content || '',
        create_time: blog.create_time,
        views: blog.views || 0,
        tags: [],
      })
    }
    if (row.name && !map.get(blog.id).tags.includes(row.name)) {
      map.get(blog.id).tags.push(row.name)
    }
  }
  return Array.from(map.values()).map(blog => ({
    ...blog,
    excerpt: blog.content.length > 100 ? blog.content.slice(0, 100) + '...' : '',
    date: blog.create_time ? blog.create_time.slice(0, 10) : ''
  }))
}

onMounted(() => {
  loadPosts()
})
</script>

<style scoped>
.page { padding: 90px 1rem 3rem; max-width: 900px; margin: 0 auto; }

.page-header { text-align: center; margin-bottom: 2.5rem; }
.page-header h2 {
  font-size: 1.8rem; font-weight: 800;
  color: var(--text);
  margin-bottom: 0.4rem;
}
.page-header p { color: var(--text-muted); font-size: 14px; }

.list-controls {
  display: flex; gap: 0.75rem;
  margin-bottom: 1.25rem;
  flex-wrap: wrap;
}
.search-wrap { flex: 1; min-width: 200px; position: relative; }
.search-wrap input {
  width: 100%; padding: 0.6rem 1rem 0.6rem 2.5rem;
  border-radius: 24px; border: 1px solid var(--border-strong);
  background: var(--bg-card); color: var(--text); font-size: 14px;
  outline: none; transition: all var(--transition);
  box-shadow: var(--shadow-sm);
}
.search-wrap input:focus { border-color: var(--primary); box-shadow: 0 0 0 3px rgba(16,185,129,0.12); }
.search-wrap input::placeholder { color: var(--text-dim); }
.search-icon { position: absolute; left: 0.8rem; top: 50%; transform: translateY(-50%); color: var(--text-dim); font-size: 15px; pointer-events: none; }
.search-clear {
  position: absolute; right: 0.8rem; top: 50%; transform: translateY(-50%);
  color: var(--text-dim); font-size: 14px; cursor: pointer; transition: color 0.2s; user-select: none;
}
.search-clear:hover { color: var(--text); }
.search-info { margin-bottom: 1rem; font-size: 14px; color: var(--text-muted); background: var(--bg-card); padding: 0.6rem 1rem; border-radius: var(--radius); border: 1px solid var(--border); }
.search-info strong { color: var(--primary); }

.tag-filters { display: flex; gap: 0.4rem; flex-wrap: wrap; align-items: center; }
.tag-btn {
  padding: 0.38rem 0.85rem; border-radius: 18px;
  border: 1px solid var(--border-strong); background: var(--bg-card);
  color: var(--text-secondary); font-size: 13px; cursor: pointer; transition: all var(--transition);
  font-weight: 500;
}
.tag-btn:hover, .tag-btn.active {
  border-color: var(--primary); color: var(--primary);
  background: var(--primary-bg);
}

.cards-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.9rem;
}

.pagination { margin-top: 2rem; display: flex; justify-content: center; gap: 0.45rem; }
.page-num {
  width: 36px; height: 36px; display: flex; align-items: center; justify-content: center;
  border-radius: 10px; border: 1px solid var(--border-strong); background: var(--bg-card);
  color: var(--text-secondary); font-size: 13px; cursor: pointer; transition: all var(--transition);
  font-weight: 500;
}
.page-num:hover, .page-num.active {
  border-color: var(--primary); color: #fff;
  background: var(--primary);
  box-shadow: 0 2px 8px rgba(16,185,129,0.25);
}
.empty { text-align: center; color: var(--text-dim); padding: 3rem 0; font-size: 15px; background: var(--bg-card); border-radius: var(--radius); border: 1px dashed var(--border); }

.card-enter { animation: fadeUp 0.35s ease both; }
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}

@media (max-width: 640px) {
  .page { padding: 80px 0.75rem 2rem; }
  .list-controls { flex-direction: column; }
}
</style>
