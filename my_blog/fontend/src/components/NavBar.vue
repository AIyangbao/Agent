<template>
  <nav class="navbar">
    <span class="nav-logo" @click="$router.push('/')">✦ 技术宅小窝</span>
    <div class="nav-links">
      <router-link to="/" class="nav-link">首页</router-link>
      <router-link to="/posts" class="nav-link">文章</router-link>
      <router-link v-if="user.isLoggedIn" to="/write" class="nav-link">写文章</router-link>

      <template v-if="!user.isLoggedIn">
        <button class="nav-btn" @click="$router.push('/auth')">登录 / 注册</button>
      </template>
      <template v-else>
        <div class="nav-user">
          <span>{{ user.username }}</span>
          <div
            class="avatar"
            :style="user.avatar ? { backgroundImage: 'url(' + user.avatar + ')' } : {}"
            @click="triggerUpload"
            title="点击更换头像"
          >
            <span v-if="!user.avatar">{{ user.initial }}</span>
          </div>
          <span class="logout-link" @click="handleLogout">退出</span>
          <input ref="fileInput" type="file" accept="image/jpeg,image/jpg,image/png" class="file-hidden" @change="onFileChange" />
        </div>
      </template>
    </div>
  </nav>
</template>

<script setup>
import { ref } from 'vue'
import { useUserStore } from '../store'
import { useRouter } from 'vue-router'

const user = useUserStore()
const router = useRouter()
const fileInput = ref(null)

function triggerUpload() {
  fileInput.value?.click()
}

function onFileChange(e) {
  const file = e.target.files[0]
  if (!file) return
  if (!file.type.match(/image\/(jpe?g|png)/)) {
    alert('仅支持 JPG / PNG 格式')
    return
  }
  const reader = new FileReader()
  reader.onload = () => {
    user.setAvatar(reader.result)
  }
  reader.readAsDataURL(file)
}

function handleLogout() {
  if (!confirm('确定要退出登录吗？')) return
  user.logout()
  router.push('/')
}
</script>

<style scoped>
.navbar {
  position: fixed; top: 0; left: 0; right: 0; height: 60px;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 2rem; z-index: 100;
  background: rgba(8, 4, 20, 0.6);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border);
}
.nav-logo {
  font-size: 18px; font-weight: 700;
  background: linear-gradient(90deg, var(--primary), var(--accent));
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  cursor: pointer; letter-spacing: 0.5px;
}
.nav-links { display: flex; gap: 1.5rem; align-items: center; }
.nav-link {
  font-size: 14px; color: var(--text-muted);
  cursor: pointer; transition: color 0.25s; text-decoration: none; letter-spacing: 0.3px;
}
.nav-link:hover, .router-link-active { color: var(--primary); }
.nav-btn {
  font-size: 13px; padding: 0.4rem 1.1rem;
  border-radius: 20px; border: 1px solid var(--border-accent);
  background: rgba(124, 58, 237, 0.15); color: var(--primary);
  cursor: pointer; transition: all 0.25s;
}
.nav-btn:hover { background: rgba(124, 58, 237, 0.35); border-color: var(--primary); }
.nav-user { display: flex; align-items: center; gap: 0.75rem; font-size: 14px; color: var(--text-muted); }
.avatar {
  width: 32px; height: 32px; border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  background-size: cover; background-position: center;
  display: flex; align-items: center; justify-content: center;
  font-size: 13px; font-weight: 600; color: white; cursor: pointer;
  transition: transform 0.25s; overflow: hidden;
  flex-shrink: 0;
}
.avatar:hover { transform: scale(1.15); }
.logout-link {
  font-size: 12px; color: var(--text-dim); cursor: pointer; transition: color 0.25s;
}
.logout-link:hover { color: #f87171; }
.file-hidden { display: none; }
@media (max-width: 640px) {
  .navbar { padding: 0 1rem; }
  .nav-links { gap: 0.75rem; }
}
</style>
