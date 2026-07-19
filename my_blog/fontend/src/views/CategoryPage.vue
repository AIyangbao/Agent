<template>
  <div class="category-page">
    <!-- ====== Hero 区域 ====== -->
    <section class="hero-area">
      <div class="hero-content">
        <h1 class="hero-title">分类</h1>
        <p class="hero-subtitle">
          <svg class="hero-sub-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
          全部分类 · {{ totalCount }} 篇文章
        </p>
      </div>
    </section>

    <!-- ====== 分类卡片网格 ====== -->
    <main class="category-content">
      <div class="cat-grid">
        <div
          v-for="(cat, i) in categories"
          :key="cat.name"
          class="cat-card"
          :style="{ animationDelay: i * 0.06 + 's' }"
          @click="goCategory(cat.name)"
        >
          <div class="cat-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
          </div>
          <div class="cat-info">
            <h3 class="cat-name">{{ cat.name }}</h3>
            <span class="cat-count">{{ cat.count }} 篇文章</span>
          </div>
          <div class="cat-arrow">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9,18 15,12 9,6"/></svg>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="!categories.length" class="empty-state">
        <span class="empty-icon">📂</span>
        <p>还没有任何分类</p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { fetchPosts } from '../api/posts'

const router = useRouter()

// 数据
const totalPosts = ref(0)
const recentPosts = ref([])

// 技术类标签（用于自动归类，与首页一致）
const TECH_TAGS = ['Python', 'AI', 'Vue', 'Docker', 'FastAPI', 'Markdown', 'MDX', 'JavaScript']

// 分类计算（技术 / 二次元）
const categories = computed(() => {
  const list = recentPosts.value
  const techCount = list.filter(p => (p.tags || []).some(t => TECH_TAGS.includes(t))).length
  const acgCount = list.length - techCount
  return [
    { name: '技术', count: techCount },
    { name: '二次元', count: acgCount },
  ]
})

const totalCount = computed(() => totalPosts.value || recentPosts.value.length)

function goCategory(name) {
  router.push({ path: '/', query: { cat: name } })
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
        tags: [],
      })
    }
    if (row.name && !map.get(blog.id).tags.includes(row.name)) {
      map.get(blog.id).tags.push(row.name)
    }
  }
  return Array.from(map.values())
}

onMounted(async () => {
  try {
    const data = await fetchPosts({ pageSize: 100 })
    const list = data.list || []
    recentPosts.value = formatPosts(list)
    totalPosts.value = data.total || list.length
  } catch (e) {
    console.error('获取分类数据失败', e)
  }
})
</script>

<style scoped>
.category-page { min-height: 100vh; position: relative; z-index: 1; }

/* ========== Hero 区域 ========== */
.hero-area {
  position: relative;
  width: 100%;
  height: 42vh; min-height: 280px;
  overflow: hidden;
  display: flex; align-items: center; justify-content: center;
  background: url('/bg-firefly.webp') center 25% / cover no-repeat;
}
.hero-area::after {
  content: '';
  position: absolute; inset: 0;
  background: linear-gradient(180deg,
    rgba(0,0,0,0) 45%,
    rgba(240,242,245,0.5) 80%,
    var(--bg-body) 100%
  );
  z-index: 1;
}
html[data-theme='dark'] .hero-area::after {
  background: linear-gradient(180deg,
    rgba(0,0,0,0) 40%,
    rgba(15,23,42,0.6) 75%,
    var(--bg-body) 100%
  );
}
.hero-content {
  position: relative; z-index: 2;
  text-align: center; color: #fff;
}
.hero-title {
  font-size: 2.8rem; font-weight: 700;
  letter-spacing: 4px; margin-bottom: 0.6rem;
  text-shadow: 0 2px 12px rgba(0,0,0,0.4);
}
.hero-subtitle {
  display: inline-flex; align-items: center; gap: 0.4rem;
  font-size: 0.95rem; font-weight: 400;
  opacity: 0.9; letter-spacing: 1px;
  text-shadow: 0 1px 6px rgba(0,0,0,0.35);
}
.hero-sub-icon { width: 17px; height: 17px; }

/* ========== 内容区 ========== */
.category-content {
  max-width: 1100px;
  margin: 0 auto;
  padding: 1.5rem 1.5rem 3rem;
}

/* 分类卡片网格 */
.cat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.1rem;
}
.cat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: var(--bg-card);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-lg);
  padding: 1.4rem 1.5rem;
  cursor: pointer;
  transition: all var(--transition);
  box-shadow: var(--shadow-sm);
  animation: fadeUp 0.4s ease both;
}
.cat-card:hover {
  transform: translateY(-3px);
  border-color: var(--primary-light);
  box-shadow: var(--shadow-md);
}
.cat-icon {
  width: 50px; height: 50px; flex-shrink: 0;
  border-radius: 12px;
  background: var(--primary-bg);
  color: var(--primary);
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;
}
.cat-icon svg { width: 24px; height: 24px; }
.cat-card:hover .cat-icon {
  background: var(--primary);
  color: #fff;
}
.cat-info { flex: 1; min-width: 0; }
.cat-name {
  font-size: 18px; font-weight: 700;
  color: var(--text);
  margin-bottom: 0.2rem;
  transition: color 0.2s;
}
.cat-card:hover .cat-name { color: var(--primary); }
.cat-count {
  font-size: 13px;
  color: var(--text-dim);
}
.cat-arrow {
  width: 36px; height: 36px; flex-shrink: 0;
  border-radius: 50%;
  background: var(--bg-body);
  border: 1px solid var(--border-strong);
  color: var(--text-secondary);
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;
}
.cat-arrow svg { width: 18px; height: 18px; }
.cat-card:hover .cat-arrow {
  background: var(--primary);
  border-color: var(--primary);
  color: #fff;
  transform: translateX(3px);
}

.empty-state {
  text-align: center; padding: 3rem 1rem;
  color: var(--text-dim);
}
.empty-icon { font-size: 48px; display: block; margin-bottom: 0.75rem; }

/* ========== 动画 ========== */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ========== 响应式 ========== */
@media (max-width: 640px) {
  .hero-title { font-size: 2.2rem; }
  .cat-grid { grid-template-columns: 1fr; }
  .category-content { padding: 1.25rem 1rem 2.5rem; }
}
</style>
