<template>
  <div class="hero">
    <span class="hero-tag">✦ 二次元 × 技术</span>
    <h1>二次元技术宅小窝</h1>
    <p>探索代码与二次元交汇的世界，记录技术成长的每一步足迹</p>
    <div class="hero-btns">
      <button class="btn-primary" @click="$router.push('/posts')">浏览文章 →</button>
      <a href="https://github.com/AIyangbao" target="_blank" class="btn-outline">Github</a>
    </div>
    <div class="hero-stats">
      <div class="stat">
        <div class="stat-num">{{ totalPosts }}</div>
        <div class="stat-label">篇文章</div>
      </div>
      <div class="stat">
        <div class="stat-num">{{ totalTags }}</div>
        <div class="stat-label">个标签</div>
      </div>
      <div class="stat">
        <div class="stat-num">{{ totalViews }}</div>
        <div class="stat-label">次阅读</div>
      </div>
    </div>
    <div class="social-bar">
      <a href="https://www.bilibili.com" target="_blank" class="social-link bilibili">
        <span class="social-icon">📺</span> Bilibili
      </a>
      <a href="https://www.douyin.com" target="_blank" class="social-link douyin">
        <span class="social-icon">🎵</span> 抖音
      </a>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { fetchPosts } from '../api/posts'

const totalPosts = ref(0)
const totalTags = 6   // Python, AI, Vue, Docker, FastAPI, 其他
const totalViews = ref(0)

onMounted(async () => {
  try {
    const data = await fetchPosts({ pageSize: 1 })
    totalPosts.value = data.total || 0
    // 视图统计暂用 total（等后端加 views 字段再替换）
    totalViews.value = data.total || 0
  } catch (e) {
    console.error('获取统计数据失败', e)
  }
})
</script>

<style scoped>
.hero {
  height: calc(100vh - 60px);
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  text-align: center; gap: 1.25rem; padding: 2rem;
}
.hero-tag {
  display: inline-block; font-size: 12px;
  padding: 0.3rem 0.9rem; border-radius: 20px;
  border: 1px solid var(--border-accent); color: var(--primary);
  letter-spacing: 1px; text-transform: uppercase;
  animation: fadeDown 0.6s ease both;
}
.hero h1 {
  font-size: clamp(2.2rem, 5vw, 3.5rem); font-weight: 800; line-height: 1.15;
  background: linear-gradient(135deg, #fff 0%, var(--primary) 60%, var(--accent) 100%);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  animation: fadeDown 0.7s ease 0.1s both;
}
.hero p {
  font-size: clamp(0.95rem, 2vw, 1.15rem); color: var(--text-muted);
  max-width: 500px; line-height: 1.7;
  animation: fadeDown 0.7s ease 0.2s both;
}
.hero-btns {
  display: flex; gap: 1rem; flex-wrap: wrap; justify-content: center;
  animation: fadeDown 0.7s ease 0.3s both;
}
.btn-primary {
  padding: 0.65rem 1.8rem; border-radius: 24px; border: none;
  background: linear-gradient(90deg, var(--primary-dark), #9333ea);
  color: white; font-size: 15px; font-weight: 600;
  cursor: pointer; transition: all 0.25s; letter-spacing: 0.3px;
}
.btn-primary:hover { transform: translateY(-2px); filter: brightness(1.1); }
.btn-outline {
  padding: 0.65rem 1.8rem; border-radius: 24px;
  border: 1px solid var(--border-accent); background: transparent;
  color: var(--text); font-size: 15px; cursor: pointer; transition: all 0.25s;
}
.btn-outline:hover { background: rgba(167,139,250,0.1); border-color: var(--primary); }
.hero-stats {
  display: flex; gap: 2.5rem; margin-top: 0.5rem;
  animation: fadeDown 0.7s ease 0.4s both;
}
.stat { text-align: center; }
.stat-num { font-size: 24px; font-weight: 700; color: var(--primary); }
.stat-label { font-size: 12px; color: var(--text-dim); margin-top: 2px; }
@media (max-width: 640px) { .hero-stats { gap: 1.5rem; } }

.social-bar {
  display: flex; gap: 1rem; flex-wrap: wrap; justify-content: center;
  animation: fadeDown 0.7s ease 0.5s both;
}
.social-link {
  display: inline-flex; align-items: center; gap: 0.4rem;
  padding: 0.5rem 1.5rem; border-radius: 24px;
  font-size: 14px; font-weight: 500; text-decoration: none;
  transition: all 0.25s; letter-spacing: 0.3px;
}
.social-icon { font-size: 16px; }
.bilibili {
  border: 1px solid rgba(251,114,153,0.4); color: #fb7299; background: rgba(251,114,153,0.08);
}
.bilibili:hover { background: rgba(251,114,153,0.18); transform: translateY(-2px); box-shadow: 0 4px 16px rgba(251,114,153,0.2); }
.douyin {
  border: 1px solid rgba(255,255,255,0.25); color: var(--text); background: rgba(255,255,255,0.06);
}
.douyin:hover { background: rgba(255,255,255,0.12); transform: translateY(-2px); box-shadow: 0 4px 16px rgba(255,255,255,0.08); }

@keyframes fadeDown {
  from { opacity: 0; transform: translateY(-18px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
