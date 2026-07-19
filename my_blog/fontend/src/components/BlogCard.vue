<template>
  <div class="blog-card" @click="$emit('click')">
    <!-- 左侧绿色装饰条 -->
    <div class="card-accent"></div>
    <div class="card-cover" :style="{ background: coverGradient }">
      <span class="cover-emoji">{{ coverEmoji }}</span>
    </div>
    <div class="card-body">
      <h3 class="card-title">{{ post.title }}</h3>
      <div class="card-meta-row">
        <span class="meta-badge date-badge">📅 {{ post.date || '1970-01-01' }}</span>
        <span class="meta-badge cat-badge">📄 文章示例</span>
      </div>
      <p class="card-excerpt">{{ post.excerpt || '暂无摘要...' }}</p>
      <div class="card-tag-row">
        <span v-for="tag in (post.tags || []).slice(0, 4)" :key="tag" class="hash-tag">#{{ tag }}</span>
      </div>
      <div class="card-meta">
        <span class="meta-date">👁 {{ post.views }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({ post: Object })
defineEmits(['click'])

const colorMap = {
  'Python': 'linear-gradient(135deg, #3b82f6, #1d4ed8)',
  'AI': 'linear-gradient(135deg, #8b5cf6, #6d28d9)',
  'Vue': 'linear-gradient(135deg, #10b981, #059669)',
  'Docker': 'linear-gradient(135deg, #06b6d4, #0891b2)',
  'FastAPI': 'linear-gradient(135deg, #f59e0b, #d97706)',
}
const emojiMap = {
  'Python': '🐍', 'AI': '🤖', 'Vue': '💚',
  'Docker': '🐳', 'FastAPI': '⚡',
}

function getCoverGradient(post) {
  const tag = (post.tags && post.tags[0]) || ''
  return colorMap[tag] || 'linear-gradient(135deg, #6366f1, #4f46e5)'
}

function getCoverEmoji(post) {
  const tag = (post.tags && post.tags[0]) || ''
  return emojiMap[tag] || '📄'
}
</script>

<script>
import { computed } from 'vue'

export default {
  setup(props) {
    const coverGradient = computed(() => getCoverGradient(props.post))
    const coverEmoji = computed(() => getCoverEmoji(props.post))
    return { coverGradient, coverEmoji }
  }
}
</script>

<style scoped>
.blog-card {
  display: flex; gap: 0;
  background: var(--bg-card);
  border: 1px solid var(--border-strong);
  border-left: 3px solid var(--primary);
  border-radius: 0 var(--radius) var(--radius) 0;
  padding: 0;
  cursor: pointer;
  transition: all var(--transition);
  box-shadow: var(--shadow-sm);
  animation: fadeUp 0.35s ease both;
  overflow: hidden;
}
.blog-card:hover {
  border-left-color: var(--primary-dark);
  transform: translateX(3px);
  box-shadow: var(--shadow-md);
}

/* 绿色装饰条 */
.card-accent {
  width: 3px; flex-shrink: 0;
  background: var(--primary);
  transition: background 0.2s;
}
.blog-card:hover .card-accent { background: var(--primary-dark); }

/* 封面 */
.card-cover {
  width: 140px; min-height: 105px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  overflow: hidden;
  order: -1;
}
.cover-emoji { font-size: 32px; opacity: 0.8; }

/* 内容区 */
.card-body { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 0.4rem; padding: 0.9rem 1rem 0.9rem 0.95rem; }
.card-title {
  font-size: 15.5px; font-weight: 700; color: var(--text); line-height: 1.4;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
  overflow: hidden; transition: color var(--transition);
}
.blog-card:hover .card-title { color: var(--primary); }

.card-meta-row { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }
.meta-badge {
  font-size: 11px; padding: 0.1rem 0.5rem;
  border-radius: 6px; font-weight: 500; display: inline-flex; align-items: center; gap: 0.2rem;
}
.date-badge { background: #ecfdf5; color: #047857; }
.cat-badge { background: #f0f9ff; color: #0369a1; }

.card-excerpt {
  font-size: 12.5px; color: var(--text-muted); line-height: 1.55;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-tag-row { display: flex; gap: 0.35rem; flex-wrap: wrap; }
.hash-tag { font-size: 11px; color: var(--text-dim); transition: color 0.15s; }
.hash-tag:hover { color: var(--primary); }

.card-meta {
  display: flex; align-items: center; gap: 0.85rem;
  margin-top: auto; padding-top: 0.45rem;
  border-top: 1px solid var(--border);
}
.meta-date, .meta-views { font-size: 11px; color: var(--text-dim); }

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}

@media (max-width: 520px) {
  .blog-card { flex-direction: column; }
  .card-cover { width: 100%; height: 110px; order: 0; }
  .card-body { padding: 0.75rem; }
}
</style>
