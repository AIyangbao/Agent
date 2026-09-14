<template>
  <div class="page">
    <div class="write-wrap">
      <div class="editor-header">
        <h2>{{ isEdit ? '✏️ 编辑文章' : '✍️ 写新文章' }}</h2>
        <div class="editor-actions">
          <button class="btn-outline" @click="cancelEdit">取消</button>
          <button class="btn-primary" :disabled="isPublishing" @click="publish">
            {{ isPublishing ? (isEdit ? '保存中...' : '发布中...') : (isEdit ? '保存修改' : '发布') }}
          </button>
        </div>
      </div>

      <div class="editor-card">
        <input type="text" class="editor-title" v-model="title" placeholder="文章标题...">

        <!-- 标签统一以 tag_names 提交：后端 add_blog / update_blog 会「存在则取 id，不存在则新建」，
             所以自定义标签（不在下方下拉框里的）也能真正落库 -->
        <div class="editor-meta-row">
          <select v-model="tag">
            <option value="">选择标签</option>
            <option value="Python">Python</option>
            <option value="AI">AI</option>
            <option value="Vue">Vue</option>
            <option value="FastAPI">FastAPI</option>
            <option value="Docker">Docker</option>
          </select>
          <input type="text" v-model="extraTags" placeholder="自定义标签（逗号分隔）">
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
import { ref, computed, inject, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../store'
import { createPost, updatePost, fetchPostById } from '../api/posts'

const route = useRoute()
const router = useRouter()
const toast = inject('toast')
const user = useUserStore()

// 编辑模式：/write?edit=<文章id>。route.path 仍是 /write，HomePage 的 isEditorPage 判断不受影响
const editId = computed(() => (route.query.edit ? Number(route.query.edit) : null))
const isEdit = computed(() => editId.value != null)

// 下拉框里的标签名集合，用于回填时判断"这个标签名能不能塞进下拉框"
const TAG_MAP = { 'Python': 1, 'AI': 2, 'Vue': 3, 'FastAPI': 4, 'Docker': 5 }

const title = ref('')
const content = ref('')
const tag = ref('')
const extraTags = ref('')
const editorRef = ref(null)
const isPublishing = ref(false)
const isLoaded = ref(false) // 编辑模式：原文是否已回填（防止"保存修改"在回填前误触发空内容覆盖）

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

// 收集标签名：下拉框 + 自定义输入，去重（提交时统一以 tag_names 交给后端解析）
function collectTagNames() {
  const names = []
  if (tag.value) names.push(tag.value)
  extraTags.value.split(',').forEach(s => {
    const t = s.trim()
    if (t) names.push(t)
  })
  return [...new Set(names)]
}

// 编辑模式：进入页面先拉原文回填（标题/正文/标签）
onMounted(async () => {
  if (!isEdit.value) return
  try {
    const data = await fetchPostById(editId.value)
    title.value = data.title || ''
    content.value = data.content || ''
    // 原文标签回显：第一个在下拉框里的放 select，其余（含自定义标签）放文本框，保证保存时不丢标签
    const names = Array.isArray(data.tags_name) ? data.tags_name : []
    const inSelect = names.find(n => TAG_MAP[n] != null)
    tag.value = inSelect || ''
    extraTags.value = names.filter(n => n !== inSelect).join(', ')
    isLoaded.value = true
  } catch (e) {
    toast(e.message || '文章加载失败', 'error')
    router.push('/posts')
  }
})

function cancelEdit() {
  // 编辑模式取消 → 回到文章详情；新建模式取消 → 回文章列表
  router.push(isEdit.value ? `/posts/${editId.value}` : '/posts')
}

async function publish() {
  const t = title.value.trim()
  const c = content.value.trim()
  if (!t) { toast('文章标题不能为空', 'error'); return }
  if (!c) { toast('文章内容不能为空', 'error'); return }
  if (isEdit.value && !isLoaded.value) { toast('原文还没加载完，稍等一下', 'error'); return }

  isPublishing.value = true
  try {
    const names = collectTagNames()

    if (isEdit.value) {
      // 编辑：标题/正文/标签一起提交
      // RAG 向量由后端 update_blog_with_rag 自动 upsert，前端不用管
      await updatePost(editId.value, { title: t, content: c, tag_names: names })
      toast('文章已保存 ✅', 'success')
      router.push(`/posts/${editId.value}`)
      return
    }

    await createPost({ title: t, content: c, tag_names: names })
    toast('文章发布成功 🎉', 'success')
    router.push('/posts')
  } catch (e) {
    toast(e.message || (isEdit.value ? '保存失败' : '发布失败'), 'error')
  } finally {
    isPublishing.value = false
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
.editor-header h2 { font-size: 1.35rem; font-weight: 700; color: var(--text); }
.editor-actions { display: flex; gap: 0.6rem; }
.editor-card {
  background: var(--bg-card); border: 1px solid var(--border-strong);
  border-radius: var(--radius-lg); padding: 1.5rem;
  box-shadow: var(--shadow-sm); display: flex; flex-direction: column; gap: 1rem;
}
.editor-title {
  width: 100%; padding: 0.75rem 1rem; border-radius: 10px;
  border: 1px solid var(--border-strong); background: var(--bg-body);
  color: var(--text); font-size: 20px; font-weight: 700;
  outline: none; transition: all var(--transition);
  box-shadow: inset 0 1px 2px rgba(0,0,0,0.03);
}
.editor-title:focus { border-color: var(--primary); box-shadow: 0 0 0 3px rgba(16,185,129,0.12); }
.editor-title::placeholder { color: var(--text-dim); }
.editor-meta-row { display: flex; gap: 0.75rem; flex-wrap: wrap; }
.editor-meta-row select, .editor-meta-row input {
  flex: 1; min-width: 140px; padding: 0.55rem 0.9rem; border-radius: 10px;
  border: 1px solid var(--border-strong); background: var(--bg-body);
  color: var(--text); font-size: 13px; outline: none; transition: all var(--transition);
  box-shadow: inset 0 1px 2px rgba(0,0,0,0.03);
}
.editor-meta-row select:focus, .editor-meta-row input:focus { border-color: var(--primary); box-shadow: 0 0 0 3px rgba(16,185,129,0.08); }
.editor-toolbar {
  display: flex; gap: 0.3rem; flex-wrap: wrap;
  padding: 0.5rem 0; border-bottom: 1px solid var(--border-strong);
}
.toolbar-btn {
  width: 32px; height: 32px; display: flex; align-items: center; justify-content: center;
  border-radius: 8px; border: none; background: transparent;
  color: var(--text-muted); font-size: 14px; cursor: pointer; transition: all var(--transition); font-weight: 700;
}
.toolbar-btn:hover { background: var(--primary-bg); color: var(--primary-dark); }
.editor-content {
  width: 100%; min-height: 400px; padding: 1rem; border-radius: 10px;
  border: 1px solid var(--border-strong); background: var(--bg-body);
  color: var(--text); font-size: 15px; font-family: 'Fira Code', monospace;
  line-height: 1.75; outline: none; resize: vertical; transition: all var(--transition);
  box-shadow: inset 0 1px 2px rgba(0,0,0,0.03);
}
.editor-content:focus { border-color: var(--primary); box-shadow: 0 0 0 3px rgba(16,185,129,0.08); }
.editor-content::placeholder { color: var(--text-dim); }

.btn-primary {
  padding: 0.5rem 1.4rem; border-radius: 24px; border: none;
  background: var(--primary); color: white; font-size: 14px; font-weight: 600; cursor: pointer;
  transition: all var(--transition); box-shadow: 0 2px 10px rgba(5,150,105,0.25);
}
.btn-primary:hover { transform: translateY(-1px); background: var(--primary-dark); box-shadow: 0 4px 14px rgba(5,150,105,0.35); }
.btn-primary:disabled { opacity: 0.65; cursor: not-allowed; transform: none; box-shadow: none; }
.btn-outline {
  padding: 0.5rem 1.1rem; border-radius: 24px;
  border: 1px solid var(--border-strong); background: transparent;
  color: var(--text-secondary); font-size: 14px; cursor: pointer; transition: all var(--transition); font-weight: 500;
}
.btn-outline:hover { background: var(--bg-body); border-color: var(--primary); color: var(--primary); }
</style>
