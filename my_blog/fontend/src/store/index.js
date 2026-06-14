import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  const username = ref(null)
  const avatar = ref(null)

  const isLoggedIn = computed(() => !!username.value)
  const initial = computed(() => username.value ? username.value[0].toUpperCase() : '')

  function login(name) {
    username.value = name
    localStorage.setItem('blog_user', name)
  }

  function logout() {
    username.value = null
    avatar.value = null
    localStorage.removeItem('blog_user')
    localStorage.removeItem('blog_avatar')
  }

  function restore() {
    const saved = localStorage.getItem('blog_user')
    if (saved) username.value = saved
    const savedAvatar = localStorage.getItem('blog_avatar')
    if (savedAvatar) avatar.value = savedAvatar
  }

  function setAvatar(dataUrl) {
    avatar.value = dataUrl
    localStorage.setItem('blog_avatar', dataUrl)
  }

  return { username, avatar, isLoggedIn, initial, login, logout, restore, setAvatar }
})
