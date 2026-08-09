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
        <!-- 登录方式切换 -->
        <div class="auth-mode">
          <button type="button" class="auth-mode-btn" :class="{ active: loginMode === 'password' }" @click="loginMode = 'password'">密码登录</button>
          <button type="button" class="auth-mode-btn" :class="{ active: loginMode === 'sms' }" @click="loginMode = 'sms'">验证码登录</button>
        </div>

        <!-- 密码登录 -->
        <template v-if="loginMode === 'password'">
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
        </template>

        <!-- 验证码登录 -->
        <template v-else>
          <div class="form-group">
            <label class="form-label">手机号</label>
            <div class="input-wrap">
              <span class="input-icon">📱</span>
              <input class="form-control" v-model="smsForm.phone" placeholder="请输入手机号" maxlength="11" inputmode="numeric" />
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">验证码</label>
            <div class="input-wrap code-wrap">
              <span class="input-icon">🔑</span>
              <input class="form-control" v-model="smsForm.code" placeholder="6位验证码" maxlength="6" inputmode="numeric" />
              <button type="button" class="code-btn" :disabled="countdown > 0 || sending" @click="sendCode">
                {{ sending ? '发送中…' : (countdown > 0 ? `${countdown}s 后重发` : '获取验证码') }}
              </button>
            </div>
          </div>
        </template>

        <button class="btn-block" type="submit" :disabled="loading">登 录</button>
      </form>

      <!-- 注册 -->
      <form v-else @submit.prevent="handleRegister">
        <!-- 注册方式切换 -->
        <div class="auth-mode">
          <button type="button" class="auth-mode-btn" :class="{ active: regMode === 'username' }" @click="regMode = 'username'">用户名注册</button>
          <button type="button" class="auth-mode-btn" :class="{ active: regMode === 'phone' }" @click="regMode = 'phone'">验证码注册</button>
        </div>

        <!-- 用户名注册 -->
        <template v-if="regMode === 'username'">
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
        </template>

        <!-- 手机号注册 -->
        <template v-else>
          <div class="form-group">
            <label class="form-label">手机号</label>
            <div class="input-wrap">
              <span class="input-icon">📱</span>
              <input class="form-control" v-model="smsForm.phone" placeholder="请输入手机号" maxlength="11" inputmode="numeric" />
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">验证码</label>
            <div class="input-wrap code-wrap">
              <span class="input-icon">🔑</span>
              <input class="form-control" v-model="smsForm.code" placeholder="6位验证码" maxlength="6" inputmode="numeric" />
              <button type="button" class="code-btn" :disabled="countdown > 0 || sending" @click="sendCode">
                {{ sending ? '发送中…' : (countdown > 0 ? `${countdown}s 后重发` : '获取验证码') }}
              </button>
            </div>
          </div>
        </template>

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
import { ref, onUnmounted } from 'vue'
import { useUserStore } from '../store'
import { useRouter } from 'vue-router'
import { inject } from 'vue'
import { login as apiLogin, register as apiRegister, registerByPhone, smsSend, smsLogin } from '../api/auth'

const user = useUserStore()
const router = useRouter()
const toast = inject('toast')

const isLogin = ref(true)
const loading = ref(false)
const loginMode = ref('password') // password | sms
const regMode = ref('username') // username | phone

const loginForm = ref({ username: '', password: '' })
const regForm = ref({ username: '', password: '', confirm: '' })
const smsForm = ref({ phone: '', code: '' })

// 发送验证码倒计时（60s）
const sending = ref(false)
const countdown = ref(0)
let timer = null
function startCountdown() {
  countdown.value = 60
  timer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) { clearInterval(timer); timer = null }
  }, 1000)
}
onUnmounted(() => { if (timer) clearInterval(timer) })

const PHONE_RE = /^1[3-9]\d{9}$/

async function sendCode() {
  const phone = smsForm.value.phone.trim()
  if (!PHONE_RE.test(phone)) { toast('请输入正确的手机号', 'error'); return }
  sending.value = true
  try {
    await smsSend(phone)
    startCountdown()
    toast('验证码已发送（开发期请查看后端日志）', 'success')
  } catch (e) {
    toast(e.message || '发送失败', 'error')
  } finally {
    sending.value = false
  }
}

async function handleLogin() {
  if (loginMode.value === 'sms') return handleSmsLogin()
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

async function handleSmsLogin() {
  const phone = smsForm.value.phone.trim()
  const code = smsForm.value.code.trim()
  if (!PHONE_RE.test(phone)) { toast('请输入正确的手机号', 'error'); return }
  if (!code) { toast('请输入验证码', 'error'); return }
  loading.value = true
  try {
    const res = await smsLogin(phone, code)
    // 短信登录没有用户名，用手机号作为展示名（与 user.login 签名一致）
    user.login(phone, res.access_token)
    toast(`欢迎回来，${phone} ✨`, 'success')
    setTimeout(() => router.push('/posts'), 800)
  } catch (e) {
    toast(e.message || '登录失败', 'error')
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  if (regMode.value === 'phone') return handlePhoneRegister()
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

async function handlePhoneRegister() {
  const phone = smsForm.value.phone.trim()
  const code = smsForm.value.code.trim()
  if (!PHONE_RE.test(phone)) { toast('请输入正确的手机号', 'error'); return }
  if (!code || code.length !== 6) { toast('请输入6位验证码', 'error'); return }
  loading.value = true
  try {
    const res = await registerByPhone(phone, code)
    const username = res.username || `u_${phone}`
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
.auth-mode {
  display: flex; gap: 0.5rem; margin-bottom: 1.25rem;
  background: var(--bg-body); border: 1px solid var(--border-strong);
  border-radius: 10px; padding: 0.3rem;
}
.auth-mode-btn {
  flex: 1; padding: 0.5rem; border: none; border-radius: 8px;
  background: transparent; color: var(--text-secondary); font-size: 13px;
  cursor: pointer; transition: all var(--transition); font-weight: 500;
}
.auth-mode-btn.active { background: var(--primary); color: #fff; font-weight: 700; }
.code-wrap .form-control { padding-right: 7.5rem; }
.code-btn {
  position: absolute; right: 0.4rem; top: 50%; transform: translateY(-50%);
  border: none; background: var(--primary-bg); color: var(--primary);
  font-size: 12.5px; font-weight: 600; padding: 0.4rem 0.6rem;
  border-radius: 8px; cursor: pointer; transition: all var(--transition); white-space: nowrap;
}
.code-btn:hover:not(:disabled) { background: var(--primary); color: #fff; }
.code-btn:disabled { opacity: 0.55; cursor: not-allowed; }
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
