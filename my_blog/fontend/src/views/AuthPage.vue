<template>
  <div class="auth-wrap">
    <div class="auth-card">
      <div class="auth-logo">✦ 技术宅小窝</div>
      <div class="auth-sub">{{ isLogin ? '欢迎回来，继续探索吧' : '创建账号，加入我们' }}</div>

      <div class="auth-tabs">
        <button class="auth-tab" :class="{ active: isLogin }" @click="isLogin = true">登录</button>
        <button class="auth-tab" :class="{ active: !isLogin }" @click="isLogin = false">注册</button>
      </div>

      <!-- 登录 -->
      <form v-if="isLogin" @submit.prevent="handleLogin">
        <div class="form-group">
          <label class="form-label">用户名</label>
          <div class="input-wrap">
            <span class="input-icon">👤</span>
            <input class="form-control" v-model="loginForm.username" placeholder="请输入用户名" required />
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">密码</label>
          <div class="input-wrap">
            <span class="input-icon">🔒</span>
            <input class="form-control" v-model="loginForm.password" type="password" placeholder="请输入密码" required />
          </div>
        </div>
        <button class="btn-block" type="submit">登 录</button>
      </form>

      <!-- 注册 -->
      <form v-else @submit.prevent="handleRegister">
        <div class="form-group">
          <label class="form-label">用户名</label>
          <div class="input-wrap">
            <span class="input-icon">👤</span>
            <input class="form-control" v-model="regForm.username" placeholder="4-20个字符" required />
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">密码</label>
          <div class="input-wrap">
            <span class="input-icon">🔒</span>
            <input class="form-control" v-model="regForm.password" type="password" placeholder="至少6位" required />
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">确认密码</label>
          <div class="input-wrap">
            <span class="input-icon">🔒</span>
            <input class="form-control" v-model="regForm.confirm" type="password" placeholder="再次输入密码" required />
          </div>
        </div>
        <button class="btn-block" type="submit">注 册</button>
      </form>

      <div class="auth-switch">
        {{ isLogin ? '还没有账号？' : '已有账号？' }}
        <a @click="isLogin = !isLogin">{{ isLogin ? '立即注册' : '直接登录' }}</a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useUserStore } from '../store'
import { useRouter } from 'vue-router'
import { inject } from 'vue'
import { login as apiLogin, register as apiRegister } from '../api/auth'

const user = useUserStore()
const router = useRouter()
const toast = inject('toast')

const isLogin = ref(true)
const loading = ref(false)

const loginForm = ref({ username: '', password: '' })
const regForm = ref({ username: '', password: '', confirm: '' })

async function handleLogin() {
  const { username, password } = loginForm.value
  if (!username || !password) { toast('请填写完整信息', 'error'); return }
  loading.value = true
  try {
    await apiLogin(username, password)
    user.login(username)
    toast(`欢迎回来，${username} ✨`, 'success')
    setTimeout(() => router.push('/posts'), 800)
  } catch (e) {
    toast(e.message || '登录失败', 'error')
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  const { username, password, confirm } = regForm.value
  if (username.length < 4) { toast('用户名至少4个字符', 'error'); return }
  if (password.length < 6) { toast('密码至少6位', 'error'); return }
  if (password !== confirm) { toast('两次密码不一致', 'error'); return }
  loading.value = true
  try {
    await apiRegister(username, password)
    user.login(username)
    toast(`注册成功，欢迎 ${username} 🎉`, 'success')
    setTimeout(() => router.push('/posts'), 800)
  } catch (e) {
    toast(e.message || '注册失败', 'error')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-wrap {
  min-height: 100vh; display: flex;
  align-items: center; justify-content: center; padding: 60px 1rem 2rem;
}
.auth-card {
  width: 100%; max-width: 400px;
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: 16px; padding: 2.25rem; backdrop-filter: blur(20px);
}
.auth-logo {
  text-align: center; font-size: 22px; font-weight: 700;
  background: linear-gradient(90deg, var(--primary), var(--accent));
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.4rem;
}
.auth-sub { text-align: center; font-size: 13px; color: var(--text-dim); margin-bottom: 1.75rem; }
.auth-tabs { display: flex; margin-bottom: 1.5rem; border-radius: 8px; border: 1px solid var(--border); overflow: hidden; }
.auth-tab {
  flex: 1; padding: 0.55rem; text-align: center; font-size: 14px;
  cursor: pointer; transition: all 0.25s; color: var(--text-dim);
  background: transparent; border: none;
}
.auth-tab.active { background: rgba(124, 58, 237, 0.25); color: var(--primary); font-weight: 600; }
.form-group { margin-bottom: 1rem; }
.form-label { display: block; font-size: 13px; color: var(--text-muted); margin-bottom: 0.4rem; }
.input-wrap { position: relative; }
.input-icon { position: absolute; left: 0.8rem; top: 50%; transform: translateY(-50%); color: var(--text-dim); font-size: 15px; pointer-events: none; }
.form-control {
  width: 100%; padding: 0.65rem 0.9rem 0.65rem 2.4rem;
  border-radius: 8px; border: 1px solid var(--border);
  background: rgba(10, 6, 25, 0.6); color: var(--text); font-size: 14px;
  outline: none; transition: border-color 0.25s;
}
.form-control:focus { border-color: var(--border-accent); }
.form-control::placeholder { color: var(--text-dim); }
.btn-block {
  width: 100%; padding: 0.75rem; border-radius: 8px; border: none;
  background: linear-gradient(90deg, var(--primary-dark), #9333ea);
  color: white; font-size: 15px; font-weight: 600; cursor: pointer;
  transition: all 0.25s; letter-spacing: 0.3px; margin-top: 0.5rem;
}
.btn-block:hover { filter: brightness(1.1); transform: translateY(-1px); }
.auth-switch { text-align: center; margin-top: 1.25rem; font-size: 13px; color: var(--text-dim); }
.auth-switch a { color: var(--primary); cursor: pointer; }
.auth-switch a:hover { text-decoration: underline; }
@media (max-width: 640px) { .auth-card { padding: 1.5rem; } }
</style>
