<template>
  <div id="app-root">
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
import { ref, provide, computed } from 'vue'
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

<style scoped>
#app-root {
  min-height: 100vh;
  position: relative;
}

.scroll-top {
  position: fixed; bottom: 2rem; right: 1.5rem;
  width: 40px; height: 40px;
  border-radius: 50%;
  background: var(--bg-card);
  border: 1px solid var(--border);
  color: var(--primary);
  font-size: 18px;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; opacity: 0; transition: opacity 0.3s, transform 0.3s;
  box-shadow: var(--shadow-md);
  z-index: 50;
}
.scroll-top.show { opacity: 1; }
.scroll-top:hover { transform: translateY(-2px); background: var(--primary); color: #fff; }

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
  box-shadow: var(--shadow-lg);
}
.toast.show { transform: translateX(-50%) translateY(0); opacity: 1; }
.toast.success { border-color: var(--success); color: var(--success); }
.toast.error { border-color: var(--danger); color: var(--danger); }
</style>
