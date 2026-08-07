<template>
  <nav class="navbar">
    <div class="nav-inner">
      <!-- Logo -->
      <span class="nav-logo" @click="$router.push('/')">
        <span class="logo-icon">🌿</span>
        <span class="logo-text">技术宅小窝</span>
      </span>

      <!-- 导航链接 -->
      <div class="nav-links">
        <router-link to="/" class="nav-link" :class="{ active: isHomeActive }">
          <span class="link-icon">⌂</span> 主页
        </router-link>
        <router-link v-if="user.isLoggedIn" to="/write" class="nav-link" active-class="active">
          <span class="link-icon">✎</span> 写文章
        </router-link>
        <router-link v-if="user.isLoggedIn" to="/ai" class="nav-link" active-class="active">
          <span class="link-icon">🤖</span> AI
        </router-link>

        <!-- 用户区域 -->
        <template v-if="!user.isLoggedIn">
          <button class="nav-btn-login" @click="$router.push('/auth')">登录</button>
        </template>
        <template v-else>
          <div class="nav-user" @mouseenter="showMenu = true" @mouseleave="showMenu = false">
            <div
              class="avatar"
              :style="user.avatar ? { backgroundImage: 'url(' + user.avatar + ')' } : {}"
              title="个人中心"
              @click="$router.push('/profile'); showMenu = false"
            >
              <span v-if="!user.avatar">{{ user.initial || 'U' }}</span>
            </div>
            <transition name="fade">
              <div v-if="showMenu" class="user-dropdown">
                <div class="dropdown-user-info">{{ user.username }}</div>
                <div class="dropdown-divider"></div>
                <router-link to="/profile" class="dropdown-item" @click="showMenu = false">个人中心</router-link>
                <div class="dropdown-item logout" @click="handleLogout">退出登录</div>
              </div>
            </transition>
          </div>
        </template>

        <!-- 主题切换器（导航栏右侧） -->
        <div class="theme-switcher" @mouseenter="showTheme = true" @mouseleave="showTheme = false">
          <button class="theme-btn" :title="currentThemeLabel" @click="toggleThemeMenu">
            <!-- 太阳图标（亮色/系统） -->
            <svg v-if="resolvedTheme !== 'dark'" class="theme-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
            </svg>
            <!-- 月亮图标（暗色） -->
            <svg v-else class="theme-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
            </svg>
          </button>
          <transition name="fade">
            <div v-if="showTheme" class="theme-dropdown">
              <div
                v-for="opt in themeOptions"
                :key="opt.value"
                class="theme-option"
                :class="{ active: currentTheme === opt.value }"
                @click="setTheme(opt.value)"
              >
                <!-- 太阳 -->
                <svg v-if="opt.value === 'light'" class="opt-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
                <!-- 月亮 -->
                <svg v-else-if="opt.value === 'dark'" class="opt-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
                <!-- 跟随系统（显示器） -->
                <svg v-else class="opt-icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
                <span>{{ opt.label }}</span>
                <span v-if="currentTheme === opt.value" class="opt-check">✓</span>
              </div>
            </div>
          </transition>
        </div>
      </div>

      <!-- 移动端菜单按钮 -->
      <button class="menu-toggle" @click="mobileOpen = !mobileOpen">
        <span :class="{ open: mobileOpen }"></span>
      </button>
    </div>

    <!-- 移动端下拉菜单 -->
    <transition name="slide-down">
      <div v-if="mobileOpen" class="mobile-menu">
        <router-link to="/" class="mobile-link" @click="mobileOpen = false">主页</router-link>
        <router-link v-if="user.isLoggedIn" to="/write" class="mobile-link" @click="mobileOpen = false">写文章</router-link>
        <router-link v-if="user.isLoggedIn" to="/ai" class="mobile-link" @click="mobileOpen = false">AI</router-link>
        <router-link v-if="user.isLoggedIn" to="/profile" class="mobile-link" @click="mobileOpen = false">个人中心</router-link>
        <div v-if="!user.isLoggedIn" class="mobile-link" @click="$router.push('/auth'); mobileOpen=false">登录 / 注册</div>
        <div v-else class="mobile-link danger" @click="handleLogout(); mobileOpen=false">退出</div>
        <!-- 移动端主题切换 -->
        <div class="mobile-theme">
          <span class="mobile-theme-label">主题</span>
          <button
            v-for="opt in themeOptions"
            :key="opt.value"
            class="mobile-theme-opt"
            :class="{ active: currentTheme === opt.value }"
            @click="setTheme(opt.value)"
          >{{ opt.label }}</button>
        </div>
      </div>
    </transition>
  </nav>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useUserStore } from '../store'
import { useRouter, useRoute } from 'vue-router'

const user = useUserStore()
const router = useRouter()
const route = useRoute()
const showMenu = ref(false)
const mobileOpen = ref(false)
const showTheme = ref(false)

// 主页导航高亮：仅纯首页（/ 无 query、非详情/AI/标签/分类/写文章）才亮
const isHomeActive = computed(() => {
  return route.path === '/' && !route.query.view && !route.query.cat && !route.query.tag && !route.params.id
})

// ========== 主题切换 ==========
const THEME_KEY = 'blog-theme'
const currentTheme = ref('system')

const themeOptions = [
  { value: 'light', label: '亮色' },
  { value: 'dark',  label: '暗色' },
  { value: 'system', label: '跟随系统' },
]

const currentThemeLabel = computed(() => {
  const opt = themeOptions.find(o => o.value === currentTheme.value)
  return opt ? `主题：${opt.label}` : '主题'
})

// 解析实际生效的主题（处理 system 模式）
const resolvedTheme = computed(() => {
  if (currentTheme.value !== 'system') return currentTheme.value
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
})

function applyTheme(t) {
  const actual = t === 'system'
    ? (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
    : t
  document.documentElement.setAttribute('data-theme', actual)
}

function setTheme(val) {
  currentTheme.value = val
  localStorage.setItem(THEME_KEY, val)
  applyTheme(val)
  showTheme.value = false
}

function toggleThemeMenu() {
  showTheme.value = !showTheme
}

function handleLogout() {
  if (!confirm('确定要退出登录吗？')) return
  user.logout()
  router.push('/')
}

onMounted(() => {
  // 读取存储的主题偏好，默认 system
  const saved = localStorage.getItem(THEME_KEY)
  if (saved && ['light', 'dark', 'system'].includes(saved)) {
    currentTheme.value = saved
  }
  applyTheme(currentTheme.value)

  // 监听系统主题变化
  const mq = window.matchMedia('(prefers-color-scheme: dark)')
  mq.addEventListener('change', () => {
    if (currentTheme.value === 'system') applyTheme('system')
  })
})

watch(currentTheme, (val) => applyTheme(val))
</script>

<style scoped>
.navbar {
  position: fixed; top: 0; left: 12px; right: 12px; z-index: 100;
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(12px) saturate(1.8);
  border-bottom: 1px solid rgba(5, 150, 105, 0.15);
  border-radius: 14px;
  transition: background 0.3s, border-color 0.3s;
}

/* ===== 暗色导航栏 ===== */
html[data-theme='dark'] .navbar {
  background: rgba(15, 23, 42, 0.65);
  border-bottom-color: rgba(148, 163, 184, 0.1);
}
html[data-theme='dark'] .avatar { border-color: rgba(100, 116, 139, 0.4); }
html[data-theme='dark'] .mobile-menu {
  background: rgba(15, 23, 42, 0.95);
}
.nav-inner {
  max-width: 1200px;
  margin: 0 auto;
  display: flex; align-items: center;
  justify-content: space-between;
  height: 60px; padding: 0 2rem;
}

/* 主题切换器 */
.theme-switcher { position: relative; margin-right: 0.5rem; }
.theme-btn {
  width: 32px; height: 32px; border-radius: 6px;
  border: none; background: transparent;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; font-size: 17px;
  transition: all 0.2s;
}
.theme-btn:hover {
  opacity: 0.7;
  transform: rotate(15deg);
}
.theme-icon-svg {
  width: 18px; height: 18px;
  color: var(--text-secondary);
  transition: color 0.2s;
}
html[data-theme='dark'] .theme-icon-svg { color: #94a3b8; }
.opt-icon-svg { width: 15px; height: 15px; color: currentColor; }

.theme-dropdown {
  position: absolute; top: calc(100% + 8px); left: 0;
  min-width: 140px;
  background: var(--bg-card);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius);
  box-shadow: var(--shadow-lg);
  padding: 0.4rem 0;
  z-index: 200;
}
.theme-option {
  display: flex; align-items: center; gap: 0.5rem;
  padding: 0.5rem 0.9rem;
  font-size: 13px; color: var(--text-secondary);
  cursor: pointer; transition: all 0.15s;
}
.theme-option:hover { background: var(--bg-body); color: var(--primary); }
.theme-option.active { color: var(--primary); font-weight: 600; }
.opt-check { margin-left: auto; color: var(--primary); font-size: 12px; }

/* Logo */
.nav-logo {
  display: flex; align-items: center; gap: 0.45rem;
  cursor: pointer; user-select: none;
  flex-shrink: 0;
}
.logo-icon { font-size: 22px; }
.logo-text {
  font-size: 17px; font-weight: 700;
  color: var(--text); letter-spacing: 0.3px;
}

/* 导航链接 */
.nav-links {
  display: flex; align-items: center; gap: 0.25rem;
}
.nav-link {
  display: inline-flex; align-items: center; gap: 0.3rem;
  padding: 0.45rem 0.85rem;
  font-size: 14px; font-weight: 500;
  color: var(--text-secondary); text-decoration: none;
  border-radius: 8px; transition: all var(--transition);
  letter-spacing: 0.2px;
}
.nav-link:hover { color: var(--primary); background: var(--primary-bg); }
.nav-link.active {
  color: var(--primary); font-weight: 600;
  background: var(--primary-bg);
}
.link-icon { font-size: 15px; opacity: 0.7; }

/* 登录按钮 */
.nav-btn-login {
  padding: 0.4rem 1.2rem;
  border-radius: 20px;
  background: var(--primary);
  color: #fff !important; font-size: 13px; font-weight: 600;
  transition: all var(--transition);
}
.nav-btn-login:hover { background: var(--primary-dark); transform: translateY(-1px); }

/* 用户头像 + 下拉 */
.nav-user { position: relative; margin-left: 0.5rem; }
.avatar {
  width: 34px; height: 34px; border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  background-size: cover; background-position: center;
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; font-weight: 700; color: #fff; cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s; overflow: hidden;
  border: 2px solid rgba(255,255,255,0.8);
  box-shadow: var(--shadow-sm);
}
.avatar:hover { transform: scale(1.08); box-shadow: var(--shadow-md); }

.user-dropdown {
  position: absolute; top: calc(100% + 8px); right: 0;
  min-width: 160px;
  background: var(--bg-card);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius);
  box-shadow: var(--shadow-lg);
  padding: 0.5rem 0;
  z-index: 200;
}
.dropdown-user-info {
  padding: 0.6rem 1rem;
  font-size: 13px; font-weight: 600; color: var(--text);
}
.dropdown-divider { height: 1px; background: var(--border); margin: 0.3rem 0; }
.dropdown-item {
  display: block; width: 100%; padding: 0.5rem 1rem;
  font-size: 13px; color: var(--text-secondary);
  cursor: pointer; transition: all 0.15s;
  text-align: left;
}
.dropdown-item:hover { background: var(--bg-body); color: var(--primary); }
.dropdown-item.logout { color: var(--danger); }
.dropdown-item.logout:hover { background: #fef2f2; }

/* 移动端菜单按钮 */
.menu-toggle {
  display: none; width: 28px; height: 24px; position: relative;
}
.menu-toggle span,
.menu-toggle span::before,
.menu-toggle span::after {
  display: block; width: 100%; height: 2px;
  background: var(--text-secondary); border-radius: 2px;
  position: absolute; transition: all 0.3s;
}
.menu-toggle span { top: 50%; }
.menu-toggle span::before { content:''; top: -7px; }
.menu-toggle span::after { content:''; top: 7px; }
.menu-toggle span.open { background: transparent; }
.menu-toggle span.open::before { top: 0; transform: rotate(45deg); }
.menu-toggle span.open::after { top: 0; transform: rotate(-45deg); }

/* 移动端下拉菜单 */
.mobile-menu {
  display: none;
}

@media (max-width: 768px) {
  .nav-links { display: none; }
  .menu-toggle { display: block; }
  .mobile-menu {
    display: flex; flex-direction: column;
    background: rgba(255,255,255,0.95); backdrop-filter: blur(16px);
    border-top: 1px solid var(--border);
    padding: 0.75rem 1.5rem; gap: 0.15rem;
  }
  .mobile-link {
    padding: 0.65rem 0.5rem;
    font-size: 14px; color: var(--text-secondary);
    text-decoration: none; border-radius: 8px;
    transition: all 0.15s;
  }
  .mobile-link:hover, .mobile-link.router-link-exact-active {
    color: var(--primary); background: var(--primary-bg);
    font-weight: 500;
  }
  .mobile-link.danger { color: var(--danger); }
  .mobile-theme {
    display: flex; align-items: center; gap: 0.5rem;
    padding: 0.5rem 0.5rem; flex-wrap: wrap;
    border-top: 1px solid var(--border);
    margin-top: 0.25rem;
  }
  .mobile-theme-label { font-size: 13px; color: var(--text-secondary); }
  .mobile-theme-opt {
    padding: 0.35rem 0.7rem; border-radius: 16px; font-size: 12px;
    background: var(--bg-body); color: var(--text-secondary);
    border: 1px solid var(--border); transition: all 0.15s;
  }
  .mobile-theme-opt.active {
    background: var(--primary-bg); color: var(--primary);
    border-color: var(--border-accent); font-weight: 600;
  }
  .nav-inner { padding: 0 1rem; }
}

.slide-down-enter-active, .slide-down-leave-active { transition: all 0.2s ease; }
.slide-down-enter-from, .slide-down-leave-to { opacity: 0; transform: translateY(-8px); max-height: 0; }
</style>
