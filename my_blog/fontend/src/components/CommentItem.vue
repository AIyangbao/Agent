<template>
  <div class="comment-card" :class="{ optimistic: comment._optimistic }">
    <div class="comment-header">
      <div class="comment-avatar">{{ initial }}</div>
      <span class="comment-user">{{ comment.username }}</span>
      <span class="comment-time">{{ time }}</span>
      <span v-if="comment._optimistic" class="sync-badge">同步中...</span>
      <span class="comment-actions" v-if="user.isLoggedIn && !comment._optimistic">
        <button class="link-btn" @click="toggleReply">{{ replying ? '取消' : '回复' }}</button>
        <button class="link-btn danger" v-if="isMine" @click="remove">删除</button>
      </span>
    </div>
    <div class="comment-text">{{ comment.content }}</div>

    <!-- 回复输入框 -->
    <div v-if="replying" class="reply-form">
      <textarea
        v-model="replyText"
        rows="2"
        class="form-input"
        :placeholder="`回复 @${comment.username}`"
      ></textarea>
      <button class="btn-primary sm" :disabled="!replyText.trim()" @click="sendReply">发送</button>
    </div>

    <!-- 楼中楼递归 -->
    <div v-if="comment.replies && comment.replies.length" class="replies">
      <CommentItem
        v-for="r in comment.replies"
        :key="r.id"
        :comment="r"
        :current-user="currentUser"
        @reply="(p) => $emit('reply', p)"
        @delete="(id) => $emit('delete', id)"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, inject } from 'vue'
import { useUserStore } from '../store'

defineOptions({ name: 'CommentItem' })

const props = defineProps({
  comment: { type: Object, required: true },
  currentUser: { type: String, default: '' },
})
const emit = defineEmits(['reply', 'delete'])
const user = useUserStore()
const toast = inject('toast', (msg) => console.warn('[toast]', msg))

const replying = ref(false)
const replyText = ref('')

const initial = computed(() =>
  props.comment.username ? props.comment.username[0].toUpperCase() : '?'
)
const time = computed(() => formatTime(props.comment.create_time))
const isMine = computed(
  () => !!props.comment.username && props.comment.username === props.currentUser
)

function formatTime(t) {
  if (!t) return ''
  const d = new Date(t)
  if (isNaN(d.getTime())) return String(t)
  const p = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`
}

function toggleReply() {
  replying.value = !replying.value
}
function sendReply() {
  const c = replyText.value.trim()
  if (!c) return
  emit('reply', { parentId: props.comment.id, content: c })
  replyText.value = ''
  replying.value = false
}
function remove() {
  if (!confirm('确定删除这条评论吗？')) return
  emit('delete', props.comment.id)
}
</script>

<style scoped>
.comment-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1rem 1.25rem;
  margin-bottom: 0.75rem;
  backdrop-filter: blur(8px);
  transition: opacity 0.3s;
}
.comment-card.optimistic {
  opacity: 0.7;
  border-left: 3px solid var(--accent, #9333ea);
}
.sync-badge {
  font-size: 11px;
  color: var(--accent, #9333ea);
  animation: pulse 1.5s ease-in-out infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}
.comment-header {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 0.5rem;
}
.comment-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-dark), var(--accent));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 600;
  color: white;
  flex-shrink: 0;
}
.comment-user {
  font-size: 13px;
  font-weight: 600;
  color: var(--text);
}
.comment-time {
  font-size: 12px;
  color: var(--text-dim);
  margin-left: 0.2rem;
}
.comment-actions {
  margin-left: auto;
  display: flex;
  gap: 0.6rem;
}
.link-btn {
  background: none;
  border: none;
  color: var(--text-dim);
  font-size: 12px;
  cursor: pointer;
  padding: 0;
  transition: color 0.2s;
}
.link-btn:hover {
  color: var(--border-accent);
}
.link-btn.danger:hover {
  color: #ef4444;
}
.comment-text {
  font-size: 14px;
  color: var(--text-muted);
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}
.reply-form {
  margin-top: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.replies {
  margin-top: 0.75rem;
  margin-left: 1.2rem;
  border-left: 2px solid var(--border);
  padding-left: 0.9rem;
}
.form-input {
  width: 100%;
  padding: 0.65rem 0.9rem;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: rgba(10, 6, 25, 0.6);
  color: var(--text);
  font-size: 14px;
  font-family: inherit;
  outline: none;
  resize: vertical;
  transition: border-color 0.25s;
}
.form-input:focus {
  border-color: var(--border-accent);
}
.form-input::placeholder {
  color: var(--text-dim);
}
.btn-primary {
  align-self: flex-start;
  padding: 0.5rem 1.2rem;
  border-radius: 24px;
  border: none;
  background: linear-gradient(90deg, var(--primary-dark), #9333ea);
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s;
}
.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  filter: brightness(1.1);
}
.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.btn-primary.sm {
  padding: 0.35rem 0.9rem;
  font-size: 13px;
}
</style>
