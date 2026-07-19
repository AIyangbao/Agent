<template>
  <div class="comments-section">
    <div class="comments-title">💬 评论 <span class="count" v-if="list.length">({{ list.length }})</span></div>

    <div class="comment-form">
      <textarea
        class="form-input"
        v-model="text"
        rows="3"
        placeholder="留下你的想法..."
        :disabled="!user.isLoggedIn"
      ></textarea>
      <button
        class="btn-primary"
        :disabled="!user.isLoggedIn"
        @click="submit"
      >
        {{ user.isLoggedIn ? '发表评论' : '请先登录' }}
      </button>
    </div>

    <div v-if="!list.length" class="empty">暂无评论，来说第一句话吧 ✨</div>
    <div v-for="c in list" :key="c.id" class="comment-card">
      <div class="comment-header">
        <div class="comment-avatar">{{ c.user[0].toUpperCase() }}</div>
        <span class="comment-user">{{ c.user }}</span>
        <span class="comment-time">{{ c.time }}</span>
      </div>
      <div class="comment-text">{{ c.text }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useUserStore } from '../store'
import { inject } from 'vue'

const props = defineProps({ list: Array })
const emit = defineEmits(['add'])

const user = useUserStore()
const toast = inject('toast', (msg) => console.warn('[toast]', msg))
const text = ref('')

function submit() {
  const t = text.value.trim()
  if (!t) { toast('评论不能为空', 'error'); return }
  emit('add', t)
  text.value = ''
  toast('评论成功 ✨', 'success')
}
</script>

<style scoped>
.comments-section { margin-top: 2.5rem; }
.comments-title {
  font-size: 1.15rem; font-weight: 600; margin-bottom: 1.25rem;
  display: flex; align-items: center; gap: 0.5rem; color: var(--text);
}
.count { font-size: 14px; color: var(--text-dim); }
.comment-form {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 1.25rem; margin-bottom: 1.5rem;
  backdrop-filter: blur(12px);
}
.form-input {
  width: 100%; padding: 0.65rem 0.9rem; border-radius: 8px;
  border: 1px solid var(--border); background: rgba(10, 6, 25, 0.6);
  color: var(--text); font-size: 14px; font-family: inherit; outline: none;
  resize: vertical; margin-bottom: 0.75rem; transition: border-color 0.25s;
}
.form-input:focus { border-color: var(--border-accent); }
.form-input::placeholder { color: var(--text-dim); }
.btn-primary {
  padding: 0.5rem 1.2rem; border-radius: 24px; border: none;
  background: linear-gradient(90deg, var(--primary-dark), #9333ea);
  color: white; font-size: 14px; font-weight: 600; cursor: pointer;
  transition: all 0.25s;
}
.btn-primary:hover:not(:disabled) { transform: translateY(-1px); filter: brightness(1.1); }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.comment-card {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 1rem 1.25rem; margin-bottom: 0.75rem;
  backdrop-filter: blur(8px);
}
.comment-header { display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.5rem; }
.comment-avatar {
  width: 28px; height: 28px; border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-dark), var(--accent));
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 600; color: white; flex-shrink: 0;
}
.comment-user { font-size: 13px; font-weight: 600; color: var(--text); }
.comment-time { font-size: 12px; color: var(--text-dim); margin-left: auto; }
.comment-text { font-size: 14px; color: var(--text-muted); line-height: 1.6; }
.empty { color: var(--text-dim); font-size: 14px; text-align: center; padding: 1.5rem 0; }
</style>
