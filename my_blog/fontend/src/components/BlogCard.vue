<template>
  <div class="blog-card" @click="$emit('click')">
    <div class="card-tags">
      <span v-for="tag in post.tags" :key="tag" class="card-tag" :class="tagClass(tag)">
        {{ tag }}
      </span>
    </div>
    <div class="card-title">{{ post.title }}</div>
    <div class="card-excerpt">{{ post.excerpt }}</div>
    <div class="card-meta">
      <span class="card-date">📅 {{ post.date }}</span>
      <span class="card-views">👁 {{ post.views }}</span>
    </div>
  </div>
</template>

<script setup>
import { tagClassMap } from '../data/mock'

defineProps({ post: Object })
defineEmits(['click'])

function tagClass(tag) {
  return (tagClassMap[tag] || '').toLowerCase()
}
</script>

<style scoped>
.blog-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.4rem;
  cursor: pointer;
  transition: all 0.25s;
  backdrop-filter: blur(12px);
  display: flex; flex-direction: column; gap: 0.75rem;
}
.blog-card:hover {
  border-color: var(--border-accent);
  background: var(--bg-card-hover);
  transform: translateY(-3px);
}
.card-tags { display: flex; gap: 0.4rem; flex-wrap: wrap; }
.card-tag {
  font-size: 11px; padding: 0.2rem 0.6rem;
  border-radius: 10px; border: 1px solid var(--border); color: var(--primary);
}
.card-tag.python { color: #60a5fa; border-color: rgba(96,165,250,0.3); }
.card-tag.ai { color: var(--accent); border-color: rgba(244,114,182,0.3); }
.card-tag.vue { color: #4ade80; border-color: rgba(74,222,128,0.3); }
.card-tag.docker { color: #38bdf8; border-color: rgba(56,189,248,0.3); }
.card-tag.fastapi { color: #a78bfa; border-color: rgba(167,139,250,0.3); }
.card-title { font-size: 16px; font-weight: 600; color: var(--text); line-height: 1.4; }
.card-excerpt {
  font-size: 13px; color: var(--text-muted); line-height: 1.65;
  display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;
}
.card-meta {
  display: flex; align-items: center; justify-content: space-between;
  margin-top: auto; padding-top: 0.75rem; border-top: 1px solid var(--border);
}
.card-date, .card-views { font-size: 12px; color: var(--text-dim); }
</style>
