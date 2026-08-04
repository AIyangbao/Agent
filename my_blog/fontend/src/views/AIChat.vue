<template>
  <div class="ai-page">
    <div class="ai-chat-container">
      <!-- 顶部标题栏 -->
      <div class="chat-header">
        <div class="chat-header-left">
          <span class="chat-icon">🤖</span>
          <div>
            <h2>AI 对话助手</h2>
            <p class="chat-subtitle">
              <span v-if="apiOnline" class="dot dot-online"></span>
              <span v-else class="dot dot-offline"></span>
              {{ statusText }}
            </p>
          </div>
        </div>
        <button class="btn-clear" @click="clearChat" v-if="messages.length">清空对话</button>
      </div>

      <!-- 消息区域 -->
      <div class="chat-messages" ref="msgContainer">
        <!-- 空状态 → 欢迎语 -->
        <div v-if="messages.length === 0" class="welcome">
          <div class="welcome-icon">✨</div>
          <h3>你好，我是你的 AI 助手</h3>
          <p>可以问我关于技术的问题，或者聊聊你的想法</p>
          <div class="suggestions">
            <button v-for="q in quickQuestions" :key="q" class="sug-btn" @click="sendMessage(q)">
              {{ q }}
            </button>
          </div>
        </div>

        <!-- 消息列表 -->
        <div
          v-for="(msg, i) in messages"
          :key="i"
          class="msg-row"
          :class="msg.role"
        >
          <div class="msg-bubble" :class="msg.role">
            <div class="msg-avatar">
              <template v-if="msg.role === 'user'">
                <img v-if="userStore.avatar" :src="userStore.avatar" class="avatar-img" alt="avatar" />
                <span v-else class="avatar-placeholder">{{ userStore.initial || '🧑‍💻' }}</span>
              </template>
              <span v-else>🤖</span>
            </div>
            <div class="msg-content">
              <!-- AI 消息：流式阶段用纯文本（避免 Markdown 未闭合错乱），结束后渲染 Markdown -->
              <div v-if="msg.role === 'assistant' && msg.streaming" class="user-text" style="white-space:pre-wrap">{{ msg.content }}</div>
              <div v-else-if="msg.role === 'assistant'" class="markdown-body" v-html="renderMarkdown(msg.content)"></div>
              <!-- 用户消息纯文本 -->
              <div v-else class="user-text">{{ msg.content }}</div>
              <!-- RAG 参考来源 -->
              <div v-if="msg.role === 'assistant' && msg.citations && msg.citations.length" class="msg-citations">
                <span class="cites-label">📚 参考来源</span>
                <a
                  v-for="(c, ci) in msg.citations"
                  :key="ci"
                  :href="c.link"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="cite-item"
                >{{ c.title }}<span class="cite-sim">相关度 {{ Math.max(0, Math.round((1 - c.distance / 2) * 100)) }}%</span></a>
              </div>
            </div>
          </div>
        </div>

        <!-- 加载中 -->
        <div v-if="loading" class="msg-row assistant">
          <div class="msg-bubble assistant typing">
            <div class="msg-avatar">🤖</div>
            <div class="typing-dots">
              <span></span><span></span><span></span>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="chat-input-area">
        <textarea
          ref="inputRef"
          v-model="input"
          class="chat-input"
          placeholder="输入消息，Enter 发送，Shift+Enter 换行..."
          rows="1"
          @keydown="onKeydown"
          @input="autoResize"
          :disabled="loading"
        ></textarea>
        <button
          class="btn-send"
          :disabled="!input.trim() || loading"
          @click="sendMessage()"
          title="发送 (Enter)"
        >
          <span v-if="!loading">↑</span>
          <span v-else class="spinner"></span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, reactive } from 'vue'
import { chatWithAIStream } from '../api/ai'
import { useUserStore } from '../store'
import { renderMarkdown } from '../utils/markdown.js'

const userStore = useUserStore()

// ---------- 状态 ----------
const messages = ref([])          // [{ role:'user'|'assistant', content }]
const input = ref('')
const loading = ref(false)
const apiOnline = ref(false)
const statusText = ref('演示模式 — 后端未启动时会用模拟回复')
const msgContainer = ref(null)
const inputRef = ref(null)

// 快捷问题
const quickQuestions = [
  '介绍一下你的博客项目',
  'FastAPI 和 Flask 有什么区别？',
  '解释一下 Docker 的核心概念',
]

// ---------- 发送消息（流式） ----------
async function sendMessage(text) {
  const msg = (text || input.value).trim()
  if (!msg || loading.value) return

  // 添加用户消息
  messages.value.push({ role: 'user', content: msg })
  input.value = ''
  autoResize()
  await scrollBottom()

  // 预留 assistant 占位消息，流式过程中逐 token 追加
  const assistantMsg = reactive({ role: 'assistant', content: '', streaming: true, citations: null })
  messages.value.push(assistantMsg)
  loading.value = true

  try {
    // history 取除去占位 assistant 以外的所有消息
    const history = messages.value
      .slice(0, -1)
      .map(m => ({ role: m.role, content: m.content }))

    // 流式接收，每收到一段就追加并滚动到底部
    await chatWithAIStream(
      msg,
      history,
      (token) => {
        assistantMsg.content += token
        scrollBottom()
      },
      (citations) => {
        assistantMsg.citations = citations
      },
    )

    apiOnline.value = true
    statusText.value = '已连接'
  } catch (e) {
    apiOnline.value = false
    const code = e.code || 'NETWORK'
    if (code === 'AUTH') {
      // 401：登录失效，提示重新登录（不进演示模式）
      statusText.value = '登录失效，请重新登录'
      assistantMsg.content = '⚠️ 登录状态已失效，请**重新登录**后再使用 AI 助手。\n\n> 点击右上角头像退出，再重新登录即可。'
    } else if (code === 'SERVER' || code === 'STREAM') {
      // 5xx / 流中断：服务异常
      statusText.value = 'AI 服务异常'
      if (assistantMsg.content) {
        // 已经流式输出了部分内容 → 追加中断提示
        assistantMsg.content += `\n\n> ⚠️ 生成中断：${e.message || '服务异常'}`
      } else {
        assistantMsg.content = `⚠️ AI 服务暂时不可用（${e.message || '服务异常'}）。\n\n请稍后重试，或检查后端服务是否正常运行。`
      }
    } else {
      // NETWORK / 未知：后端完全没起 → 演示模式
      statusText.value = '演示模式 — 后端未启动时会用模拟回复'
      assistantMsg.content = getMockReply(msg)
    }
  } finally {
    // 流结束：关闭 streaming，触发 Markdown 最终渲染
    assistantMsg.streaming = false
    loading.value = false
    await scrollBottom()
  }
}

// ---------- 模拟回复 ----------
function getMockReply(msg) {
  const lower = msg.toLowerCase()
  if (lower.includes('博客') || lower.includes('blog')) {
    return '我的博客系统叫"技术宅小窝"，技术栈是 **Vue3 + FastAPI + MySQL + Docker**，已经部署在阿里云 ECS 上，支持 HTTPS 访问。包含了用户认证、文章管理、标签筛选、全文搜索等功能。'
  }
  if (lower.includes('fastapi') && (lower.includes('flask') || lower.includes('区别'))) {
    return '**FastAPI vs Flask 核心区别：**\n\n| 特性 | FastAPI | Flask |\n|------|---------|-------|\n| 异步支持 | 原生 async/await | 需额外插件 |\n| 数据校验 | Pydantic 自动校验 | 需手动处理 |\n| API 文档 | 自动生成 Swagger | 需 flask-swagger |\n| 性能 | 接近 NodeJS/Go | 同步阻塞模型 |\n| 类型提示 | 一等公民 | 可选 |\n\n简单说：**新项目无脑 FastAPI**，老项目维护用 Flask。'
  }
  if (lower.includes('docker')) {
    return '**Docker 核心概念：**\n\n1. **镜像 (Image)** — 应用的只读模板，类似"安装包"\n2. **容器 (Container)** — 镜像的运行实例，轻量级沙箱\n3. **Dockerfile** — 定义镜像构建步骤\n4. **Docker Compose** — 编排多容器应用（如 MySQL + FastAPI + Nginx）\n5. **卷 (Volume)** — 持久化数据，容器删除数据不丢\n\n类比：镜像 = 类，容器 = 实例对象。'
  }
  return `收到你的问题：「${msg}」\n\n> ⚠️ 当前处于演示模式，后端 AI 接口暂未启动。启动后端后即可获得真实的 AI 回复。\n\n你可以试试问关于 FastAPI、Docker、博客项目等问题。`
}

// ---------- 键盘事件 ----------
function onKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

// ---------- textarea 自适应高度 ----------
function autoResize() {
  const ta = inputRef.value
  if (!ta) return
  ta.style.height = 'auto'
  ta.style.height = Math.min(ta.scrollHeight, 150) + 'px'
}

// ---------- 滚动到底部 ----------
async function scrollBottom() {
  await nextTick()
  const el = msgContainer.value
  if (el) {
    el.scrollTop = el.scrollHeight
  }
}

// ---------- 清空对话 ----------
function clearChat() {
  messages.value = []
}

// ---------- 挂载后聚焦输入框 ----------
onMounted(() => {
  inputRef.value?.focus()
})
</script>

<style scoped>
.ai-page {
  padding: 80px 1rem 2rem;
  min-height: 100vh;
  display: flex;
  justify-content: center;
}

.ai-chat-container {
  width: 100%;
  max-width: 760px;
  height: calc(100vh - 120px);
  display: flex;
  flex-direction: column;
  background: var(--bg-card);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

/* ---- 顶部 ---- */
.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--border-strong);
  flex-shrink: 0;
  background: var(--bg-card);
}
.chat-header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.chat-icon { font-size: 26px; }
.chat-header h2 {
  font-size: 1.05rem; font-weight: 700; color: var(--text); margin: 0;
}
.chat-subtitle {
  font-size: 12px; color: var(--text-dim);
  display: flex; align-items: center; gap: 0.35rem; margin-top: 1px;
}
.dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.dot-online { background: var(--success); box-shadow: 0 0 6px var(--success); }
.dot-offline { background: #f59e0b; box-shadow: 0 0 6px #f59e0b; }
.btn-clear {
  padding: 0.35rem 0.9rem; border-radius: 16px;
  border: 1px solid var(--border-strong); background: transparent;
  color: var(--text-muted); font-size: 12px; cursor: pointer; transition: all 0.2s;
}
.btn-clear:hover { border-color: var(--danger); color: var(--danger); }

/* ---- 消息区域 ---- */
.chat-messages {
  flex: 1; overflow-y: auto;
  padding: 1.25rem 1.25rem 0.5rem;
  scroll-behavior: smooth;
  background: var(--bg-body);
}

/* 欢迎语 */
.welcome { text-align: center; padding: 3rem 1rem; animation: fadeUp 0.5s ease; }
.welcome-icon { font-size: 44px; margin-bottom: 1rem; }
.welcome h3 { font-size: 1.2rem; color: var(--text); margin-bottom: 0.45rem; }
.welcome p { font-size: 14px; color: var(--text-muted); margin-bottom: 1.5rem; }
.suggestions { display: flex; flex-wrap: wrap; gap: 0.5rem; justify-content: center; }
.sug-btn {
  padding: 0.45rem 1rem; border-radius: 20px;
  border: 1px solid var(--border-accent); background: var(--primary-bg);
  color: var(--primary-dark); font-size: 13px; cursor: pointer; transition: all 0.2s; font-weight: 500;
}
.sug-btn:hover { background: var(--primary); color: #fff; border-color: var(--primary); }

/* ---- 消息气泡 ---- */
.msg-row { margin-bottom: 1rem; }
.msg-row.user { display: flex; justify-content: flex-end; }
.msg-bubble {
  display: flex; gap: 0.55rem; max-width: 85%; animation: fadeUp 0.3s ease;
}
.msg-bubble.user { flex-direction: row-reverse; }
.msg-avatar {
  width: 32px; height: 32px; flex-shrink: 0; margin-top: 2px;
  display: flex; align-items: center; justify-content: center;
}
.avatar-img { width: 32px; height: 32px; border-radius: 50%; object-fit: cover; border: 1px solid var(--border-strong); }
.avatar-placeholder {
  width: 32px; height: 32px; border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  color: #fff; font-size: 13px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
}
.msg-content {
  padding: 0.65rem 1rem; border-radius: 16px;
  font-size: 14px; line-height: 1.65; word-break: break-word;
}
/* AI 气泡 — 浅色背景 */
.msg-bubble.assistant .msg-content {
  background: #fff; border: 1px solid var(--border-strong);
  border-radius: 4px 16px 16px 16px; box-shadow: var(--shadow-sm);
  color: var(--text-secondary);
}
/* 用户气泡 — 绿色主色调 */
.msg-bubble.user .msg-content {
  background: var(--primary); color: #fff;
  border-radius: 16px 4px 16px 16px;
}
.user-text { white-space: pre-wrap; }

/* ---- 打字动画 ---- */
.typing { align-items: center; }
.typing-dots { display: flex; gap: 4px; padding: 0.5rem 0.25rem; }
.typing-dots span {
  width: 7px; height: 7px; border-radius: 50%;
  background: var(--text-dim); animation: bounce 1.4s infinite ease-in-out both;
}
.typing-dots span:nth-child(1) { animation-delay: -0.32s; }
.typing-dots span:nth-child(2) { animation-delay: -0.16s; }
.typing-dots span:nth-child(3) { animation-delay: 0s; }

/* ---- 输入区域 ---- */
.chat-input-area {
  display: flex; align-items: flex-end; gap: 0.6rem;
  padding: 0.75rem 1.25rem; border-top: 1px solid var(--border-strong);
  flex-shrink: 0; background: var(--bg-card);
}
.chat-input {
  flex: 1; padding: 0.65rem 1rem; border-radius: 14px;
  border: 1px solid var(--border-strong);
  background: var(--bg-body); color: var(--text);
  font-size: 14px; font-family: inherit; line-height: 1.5;
  outline: none; resize: none; max-height: 150px; transition: all 0.2s;
}
.chat-input:focus { border-color: var(--primary); box-shadow: 0 0 0 3px rgba(16,185,129,0.1); }
.chat-input::placeholder { color: var(--text-dim); }
.chat-input:disabled { opacity: 0.5; }
.btn-send {
  width: 38px; height: 38px; border-radius: 50%; border: none;
  background: var(--primary); color: #fff; font-size: 18px;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; transition: all 0.2s; box-shadow: 0 2px 10px rgba(5,150,105,0.25);
}
.btn-send:hover:not(:disabled) { transform: translateY(-1px); background: var(--primary-dark); box-shadow: 0 4px 14px rgba(5,150,105,0.35); }
.btn-send:disabled { opacity: 0.4; cursor: not-allowed; }
.spinner {
  width: 14px; height: 14px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff; border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

/* ---- Markdown 内容样式（浅色适配）---- */
.markdown-body :deep(p) { margin: 0 0 0.5rem; }
.markdown-body :deep(p:last-child) { margin-bottom: 0; }
.markdown-body :deep(:not(pre) > code) {
  background: #f1f5f9; color: #be123c; padding: 0.15em 0.4em;
  border-radius: 5px; font-size: 13px; font-family: 'Fira Code', monospace;
}
.markdown-body :deep(pre) {
  background: #282c34; border: 1px solid #334155;
  border-radius: 10px; padding: 0; overflow: hidden; margin: 0.5rem 0;
}
.markdown-body :deep(pre code) { background: none; padding: 0; font-size: 13px; }
.markdown-body :deep(strong) { color: var(--text); font-weight: 700; }
.markdown-body :deep(h2), .markdown-body :deep(h3), .markdown-body :deep(h4) {
  margin: 0.6rem 0 0.3rem; color: var(--text); font-weight: 700;
}
.markdown-body :deep(h2) { font-size: 1.1rem; }
.markdown-body :deep(h3) { font-size: 1rem; }
.markdown-body :deep(h4) { font-size: 0.95rem; }
.markdown-body :deep(li) { margin-left: 1.2rem; margin-bottom: 0.15rem; }
.markdown-body :deep(blockquote) {
  border-left: 3px solid var(--primary);
  padding: 0.3rem 0 0.3rem 0.75rem; margin: 0.4rem 0;
  color: var(--text-muted); font-style: italic; background: var(--primary-bg);
  border-radius: 0 var(--radius) var(--radius) 0;
}
.markdown-body :deep(table) {
  border-collapse: collapse; width: 100%; margin: 0.5rem 0; font-size: 13px;
  border: 1px solid var(--border-strong); border-radius: var(--radius); overflow: hidden;
}
.markdown-body :deep(th), .markdown-body :deep(td) {
  border: 1px solid var(--border-strong); padding: 0.4rem 0.65rem; text-align: left;
}
.markdown-body :deep(th) { background: var(--bg-body); font-weight: 600; color: var(--text); }

/* ---- RAG 参考来源 ---- */
.msg-citations {
  margin-top: 0.6rem; padding-top: 0.6rem;
  border-top: 1px dashed var(--border-strong);
  display: flex; flex-wrap: wrap; gap: 0.4rem; align-items: center;
}
.cites-label {
  font-size: 12px; color: var(--text-muted); font-weight: 600;
  margin-right: 0.1rem;
}
.cite-item {
  display: inline-flex; align-items: center; gap: 0.35rem;
  padding: 0.3rem 0.7rem; border-radius: 12px;
  background: var(--primary-bg); border: 1px solid var(--border-accent);
  color: var(--primary-dark); font-size: 12.5px; text-decoration: none;
  transition: all 0.2s; max-width: 100%;
}
.cite-item:hover { background: var(--primary); color: #fff; border-color: var(--primary); }
.cite-sim { font-size: 11px; opacity: 0.7; font-weight: 500; }

/* ---- 动画 ---- */
@keyframes fadeUp { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
@keyframes bounce { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); } }
@keyframes spin { to { transform: rotate(360deg); } }

/* ---- 响应式 ---- */
@media (max-width: 640px) {
  .ai-chat-container { height: calc(100vh - 100px); border-radius: 0; border: none; }
  .msg-bubble { max-width: 92%; }
  .suggestions { flex-direction: column; align-items: center; }
}
</style>
