<template>
  <div class="page">
    <div class="write-wrap">
      <div class="editor-header">
        <h2>✍️ 写新文章</h2>
        <div class="editor-actions">
          <button class="btn-outline" @click="$router.push('/posts')">取消</button>
          <button class="btn-primary" @click="publish">发布</button>
        </div>
      </div>

      <div class="editor-card">
        <input type="text" class="editor-title" v-model="title" placeholder="文章标题...">

        <div class="editor-meta-row">
          <select v-model="tag">
            <option value="">选择标签</option>
            <option value="Python">Python</option>
            <option value="AI">AI</option>
            <option value="Vue">Vue</option>
            <option value="FastAPI">FastAPI</option>
            <option value="Docker">Docker</option>
            <option value="其他">其他</option>
          </select>
          <input type="text" v-model="extraTags" placeholder="其他标签（逗号分隔）">
        </div>

        <div class="editor-toolbar">
          <button class="toolbar-btn" title="加粗" @click="insert('**', '**')"><b>B</b></button>
          <button class="toolbar-btn" title="斜体" @click="insert('*', '*')"><i>I</i></button>
          <button class="toolbar-btn" title="标题" @click="insert('## ', '')">H</button>
          <button class="toolbar-btn" title="代码块" @click="insert('```\n', '\n```')">{ }</button>
          <button class="toolbar-btn" title="行内代码" @click="insert('`', '`')">`</button>
          <button class="toolbar-btn" title="引用" @click="insert('> ', '')">❝</button>
          <button class="toolbar-btn" title="无序列表" @click="insert('- ', '')">•</button>
          <button class="toolbar-btn" title="有序列表" @click="insert('1. ', '')">1.</button>
          <button class="toolbar-btn" title="分割线" @click="insert('\n---\n', '')">—</button>
        </div>

        <textarea
          ref="editorRef"
          class="editor-content"
          v-model="content"
          placeholder="用 Markdown 写下你的内容...&#10;&#10;## 一级标题&#10;&#10;正文内容..."
        ></textarea>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, inject } from 'vue'
import { useRouter } from 'vue-router'
import { posts } from '../data/mock'
import { useUserStore } from '../store'
import { createPost } from '../api/posts'

const router = useRouter()
const toast = inject('toast')
const user = useUserStore()

const title = ref('')
const content = ref('')
const tag = ref('')
const extraTags = ref('')
const editorRef = ref(null)

function insert(before, after) {
  const ta = editorRef.value
  const s = ta.selectionStart, e = ta.selectionEnd
  const sel = ta.value.slice(s, e)
  const origLen = content.value.length
  content.value = content.value.slice(0, s) + before + sel + after + content.value.slice(e)

  // 恢复光标位置 (要用 nextTick)
  const curLen = content.value.length
  const caret = s + before.length
  setTimeout(() => {
    ta.selectionStart = caret
    ta.selectionEnd = caret + sel.length
    ta.focus()
  }, 0)
}

async function publish() {
  const t = title.value.trim()
  const c = content.value.trim()
  if (!t) { toast('文章标题不能为空', 'error'); return }
  if (!c) { toast('文章内容不能为空', 'error'); return }

  const tags = []
  if (tag.value) tags.push(tag.value)
  extraTags.value.split(',').forEach(t => {
    const tt = t.trim()
    if (tt) tags.push(tt)
  })
  if (!tags.length) tags.push('其他')

  try {
    const res = await createPost({ title: t, content: c, tags })
    // 后端返回成功后，也更新本地 mock 列表（后备）
    posts.unshift({ ...res, date: new Date().toISOString().slice(0, 10), views: 0, author: user.username })
    title.value = ''
    content.value = ''
    tag.value = ''
    extraTags.value = ''
    toast('文章发布成功 🎉', 'success')
    setTimeout(() => router.push('/posts'), 600)
  } catch (e) {
    toast(e.message || '发布失败', 'error')
  }
}
</script>

<style scoped>
.page { padding: 80px 1rem 3rem; }
.write-wrap { max-width: 860px; margin: 0 auto; }
.editor-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 1.25rem; flex-wrap: wrap; gap: 0.75rem;
}
.editor-header h2 { font-size: 1.35rem; font-weight: 600; color: var(--text); }
.editor-actions { display: flex; gap: 0.6rem; }
.editor-card {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 1.5rem; backdrop-filter: blur(12px);
  display: flex; flex-direction: column; gap: 1rem;
}
.editor-title {
  width: 100%; padding: 0.75rem 1rem; border-radius: 8px;
  border: 1px solid var(--border); background: rgba(10, 6, 25, 0.6);
  color: var(--text); font-size: 20px; font-weight: 600;
  outline: none; transition: border-color 0.25s;
}
.editor-title:focus { border-color: var(--border-accent); }
.editor-title::placeholder { color: var(--text-dim); }
.editor-meta-row { display: flex; gap: 0.75rem; flex-wrap: wrap; }
.editor-meta-row select, .editor-meta-row input {
  flex: 1; min-width: 140px; padding: 0.55rem 0.9rem; border-radius: 8px;
  border: 1px solid var(--border); background: rgba(10, 6, 25, 0.6);
  color: var(--text); font-size: 13px; outline: none; transition: border-color 0.25s;
}
.editor-meta-row select:focus, .editor-meta-row input:focus { border-color: var(--border-accent); }
.editor-toolbar {
  display: flex; gap: 0.3rem; flex-wrap: wrap;
  padding: 0.5rem 0; border-bottom: 1px solid var(--border);
}
.toolbar-btn {
  width: 30px; height: 30px; display: flex; align-items: center; justify-content: center;
  border-radius: 6px; border: none; background: transparent;
  color: var(--text-muted); font-size: 14px; cursor: pointer; transition: all 0.25s; font-weight: 600;
}
.toolbar-btn:hover { background: rgba(167,139,250,0.15); color: var(--primary); }
.editor-content {
  width: 100%; min-height: 400px; padding: 1rem; border-radius: 8px;
  border: 1px solid var(--border); background: rgba(10, 6, 25, 0.6);
  color: var(--text); font-size: 15px; font-family: 'Fira Code', monospace;
  line-height: 1.75; outline: none; resize: vertical; transition: border-color 0.25s;
}
.editor-content:focus { border-color: var(--border-accent); }
.editor-content::placeholder { color: var(--text-dim); }

.btn-primary {
  padding: 0.5rem 1.4rem; border-radius: 24px; border: none;
  background: linear-gradient(90deg, var(--primary-dark), #9333ea);
  color: white; font-size: 14px; font-weight: 600; cursor: pointer;
  transition: all 0.25s;
}
.btn-primary:hover { transform: translateY(-1px); filter: brightness(1.1); }
.btn-outline {
  padding: 0.5rem 1.1rem; border-radius: 24px;
  border: 1px solid var(--border-accent); background: transparent;
  color: var(--text); font-size: 14px; cursor: pointer; transition: all 0.25s;
}
.btn-outline:hover { background: rgba(167,139,250,0.1); border-color: var(--primary); }
</style>
