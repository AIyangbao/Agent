<template>
  <div id="app-root">
    <!-- 视频背景 -->
    <video autoplay muted loop playsinline class="bg-video">
      <source src="/流萤-飞萤的余辉 firefly HSR by时桐七夜.mp4" type="video/mp4" />
    </video>
    <div class="bg-overlay"></div>

    <NavBar />
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>

    <div class="scroll-top" :class="{ show: showScroll }" @click="scrollTop">↑</div>

    <Teleport to="body">
      <div class="toast" :class="toastClass">{{ toastMsg }}</div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, provide, onMounted } from 'vue'
import NavBar from './components/NavBar.vue'
import { useUserStore } from './store'

const user = useUserStore()
user.restore()

const showScroll = ref(false)
const toastMsg = ref('')
const toastType = ref('')

window.addEventListener('scroll', () => {
  showScroll.value = window.scrollY > 300
})

function scrollTop() { window.scrollTo({ top: 0, behavior: 'smooth' }) }

function showToast(msg, type = '') {
  toastMsg.value = msg
  toastType.value = type
  setTimeout(() => {
    toastMsg.value = ''
    toastType.value = ''
  }, 2800)
}

provide('toast', showToast)

const toastClass = computed(() => ({
  show: !!toastMsg.value,
  success: toastType.value === 'success',
  error: toastType.value === 'error'
}))
</script>

<script>
import { computed } from 'vue'
</script>

<style scoped>
.bg-video {
  position: fixed; top: 0; left: 0;
  width: 100%; height: 100%;
  object-fit: cover; z-index: -2;
}
.bg-overlay {
  position: fixed; top: 0; left: 0;
  width: 100%; height: 100%;
  background: linear-gradient(135deg, rgba(10,5,25,0.75) 0%, rgba(30,10,60,0.65) 100%);
  z-index: -1;
}
.scroll-top {
  position: fixed; bottom: 2rem; right: 1.5rem;
  width: 40px; height: 40px;
  border-radius: 50%;
  background: var(--bg-card);
  border: 1px solid var(--border-accent);
  color: var(--primary);
  font-size: 18px;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; opacity: 0; transition: opacity 0.3s, transform 0.3s;
  z-index: 50;
}
.scroll-top.show { opacity: 1; }
.scroll-top:hover { transform: translateY(-2px); }

.toast {
  position: fixed; bottom: 2rem; left: 50%;
  transform: translateX(-50%) translateY(4rem);
  background: var(--bg-card);
  border: 1px solid var(--border-accent);
  border-radius: var(--radius);
  padding: 0.75rem 1.5rem;
  font-size: 14px; color: var(--text);
  transition: transform 0.3s, opacity 0.3s;
  opacity: 0; z-index: 9999; pointer-events: none;
}
.toast.show { transform: translateX(-50%) translateY(0); opacity: 1; }
.toast.success { border-color: var(--success); color: var(--success); }
.toast.error { border-color: var(--danger); color: var(--danger); }
</style>
