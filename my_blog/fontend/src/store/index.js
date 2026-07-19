import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  const username = ref(null)
  const avatar = ref(null)
  const token = ref(null)

  const isLoggedIn = computed(() => !!username.value)
  const initial = computed(() => username.value ? username.value[0].toUpperCase() : '')

  function login(name, accessToken) {
    username.value = name
    token.value = accessToken
    localStorage.setItem('blog_user', name)
    localStorage.setItem('blog_token', accessToken)
  }

  function logout() {
    username.value = null
    avatar.value = null
    token.value = null
    localStorage.removeItem('blog_user')
    localStorage.removeItem('blog_avatar')
    localStorage.removeItem('blog_token')
  }

  function restore() {
    const saved = localStorage.getItem('blog_user')
    if (saved) username.value = saved
    const savedAvatar = localStorage.getItem('blog_avatar')
    if (savedAvatar) avatar.value = savedAvatar
    const savedToken = localStorage.getItem('blog_token')
    if (savedToken) token.value = savedToken
  }

  function setAvatar(dataUrl) {
    avatar.value = dataUrl
    localStorage.setItem('blog_avatar', dataUrl)
  }

  return { username, avatar, isLoggedIn, initial, login, logout, restore, setAvatar }
})
