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
      <div v-if="!filteredPosts.length" class="empty">没有找到相关文章 ∅</div>
    </div>

    <div class="pagination">
      <span class="page-num active">1</span>
      <span class="page-num">2</span>
      <span class="page-num">→</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { posts } from '../data/mock'
import BlogCard from '../components/BlogCard.vue'

const keyword = ref('')
const currentTag = ref('all')

const allTags = computed(() => {
  const set = new Set()
  posts.forEach(p => p.tags.forEach(t => set.add(t)))
  return ['all', ...set]
})

const filteredPosts = ref([...posts])

function setTag(tag) {
  currentTag.value = tag
  filter()
}

function filter() {
  const kw = keyword.value.toLowerCase()
  filteredPosts.value = posts.filter(p => {
    const tagMatch = currentTag.value === 'all' || p.tags.includes(currentTag.value)
    const kwMatch = !kw || p.title.toLowerCase().includes(kw) || p.excerpt.toLowerCase().includes(kw)
    return tagMatch && kwMatch
  })
}
</script>

<style scoped>
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
