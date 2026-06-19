<template>
  <div class="page">
    <div class="page-header">
      <h2>全部文章</h2>
      <p>在这里你能找到 Python、AI、Vue、Docker 等各种话题</p>
    </div>

    <div class="list-controls">
      <div class="search-wrap">
        <span class="search-icon">🔍</span>
        <input v-model="keyword" placeholder="搜索文章标题或关键词..." @input="filter" />
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
import { ref, computed, onMounted } from 'vue'
import { fetchPosts } from '../api/posts'
import BlogCard from '../components/BlogCard.vue'

const keyword = ref('')
const currentTag = ref('all')
const page = ref(1)
const pageSize = 10
const loading = ref(false)
const total = ref(0)
const posts = ref([])

const allTags = computed(() => {
  const set = new Set()
  posts.value.forEach(p => (p.tags || []).forEach(t => set.add(t)))
  return ['all', ...set]
})

const filteredPosts = computed(() => {
  const kw = keyword.value.toLowerCase()
  return posts.value.filter(p => {
    const tagMatch = currentTag.value === 'all' || (p.tags || []).includes(currentTag.value)
    const kwMatch = !kw || p.title.toLowerCase().includes(kw) || (p.excerpt || '').toLowerCase().includes(kw)
    return tagMatch && kwMatch
  })
})

const totalPages = computed(() => Math.ceil(total.value / pageSize) || 1)

function setTag(tag) {
  currentTag.value = tag
}

function goPage(p) {
  page.value = p
  loadPosts()
}

function filter() {
  // 前端搜索，不需要重新请求
}

async function loadPosts() {
  loading.value = true
  try {
    const params = { page: page.value, pageSize }
    if (currentTag.value !== 'all') {
      params.tag = currentTag.value
    }
    const data = await fetchPosts(params)
    // 后端 join 查询返回的每条 blog 带有 tag.name，同 id 会出现多次，需要去重+合并标签
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
    // mappings() 返回 {"Blog": {...}, "name": "..."}，提取内层 Blog 对象
    const blog = row.Blog || row
    if (!map.has(blog.id)) {
      map.set(blog.id, {
        id: blog.id,
        title: blog.title,
        content: blog.content || '',
        create_time: blog.create_time,
        views: blog.views || 0,
        tags: []
      })
    }
    // 收集标签名（带 tagId 筛选时 row.name 存在；查全部时无此字段）
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
/* 原有样式保持不变 */
.page { padding: 80px 1rem 3rem; }
.page-header { text-align: center; margin-bottom: 2.5rem; }
.page-header h2 {
  font-size: 2rem; font-weight: 700;
  background: linear-gradient(90deg, var(--primary), var(--accent));
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  margin-bottom: 0.5rem;
}
.page-header p { color: var(--text-muted); font-size: 15px; }
.list-controls {
  max-width: 860px; margin: 0 auto 2rem; display: flex; gap: 0.75rem; flex-wrap: wrap;
}
.search-wrap { flex: 1; min-width: 200px; position: relative; }
.search-wrap input {
  width: 100%; padding: 0.6rem 1rem 0.6rem 2.5rem;
  border-radius: 24px; border: 1px solid var(--border);
  background: var(--bg-card); color: var(--text); font-size: 14px;
  outline: none; transition: border-color 0.25s;
}
.search-wrap input:focus { border-color: var(--border-accent); }
.search-wrap input::placeholder { color: var(--text-dim); }
.search-icon { position: absolute; left: 0.8rem; top: 50%; transform: translateY(-50%); color: var(--text-dim); font-size: 15px; pointer-events: none; }
.tag-filters { display: flex; gap: 0.5rem; flex-wrap: wrap; align-items: center; }
.tag-btn {
  padding: 0.4rem 0.9rem; border-radius: 20px;
  border: 1px solid var(--border); background: transparent;
  color: var(--text-muted); font-size: 13px; cursor: pointer; transition: all 0.25s;
}
.tag-btn:hover, .tag-btn.active { border-color: var(--primary); color: var(--primary); background: rgba(167,139,250,0.1); }
.cards-grid {
  max-width: 860px; margin: 0 auto;
  display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 1.25rem;
}
.pagination { max-width: 860px; margin: 2rem auto 0; display: flex; justify-content: center; gap: 0.5rem; }
.page-num {
  width: 36px; height: 36px; display: flex; align-items: center; justify-content: center;
  border-radius: 8px; border: 1px solid var(--border); background: var(--bg-card);
  color: var(--text-muted); font-size: 14px; cursor: pointer; transition: all 0.25s;
}
.page-num:hover, .page-num.active { border-color: var(--primary); color: var(--primary); background: rgba(167,139,250,0.1); }
.empty { grid-column: 1/-1; text-align: center; color: var(--text-dim); padding: 3rem 0; font-size: 15px; }

.card-enter { animation: fadeIn 0.4s ease both; }
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
