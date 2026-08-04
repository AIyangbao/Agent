<template>
  <div class="home-page">
    <!-- ====== Hero 区域（壁纸背景 + 标题） ====== -->
    <section class="hero-area">
      <div class="hero-content">
        <h1 class="hero-title">{{ displayTitle }}</h1>
        <p class="hero-subtitle">{{ displaySubtitle }}</p>
      </div>
    </section>

    <!-- ====== 三栏内容区 ====== -->
    <main class="content-area" :class="{ 'focus-mode': variant === 'focus' }">
      <!-- 左侧栏 -->
      <aside class="sidebar-left">
        <!-- 个人信息卡片 -->
        <div class="card profile-card">
          <div class="profile-avatar">
            <img src="/avatar-firefly.jpg" alt="流月" draggable="false" />
          </div>
          <h3 class="profile-name">流月</h3>
          <p class="profile-bio">Hello, I'm <span class="bio-accent">流月.</span></p>
          <p class="profile-desc">广州华商学院 · AI专业 · Python / Vue / FastAPI</p>
          <div class="social-icons">
            <a href="https://github.com/AIyangbao" target="_blank" class="soc-icon" title="GitHub">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/></svg>
            </a>
            <a href="mailto:194564638@qq.com" class="soc-icon" title="Email">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
            </a>
            <a href="https://blog.fireflyai.site" target="_blank" class="soc-icon" title="博客">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
            </a>
            <a href="/api/blogs/rss" target="_blank" class="soc-icon" title="RSS订阅" rel="noopener">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 11a9 9 0 0 1 9 9"/><path d="M4 4a16 16 0 0 1 16 16"/><circle cx="5" cy="19" r="1"/></svg>
            </a>
          </div>
        </div>

        <!-- 公告 -->
        <div class="card announcement-card" v-if="showAnnouncement">
          <div class="ann-header">
            <h4 class="card-title-sm" style="border:none;padding:0;margin:0;">📢 公告</h4>
            <button class="ann-close" @click="showAnnouncement = false" title="关闭">×</button>
          </div>
          <p class="ann-text">欢迎来到我的博客！这是个人技术博客，记录学习与项目心得 ✨</p>
          <a href="#" class="more-link small" style="margin-top:0.5rem;display:inline-block;" onclick="return false;">了解更多</a>
        </div>

        <!-- 音乐播放器 -->
        <div class="card music-card">
          <h4 class="card-title-sm">🎵 音乐</h4>
          <div class="music-now">
            <div class="music-cover" :class="{ spinning: isPlaying }" :style="coverBg(currentIndex)">
              <img v-if="currentSong && isImageUrl(currentSong.cover)" :src="currentSong.cover" :alt="currentSong.title" class="music-cover-img" />
              <span v-else>{{ currentSong?.cover || '🎵' }}</span>
            </div>
            <div class="music-info">
              <span class="music-name">{{ currentSong?.title || '暂无播放' }}</span>
              <span class="music-artist">{{ currentSong?.artist || '—' }}</span>
              <span v-if="playError" class="music-error">{{ playError }}</span>
            </div>
            <button class="mc-btn mc-list" title="播放列表" @click="showPlaylist = !showPlaylist">☰</button>
          </div>
          <div class="music-controls">
            <button class="mc-btn" title="上一首" @click="prevSong">⏮</button>
            <button class="mc-btn mc-play" title="播放/暂停" @click="togglePlay">{{ isPlaying ? '⏸' : '▶' }}</button>
            <button class="mc-btn" title="下一首" @click="nextSong">⏭</button>
          </div>
          <div class="music-progress" @click="seek">
            <div class="progress-bar"><div class="progress-fill" :style="{ width: musicProgress + '%' }"></div></div>
            <span class="progress-time">{{ formatTime(currentTime) }} / {{ formatTime(duration) }}</span>
          </div>
          <transition name="playlist-fade">
            <ul v-if="showPlaylist" class="music-list">
              <li v-for="(s, i) in playlist" :key="s.id" class="music-list-item" :class="{ active: i === currentIndex }" @click="playSong(i)">
                <span class="ml-cover" :style="coverBg(i)">
                  <img v-if="isImageUrl(s.cover)" :src="s.cover" :alt="s.title" class="ml-cover-img" />
                  <span v-else>{{ s.cover }}</span>
                </span>
                <span class="ml-info"><span class="ml-title">{{ s.title }}</span><span class="ml-artist">{{ s.artist }}</span></span>
                <span class="ml-eq" v-if="i === currentIndex && isPlaying"><i></i><i></i><i></i></span>
                <span class="ml-playing" v-else-if="i === currentIndex">正在播放</span>
              </li>
            </ul>
          </transition>
        </div>

        <!-- 分类 -->
        <div class="card category-card">
          <h4 class="card-title-sm">| 分类</h4>
          <div class="category-list">
            <div v-for="cat in fixedCategories" :key="cat.name" class="category-item" :class="{ 'cat-active': cat.name === activeCategory }" @click="$emit('category-change', cat.name)">
              <span class="cat-name">{{ cat.name }}</span>
              <span class="cat-count-badge">{{ cat.count }}</span>
            </div>
          </div>
        </div>

        <!-- 标签云 -->
        <div class="card tags-card" v-if="displayTags.length > 1">
          <h4 class="card-title-sm">| 标签</h4>
          <div class="tag-cloud">
            <router-link v-for="tag in displayTags.filter(t => t !== 'all')" :key="tag" :to="{ path: '/', query: { tag } }" class="cloud-tag">{{ tag }}</router-link>
          </div>
        </div>
      </aside>

      <!-- 中间：页面内容（slot） -->
      <section class="main-content">
        <slot />
      </section>

      <!-- 右侧栏 -->
      <aside class="sidebar-right">
        <!-- 最新动态 -->
        <div class="card activity-card">
          <div class="activity-header">
            <h4 class="card-title-sm" style="border:none;padding:0;margin:0;">动态</h4>
            <a href="#" class="more-link small" style="padding:0;" onclick="return false;">更多动态</a>
          </div>
          <div class="activity-list">
            <div class="activity-item" v-for="(item, i) in mockActivities" :key="i">
              <span class="activity-time">{{ item.time }}</span>
              <p class="activity-text">{{ item.text }}</p>
            </div>
          </div>
        </div>

        <!-- 站点统计 -->
        <div class="card stats-card">
          <h4 class="stats-title">站点统计</h4>
          <div class="stats-grid">
            <div class="stat-item" v-for="s in siteStats" :key="s.label">
              <span class="stat-icon" v-html="s.icon"></span>
              <span class="stat-label">{{ s.label }}</span>
              <strong>{{ s.value }}</strong>
            </div>
          </div>
        </div>

        <!-- 日历 -->
        <div class="card calendar-card">
          <div class="cal-header">
            <button class="cal-nav" @click.stop.prevent="prevMonth" type="button" title="上个月">&lt;</button>
            <span class="cal-title">{{ calYear }}年{{ calMonth }}月</span>
            <button class="cal-nav" @click.stop.prevent="nextMonth" type="button" title="下个月">&gt;</button>
            <button v-if="!isCurrentMonth" class="cal-today-btn" @click.stop.prevent="goToday" type="button" title="回到本月">⟲</button>
          </div>
          <table class="cal-table">
            <thead><tr><th>日</th><th>一</th><th>二</th><th>三</th><th>四</th><th>五</th><th>六</th></tr></thead>
            <tbody>
              <tr v-for="(week, wi) in calWeeks" :key="wi">
                <td v-for="(day, di) in week" :key="di" class="cal-day" :class="{ 'cal-empty': !day, 'cal-today': day === todayDay && isCurrentMonth, 'cal-other': day && !inCurrentMonth(wi * 7 + di) }">{{ day || '' }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 站点信息 -->
        <div class="card info-card">
          <h4 class="card-title-sm">ℹ️ 站点信息</h4>
          <div class="info-list">
            <div class="info-item"><span class="info-label">构建平台</span><span class="info-value">FastAPI + Vue3 + Docker</span></div>
            <div class="info-item"><span class="info-label">博客版本</span><span class="info-value">v2.0 (Firefly)</span></div>
            <div class="info-item"><span class="info-label">文章许可</span><span class="info-value">CC BY-NC-SA 4.0</span></div>
          </div>
          <button class="btn-expand-info" @click="showInfoDetail = !showInfoDetail">{{ showInfoDetail ? '∧ 收起' : '∨ 展开构建信息' }}</button>
          <transition name="fade">
            <div v-if="showInfoDetail" class="info-detail">
              <p>后端：Python 3.12 + FastAPI + SQLAlchemy + MySQL</p>
              <p>前端：Vue 3 + Vite + Pinia + Vue Router</p>
              <p>部署：Docker Compose + Nginx + SSL (阿里云 ECS)</p>
            </div>
          </transition>
        </div>
      </aside>
    </main>

    <!-- 页脚 -->
    <footer class="site-footer">
      <p class="footer-copy">© {{ currentYear }} <strong>FlowingMoon</strong>. All Rights Reserved.</p>
      <p class="footer-motto">"Chose the distance, so I walk on — through every wind and storm."</p>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, provide } from 'vue'
import { useRoute } from 'vue-router'
import { fetchPosts } from '../api/posts'
import { apiUrl } from '../config'

const props = defineProps({
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' },
  // 'blog' = 完整三栏（内容浏览页）；'focus' = 仅中间栏居中加宽，隐藏左右侧栏（编辑器/AI/登录等工具页）
  variant: { type: String, default: 'blog' },
})

defineEmits(['category-change'])

const route = useRoute()

// ========== Hero 标题 ==========
const displayTitle = computed(() => props.title || '技术宅小窝')
const displaySubtitle = computed(() => {
  if (props.subtitle) return props.subtitle
  return '记录学习与项目心得 · In Code We Trust |'
})

// ========== 公告 ==========
const showAnnouncement = ref(true)

// ========== 站点信息展开 ==========
const showInfoDetail = ref(false)

// ========== 音乐播放器 ==========
const playlist = ref([
  { id: 1, title: 'Take Me Hand', artist: 'Cecile Corbel', cover: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 60 60'%3E%3Crect width='60' height='60' fill='%2310b981'/%3E%3Ctext x='30' y='42' font-size='34' text-anchor='middle' fill='white'%3E%E2%99%AB%3C/text%3E%3C/svg%3E", src: '/music/take-me-hand.mp3' },
  { id: 2, title: 'Take Me Hand', artist: 'Cecile Corbel', cover: '🌟', src: '/music/take-me-hand.mp3' },
  { id: 3, title: 'Take Me Hand', artist: 'Cecile Corbel', cover: '🌃', src: '/music/take-me-hand.mp3' },
])

const COVER_GRADIENTS = [
  'linear-gradient(135deg,#ecfdf5,#d1fae5)',
  'linear-gradient(135deg,#e0f2fe,#bae6fd)',
  'linear-gradient(135deg,#fef3c7,#fde68a)',
  'linear-gradient(135deg,#fce7f3,#fbcfe8)',
]
function coverStyle(i) { return { background: COVER_GRADIENTS[i % COVER_GRADIENTS.length] } }
function isImageUrl(val) {
  if (typeof val !== 'string') return false
  const v = val.trim()
  return /^(https?:\/\/|\/|data:image\/)/.test(v) || /\.(jpe?g|png|webp|gif|svg|avif|bmp)$/i.test(v)
}
function coverBg(i) {
  const song = playlist.value[i]
  if (!song || !isImageUrl(song.cover)) return coverStyle(i)
  return {}
}

const audio = new Audio()
const currentIndex = ref(0)
const isPlaying = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const showPlaylist = ref(false)
const playError = ref('')
const currentSong = computed(() => playlist.value[currentIndex.value] || null)
const musicProgress = computed(() => (!duration.value) ? 0 : Math.min(100, Math.round((currentTime.value / duration.value) * 100)))

audio.addEventListener('timeupdate', () => { currentTime.value = audio.currentTime })
audio.addEventListener('loadedmetadata', () => { duration.value = audio.duration || 0 })
audio.addEventListener('ended', () => nextSong())
audio.addEventListener('error', () => { isPlaying.value = false; playError.value = '音频加载失败，请检查文件路径或网络' })

function playSong(index) {
  if (index < 0 || index >= playlist.value.length) return
  currentIndex.value = index
  const song = playlist.value[index]
  playError.value = ''
  audio.src = song.src
  audio.play().then(() => { isPlaying.value = true }).catch(() => { isPlaying.value = false })
}
function togglePlay() {
  if (!currentSong.value || !audio.src) { playSong(currentIndex.value); return }
  if (audio.paused) { audio.play().then(() => { isPlaying.value = true }).catch(() => {}) }
  else { audio.pause(); isPlaying.value = false }
}
function nextSong() { playSong((currentIndex.value + 1) % playlist.value.length) }
function prevSong() { playSong((currentIndex.value - 1 + playlist.value.length) % playlist.value.length) }
function seek(e) {
  if (!duration.value) return
  const bar = e.currentTarget, rect = bar.getBoundingClientRect()
  const ratio = (e.clientX - rect.left) / bar.width
  audio.currentTime = Math.max(0, Math.min(1, ratio)) * duration.value
}
function formatTime(sec) {
  if (!sec || isNaN(sec)) return '0:00'
  const m = Math.floor(sec / 60), s = Math.floor(sec % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}

// ========== 侧栏数据 ==========
const TECH_TAGS = ['Python', 'AI', 'Vue', 'Docker', 'FastAPI', 'Markdown', 'MDX', 'JavaScript']

// 文章数据（用于侧栏标签云/分类计数）
const totalPosts = ref(0)
const recentPosts = ref([])

const fixedCategories = computed(() => {
  const techCount = recentPosts.value.filter(p => (p.tags || []).some(t => TECH_TAGS.includes(t))).length
  const acgCount = recentPosts.value.length - techCount
  return [
    { name: '技术', count: techCount },
    { name: '二次元', count: acgCount },
  ]
})
const activeCategory = ref('')

// 共享给 HomePage 的筛选栏使用
provide('fixedCategories', fixedCategories)
provide('recentPosts', recentPosts)

const allTags = computed(() => {
  const set = new Set()
  recentPosts.value.forEach(p => (p.tags || []).forEach(t => set.add(t)))
  return ['all', ...set]
})
const displayTags = computed(() => allTags.value)

const tagCount = computed(() => allTags.value.length - 1) // 排除 'all'
const totalWords = ref(13767)
const startDate = new Date('2026-07-04')
const runningDays = Math.max(1, Math.ceil((Date.now() - startDate) / 86400000))
const currentYear = new Date().getFullYear()

const lastActivity = computed(() => {
  const dates = recentPosts.value.map(p => p.date).filter(Boolean).sort().reverse()
  if (!dates.length) return '刚刚'
  const d = new Date(dates[0])
  const days = Math.floor((Date.now() - d.getTime()) / 86400000)
  if (days <= 0) return '今天'
  if (days === 1) return '昨天'
  return days + ' 天前'
})

function formatNumber(n) {
  if (n >= 10000) return (n / 10000).toFixed(n % 10000 === 0 ? 0 : 1) + '万'
  return n.toLocaleString()
}

const siteStats = computed(() => [
  { icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14,2 14,8 20,8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>', label: '文章', value: totalPosts.value || 0 },
  { icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13,2 3,14 12,14 11,22 21,10 12,10"/></svg>', label: '动态', value: mockActivities.value.length },
  { icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>', label: '分类', value: fixedCategories.value.length || 0 },
  { icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>', label: '标签', value: tagCount.value },
  { icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>', label: '总字数', value: formatNumber(totalWords.value) },
  { icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12,6 12,12 16,14"/></svg>', label: '运行时长', value: runningDays + ' 天' },
  { icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23,6 13.5,15.5 8.5,10.5 1,18"/><polyline points="17,6 23,6 23,12"/></svg>', label: '最后活动', value: lastActivity.value },
])

// Mock 动态
const mockActivities = ref([
  { time: '刚刚', text: '完成了 AI Agent 架构的流式输出改造 ✨' },
  { time: '今天', text: '发布了新博客：从零搭建博客 AI Agent' },
  { time: '昨天', text: '修复了前端 Token 同步问题' },
])

// ========== 日历 ==========
const calYear = ref(new Date().getFullYear())
const calMonth = ref(new Date().getMonth() + 1)
const todayDay = new Date().getDate()
const isCurrentMonth = computed(() => {
  const now = new Date()
  return calYear.value === now.getFullYear() && calMonth.value === (now.getMonth() + 1)
})
function getDaysInMonth(y, m) { try { const d = new Date(y, m, 0).getDate(); return typeof d === 'number' && !isNaN(d) && d > 0 ? d : 30 } catch(e) { return 30 } }
function getFirstDayOfWeek(y, m) { try { const d = new Date(y, m - 1, 1).getDay(); return typeof d === 'number' && !isNaN(d) && d >= 0 && d <= 6 ? d : 0 } catch(e) { return 0 } }
const calWeeks = computed(() => {
  try {
    const y = Number(calYear.value) || 2026
    const m = Number(calMonth.value) || 8
    const days = getDaysInMonth(y, m), firstDay = getFirstDayOfWeek(y, m)
    // 安全守卫：非法值时返回当月默认日历
    if (!days || days < 28 || days > 31 || isNaN(days)) {
      return [[null,null,null,null,null,null,null],[1,2,3,4,5,6,7],[8,9,10,11,12,13,14],[15,16,17,18,19,20,21],[22,23,24,25,26,27,28],[29,30,31,null,null,null,null]]
    }
    const weeks = [], week = new Array(7).fill(null), dayIdx = 1
    // 第一周：从星期几开始填
    for (let i = firstDay; i < 7 && dayIdx <= days; i++) { week[i] = dayIdx++ }
    weeks.push([...week])
    // 剩余周
    while (dayIdx <= days) {
      week = new Array(7).fill(null)
      for (let i = 0; i < 7 && dayIdx <= days; i++) { week[i] = dayIdx++ }
      weeks.push(week)
    }
    return weeks.length > 0 ? weeks : [[1]]
  } catch(e) {
    console.error('[日历] 渲染异常', e)
    return [[null,null,null,null,null,null,null],[1,2,3,4,5,6,7],[8,9,10,11,12,13,14],[15,16,17,18,19,20,21],[22,23,24,25,26,27,28],[29,30,31,null,null,null,null]]
  }
})
function inCurrentMonth(idx) { return isCurrentMonth.value }
function prevMonth() { try { if (calMonth.value <= 1) { calMonth.value = 12; calYear.value-- } else { calMonth.value-- } } catch(e) { console.error('[日历] 上月切换失败', e) } }
function nextMonth() { try { if (calMonth.value >= 12) { calMonth.value = 1; calYear.value++ } else { calMonth.value++ } } catch(e) { console.error('[日历] 下月切换失败', e) } }
function goToday() { try { const now = new Date(); calYear.value = now.getFullYear(); calMonth.value = now.getMonth() + 1 } catch(e) { console.error('[日历] 回到本月失败', e) } }

// ========== 加载侧栏数据 ==========
async function loadSidebarData() {
  try {
    const data = await fetchPosts({ pageSize: 100 })
    const list = data.list || []
    recentPosts.value = formatPosts(list)
    totalPosts.value = data.total || list.length
    totalWords.value = list.reduce((sum, row) => {
      const b = row.Blog || row
      return sum + (b.content || '').length
    }, 0)
  } catch (e) {
    console.error('[MainLayout] 加载侧栏数据失败', e)
  }
}

// 拉取音乐列表
async function fetchMusicList() {
  try {
    const res = await fetch(apiUrl('/music/list'))
    if (!res.ok) return
    const json = await res.json()
    if (json && Array.isArray(json.data) && json.data.length) { playlist.value = json.data }
  } catch (e) { /* 后端未就绪时静默保留 demo 列表 */ }
}

function formatPosts(rows) {
  if (!Array.isArray(rows)) return []
  return rows.map(row => {
    const blog = row.Blog || row
    if (!blog || blog.id == null) return null
    const tags = row.name ? [row.name] : (blog.tags_name || [])
    const content = blog.content || ''
    return {
      id: blog.id,
      title: blog.title || '无标题',
      content,
      excerpt: content.length > 120 ? content.slice(0, 120) + '...' : '',
      create_time: blog.create_time || '',
      date: (blog.create_time || '').length >= 16 ? String(blog.create_time).replace('T', ' ').slice(0, 19) : (blog.create_time || ''),
      views: blog.views || 0,
      tags,
    }
  }).filter(Boolean)
}

onMounted(() => {
  loadSidebarData()
  fetchMusicList()
})

onUnmounted(() => {
  audio.pause()
  audio.src = ''
})
</script>

<style scoped>
.home-page { min-height: 100vh; position: relative; z-index: 1; }

/* ========== Hero 区域 ========== */
.hero-area {
  position: relative; width: 100%; height: 55vh; min-height: 360px;
  overflow: hidden; display: flex; align-items: center; justify-content: center;
  background: url('/bg-firefly.webp') center 25% / cover no-repeat;
}
.hero-area::after {
  content: ''; position: absolute; inset: 0; z-index: 1;
  background: linear-gradient(180deg, rgba(0,0,0,0) 45%, rgba(240,242,245,0.5) 80%, var(--bg-body) 100%);
}
html[data-theme='dark'] .hero-area::after {
  background: linear-gradient(180deg, rgba(0,0,0,0) 40%, rgba(15,23,42,0.6) 75%, var(--bg-body) 100%);
}
.hero-content { position: relative; z-index: 2; text-align: center; color: #fff; }
.hero-title {
  font-size: 2.6rem; font-weight: 700; letter-spacing: 2px; margin-bottom: 0.5rem;
  text-shadow: 0 2px 12px rgba(0,0,0,0.4);
}
.hero-subtitle {
  font-size: 1rem; font-weight: 400; opacity: 0.88; letter-spacing: 3px;
  text-shadow: 0 1px 6px rgba(0,0,0,0.35);
}

/* ========== 三栏布局 ========== */
.content-area {
  max-width: 1220px; margin: 0 auto; padding: 1.5rem 1.5rem 3rem;
  display: grid; grid-template-columns: 250px minmax(0, 1fr) 270px;
  gap: 1.25rem; align-items: start;
}

/* focus 变体：隐藏左右侧栏，中间内容居中加宽，用于编辑器/AI/登录等工具页 */
.content-area.focus-mode {
  grid-template-columns: minmax(0, 1fr);
  max-width: 960px;
  gap: 0;
}
.content-area.focus-mode .sidebar-left,
.content-area.focus-mode .sidebar-right { display: none; }
.content-area.focus-mode .main-content { max-width: 100%; }

/* ========== 卡片通用 ========== */
.card {
  background: var(--bg-card); backdrop-filter: blur(12px);
  border: 1px solid var(--border-strong); border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm); overflow: hidden;
}
.card-title-sm {
  font-size: 15px; font-weight: 700; color: var(--text);
  margin-bottom: 0.85rem; padding-bottom: 0.6rem; border-bottom: 1px solid var(--border-strong);
}

/* ========== 左栏 ========== */
.sidebar-left { display: flex; flex-direction: column; gap: 1rem; position: sticky; top: 76px; }

/* 个人信息 */
.profile-card { text-align: center; padding: 1.6rem 1.2rem; }
.profile-avatar {
  width: 108px; height: 108px; margin: 0 auto 0.85rem; border-radius: 14px;
  overflow: hidden; box-shadow: 0 6px 24px rgba(0,0,0,0.12);
}
.profile-avatar img { width: 100%; height: 100%; object-fit: cover; display: block; }
.profile-name {
  font-size: 20px; font-weight: 700; color: var(--text); margin-bottom: 0.25rem;
  position: relative; display: inline-block;
}
.profile-name::after {
  content: ''; position: absolute; left: 50%; transform: translateX(-50%);
  bottom: -4px; width: 60%; height: 2.5px; background: var(--primary); border-radius: 2px; opacity: 0.7;
}
.profile-bio { font-size: 13px; color: var(--text-secondary); font-weight: 400; margin-bottom: 0.2rem; }
.bio-accent { color: var(--primary); font-weight: 600; }
.profile-desc { font-size: 11.5px; color: var(--text-dim); line-height: 1.55; margin-bottom: 0.85rem; }

/* 社交图标 */
.social-icons { display: flex; justify-content: center; gap: 0.6rem; }
.soc-icon {
  width: 38px; height: 38px; border-radius: 7px; display: flex; align-items: center; justify-content: center;
  background: var(--primary); color: #fff; text-decoration: none; transition: all var(--transition);
}
.soc-icon svg { width: 17px; height: 17px; flex-shrink: 0; }
.soc-icon:hover { background: var(--primary-dark); transform: translateY(-2px) scale(1.08); }
html[data-theme='dark'] .soc-icon { background: rgba(51, 65, 85, 0.6); }
html[data-theme='dark'] .soc-icon:hover { background: rgba(71, 85, 105, 0.8); }

/* 公告 */
.announcement-card { padding: 1rem 1.2rem; border-left: 3px solid var(--primary); }
.ann-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem; }
.ann-close {
  width: 20px; height: 20px; border-radius: 50%; background: var(--bg-body);
  color: var(--text-dim); font-size: 14px; line-height: 1; display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: all 0.15s; border: none;
}
.ann-close:hover { background: var(--bg-body, #fef2f2); color: var(--danger); }
.ann-text { font-size: 12.5px; color: var(--text-secondary); line-height: 1.65; }

/* 音乐 */
.music-card { padding: 1rem 1.2rem; }
.music-now { display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.6rem; }
.music-cover {
  width: 42px; height: 42px; border-radius: 8px;
  background: linear-gradient(135deg, #ecfdf5, #d1fae5);
  display: flex; align-items: center; justify-content: center; font-size: 18px; flex-shrink: 0;
  transition: transform 0.3s;
}
.music-cover.spinning { animation: cover-spin 8s linear infinite; border-radius: 50%; }
@keyframes cover-spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.music-info { display: flex; flex-direction: column; gap: 1px; min-width: 0; flex: 1; }
.music-name { font-size: 12.5px; font-weight: 600; color: var(--text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.music-artist { font-size: 11px; color: var(--text-dim); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.music-error { font-size: 11px; color: #ef4444; margin-top: 2px; line-height: 1.3; }
.mc-list { font-size: 13px; }
.music-controls { display: flex; align-items: center; justify-content: center; gap: 0.35rem; margin-bottom: 0.5rem; }
.mc-btn {
  width: 28px; height: 28px; border-radius: 50%; background: var(--bg-body); border: 1px solid var(--border-strong);
  font-size: 11px; cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: all 0.15s; color: var(--text-secondary);
}
.mc-btn:hover { background: var(--primary-bg); color: var(--primary); border-color: var(--primary-light); }
.mc-play { width: 32px; height: 32px; background: var(--primary); color: #fff !important; border-color: var(--primary); font-size: 13px; }
.mc-play:hover { background: var(--primary-dark); }
.music-progress { display: flex; align-items: center; gap: 0.5rem; cursor: pointer; }
.progress-bar { flex: 1; height: 3px; background: var(--border-strong); border-radius: 99px; overflow: hidden; }
.progress-fill { height: 100%; background: var(--primary); border-radius: 99px; transition: width 0.25s linear; }
.progress-time { font-size: 10px; color: var(--text-dim); white-space: nowrap; }

/* 播放列表 */
.music-list { list-style: none; margin: 0.6rem 0 0; padding: 0.4rem 0 0; border-top: 1px solid var(--border-strong); display: flex; flex-direction: column; gap: 0.15rem; }
.music-list-item {
  display: flex; align-items: center; gap: 0.55rem; padding: 0.4rem 0.5rem; border-radius: 8px;
  cursor: pointer; transition: background 0.15s;
}
.music-list-item:hover { background: var(--bg-body); }
.music-list-item.active { background: rgba(16,185,129,0.1); }
.ml-cover { width: 30px; height: 30px; border-radius: 6px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; font-size: 14px; overflow: hidden; }
.music-cover-img, .ml-cover-img { width: 100%; height: 100%; object-fit: cover; border-radius: inherit; display: block; }
.ml-info { display: flex; flex-direction: column; min-width: 0; flex: 1; }
.ml-title { font-size: 12px; font-weight: 600; color: var(--text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.ml-artist { font-size: 10px; color: var(--text-dim); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.ml-playing { font-size: 10px; color: var(--primary); flex-shrink: 0; }
.ml-eq { display: flex; align-items: flex-end; gap: 2px; height: 14px; flex-shrink: 0; }
.ml-eq i { width: 3px; background: var(--primary); border-radius: 2px; animation: eq-bounce 0.8s ease-in-out infinite; }
.ml-eq i:nth-child(1) { height: 6px; animation-delay: 0s; }
.ml-eq i:nth-child(2) { height: 12px; animation-delay: 0.2s; }
.ml-eq i:nth-child(3) { height: 8px; animation-delay: 0.4s; }
@keyframes eq-bounce { 0%, 100% { transform: scaleY(0.4); } 50% { transform: scaleY(1); } }
.playlist-fade-enter-active, .playlist-fade-leave-active { transition: opacity 0.2s; }
.playlist-fade-enter-from, .playlist-fade-leave-to { opacity: 0; }

/* 分类 */
.category-card { padding: 1rem 1.15rem; }
.category-list { display: flex; flex-direction: column; gap: 0.3rem; }
.category-item {
  display: flex; align-items: center; justify-content: space-between; padding: 0.5rem 0.6rem;
  border-radius: 8px; text-decoration: none; transition: all 0.15s; font-size: 15px; cursor: pointer;
}
.category-item:hover { background: var(--primary-bg); }
.cat-active { background: rgba(16, 185, 129, 0.1); }
.cat-active .cat-name { color: var(--primary); }
.cat-name { color: var(--text); font-weight: 600; transition: color 0.15s; }
.category-item:hover .cat-name { color: var(--primary); }
.cat-count-badge {
  font-size: 11.5px; font-weight: 700; color: #fff; background: var(--primary);
  padding: 0.1rem 0.6rem; border-radius: 99px; min-width: 26px; text-align: center;
}

/* 标签云 */
.tags-card { padding: 1rem 1.15rem; }
.tag-cloud { display: flex; flex-wrap: wrap; gap: 0.4rem; }
.cloud-tag {
  padding: 0.3rem 0.7rem; border-radius: 10px; font-size: 12px;
  color: var(--text-secondary); background: rgba(80, 90, 110, 0.12);
  border: 1px solid rgba(100, 116, 139, 0.14); text-decoration: none;
  transition: all 0.15s; font-weight: 500;
}
.cloud-tag:hover { color: #fff; background: var(--primary); border-color: var(--primary); transform: translateY(-1px); }

/* ========== 中间主区域 ========== */
.main-content { min-width: auto; overflow: visible; }
.main-content > * { overflow: visible; }

/* ========== 右栏 ========== */
.sidebar-right { display: flex; flex-direction: column; gap: 1rem; position: sticky; top: 76px; }

/* 动态 */
.activity-card { padding: 1rem 1.2rem; }
.activity-header { display: flex; align-items: center; justify-content: space-between; }
.activity-list { display: flex; flex-direction: column; gap: 0.5rem; }
.activity-item { padding: 0.5rem 0; border-bottom: 1px dashed var(--border); }
.activity-item:last-child { border-bottom: none; }
.activity-time { font-size: 11px; color: var(--text-dim); display: block; margin-bottom: 0.2rem; }
.activity-text { font-size: 13px; color: var(--text-secondary); line-height: 1.5; }

/* 统计 */
.stats-card { padding: 1rem 1.15rem; }
.stats-title { font-size: 14px; font-weight: 700; color: var(--text); margin-bottom: 0.8rem; }
.stats-grid { display: flex; flex-direction: column; gap: 0.65rem; }
.stat-item {
  display: flex; align-items: center; gap: 0.55rem; padding: 0.4rem 0;
  font-size: 13px; color: var(--text);
}
.stat-icon {
  width: 18px; height: 18px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  color: var(--primary);
}
.stat-icon :deep(svg) { width: 100%; height: 100%; stroke: var(--primary); stroke-width: 2.2; }
.stat-label { flex: 1; color: var(--text-secondary); }
.stat-item strong { color: var(--text); font-size: 13.5px; font-weight: 700; }

/* 日历 */
.calendar-card { padding: 1rem 1.15rem; }
.cal-header { display: flex; align-items: center; justify-content: center; gap: 0.6rem; margin-bottom: 0.6rem; }
.cal-nav {
  width: 26px; height: 26px; border-radius: 6px; border: 1px solid var(--border-strong);
  background: var(--bg-card); color: var(--text-secondary); font-size: 14px;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: all 0.15s;
}
.cal-nav:hover { background: var(--primary-bg); color: var(--primary); border-color: var(--primary); }
.cal-title { font-size: 14px; font-weight: 600; color: var(--text); }
.cal-today-btn {
  width: 26px; height: 26px; border-radius: 6px; border: 1px solid var(--border-strong);
  background: var(--bg-card); color: var(--text-dim); font-size: 13px;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: all 0.15s;
}
.cal-today-btn:hover { background: var(--primary-bg); color: var(--primary); }
.cal-table { width: 100%; border-collapse: collapse; }
.cal-table th { font-size: 11px; color: var(--text-dim); font-weight: 500; padding: 0.3rem 0; }
.cal-day {
  text-align: center; padding: 0.35rem 0; font-size: 12.5px; color: var(--text-secondary);
  border-radius: 6px; cursor: default; transition: all 0.15s;
}
.cal-today { background: var(--primary); color: #fff !important; font-weight: 700; }
.cal-other { color: var(--text-dim); opacity: 0.5; }
.cal-empty { /* transparent placeholder */ }

/* 站点信息 */
.info-card { padding: 1rem 1.2rem; }
.info-list { display: flex; flex-direction: column; gap: 0.5rem; margin-bottom: 0.6rem; }
.info-item { display: flex; justify-content: space-between; font-size: 12.5px; }
.info-label { color: var(--text-dim); }
.info-value { color: var(--text-secondary); font-weight: 500; }
.btn-expand-info {
  width: 100%; padding: 0.45rem; border-radius: 8px; border: 1px solid var(--border-strong);
  background: var(--primary-bg); color: var(--text-secondary); font-size: 12px;
  cursor: pointer; transition: all 0.15s;
}
.btn-expand-info:hover { background: var(--primary); color: #fff; }
.info-detail { margin-top: 0.6rem; padding-top: 0.6rem; border-top: 1px solid var(--border); }
.info-detail p { font-size: 11.5px; color: var(--text-dim); line-height: 1.6; margin: 0.2rem 0; }
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

/* ========== 页脚 ========== */
.site-footer {
  text-align: center; padding: 2rem 1rem;
  border-top: 1px solid var(--border); margin-top: 2rem;
}
.footer-copy { font-size: 13px; margin-bottom: 0.3rem; color: var(--text-dim); }
.footer-copy strong { color: var(--primary); font-weight: 700; }
.footer-motto { font-size: 12px; font-style: italic; color: var(--text-dim); opacity: 0.75; }

/* ========== more-link 复用 ========== */
.more-link {
  font-size: 13px; color: var(--primary); text-decoration: none;
  font-weight: 500; white-space: nowrap; transition: color var(--transition);
}
.more-link:hover { color: var(--primary-dark); }
.more-link.small { font-size: 12px; }
</style>
