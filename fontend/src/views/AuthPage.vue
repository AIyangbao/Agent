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
    const res = await apiLogin(username, password)
    user.login(username, res.access_token)
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
    const res = await apiRegister(username, password)
    user.login(username, res.access_token)
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
  align-items: center; justify-content: center; padding: 80px 1rem 2rem;
}
.auth-card {
  width: 100%; max-width: 400px;
  background: var(--bg-card); border: 1px solid var(--border-strong);
  border-radius: var(--radius-lg); padding: 2.25rem;
  box-shadow: var(--shadow-md);
}
.auth-logo {
  text-align: center; font-size: 22px; font-weight: 800; color: var(--primary-dark);
  margin-bottom: 0.35rem;
}
.auth-sub { text-align: center; font-size: 13px; color: var(--text-muted); margin-bottom: 1.75rem; }
.auth-tabs {
  display: flex; margin-bottom: 1.5rem;
  border-radius: 10px; border: 1px solid var(--border-strong); overflow: hidden;
}
.auth-tab {
  flex: 1; padding: 0.55rem; text-align: center; font-size: 14px;
  cursor: pointer; transition: all var(--transition); color: var(--text-secondary);
  background: transparent; border: none; font-weight: 500;
}
.auth-tab.active { background: var(--primary-bg); color: var(--primary); font-weight: 700; }
.form-group { margin-bottom: 1rem; }
.form-label { display: block; font-size: 13px; color: var(--text-secondary); margin-bottom: 0.4rem; font-weight: 500; }
.input-wrap { position: relative; }
.input-icon { position: absolute; left: 0.8rem; top: 50%; transform: translateY(-50%); color: var(--text-dim); font-size: 15px; pointer-events: none; }
.form-control {
  width: 100%; padding: 0.65rem 0.9rem 0.65rem 2.4rem;
  border-radius: 10px; border: 1px solid var(--border-strong);
  background: var(--bg-body); color: var(--text); font-size: 14px;
  outline: none; transition: all var(--transition);
  box-shadow: inset 0 1px 2px rgba(0,0,0,0.03);
}
.form-control:focus { border-color: var(--primary); box-shadow: 0 0 0 3px rgba(16,185,129,0.12); }
.form-control::placeholder { color: var(--text-dim); }
.btn-block {
  width: 100%; padding: 0.72rem; border-radius: 12px; border: none;
  background: var(--primary); color: white; font-size: 15px; font-weight: 700;
  cursor: pointer; transition: all var(--transition); letter-spacing: 0.5px;
  margin-top: 0.5rem; box-shadow: 0 4px 14px rgba(5,150,105,0.28);
}
.btn-block:hover { background: var(--primary-dark); transform: translateY(-1px); box-shadow: 0 6px 18px rgba(5,150,105,0.35); }
.auth-switch { text-align: center; margin-top: 1.25rem; font-size: 13px; color: var(--text-muted); }
.auth-switch a { color: var(--primary); cursor: pointer; font-weight: 500; }
.auth-switch a:hover { text-decoration: underline; }

@media (max-width: 640px) { .auth-card { padding: 1.6rem; } }
</style>
