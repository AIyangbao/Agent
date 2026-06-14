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
          <span>✍️ {{ post.author }}</span>
          <span>📅 {{ post.date }}</span>
          <span>👁 {{ post.views }} 次阅读</span>
        </div>
      </div>
      <div class="article-divider"></div>
      <div class="article-body" v-html="mdToHtml(post.content)"></div>

      <CommentSection :list="postComments" @add="addComment" />
    </div>
  </div>
  <div class="page empty-page" v-else>
    <p>文章不存在或已删除</p>
    <button class="btn-outline" @click="$router.push('/posts')">返回列表</button>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { posts, comments, tagClassMap } from '../data/mock'
import { useUserStore } from '../store'
import CommentSection from '../components/CommentSection.vue'
import { inject } from 'vue'

const props = defineProps({ id: String })
const toast = inject('toast')
const user = useUserStore()

const post = computed(() => posts.find(p => p.id === parseInt(props.id)))

const localComments = ref(JSON.parse(JSON.stringify(comments)))
const postComments = computed(() => localComments.value[props.id] || [])

function addComment(text) {
  if (!localComments.value[props.id]) localComments.value[props.id] = []
  const now = new Date()
  const time = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')} ${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}`
  localComments.value[props.id].unshift({
    id: Date.now(),
    user: user.username,
    text,
    time
  })
}

function tagClass(tag) {
  return (tagClassMap[tag] || '').toLowerCase()
}

function mdToHtml(md) {
  return md
    .replace(/```(\w*)\n([\s\S]*?)```/g, (_, lang, code) =>
      `<pre><code class="lang-${lang}">${esc(code.trim())}</code></pre>`)
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>')
    .replace(/^- (.+)$/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>\n?)+/g, m => `<ul>${m}</ul>`)
    .replace(/^---$/gm, '<hr>')
    .replace(/\\`/g, '`')
    .replace(/\n\n/g, '</p><p>')
    .replace(/^(?!<[hupbli]|<\/[hupbli]|<block|<pre)(.+)$/gm, '<p>$1</p>')
}
function esc(s) { return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;') }
</script>

<style scoped>
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
@media (max-width: 640px) { .article-body { padding: 1.25rem; } }
</style>
