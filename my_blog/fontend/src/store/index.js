import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getMe } from '../api/auth'

export const useUserStore = defineStore('user', () => {
  const username = ref(null)
  const nickname = ref(null)
  const avatar = ref(null)
  const token = ref(null)

  const isLoggedIn = computed(() => !!username.value)
  const initial = computed(() => (nickname.value || username.value) ? (nickname.value || username.value)[0].toUpperCase() : '')
  const displayName = computed(() => nickname.value || username.value || '')

  async function login(name, accessToken) {
    username.value = name
    token.value = accessToken
    localStorage.setItem('blog_user', name)
    localStorage.setItem('blog_token', accessToken)
    // 登录后从后端拉最新资料（头像/昵称），避免退出再登录头像丢失
    try {
      const data = await getMe()
      setProfile({ nickname: data.nickname, avatar: data.avatar })
    } catch (e) {
      // 拉取失败不影响登录流程，进入个人中心会再次拉取
    }
  }

  function logout() {
    username.value = null
    nickname.value = null
    avatar.value = null
    token.value = null
    localStorage.removeItem('blog_user')
    localStorage.removeItem('blog_nickname')
    localStorage.removeItem('blog_avatar')
    localStorage.removeItem('blog_token')
  }

  function restore() {
    const saved = localStorage.getItem('blog_user')
    if (saved) username.value = saved
    const savedNick = localStorage.getItem('blog_nickname')
    if (savedNick) nickname.value = savedNick
    const savedAvatar = localStorage.getItem('blog_avatar')
    if (savedAvatar) avatar.value = savedAvatar
    const savedToken = localStorage.getItem('blog_token')
    if (savedToken) token.value = savedToken
  }

  function setAvatar(dataUrl) {
    avatar.value = dataUrl
    // 存真值、空值则删，避免 localStorage 写入字符串 "null" 导致导航栏 url('null') 裂图
    if (dataUrl) localStorage.setItem('blog_avatar', dataUrl)
    else localStorage.removeItem('blog_avatar')
  }

  // 资料保存后同步到 store + localStorage（导航栏头像/昵称实时更新）
  function setProfile({ nickname: nick, avatar: av }) {
    if (nick !== undefined) {
      nickname.value = nick || null
      if (nick) localStorage.setItem('blog_nickname', nick)
      else localStorage.removeItem('blog_nickname')
    }
    if (av !== undefined) setAvatar(av)
  }

  return { username, nickname, avatar, token, isLoggedIn, initial, displayName, login, logout, restore, setAvatar, setProfile }
})
