<template>
  <div class="home-page">
    <!-- ====== Hero 区域（壁纸背景 + 标题，导航栏覆盖其上） ====== -->
    <section class="hero-area">
      <div class="hero-content">
        <h1 class="hero-title">{{ heroTitle }}</h1>
        <p class="hero-subtitle" v-if="!isDetailPage">记录学习与项目心得 · In Code We Trust |</p>
        <p class="hero-subtitle hero-detail-sub" v-else>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
          发布于 {{ detailPost?.date || '' }}
          <span class="hero-sub-sep">·</span>
          {{ detailWordCount }} 字
          <span class="hero-sub-sep">⊙</span>
          {{ detailReadTime }} 分钟 · 阅读时长
        </p>
      </div>
    </section>

    <!-- ====== 三栏内容区 ====== -->
    <main class="content-area">
      <aside class="sidebar-left">
        <!-- 个人信息卡片 -->
        <div class="card profile-card">
          <div class="profile-avatar">
            <img src="/avatar-firefly.jpg" alt="流月" draggable="false" />
          </div>
          <h3 class="profile-name">流月</h3>
          <p class="profile-bio">Hello, I'm <span class="bio-accent">流月.</span></p>
          <p class="profile-desc">广州华商学院 · AI专业 · Python / Vue / FastAPI</p>

          <!-- 社交图标（统一绿色线性） -->
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
            <div
              class="music-cover"
              :class="{ spinning: isPlaying }"
              :style="coverBg(currentIndex)"
            >
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

          <!-- 播放列表面板 -->
          <transition name="playlist-fade">
            <ul v-if="showPlaylist" class="music-list">
              <li
                v-for="(s, i) in playlist"
                :key="s.id"
                class="music-list-item"
                :class="{ active: i === currentIndex }"
                @click="playSong(i)"
              >
                <span class="ml-cover" :style="coverBg(i)">
                  <img v-if="isImageUrl(s.cover)" :src="s.cover" :alt="s.title" class="ml-cover-img" />
                  <span v-else>{{ s.cover }}</span>
                </span>
                <span class="ml-info">
                  <span class="ml-title">{{ s.title }}</span>
                  <span class="ml-artist">{{ s.artist }}</span>
                </span>
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
            <div
              v-for="cat in fixedCategories"
              :key="cat.name"
              class="category-item"
              :class="{ 'cat-active': activeTab === cat.name }"
              @click="activeTab = cat.name"
            >
              <span class="cat-name">{{ cat.name }}</span>
              <span class="cat-count-badge">{{ cat.count }}</span>
            </div>
          </div>
        </div>

        <!-- 标签云 -->
        <div class="card tags-card" v-if="allTags.length > 1">
          <h4 class="card-title-sm">| 标签</h4>
          <div class="tag-cloud">
            <router-link
              v-for="tag in allTags.filter(t => t !== 'all')"
              :key="tag"
              :to="{ path: '/', query: { tag } }"
              class="cloud-tag"
            >{{ tag }}</router-link>
          </div>
        </div>
      </aside>

      <!-- 中间：文章列表 / 分类总览 / 文章详情（路由视图过渡） -->
      <transition name="view-fade" mode="out-in">
      <section class="main-content" :key="viewKey">

        <!-- ====== 视图 D：文章详情（/posts/:id 路由） ====== -->
        <template v-if="isDetailPage">
          <!-- 加载中 -->
          <div v-if="detailLoading && !detailPost" class="detail-loading">
            <div class="loading-spinner"></div>
            <p>正在加载文章...</p>
          </div>

          <template v-else-if="detailPost">
            <!-- tab 行（跟主页一致） -->
            <div class="list-header card">
              <div class="tab-group">
                <button
                  class="tab-pill home-pill"
                  :class="{ active: false }"
                  @click="goHome"
                  title="回到首页"
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="tab-pill-icon"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9,22 9,12 15,12 15,22"/></svg>
                </button>
                <button
                  v-for="tab in tabs"
                  :key="tab.key"
                  class="tab-pill"
                  :class="{ active: activeTab === tab.key }"
                  @click="activeTab = tab.key; $router.push('/')"
                >
                  <svg v-if="tab.key === 'archive'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="tab-pill-icon"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9,22 9,12 15,12 15,22"/></svg>
                  {{ tab.label }}
                  <span v-if="tab.count !== undefined" class="tab-pill-count">{{ tab.count }}</span>
                </button>
              </div>
              <router-link to="/posts" class="more-link">更多 →</router-link>
            </div>

            <!-- 字数 + 阅读时间 -->
            <div class="detail-word-info">
              <span class="dwi-item">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="dwi-icon"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14,2 14,8 20,8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
                {{ detailWordCount }} 字
              </span>
              <span class="dwi-sep">⊙</span>
              <span class="dwi-item">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="dwi-icon"><circle cx="12" cy="12" r="10"/><polyline points="12,6 12,12 16,14"/></svg>
                {{ detailReadTime }} 分钟 · 阅读时长
              </span>
            </div>

            <!-- 绿色左边栏 + 标题 -->
            <div class="detail-title-block card">
              <div class="post-accent-bar"></div>
              <h1 class="detail-title">{{ detailPost.title }}</h1>
            </div>

            <!-- meta 行 -->
            <div class="detail-meta-row">
              <span class="dm-item">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="dm-icon"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                {{ detailPost.date || '未知日期' }}
              </span>
              <span class="dm-sep">|</span>
              <span class="dm-item">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="dm-icon"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14,2 14,8 20,8"/></svg>
                {{ detailPost.category }}
              </span>
              <span class="dm-sep">|</span>
              <span v-for="tag in (detailPost.tags || []).slice(0, 4)" :key="tag" class="dm-tag">#{{ tag }}</span>
            </div>

            <!-- 封面图 -->
            <div v-if="detailPost.cover_image" class="detail-cover">
              <img :src="detailPost.cover_image" :alt="detailPost.title" />
            </div>

            <!-- Markdown 正文 -->
            <article class="detail-body card" v-html="renderedContent"></article>

            <!-- 删除按钮 -->
            <div class="-detail-actions" v-if="isLoggedIn">
              <button class="btn-delete" @click="handleDeleteDetail">删除此文章</button>
            </div>

            <!-- 评论 -->
            <CommentSection :blogId="detailPost.id" :list="[]" />
          </template>

          <!-- 加载失败 -->
          <div v-else-if="!detailLoading && !detailPost" class="empty-state">
            <span class="empty-icon">😵</span>
            <p>文章加载失败或不存在</p>
            <button class="btn-empty" @click="$router.push('/')">返回首页</button>
          </div>
        </template>

        <!-- ====== 视图 F：AI 对话助手（/ai 路由） ====== -->
        <template v-if="isAIPage">
          <!-- Tab 行 -->
          <div class="list-header card">
            <div class="tab-group">
              <button
                class="tab-pill home-pill"
                :class="{ active: activeTab === 'home' }"
                @click="goHome"
                title="回到首页"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="tab-pill-icon"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9,22 9,12 15,12 15,22"/></svg>
              </button>
              <button
                v-for="tab in tabs"
                :key="tab.key"
                class="tab-pill"
                :class="{ active: activeTab === tab.key }"
                @click="selectTab(tab.key)"
              >
                {{ tab.label }}
                <span v-if="tab.count !== undefined" class="tab-pill-count">{{ tab.count }}</span>
              </button>
            </div>
            <router-link to="/category" class="more-link">更多 →</router-link>
          </div>

          <!-- AI 聊天容器 -->
          <div class="ai-chat-wrapper card">
            <!-- 顶部标题栏 -->
            <div class="chat-header">
              <div class="chat-header-left">
                <span class="chat-icon">🤖</span>
                <div>
                  <h2>AI 对话助手</h2>
                  <p class="chat-subtitle">
                    <span v-if="aiApiOnline" class="dot dot-online"></span>
                    <span v-else class="dot dot-offline"></span>
                    {{ aiStatusText }}
                  </p>
                </div>
              </div>
              <button class="btn-clear" @click="aiClearChat" v-if="aiMessages.length">清空对话</button>
            </div>

            <!-- 消息区域 -->
            <div class="chat-messages" ref="aiMsgContainer">
              <!-- 空状态欢迎语 -->
              <div v-if="aiMessages.length === 0" class="welcome">
                <div class="welcome-icon">✨</div>
                <h3>你好，我是你的 AI 助手</h3>
                <p>可以问我关于技术的问题，或者聊聊你的想法</p>
                <div class="suggestions">
                  <button v-for="q in aiQuickQuestions" :key="q" class="sug-btn" @click="aiSendMessage(q)">
                    {{ q }}
                  </button>
                </div>
              </div>

              <!-- 消息列表 -->
              <div
                v-for="(msg, i) in aiMessages"
                :key="i"
                class="msg-row"
                :class="msg.role"
              >
                <div class="msg-bubble" :class="msg.role">
                  <div class="msg-avatar">
                    <template v-if="msg.role === 'user'">
                      <img v-if="user.avatar" :src="user.avatar" class="avatar-img" alt="avatar" />
                      <span v-else class="avatar-placeholder">{{ user.initial || '🧑‍💻' }}</span>
                    </template>
                    <span v-else>🤖</span>
                  </div>
                  <div class="msg-content">
                    <div v-if="msg.role === 'assistant' && msg.streaming" class="user-text" style="white-space:pre-wrap">{{ msg.content }}</div>
                    <div v-else-if="msg.role === 'assistant'" class="markdown-body" v-html="renderMarkdown(msg.content)"></div>
                    <div v-else class="user-text">{{ msg.content }}</div>
                  </div>
                </div>
              </div>

              <!-- 加载中 -->
              <div v-if="aiLoading" class="msg-row assistant">
                <div class="msg-bubble assistant typing">
                  <div class="msg-avatar">🤖</div>
                  <div class="typing-dots">
                    <span></span><span></span><span></span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 输入区域 -->
            <div class="chat-input-area">
              <textarea
                ref="aiInputRef"
                v-model="aiInput"
                class="chat-input"
                placeholder="输入消息，Enter 发送，Shift+Enter 换行..."
                rows="1"
                @keydown="aiOnKeydown"
                @input="aiAutoResize"
                :disabled="aiLoading"
              ></textarea>
              <button
                class="btn-send"
                :disabled="!aiInput.trim() || aiLoading"
                @click="aiSendMessage()"
                title="发送 (Enter)"
              >
                <span v-if="!aiLoading">↑</span>
                <span v-else class="spinner"></span>
              </button>
            </div>
          </div>
        </template>

        <!-- ====== 视图 G：写文章编辑器（/write 路由） ====== -->
        <template v-if="isEditorPage">
          <!-- Tab 行 -->
          <div class="list-header card">
            <div class="tab-group">
              <button
                class="tab-pill home-pill"
                :class="{ active: activeTab === 'home' }"
                @click="goHome"
                title="回到首页"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="tab-pill-icon"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9,22 9,12 15,12 15,22"/></svg>
              </button>
              <button
                v-for="tab in tabs"
                :key="tab.key"
                class="tab-pill"
                :class="{ active: activeTab === tab.key }"
                @click="selectTab(tab.key)"
              >
                {{ tab.label }}
                <span v-if="tab.count !== undefined" class="tab-pill-count">{{ tab.count }}</span>
              </button>
            </div>
            <router-link to="/category" class="more-link">更多 →</router-link>
          </div>

          <!-- 编辑器卡片 -->
          <div class="editor-wrap card">
            <!-- 标题栏：写新文章 + 取消/发布按钮 -->
            <div class="editor-header-row">
              <h2 class="editor-heading">写新文章</h2>
              <div class="editor-actions-row">
                <button class="btn-editor btn-editor-outline" @click="$router.push('/')">取消</button>
                <button class="btn-editor btn-editor-primary" @click="editorPublish" :disabled="editorPublishing">
                  {{ editorPublishing ? '发布中...' : '发布' }}
                </button>
              </div>
            </div>

            <!-- 文章标题输入 -->
            <input type="text" class="editor-title-input" v-model="editorTitle" placeholder="文章标题..." />

            <!-- 标签选择行 -->
            <div class="editor-meta-row">
              <select v-model="editorTag" class="editor-select">
                <option value="">选择标签</option>
                <option v-for="t in PREDEFINED_TAGS" :key="t" :value="t">{{ t }}</option>
              </select>
              <input type="text" v-model="editorExtraTags" placeholder="其他标签（逗号分隔）" class="editor-extra-input" />
            </div>

            <!-- 工具栏 -->
            <div class="editor-toolbar">
              <button class="toolbar-btn" title="加粗" @click="editorInsert('**', '**')"><b>B</b></button>
              <button class="toolbar-btn" title="斜体" @click="editorInsert('*', '*')"><i>I</i></button>
              <button class="toolbar-btn" title="标题" @click="editorInsert('## ', '')">H</button>
              <button class="toolbar-btn" title="代码块" @click="editorInsert('```\n', '\n```')">{ }</button>
              <button class="toolbar-btn" title="行内代码" @click="editorInsert('`', '`')">`</button>
              <button class="toolbar-btn" title="引用" @click="editorInsert('> ', '')">❝</button>
              <button class="toolbar-btn" title="无序列表" @click="editorInsert('- ', '')">•</button>
              <button class="toolbar-btn" title="有序列表" @click="editorInsert('1. ', '')">1.</button>
              <button class="toolbar-btn" title="分割线" @click="editorInsert('\n---\n', '')">—</button>
            </div>

            <!-- Markdown 内容区 -->
            <textarea
              ref="editorRef"
              class="editor-textarea"
              v-model="editorContent"
              placeholder="用 Markdown 写下你的内容...&#10;&#10;## 一级标题&#10;&#10;正文内容..."
            ></textarea>
          </div>
        </template>

        <template v-if="isCategoryPage">
          <!-- Tab 行（🏠 归档 / 技术 / 二次元） -->
          <div class="list-header card">
            <div class="tab-group">
              <button
                class="tab-pill home-pill"
                :class="{ active: activeTab === 'home' && !isCategoryPage }"
                @click="goHome"
                title="回到首页"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="tab-pill-icon"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9,22 9,12 15,12 15,22"/></svg>
              </button>
              <button
                v-for="tab in tabs"
                :key="tab.key"
                class="tab-pill"
                :class="{ active: activeTab === tab.key }"
                @click="selectTab(tab.key)"
              >
                <svg v-if="tab.key === 'archive'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="tab-pill-icon"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2 2z"/><polyline points="9,22 9,12 15,12 15,22"/></svg>
                {{ tab.label }}
                <span v-if="tab.count !== undefined" class="tab-pill-count">{{ tab.count }}</span>
              </button>
            </div>
            <router-link to="/category" class="more-link" :class="{ 'more-pill': isCategoryPage }">更多 →</router-link>
          </div>

          <!-- 标题栏 -->
          <div class="list-header card cat-overview-header">
            <h2 class="cat-overview-title">分类</h2>
            <p class="cat-overview-sub">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="cat-sub-icon"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
              全部分类 · {{ totalPosts || recentPosts.length }} 篇文章
            </p>
          </div>

          <!-- 分类卡片网格 -->
          <div class="cat-grid">
            <div
              v-for="(cat, i) in fixedCategories"
              :key="cat.name"
              class="cat-card"
              :style="{ animationDelay: i * 0.06 + 's' }"
              @click="activeTab = cat.name; $router.push({ path: '/', query: { cat: cat.name } })"
            >
              <div class="cat-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
              </div>
              <div class="cat-info">
                <h3 class="cat-name">{{ cat.name }}</h3>
                <span class="cat-count">{{ cat.count }} 篇文章</span>
              </div>
              <div class="cat-arrow">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9,18 15,12 9,6"/></svg>
              </div>
            </div>
          </div>

          <div v-if="!fixedCategories.length" class="empty-state">
            <span class="empty-icon">📂</span>
            <p>还没有任何分类</p>
          </div>
        </template>

        <!-- ====== 视图 E：标签总览（/tags）或 标签筛选（/?tag=xxx） ====== -->
        <template v-if="isTagsPage && !isDetailPage">
          <!-- Tab 行 -->
          <div class="list-header card">
            <div class="tab-group">
              <button
                class="tab-pill home-pill"
                :class="{ active: activeTab === 'home' && !isTagsPage }"
                @click="goHome"
                title="回到首页"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="tab-pill-icon"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9,22 9,12 15,12 15,22"/></svg>
              </button>
              <button
                v-for="tab in tabs"
                :key="tab.key"
                class="tab-pill"
                :class="{ active: activeTab === tab.key }"
                @click="selectTab(tab.key)"
              >
                <svg v-if="tab.key === 'archive'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="tab-pill-icon"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9,22 9,12 15,12 15,22"/></svg>
                {{ tab.label }}
                <span v-if="tab.count !== undefined" class="tab-pill-count">{{ tab.count }}</span>
              </button>
            </div>
            <router-link to="/tags" class="more-link" :class="{ 'more-pill': isTagsPage && !activeTag }">更多 →</router-link>
          </div>

          <!-- 标签总览页（/tags，无 tag 参数） -->
          <template v-if="isTagsPage && !activeTag">
            <!-- 标题栏 -->
            <div class="list-header card cat-overview-header">
              <h2 class="cat-overview-title">标签</h2>
              <p class="cat-overview-sub">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="cat-sub-icon"><path d="M20.59 13.41l-7.17 7.17a2 2 0 01-2.83 0L2 12V2h10l8.59 8.59a2 2 0 010 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>
                全部标签 · {{ tagCounts.length }} 个标签
              </p>
            </div>

            <!-- 标签云（带数量） -->
            <div class="tag-overview-cloud card">
              <router-link
                v-for="tc in tagCounts"
                :key="tc.name"
                :to="{ path: '/', query: { tag: tc.name } }"
                class="tag-chip"
              >
                {{ tc.name }}
                <span class="tag-chip-count">{{ tc.count }}</span>
              </router-link>
            </div>

            <!-- Top 10 排行榜 -->
            <div class="card top10-card">
              <h4 class="top10-title">Top 10</h4>
              <div class="top10-list">
                <div v-for="(tt, i) in topTags" :key="tt.name" class="top10-item">
                  <span class="top10-rank">{{ i + 1 }}</span>
                  <span class="top10-name">#{{ tt.name }}</span>
                  <div class="top10-bar-wrap">
                    <div class="top10-bar" :style="{ width: (tt.count / topTags[0].count * 100) + '%' }"></div>
                  </div>
                  <span class="top10-count">{{ tt.count }} 篇文章</span>
                </div>
              </div>
            </div>
          </template>

          <!-- 标签筛选页（/?tag=xxx） -->
          <template v-else>
            <!-- 面包屑 + 统计 -->
            <div class="archive-header" style="overflow:visible;">
              <div class="archive-breadcrumb" style="overflow:visible;">
                <span class="bc-label">标签</span>
                <span class="bc-sep">/</span>
                <span class="bc-value" style="display:inline-block;white-space:nowrap;overflow:visible;">#{{ activeTag }}</span>
                <span class="bc-count">{{ tagFilteredPosts.length }} 篇文章</span>
              </div>
            </div>

            <!-- 统计行 -->
            <div class="archive-stats" @click="toggleYearCollapse">
              <span class="archive-total">{{ currentYear }}<span class="stat-dot">○</span></span>
              <strong>{{ tagFilteredPosts.length }}</strong> 篇文章
              <span class="archive-toggle" :class="{ collapsed: yearCollapsed }">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9,18 15,12 9,6"/></svg>
              </span>
            </div>

            <!-- 时间线列表 -->
            <transition name="collapse-tl">
              <div v-if="!yearCollapsed" class="timeline-list">
                <div class="timeline-track"></div>
                <template v-for="(group, gi) in postsByDateTag" :key="group.date">
                  <span class="tl-date">{{ group.date }}</span>
                  <div class="tl-dot"></div>
                  <div class="tl-posts">
                    <div v-for="post in group.posts" :key="post.id" class="tl-post-item" @click="$router.push('/posts/' + post.id)">
                      <span class="tl-cat-badge">{{ (post.tags || []).some(t => TECH_TAGS.includes(t)) ? '技术' : '二次元' }}</span>
                      <span class="tl-title">{{ post.title }}</span>
                      <span class="tl-tags">
                        <span v-for="t in (post.tags || []).slice(0, 3)" :key="t" class="tl-tag">#{{ t }}</span>
                        <span v-if="(post.tags || []).length > 3" class="tl-tag tl-tag-more"># ...</span>
                      </span>
                    </div>
                  </div>
                </template>
              </div>
            </transition>

            <div v-if="!tagFilteredPosts.length" class="empty-state">
              <span class="empty-icon">🏷️</span>
              <p>该标签下暂无文章</p>
            </div>
          </template>
        </template>
        <template v-else>
        <template v-if="!isAIPage && !isEditorPage && !isCategoryPage && !(isTagsPage && !isDetailPage)">
        <div class="list-header card">
          <div class="tab-group">
            <!-- 主页小屋子 -->
            <button
              class="tab-pill home-pill"
              :class="{ active: activeTab === 'home' }"
              @click="goHome"
              title="回到首页"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="tab-pill-icon"><path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9,22 9,12 15,12 15,22"/></svg>
            </button>
            <button
              v-for="tab in tabs"
              :key="tab.key"
              class="tab-pill"
              :class="{ active: activeTab === tab.key }"
              @click="selectTab(tab.key)"
            >
              {{ tab.label }}
              <span v-if="tab.count !== undefined" class="tab-pill-count">{{ tab.count }}</span>
            </button>
          </div>
          <router-link to="/category" class="more-link">更多 →</router-link>
        </div>

        <!-- 视图 H：首页卡片列表（activeTab === 'home'） -->
        <div v-if="activeTab === 'home'" class="post-list">
          <template v-if="filteredPosts.length">
            <article
              v-for="(post, i) in filteredPosts"
              :key="post.id"
              class="post-card"
              :style="{ animationDelay: i * 0.06 + 's' }"
              @click="$router.push('/posts/' + post.id)"
            >
              <div class="post-accent-bar"></div>
              <div class="post-body">
                <h3 class="post-title">{{ post.title }}</h3>
                <div class="post-meta-row">
                  <span class="meta-item"><svg class="meta-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg> {{ post.date || '1970-01-01' }}</span>
                  <span class="meta-sep">|</span>
                  <span class="meta-item"><svg class="meta-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14,2 14,8 20,8"/></svg> {{ (post.tags || []).some(t => TECH_TAGS.includes(t)) ? '技术' : '二次元' }}</span>
                </div>
                <p class="post-excerpt">{{ post.excerpt || '暂无摘要...' }}</p>
                <div class="post-tag-row">
                  <span v-for="t in (post.tags || []).slice(0, 5)" :key="t" class="post-hash-tag">#{{ t }}</span>
                </div>
              </div>
              <div v-if="post.cover_image" class="post-cover">
                <img :src="post.cover_image" :alt="post.title" loading="lazy" />
              </div>
              <div v-else class="post-arrow">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9,18 15,12 9,6"/></svg>
              </div>
            </article>
          </template>
          <div v-else class="empty-state">
            <span class="empty-icon">📭</span>
            <p>还没有发布任何文章</p>
            <button class="btn-empty" @click="$router.push('/write')" v-if="isLoggedIn">写第一篇 →</button>
          </div>
        </div>

        <!-- 视图 A：归档时间线（activeTab === 'archive'，所有文章按日期排序） -->
        <div v-if="activeTab === 'archive'" class="archive-view">
          <!-- 统计行（可折叠） -->
          <div class="archive-stats" @click="toggleYearCollapse">
            <span class="archive-total">{{ archiveYear }}<span class="stat-dot">○</span></span>
            <strong>{{ recentPosts.length }}</strong> 篇文章
            <span class="archive-toggle" :class="{ collapsed: yearCollapsed }">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9,18 15,12 9,6"/></svg>
            </span>
          </div>

          <!-- 时间线列表 -->
          <transition name="collapse-tl">
            <div v-if="!yearCollapsed" class="timeline-list">
              <div class="timeline-track"></div>
              <div v-for="(group, gi) in allPostsByDate" :key="group.date" class="timeline-group">
                <span class="tl-date">{{ group.date }}</span>
                <div class="tl-dot"></div>
                <div class="tl-posts">
                  <div v-for="post in group.posts" :key="post.id" class="tl-post-item" @click="$router.push('/posts/' + post.id)">
                    <span class="tl-cat-badge">{{ (post.tags || []).some(t => TECH_TAGS.includes(t)) ? '技术' : '二次元' }}</span>
                    <span class="tl-title">{{ post.title }}</span>
                    <span class="tl-tags">
                      <span v-for="t in (post.tags || []).slice(0, 3)" :key="t" class="tl-tag">#{{ t }}</span>
                      <span v-if="(post.tags || []).length > 3" class="tl-tag tl-tag-more"># ...</span>
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </transition>

          <div v-if="!recentPosts.length" class="empty-state">
            <span class="empty-icon">📭</span>
            <p>还没有发布任何文章</p>
          </div>
        </div>

        <!-- 视图 B：分类时间线归档（activeTab === 分类名，技术/二次元等） -->
        <div v-if="!['home','archive'].includes(activeTab)" class="archive-view">
          <!-- 面包屑 + 统计 -->
          <div class="archive-header">
            <div class="archive-breadcrumb">
              <span class="bc-label">分类</span>
              <span class="bc-sep">/</span>
              <span class="bc-value">{{ activeTab }}</span>
              <span class="bc-count">{{ filteredPosts.length }} 篇文章</span>
            </div>
          </div>

          <!-- 统计行（可折叠） -->
          <div class="archive-stats" @click="toggleYearCollapse">
            <span class="archive-total">{{ currentYear }}<span class="stat-dot">○</span></span>
            <strong>{{ filteredPosts.length }}</strong> 篇文章
            <span class="archive-toggle" :class="{ collapsed: yearCollapsed }">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9,18 15,12 9,6"/></svg>
            </span>
          </div>

          <!-- 时间线列表（可隐藏） -->
          <transition name="collapse-tl">
            <div v-if="!yearCollapsed" class="timeline-list">
              <!-- 贯穿竖线 -->
              <div class="timeline-track"></div>
              <div v-for="(group, gi) in postsByDate" :key="group.date" class="timeline-group">
                <span class="tl-date">{{ group.date }}</span>
                <div class="tl-dot"></div>
                <div class="tl-posts">
                  <div v-for="post in group.posts" :key="post.id" class="tl-post-item" @click="$router.push('/posts/' + post.id)">
                    <span class="tl-cat-badge">{{ (post.tags || []).some(t => TECH_TAGS.includes(t)) ? '技术' : '二次元' }}</span>
                    <span class="tl-title">{{ post.title }}</span>
                    <span class="tl-tags">
                      <span v-for="t in (post.tags || []).slice(0, 3)" :key="t" class="tl-tag">#{{ t }}</span>
                      <span v-if="(post.tags || []).length > 3" class="tl-tag tl-tag-more"># ...</span>
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </transition>

          <div v-if="!filteredPosts.length" class="empty-state">
            <span class="empty-icon">📭</span>
            <p>该分类下暂无文章</p>
          </div>
        </div>
        </template>
        </template>
      </section>
      </transition>

      <!-- 右侧：统计 + 信息 -->
      <aside class="sidebar-right">
        <!-- 最新动态（mock） -->
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
            <button class="cal-nav" @click="prevMonth" title="上个月">&lt;</button>
            <span class="cal-title">{{ calYear }}年{{ calMonth }}月</span>
            <button class="cal-nav" @click="nextMonth" title="下个月">&gt;</button>
            <button
              v-if="!isCurrentMonth"
              class="cal-today-btn"
              @click="goToday"
              title="回到本月"
            >⟲</button>
          </div>
          <table class="cal-table">
            <thead>
              <tr><th>日</th><th>一</th><th>二</th><th>三</th><th>四</th><th>五</th><th>六</th></tr>
            </thead>
            <tbody>
              <tr v-for="(week, wi) in calWeeks" :key="wi">
                <td
                  v-for="(day, di) in week"
                  :key="di"
                  class="cal-day"
                  :class="{ 'cal-empty': !day, 'cal-today': day === todayDay && isCurrentMonth, 'cal-other': day && !inCurrentMonth(wi * 7 + di) }"
                >{{ day || '' }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 站点信息 -->
        <div class="card info-card">
          <h4 class="card-title-sm">ℹ️ 站点信息</h4>
          <div class="info-list">
            <div class="info-item">
              <span class="info-label">构建平台</span>
              <span class="info-value">FastAPI + Vue3 + Docker</span>
            </div>
            <div class="info-item">
              <span class="info-label">博客版本</span>
              <span class="info-value">v2.0 (Firefly)</span>
            </div>
            <div class="info-item">
              <span class="info-label">文章许可</span>
              <span class="info-value">CC BY-NC-SA 4.0</span>
            </div>
          </div>
          <button class="btn-expand-info" @click="showInfoDetail = !showInfoDetail">
            {{ showInfoDetail ? '∧ 收起' : '∨ 展开构建信息' }}
          </button>
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
import { ref, computed, onMounted, onUnmounted, watch, reactive, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchPosts, fetchPostById, deletePost, createPost } from '../api/posts'
import { chatWithAIStream, fetchAIHistory, clearAIHistory } from '../api/ai'
import { useUserStore } from '../store'
import CommentSection from '../components/CommentSection.vue'
import { renderMarkdown } from '../utils/markdown.js'

const route = useRoute()
const $router = useRouter()
const user = useUserStore()
const isLoggedIn = computed(() => user.isLoggedIn)

// 数据
const totalPosts = ref(0)
const recentPosts = ref([])
const activeTab = ref('home')
const showAnnouncement = ref(true)
const showInfoDetail = ref(false)

// 年份折叠状态
const yearCollapsed = ref(false)

function toggleYearCollapse() {
  yearCollapsed.value = !yearCollapsed.value
}

// 切换到指定 tab（中间栏 + 顶部导航栏共用，保证视图一致）
function selectTab(key) {
  activeTab.value = key
  if (key === 'archive') {
    $router.push('/?view=archive')
  } else if (key === 'home') {
    goHome()
  } else {
    // 分类 tab：用 ?cat= 激活对应分类时间线
    $router.push({ path: '/', query: { cat: key } })
  }
}

// 回到首页（小屋子按钮 + 导航栏主页链接）
function goHome() {
  activeTab.value = 'home'
  activeTag.value = ''
  // 如果不在干净首页（带分类/视图/标签参数），跳回去清掉 query
  if (route.path !== '/' || route.query.cat || route.query.view || route.query.tag) {
    $router.push('/')
  }
}

// 当前年份（用于归档视图统计行）
const currentYear = new Date().getFullYear()

// ========== 音乐播放器（HTML5 Audio 真实播放）==========
// 后端适配说明：将 playlist 替换为后端接口返回的数据即可
// 每条歌曲结构：{ id, title, artist, cover(emoji 或图片URL), src(音频URL) }
const playlist = ref([
  {
    id: 1,
    title: 'Take Me Hand',
    artist: 'Cecile Corbel',
    cover: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 60 60'%3E%3Crect width='60' height='60' fill='%2310b981'/%3E%3Ctext x='30' y='42' font-size='34' text-anchor='middle' fill='white'%3E%E2%99%AB%3C/text%3E%3C/svg%3E",
    src: '/music/take-me-hand.mp3'
  },
  {
    id: 2,
    title: 'Take Me Hand',
    artist: 'Cecile Corbel',
    cover: '🌟',
    src: '/music/take-me-hand.mp3'
  },
  {
    id: 3,
    title: 'Take Me Hand',
    artist: 'Cecile Corbel',
    cover: '🌃',
    src: '/music/take-me-hand.mp3'
  }
])

// 封面渐变色（按索引循环，后端给真实封面图后可忽略）
const COVER_GRADIENTS = [
  'linear-gradient(135deg,#ecfdf5,#d1fae5)',
  'linear-gradient(135deg,#e0f2fe,#bae6fd)',
  'linear-gradient(135deg,#fef3c7,#fde68a)',
  'linear-gradient(135deg,#fce7f3,#fbcfe8)'
]
function coverStyle(i) {
  return { background: COVER_GRADIENTS[i % COVER_GRADIENTS.length] }
}

// 判断 cover 是否为图片地址（后端接入真实封面时使用）
function isImageUrl(val) {
  if (typeof val !== 'string') return false
  const v = val.trim()
  return /^(https?:\/\/|\/|data:image\/)/.test(v) ||
         /\.(jpe?g|png|webp|gif|svg|avif|bmp)$/i.test(v)
}

// 封面背景：图片地址时不设渐变（img 会填满），否则用渐变兜底
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
const musicProgress = computed(() => {
  if (!duration.value) return 0
  return Math.min(100, Math.round((currentTime.value / duration.value) * 100))
})

audio.addEventListener('timeupdate', () => {
  currentTime.value = audio.currentTime
})
audio.addEventListener('loadedmetadata', () => {
  duration.value = audio.duration || 0
})
audio.addEventListener('ended', () => {
  nextSong()
})
audio.addEventListener('error', () => {
  isPlaying.value = false
  playError.value = '音频加载失败，请检查文件路径或网络'
})

function playSong(index) {
  if (index < 0 || index >= playlist.value.length) return
  currentIndex.value = index
  const song = playlist.value[index]
  playError.value = ''
  audio.src = song.src
  audio.play().then(() => { isPlaying.value = true }).catch(() => {
    // 自动播放被浏览器拦截或音频加载失败，保持暂停态
    isPlaying.value = false
  })
}

function togglePlay() {
  if (!currentSong.value || !audio.src) {
    playSong(currentIndex.value)
    return
  }
  if (audio.paused) {
    audio.play().then(() => { isPlaying.value = true }).catch(() => {})
  } else {
    audio.pause()
    isPlaying.value = false
  }
}

function nextSong() {
  const next = (currentIndex.value + 1) % playlist.value.length
  playSong(next)
}

function prevSong() {
  const prev = (currentIndex.value - 1 + playlist.value.length) % playlist.value.length
  playSong(prev)
}

function seek(e) {
  if (!duration.value) return
  const bar = e.currentTarget
  const rect = bar.getBoundingClientRect()
  const ratio = (e.clientX - rect.left) / rect.width
  audio.currentTime = Math.max(0, Math.min(1, ratio)) * duration.value
}

function formatTime(sec) {
  if (!sec || isNaN(sec)) return '0:00'
  const m = Math.floor(sec / 60)
  const s = Math.floor(sec % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}

// Tabs（归档 + 动态分类）
const tabs = computed(() => {
  const base = [
    { key: 'archive', label: '归档', count: totalPosts.value },
  ]
  for (const cat of fixedCategories.value) {
    if (cat.count > 0) {
      base.push({ key: cat.name, label: cat.name, count: cat.count })
    }
  }
  return base
})

// 当前 Hero 标题 + 面包屑
const isCategoryPage = computed(() => route.path === '/category')
const isTagsPage = computed(() => route.path === '/tags' || !!route.query.tag)
const isAIPage = computed(() => route.path === '/ai')
const isEditorPage = computed(() => route.path === '/write')
const isDetailPage = computed(() => !!route.params.id && !route.query.tag)

// 路由视图切换 key：用于触发中间内容区过渡动画。
// 仅按「路由级视图」变化（首页/详情/分类/标签/AI/写文章），
// 纯前端 tab 切换（path 始终为 /）key 不变，保持即时无闪。
const viewKey = computed(() => {
  if (isDetailPage.value) return 'detail-' + (route.params.id || '')
  if (isAIPage.value) return 'ai'
  if (isEditorPage.value) return 'editor'
  if (isCategoryPage.value) return 'category'
  if (isTagsPage.value) return route.query.tag ? 'tag-' + route.query.tag : 'tags'
  return 'home'
})
const heroTitle = computed(() => {
  if (isEditorPage.value) return '写新文章'
  if (isDetailPage.value) return detailPost.value?.title || '文章详情'
  if (isAIPage.value) return 'AI 对话助手'
  if (isCategoryPage.value) return '分类'
  if (isTagsPage.value) {
    const t = route.query.tag
    return t ? `#${t}` : '标签'
  }
  if (activeTab.value === 'home') return '技术宅小窝'
  return activeTab.value
})

// 详情页数据
const detailPost = ref(null)
const renderedContent = ref('')
const detailLoading = ref(false)

// 详情页字数 / 阅读时间
const detailWordCount = computed(() => {
  if (!detailPost.value?.content) return 0
  return detailPost.value.content.length
})
const detailReadTime = computed(() => {
  const w = detailWordCount.value
  if (w <= 0) return 1
  return Math.max(1, Math.ceil(w / 400))
})

// ========== AI 聊天状态 ==========
const aiMessages = ref([])
const aiInput = ref('')
const aiLoading = ref(false)
const aiApiOnline = ref(false)
const aiStatusText = ref('演示模式 — 后端未启动时会用模拟回复')
const aiMsgContainer = ref(null)
const aiInputRef = ref(null)

const aiQuickQuestions = [
  '介绍一下你的博客项目',
  'FastAPI 和 Flask 有什么区别？',
  '解释一下 Docker 的核心概念',
]

// 进入 AI 页时拉取持久化历史（后端未就绪/未登录时静默失败，不影响现有体验）
async function loadAIHistory() {
  try {
    const history = await fetchAIHistory(50)
    if (Array.isArray(history) && history.length) {
      aiMessages.value = history.map(m => ({
        role: m.role,
        content: m.content,
      }))
    }
  } catch (e) {
    /* 静默：演示模式/未登录时无需报错 */
  }
}

// AI 发送消息（流式）
async function aiSendMessage(text) {
  const msg = (text || aiInput.value).trim()
  if (!msg || aiLoading.value) return

  aiMessages.value.push({ role: 'user', content: msg })
  aiInput.value = ''
  aiAutoResize()
  await aiScrollBottom()

  const assistantMsg = reactive({ role: 'assistant', content: '', streaming: true })
  aiMessages.value.push(assistantMsg)
  aiLoading.value = true

  try {
    const history = aiMessages.value
      .slice(0, -1)
      .map(m => ({ role: m.role, content: m.content }))

    await chatWithAIStream(msg, history, (token) => {
      assistantMsg.content += token
      aiScrollBottom()
    })

    aiApiOnline.value = true
    aiStatusText.value = '已连接'
  } catch (e) {
    aiApiOnline.value = false
    const code = e.code || 'NETWORK'
    if (code === 'AUTH') {
      aiStatusText.value = '登录失效，请重新登录'
      assistantMsg.content = '⚠️ 登录状态已失效，请**重新登录**后再使用 AI 助手。\n\n> 点击右上角头像退出，再重新登录即可。'
    } else if (code === 'SERVER' || code === 'STREAM') {
      aiStatusText.value = 'AI 服务异常'
      assistantMsg.content = assistantMsg.content
        ? `${assistantMsg.content}\n\n> ⚠️ 生成中断：${e.message || '服务异常'}`
        : `⚠️ AI 服务暂时不可用（${e.message || '服务异常'}）。\n\n请稍后重试，或检查后端服务是否正常运行。`
    } else {
      aiStatusText.value = '演示模式 — 后端未启动时会用模拟回复'
      assistantMsg.content = aiGetMockReply(msg)
    }
  } finally {
    assistantMsg.streaming = false
    aiLoading.value = false
    await aiScrollBottom()
  }
}

function aiGetMockReply(msg) {
  const lower = msg.toLowerCase()
  if (lower.includes('博客') || lower.includes('blog')) {
    return '我的博客系统叫"技术宅小窝"，技术栈是 **Vue3 + FastAPI + MySQL + Docker**，已经部署在阿里云 ECS 上，支持 HTTPS 访问。包含了用户认证、文章管理、标签筛选、全文搜索等功能。'
  }
  if (lower.includes('fastapi') && (lower.includes('flask') || lower.includes('区别'))) {
    return '**FastAPI vs Flask 核心区别：**\n\n| 特性 | FastAPI | Flask |\n|------|---------|-------|\n| 异步支持 | 原生 async/await | 需额外插件 |\n| 数据校验 | Pydantic 自动校验 | 需手动处理 |\n| API 文档 | 自动生成 Swagger | 需 flask-swagger |\n| 性能 | 接近 NodeJS/Go | 同步阻塞模型 |\n| 类型提示 | 一等公民 | 可选 |\n\n简单说：**新项目无脑 FastAPI**，老项目维护用 Flask。'
  }
  if (lower.includes('docker')) {
    return '**Docker 核心概念：**\n\n1. **镜像 (Image)** — 应用的只读模板，类似"安装包"\n2. **容器 (Container)** — 镜像的运行实例，轻量级沙箱\n3. **Dockerfile** — 定义镜像构建步骤\n4. **Docker Compose** — 编排多容器应用（如 MySQL + FastAPI + Nginx）\n5. **卷 (Volume)** — 持久化数据，容器删除数据不丢\n\n类比：镜像 = 类，容器 = 实例对象。'
  }
  return `收到你的问题：「${msg}」\n\n> ⚠️ 当前处于演示模式，后端 AI 接口暂未启动。启动后端后即可获得真实的 AI 回复。\n\n你可以试试问关于 FastAPI、Docker、博客项目等问题。`
}

function aiOnKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    aiSendMessage()
  }
}

function aiAutoResize() {
  const ta = aiInputRef.value
  if (!ta) return
  ta.style.height = 'auto'
  ta.style.height = Math.min(ta.scrollHeight, 150) + 'px'
}

async function aiScrollBottom() {
  await nextTick()
  const el = aiMsgContainer.value
  if (el) el.scrollTop = el.scrollHeight
}

function aiClearChat() {
  aiMessages.value = []
  // 同步清空后端持久化历史（失败静默，本地已清空）
  clearAIHistory()
}

// ========== 写文章编辑器 ==========
const TAG_MAP = { 'Python': 1, 'AI': 2, 'Vue': 3, 'FastAPI': 4, 'Docker': 5, '其他': 6 }
const editorTitle = ref('')
const editorContent = ref('')
const editorTag = ref('')
const editorExtraTags = ref('')
const editorRef = ref(null)
const editorPublishing = ref(false)

function editorInsert(before, after) {
  const ta = editorRef.value
  if (!ta) return
  const s = ta.selectionStart, e = ta.selectionEnd
  const sel = ta.value.slice(s, e)
  editorContent.value = editorContent.value.slice(0, s) + before + sel + after + editorContent.value.slice(e)
  const caret = s + before.length
  setTimeout(() => { ta.selectionStart = caret; ta.selectionEnd = caret + sel.length; ta.focus() }, 0)
}

async function editorPublish() {
  const t = editorTitle.value.trim()
  const c = editorContent.value.trim()
  if (!t) { window.alert('文章标题不能为空'); return }
  if (!c) { window.alert('文章内容不能为空'); return }

  const tags = []
  if (editorTag.value) tags.push(editorTag.value)
  editorExtraTags.value.split(',').forEach(t => {
    const tt = t.trim(); if (tt) tags.push(tt)
  })
  if (!tags.length) tags.push('其他')

  try {
    editorPublishing.value = true
    const tagIds = tags.map(t => TAG_MAP[t]).filter(id => id != null)
    await createPost({ title: t, content: c, user_id: 1, tag_ids: tagIds })
    editorTitle.value = ''
    editorContent.value = ''
    editorTag.value = ''
    editorExtraTags.value = ''
    alert('文章发布成功 🎉')
    setTimeout(() => $router.push('/'), 600)
  } catch (e) {
    alert(e.message || '发布失败')
  } finally {
    editorPublishing.value = false
  }
}

// 过滤后的文章列表
const filteredPosts = computed(() => {
  if (activeTab.value === 'home') return recentPosts.value
  // 按分类过滤
  const isTech = activeTab.value === '技术'
  return recentPosts.value.filter(p =>
    isTech
      ? (p.tags || []).some(t => TECH_TAGS.includes(t))
      : !(p.tags || []).some(t => TECH_TAGS.includes(t))
  )
})

// 按日期分组（用于时间线视图，分类过滤后的）
const postsByDate = computed(() => {
  const groups = {}
  for (const post of filteredPosts.value) {
    const dateStr = post.date ? post.date.slice(0, 10) : '1970-01-01'
    const monthDay = dateStr.slice(5) // MM-DD
    if (!groups[monthDay]) groups[monthDay] = []
    groups[monthDay].push(post)
  }
  // 按日期倒序
  return Object.entries(groups)
    .sort((a, b) => b[0].localeCompare(a[0]))
    .map(([date, posts]) => ({ date, posts }))
})

// 标签筛选：按日期分组
const postsByDateTag = computed(() => {
  const groups = {}
  for (const post of tagFilteredPosts.value) {
    const dateStr = post.date ? post.date.slice(0, 10) : '1970-01-01'
    const monthDay = dateStr.slice(5)
    if (!groups[monthDay]) groups[monthDay] = []
    groups[monthDay].push(post)
  }
  return Object.entries(groups)
    .sort((a, b) => b[0].localeCompare(a[0]))
    .map(([date, posts]) => ({ date, posts }))
})
const allPostsByDate = computed(() => {
  const groups = {}
  for (const post of recentPosts.value) {
    const dateStr = post.date ? post.date.slice(0, 10) : '1970-01-01'
    const monthDay = dateStr.slice(5)
    if (!groups[monthDay]) groups[monthDay] = []
    groups[monthDay].push(post)
  }
  return Object.entries(groups)
    .sort((a, b) => b[0].localeCompare(a[0]))
    .map(([date, posts]) => ({ date, posts }))
})

// 归档视图显示的年份（取最近文章的年份）
const archiveYear = computed(() => {
  if (!recentPosts.value.length) return new Date().getFullYear()
  const firstDate = recentPosts.value[0].date
  return firstDate ? firstDate.slice(0, 4) : String(new Date().getFullYear())
})

// 固定 6 个标签（与后端 init_db 一致）
const PREDEFINED_TAGS = ['Python', 'AI', 'Vue', 'Docker', 'FastAPI', '其他']

// 标签英文名 → 中文显示名
const TAG_LABELS = {
  Python: '技术',
  AI: 'AI应用',
  Vue: 'Vue',
  Docker: 'Docker',
  FastAPI: 'FastAPI',
  其他: '其他'
}

// 所有标签（固定 6 个 + 文章实际使用的）
const allTags = computed(() => {
  const set = new Set(PREDEFINED_TAGS)
  recentPosts.value.forEach(p => (p.tags || []).forEach(t => set.add(t)))
  return ['all', ...set]
})

// 标签 + 计数
const tagCounts = computed(() => {
  const map = {}
  for (const p of recentPosts.value) {
    for (const t of (p.tags || [])) {
      map[t] = (map[t] || 0) + 1
    }
  }
  return Object.entries(map)
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count)
})

// 标签统计数（固定 6 个）
const tagCount = computed(() => PREDEFINED_TAGS.length)

// 当前选中的标签（从 query.tag 读取）
const activeTag = ref('')

// 按标签筛选的文章
const tagFilteredPosts = computed(() => {
  if (!activeTag.value) return []
  return recentPosts.value.filter(p => (p.tags || []).includes(activeTag.value))
})

// Top 10 标签排行（取前 10）
const topTags = computed(() => tagCounts.value.slice(0, 10))

// 固定分类：二次元 / 技术
const FIXED_CATEGORIES = ['二次元', '技术']

// 技术类标签（用于自动归类）
const TECH_TAGS = ['Python', 'AI', 'Vue', 'Docker', 'FastAPI', 'Markdown', 'MDX', 'JavaScript']

// 分类（固定两种，按标签自动计数）
const fixedCategories = computed(() => {
  const techCount = recentPosts.value.filter(p =>
    (p.tags || []).some(t => TECH_TAGS.includes(t))
  ).length
  const acgCount = recentPosts.value.length - techCount
  return [
    { name: '技术', count: techCount },
    { name: '二次元', count: acgCount },
  ]
})

const totalCategoryPosts = computed(() => recentPosts.value.length)

// 所有标签（固定6个 + 文章实际使用的）

// 最后活动时间：取最近博客的发布时间计算
const lastActivity = computed(() => {
  const dates = recentPosts.value
    .map(p => p.date)
    .filter(Boolean)
    .sort()
    .reverse()
  if (!dates.length) return '刚刚'
  const d = new Date(dates[0])
  const days = Math.floor((Date.now() - d.getTime()) / 86400000)
  if (days <= 0) return '今天'
  if (days === 1) return '昨天'
  return days + ' 天前'
})

// 站点统计
const siteStats = computed(() => [
  { icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14,2 14,8 20,8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>', label: '文章', value: totalPosts.value || 0 },
  { icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13,2 3,14 12,14 11,22 21,10 12,10"/></svg>', label: '动态', value: mockActivities.value.length },
  { icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>', label: '分类', value: fixedCategories.value.length || 0 },
  { icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>', label: '标签', value: tagCount.value },
  { icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>', label: '总字数', value: formatNumber(totalWords.value) },
  { icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12,6 12,12 16,14"/></svg>', label: '运行时长', value: runningDays + ' 天' },
  { icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23,6 13.5,15.5 8.5,10.5 1,18"/><polyline points="17,6 23,6 23,12"/></svg>', label: '最后活动', value: lastActivity.value },
])

const totalWords = ref(13767)
const startDate = new Date('2026-07-04') // 部署日期
const runningDays = Math.max(1, Math.ceil((Date.now() - startDate) / 86400000))

function formatNumber(n) {
  if (n >= 10000) return (n / 10000).toFixed(n % 10000 === 0 ? 0 : 1) + '万'
  return n.toLocaleString()
}

// ===== 日历组件 =====
const calYear = ref(new Date().getFullYear())
const calMonth = ref(new Date().getMonth() + 1)
const todayDay = new Date().getDate()

const isCurrentMonth = computed(() => {
  const now = new Date()
  return calYear.value === now.getFullYear() && calMonth.value === (now.getMonth() + 1)
})

function getDaysInMonth(y, m) {
  return new Date(y, m, 0).getDate()
}

function getFirstDayOfWeek(y, m) {
  return new Date(y, m - 1, 1).getDay()
}

const calWeeks = computed(() => {
  const days = getDaysInMonth(calYear.value, calMonth.value)
  const firstDay = getFirstDayOfWeek(calYear.value, calMonth.value)
  const weeks = []
  let week = new Array(7).fill(null)
  let dayIdx = 1
  for (let i = firstDay; i < 7 && dayIdx <= days; i++) {
    week[i] = dayIdx++
  }
  weeks.push([...week])
  while (dayIdx <= days) {
    week = new Array(7).fill(null)
    for (let i = 0; i < 7 && dayIdx <= days; i++) {
      week[i] = dayIdx++
    }
    weeks.push([...week])
  }
  return weeks
})

function inCurrentMonth(idx) {
  return isCurrentMonth.value
}

function prevMonth() {
  if (calMonth.value === 1) { calMonth.value = 12; calYear.value-- }
  else { calMonth.value-- }
}
function nextMonth() {
  if (calMonth.value === 12) { calMonth.value = 1; calYear.value++ }
  else { calMonth.value++ }
}
function goToday() {
  const now = new Date()
  calYear.value = now.getFullYear()
  calMonth.value = now.getMonth() + 1
}

// Mock 动态
const mockActivities = ref([
  { time: '刚刚', text: '完成了 AI Agent 架构的流式输出改造 ✨' },
  { time: '今天', text: '发布了新博客：从零搭建博客 AI Agent' },
  { time: '昨天', text: '修复了前端 Token 同步问题' },
])

async function loadData() {
  try {
    const data = await fetchPosts({ pageSize: 100 })
    const list = data.list || []
    recentPosts.value = formatPosts(list)
    totalPosts.value = data.total || list.length
    // 从分类页跳转过来时，根据 ?cat= 激活对应分类 tab
    if (route.query.view === 'archive') {
      activeTab.value = 'archive'
    } else if (route.query.cat && (route.query.cat === '技术' || route.query.cat === '二次元')) {
      activeTab.value = route.query.cat
    } else if (route.query.tag) {
      activeTag.value = String(route.query.tag)
    }
    // 估算总字数
    totalWords.value = list.reduce((sum, row) => {
      const b = row.Blog || row
      return sum + (b.content || '').length
    }, 0)
  } catch (e) {
    console.error('获取首页数据失败', e)
  }
}

// 加载文章详情
async function loadDetail() {
  const id = route.params.id
  if (!id) return
  detailLoading.value = true
  try {
    const data = await fetchPostById(id)
    const blog = data.Blog || data
    detailPost.value = {
      id: blog.id,
      title: blog.title,
      content: blog.content || '',
      date: blog.create_time || blog.created_at || blog.updated_at || '',
      fullTime: blog.create_time || blog.created_at || '',
      tags: data.tags_name || (blog.tags || []).map(t => typeof t === 'string' ? t : t.name).filter(Boolean),
      category: (data.tags_name && data.tags_name[0]) || ((blog.tags || [])[0]?.name) || '技术',
      cover_image: blog.cover_image || null,
      author: 'Firefly',
    }
    renderedContent.value = renderMarkdown(blog.content || '')
  } catch (e) {
    console.error('[HomePage] 加载详情失败', e)
    detailPost.value = null
  } finally {
    detailLoading.value = false
  }
}

// 删除文章（详情页用）
function handleDeleteDetail() {
  if (!detailPost.value?.id) return
  if (!confirm('确定要删除这篇文章吗？')) return
  deletePost(detailPost.value.id)
    .then(() => window.location.href = '/')
    .catch(() => alert('删除失败'))
}

// 拉取音乐列表：接后端 /api/music/list，失败则保留 demo 数据兜底
async function fetchMusicList() {
  try {
    const res = await fetch('/api/music/list')
    if (!res.ok) return
    const json = await res.json()
    if (json && Array.isArray(json.data) && json.data.length) {
      playlist.value = json.data
    }
  } catch (e) {
    // 后端未就绪时静默保留 demo 列表
  }
}

onMounted(() => {
  loadData()
  if (isDetailPage.value) loadDetail()
  fetchMusicList()
  loadAIHistory()
})

// 切到 AI 页时（如登录后进入）补拉历史，覆盖 onMounted 时尚未登录的情况
watch(isAIPage, (val) => {
  if (val) loadAIHistory()
})

// 监听路由变化（同组件导航 query 变化不会重新挂载，需监听 fullPath）
watch(() => route.fullPath, () => {
  // 根据 query 参数同步激活的 tab（归档 / 分类 / 标签）
  if (route.query.view === 'archive') {
    activeTab.value = 'archive'
    activeTag.value = ''
  } else if (route.query.cat) {
    activeTab.value = route.query.cat
    activeTag.value = ''
  } else if (route.query.tag) {
    activeTag.value = String(route.query.tag)
  } else {
    activeTab.value = 'home'
    activeTag.value = ''
  }
  // 进入/切换详情页时加载文章数据
  if (route.params.id) {
    loadDetail()
  } else {
    detailPost.value = null
    renderedContent.value = ''
  }
})

onUnmounted(() => {
  audio.pause()
  audio.src = ''
})

function formatPosts(rows) {
  const map = new Map()
  for (const row of rows) {
    const blog = row.Blog || row
    if (!map.has(blog.id)) {
      map.set(blog.id, {
        id: blog.id,
        title: blog.title,
        content: blog.content || '',
        create_time: blog.create_time,
        views: blog.views || 0,
        tags: [],
      })
    }
    if (row.name && !map.get(blog.id).tags.includes(row.name)) {
      map.get(blog.id).tags.push(row.name)
    }
  }
  return Array.from(map.values()).map(blog => {
    const ct = blog.create_time || ''
    // 格式化日期：2026-07-15 16:15:29
    const displayDate = ct.length >= 16 ? ct.replace('T', ' ').slice(0, 19) : ct
    // 取第一个标签作为分类（过滤掉非分类值）
    let cat = (blog.tags && blog.tags[0]) || '技术'
    if (['home','all','archive'].includes(cat)) cat = '技术'
    return {
      ...blog,
      excerpt: blog.content.length > 120 ? blog.content.slice(0, 120) + '...' : '',
      date: displayDate,
      category: cat,
    }
  })
}
</script>

<style scoped>
.home-page { min-height: 100vh; position: relative; z-index: 1; }

/* ========== Hero 区域（局部壁纸） ========== */
.hero-area {
  position: relative;
  width: 100%;
  height: 55vh; min-height: 360px;
  overflow: hidden;
  display: flex; align-items: center; justify-content: center;
  /* 单层 cover 满铺，position 偏上让人物脸部在可见区 */
  background: url('/bg-firefly.webp') center 25% / cover no-repeat;
}
/* 底部渐变过渡到内容区（亮色模式 → 浅色底） */
.hero-area::after {
  content: '';
  position: absolute; inset: 0;
  background: linear-gradient(180deg,
    rgba(0,0,0,0) 45%,
    rgba(240,242,245,0.5) 80%,
    var(--bg-body) 100%
  );
  z-index: 1;
}

/* ===== 暗色模式 Hero 渐变 → 深色底 ===== */
html[data-theme='dark'] .hero-area::after {
  background: linear-gradient(180deg,
    rgba(0,0,0,0) 40%,
    rgba(15,23,42,0.6) 75%,
    var(--bg-body) 100%
  );
}
.hero-content {
  position: relative; z-index: 2;
  text-align: center; color: #fff;
}
.hero-title {
  font-size: 2.6rem; font-weight: 700;
  letter-spacing: 2px; margin-bottom: 0.5rem;
  text-shadow: 0 2px 12px rgba(0,0,0,0.4);
}
.hero-subtitle {
  font-size: 1rem; font-weight: 400;
  opacity: 0.88; letter-spacing: 3px;
  text-shadow: 0 1px 6px rgba(0,0,0,0.35);
}
.hero-detail-sub {
  display: inline-flex; align-items: center; gap: 0.4rem;
  letter-spacing: 1px !important;
}
.hero-detail-sub svg { width: 15px; height: 15px; stroke: currentColor; }
.hero-sub-sep { opacity: 0.6; }

/* ========== 三栏布局 ========== */
.content-area {
  max-width: 1220px;
  margin: 0 auto;
  padding: 1.5rem 1.5rem 3rem;
  display: grid;
  grid-template-columns: 250px minmax(0, 1fr) 270px;
  gap: 1.25rem;
  align-items: start;
}

/* 路由视图切换过渡：中间内容区淡入上滑 / 淡出上移 */
.view-fade-enter-active,
.view-fade-leave-active {
  transition: opacity 0.28s cubic-bezier(0.4, 0, 0.2, 1),
              transform 0.28s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: opacity, transform;
}
.view-fade-enter-from {
  opacity: 0;
  transform: translateY(14px);
}
.view-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
/* 尊重无障碍偏好：用户要求减少动效时关闭位移动画 */
@media (prefers-reduced-motion: reduce) {
  .view-fade-enter-active,
  .view-fade-leave-active {
    transition: opacity 0.12s linear;
  }
  .view-fade-enter-from,
  .view-fade-leave-to {
    transform: none;
  }
}

/* ========== 卡片通用 ========== */
.card {
  background: var(--bg-card);
  backdrop-filter: blur(12px);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}
.card-title-sm {
  font-size: 13px; font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 0.85rem;
  padding-bottom: 0.6rem;
  border-bottom: 1px solid var(--border-strong);
}

/* ========== 左栏 ========== */
.sidebar-left { display: flex; flex-direction: column; gap: 1rem; position: sticky; top: 76px; }

/* 个人信息 */
.profile-card { text-align: center; padding: 1.6rem 1.2rem; }
.profile-avatar {
  width: 108px; height: 108px; margin: 0 auto 0.85rem;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 6px 24px rgba(0,0,0,0.12);
}
.profile-avatar img {
  width: 100%; height: 100%;
  object-fit: cover;
  display: block;
}
.profile-name {
  font-size: 20px; font-weight: 700; color: var(--text);
  margin-bottom: 0.25rem;
  position: relative; display: inline-block;
}
.profile-name::after {
  content: '';
  position: absolute; left: 50%; transform: translateX(-50%);
  bottom: -4px; width: 60%; height: 2.5px;
  background: var(--primary); border-radius: 2px;
  opacity: 0.7;
}
.profile-bio { font-size: 13px; color: var(--text-secondary); font-weight: 400; margin-bottom: 0.2rem; }
.bio-accent { color: var(--primary); font-weight: 600; }
.profile-desc { font-size: 11.5px; color: var(--text-dim); line-height: 1.55; margin-bottom: 0.85rem; }

/* 社交图标（统一绿色线性） */
.social-icons { display: flex; justify-content: center; gap: 0.6rem; }
.soc-icon {
  width: 38px; height: 38px; border-radius: 7px;
  display: flex; align-items: center; justify-content: center;
  background: var(--primary);
  color: #fff;
  text-decoration: none;
  transition: all var(--transition);
}
.soc-icon svg { width: 17px; height: 17px; flex-shrink: 0; }
.soc-icon:hover {
  background: var(--primary-dark);
  transform: translateY(-2px) scale(1.08);
}
/* 深色模式：按钮背景变暗，图标保持白色 */
html[data-theme='dark'] .soc-icon {
  background: rgba(51, 65, 85, 0.6);
}
html[data-theme='dark'] .soc-icon:hover {
  background: rgba(71, 85, 105, 0.8);
}

/* 公告 */
.announcement-card { padding: 1rem 1.2rem; border-left: 3px solid var(--primary); }
.ann-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem; }
.ann-close {
  width: 20px; height: 20px; border-radius: 50%; background: var(--bg-body);
  color: var(--text-dim); font-size: 14px; line-height: 1;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: all 0.15s;
  border: none;
}
.ann-close:hover { background: var(--danger-bg, #fef2f2); color: var(--danger); }
.ann-text { font-size: 12.5px; color: var(--text-secondary); line-height: 1.65; }

/* 音乐 */
.music-card { padding: 1rem 1.2rem; }
.music-now { display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.6rem; }
.music-cover {
  width: 42px; height: 42px; border-radius: 8px;
  background: linear-gradient(135deg, #ecfdf5, #d1fae5);
  display: flex; align-items: center; justify-content: center;
  font-size: 18px; flex-shrink: 0;
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
  width: 28px; height: 28px; border-radius: 50%;
  background: var(--bg-body); border: 1px solid var(--border-strong);
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

/* 播放列表面板 */
.music-list { list-style: none; margin: 0.6rem 0 0; padding: 0.4rem 0 0; border-top: 1px solid var(--border-strong); display: flex; flex-direction: column; gap: 0.15rem; }
.music-list-item {
  display: flex; align-items: center; gap: 0.55rem;
  padding: 0.4rem 0.5rem; border-radius: 8px; cursor: pointer; transition: background 0.15s;
}
.music-list-item:hover { background: var(--bg-body); }
.music-list-item.active { background: rgba(16,185,129,0.1); }
.ml-cover {
  width: 30px; height: 30px; border-radius: 6px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center; font-size: 14px;
  overflow: hidden;
}
/* 封面图片：URL 时渲染 img，继承父级圆角裁切；emoji 时由文字兜底 */
.music-cover-img,
.ml-cover-img {
  width: 100%; height: 100%;
  object-fit: cover;
  border-radius: inherit;
  display: block;
}
.ml-info { display: flex; flex-direction: column; min-width: 0; flex: 1; }
.ml-title { font-size: 12px; font-weight: 600; color: var(--text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.ml-artist { font-size: 10px; color: var(--text-dim); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.ml-playing { font-size: 10px; color: var(--primary); flex-shrink: 0; }
/* 播放中跳动条 */
.ml-eq { display: flex; align-items: flex-end; gap: 2px; height: 14px; flex-shrink: 0; }
.ml-eq i { width: 3px; background: var(--primary); border-radius: 2px; animation: eq-bounce 0.8s ease-in-out infinite; }
.ml-eq i:nth-child(1) { height: 6px; animation-delay: 0s; }
.ml-eq i:nth-child(2) { height: 12px; animation-delay: 0.2s; }
.ml-eq i:nth-child(3) { height: 8px; animation-delay: 0.4s; }
@keyframes eq-bounce { 0%, 100% { transform: scaleY(0.4); } 50% { transform: scaleY(1); } }
.playlist-fade-enter-active, .playlist-fade-leave-active { transition: opacity 0.2s; }
.playlist-fade-enter-from, .playlist-fade-leave-to { opacity: 0; }

/* 分类（简单列表：名字 + 绿色数字徽章） */
.category-card { padding: 1rem 1.15rem; }
.category-list {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}
.category-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.4rem 0.5rem;
  border-radius: 8px;
  text-decoration: none;
  transition: all 0.15s;
  font-size: 13.5px;
}
.category-item:hover { background: var(--primary-bg); }
.cat-active { background: rgba(16, 185, 129, 0.1); }
.cat-active .cat-name { color: var(--primary); }
.cat-name { color: var(--text-secondary); transition: color 0.15s; }
.category-item:hover .cat-name { color: var(--primary); }
.cat-count-badge {
  font-size: 11.5px;
  font-weight: 700;
  color: #fff;
  background: var(--primary);
  padding: 0.1rem 0.6rem;
  border-radius: 99px;
  min-width: 26px;
  text-align: center;
}

/* 标签（药丸云） */
.tags-card { padding: 1rem 1.15rem; }
.tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}
.cloud-tag {
  padding: 0.3rem 0.7rem;
  border-radius: 10px;
  font-size: 12px;
  color: var(--text-secondary);
  background: rgba(80, 90, 110, 0.12);
  border: 1px solid rgba(100, 116, 139, 0.14);
  text-decoration: none;
  transition: all 0.15s;
  font-weight: 500;
}
.cloud-tag:hover {
  color: #fff;
  background: var(--primary);
  border-color: var(--primary);
  transform: translateY(-1px);
}

/* ========== 中间主区域 ========== */
.main-content { min-width: auto; overflow: visible; }
.main-content > * { overflow: visible; }
.list-header {
  display: flex; align-items: center;
  justify-content: space-between;
  padding: 0.6rem 1rem;
  margin-bottom: 1rem;
}
.tab-group { display: flex; gap: 0.4rem; flex-wrap: wrap; }
.tab-pill {
  display: inline-flex; align-items: center; gap: 0.3rem;
  padding: 0.35rem 0.85rem;
  border-radius: 20px;
  border: none;
  background: rgba(16, 185, 129, 0.1);
  color: var(--text); font-size: 13px; font-weight: 500;
  cursor: pointer; transition: all 0.2s;
}
.tab-pill:hover { background: rgba(16, 185, 129, 0.18); }
.tab-pill.active {
  background: rgba(5, 150, 105, 0.25);
  color: var(--text); font-weight: 600;
  box-shadow: 0 1px 6px rgba(5, 150, 105, 0.15);
}
.tab-pill-icon {
  width: 14px; height: 14px; flex-shrink: 0;
}
.tab-pill-count {
  font-size: 11px; color: var(--text-secondary);
  opacity: 0.85;
}
/* 主页小屋子按钮（默认不亮，只有 .active 时才绿） */
.home-pill {
  padding: 0.35rem 0.5rem;
  border-radius: 8px;
}
.home-pill.active {
  background: var(--primary);
  color: #fff !important;
  font-weight: 600;
}
.home-pill:hover { background: #f0fdf4; }
.home-pill.active:hover { background: var(--primary-hover, #059669); }
.home-pill .tab-pill-icon { width: 15px; height: 15px; }
.more-link {
  font-size: 13px; color: var(--primary); text-decoration: none;
  font-weight: 500; white-space: nowrap; transition: color var(--transition);
}
.more-link:hover { color: var(--primary-dark); }
.more-pill {
  display: inline-flex;
  align-items: center;
  padding: 0.35rem 0.85rem;
  border-radius: 20px;
  background: var(--primary);
  color: #fff !important;
  font-weight: 600;
  font-size: 13px;
  text-decoration: none;
}
.more-pill:hover {
  background: var(--primary-hover, #059669);
  color: #fff !important;
}
.more-link.small { font-size: 12px; }

/* ========== 文章卡片（Firefly 风格）========== */
.post-list { display: flex; flex-direction: column; gap: 1.2rem; }
.post-card {
  display: flex; align-items: stretch;
  background: var(--bg-card);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-lg);
  padding: 0;
  cursor: pointer;
  transition: all var(--transition);
  animation: fadeUp 0.4s ease both;
  box-shadow: var(--shadow-sm);
  overflow: hidden;
  min-height: 140px;
}
.post-card:hover {
  transform: translateX(3px);
  box-shadow: var(--shadow-md);
}

/* 左侧绿色短条（仅对准标题行） */
.post-accent-bar {
  width: 4px; flex-shrink: 0;
  background: var(--primary);
  align-self: flex-start;
  margin: 1.15rem 0 0 0.6rem;
  height: 28px;
  border-radius: 0 2px 2px 0;
  transition: background 0.2s;
}
.post-card:hover .post-accent-bar { background: var(--primary-dark); }

/* 封面图在右侧（有图时显示） */
.post-cover {
  width: 190px; min-height: 140px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  overflow: hidden;
  border-radius: 0 var(--radius-lg) var(--radius-lg) 0;
}
.post-cover img {
  width: 100%; height: 100%;
  object-fit: cover;
  display: block;
}

/* 无图时的跳转箭头 */
.post-arrow {
  width: 44px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  background: rgba(16, 185, 129, 0.08);
  color: var(--primary);
  transition: all 0.2s;
}
.post-arrow svg {
  width: 20px; height: 20px;
}
.post-card:hover .post-arrow {
  background: var(--primary);
  color: #fff;
}

.post-body { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 0.5rem; padding: 1.15rem 1.2rem 1.2rem 1.1rem; }
.post-title {
  font-size: 17px; font-weight: 700; color: var(--text);
  line-height: 1.45;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
  overflow: hidden; transition: color var(--transition);
}
.post-card:hover .post-title { color: var(--primary); }

/* 元信息行：图标+文字 + 分隔符 */
.post-meta-row { display: flex; align-items: center; gap: 0.4rem; flex-wrap: wrap; }
.meta-item {
  display: inline-flex; align-items: center; gap: 0.25rem;
  font-size: 12px; color: var(--text-dim);
}
.meta-svg { width: 13px; height: 13px; stroke: currentColor; opacity: 0.7; }
.meta-sep { color: var(--border-strong); font-size: 11px; margin: 0 0.1rem; }

.post-excerpt {
  font-size: 12.5px; color: var(--text-muted); line-height: 1.6;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
  overflow: hidden;
}

.post-tag-row { display: flex; gap: 0.35rem; flex-wrap: wrap; }
.post-hash-tag {
  font-size: 11.5px;
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  background: rgba(80, 90, 110, 0.12);
  color: var(--text-secondary);
  border: 1px solid rgba(100, 116, 139, 0.15);
  transition: all 0.15s;
  font-weight: 500;
}
.post-hash-tag:hover {
  color: var(--primary);
  border-color: var(--primary);
  background: rgba(16, 185, 129, 0.1);
}

.empty-state {
  text-align: center; padding: 3rem 1rem;
  color: var(--text-dim);
}
.empty-icon { font-size: 48px; display: block; margin-bottom: 0.75rem; }
.btn-empty {
  margin-top: 0.75rem; padding: 0.5rem 1.4rem; border-radius: 20px;
  background: var(--primary); color: #fff; font-size: 13px; font-weight: 600;
  transition: all var(--transition);
}
.btn-empty:hover { background: var(--primary-dark); }

/* ========== 分类时间线归档视图 ========== */
.archive-view { display: flex; flex-direction: column; gap: 1rem; }

/* 面包屑 */
.archive-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.65rem 0.85rem;
  margin-bottom: 0.4rem;
  border-radius: var(--radius);
  border-left: 3px solid var(--primary);
  background: rgba(16,185,129,0.06);
  overflow: visible;
}
.archive-breadcrumb {
  font-size: 14px;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  gap: 0.25rem;
  min-width: 0;
  overflow: visible;
}
.bc-label { color: var(--text-dim); font-weight: 500; }
.bc-sep {
  margin: 0 0.3rem;
  color: var(--border-accent);
}
.bc-value {
  color: var(--primary);
  font-weight: 700;
  font-size: 15px;
  padding: 2px 14px 2px 16px;
  background: rgba(16,185,129,0.12);
  border-radius: 6px;
  white-space: nowrap;
  line-height: 1.6;
  flex-shrink: 0;
  width: fit-content;
  position: relative;
  z-index: 1;
}
.bc-count {
  margin-left: 1rem;
  font-size: 12px;
  color: var(--text-dim);
}

/* 统计行 */
.archive-stats {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 15px;
  padding: 0.75rem 0.85rem;
  border-bottom: 1px solid var(--border);
  cursor: pointer;
  transition: background 0.15s;
}
.archive-stats:hover { background: rgba(16,185,129,0.04); }
.archive-total {
  font-size: 22px;
  font-weight: 700;
  color: var(--text);
  letter-spacing: -0.5px;
}
.stat-dot {
  display: inline-block;
  margin: 0 0.4rem;
  color: var(--primary);
  font-size: 14px;
  vertical-align: middle;
}
.archive-total strong { font-weight: 700; }
.archive-toggle {
  margin-left: auto;
  cursor: pointer;
  color: var(--text-dim);
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex; align-items: center;
  font-size: 13px;
}
.archive-toggle svg {
  width: 14px; height: 14px;
  transition: transform 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
.archive-toggle:hover { color: var(--primary); }
.archive-toggle.collapsed svg {
  transform: rotate(-90deg);
}

/* 时间线（连续竖线版本） */
.timeline-list {
  display: flex;
  flex-direction: column;
  gap: 0;
  position: relative;
  overflow: visible;
}
/* 贯穿整个列表的细密虚线 */
.timeline-track {
  position: absolute;
  left: 74px;
  top: 10px;
  bottom: 0;
  width: 0;
  height: calc(100% - 10px);
  border-left: 1.5px dashed var(--border-strong);
}
/* 暗色模式竖线 */
html[data-theme='dark'] .timeline-track {
  border-left-color: rgba(100, 116, 139, 0.4);
}
.timeline-group {
  display: flex;
  gap: 0;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--border-light);
  position: relative;
}
.tl-date {
  width: 56px;
  flex-shrink: 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-dim);
  text-align: right;
  padding-right: 1rem;
  line-height: 2.2;
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
}
/* 绿点（压在贯穿线上，对齐参考图） */
.tl-dot {
  width: 2px;
  flex-shrink: 0;
  margin: 0 0.85rem;
  position: relative;
}
.tl-dot::before {
  content: '';
  position: absolute;
  top: 12px;
  left: 50%;
  transform: translateX(-50%);
  width: 10px; height: 10px;
  border-radius: 50%;
  background: var(--primary);
  box-shadow: 0 0 8px rgba(16,185,129,0.5), 0 0 2px rgba(16,185,129,0.8);
  z-index: 2;
}
.tl-posts { flex: 1; min-width: fit-content; overflow: visible; }

/* 时间线文章行 */
.tl-post-item {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.5rem 0.6rem;
  margin: 0 -0.6rem;
  cursor: pointer;
  transition: all 0.18s ease;
  border-radius: 8px;
  overflow: visible;
}
.tl-post-item:hover {
  background: rgba(16,185,129,0.06);
}
/* 暗色模式 hover 更明显 */
html[data-theme='dark'] .tl-post-item:hover {
  background: rgba(16,185,129,0.1);
}
.tl-cat-badge {
  font-size: 12px;
  font-weight: 600;
  color: #fff;
  background: var(--primary);
  padding: 0.15rem 0.7rem;
  border-radius: 99px;
  white-space: nowrap;
  flex-shrink: 0;
  line-height: 1.4;
  position: relative;
  z-index: 5;
}
.tl-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text);
  transition: color 0.15s;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
  min-width: 0;
}
.tl-post-item:hover .tl-title { color: var(--primary); }
.tl-tags {
  display: flex;
  gap: 0.3rem;
  flex-shrink: 0;
  margin-left: auto;
}
.tl-tag {
  font-size: 12px;
  color: var(--text-dim);
  white-space: nowrap;
  opacity: 0.75;
}
.tl-tag:hover { opacity: 1; color: var(--primary); }
.tl-tag-more { opacity: 0.5; }

/* ========== 右栏 ========== */
.sidebar-right { display: flex; flex-direction: column; gap: 1rem; position: sticky; top: 76px; }

.stats-card { padding: 1.15rem 1.3rem; }
.stats-title {
  font-size: 17px; font-weight: 700;
  color: var(--text); margin-bottom: 0.6rem;
  letter-spacing: 0.5px;
}
.stats-grid { display: flex; flex-direction: column; gap: 0.85rem; }
.stat-item {
  display: flex; align-items: center; gap: 0.6rem;
  font-size: 13.5px; color: var(--text-secondary);
  padding: 0.35rem 0;
  border-bottom: 1px solid var(--border-light);
}
.stat-item:last-child { border-bottom: none; }
.stat-icon {
  width: 18px; height: 18px; flex-shrink: 0;
  color: var(--primary);
  display: flex; align-items: center; justify-content: center;
}
.stat-icon svg { width: 16px; height: 16px; }
.stat-label { flex: 1; }
.stat-item strong { color: var(--text); font-weight: 700; font-size: 14px; }

/* 日历 */
.calendar-card { padding: 0.9rem 1.1rem; }
.cal-header {
  display: flex; align-items: center; justify-content: center;
  gap: 0.5rem; margin-bottom: 0.6rem;
}
.cal-title { font-size: 14px; font-weight: 700; color: var(--text); min-width: 90px; text-align: center; }
.cal-nav {
  width: 26px; height: 26px;
  border-radius: 6px;
  border: 1px solid var(--border-light);
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  font-size: 13px; transition: all 0.15s; line-height: 1;
}
.cal-nav:hover { background: var(--primary-bg); color: var(--primary); border-color: var(--border-accent); }
.cal-today-btn {
  width: 26px; height: 26px;
  border-radius: 6px;
  border: 1px solid var(--border-accent);
  background: var(--primary-bg);
  color: var(--primary);
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  font-size: 14px; transition: all 0.15s; line-height: 1; margin-left: 2px;
}
.cal-today-btn:hover { background: var(--primary); color: #fff; }
.cal-table { width: 100%; border-collapse: collapse; table-layout: fixed; }
.cal-table th {
  padding: 0.25rem 0; font-size: 11px; font-weight: 600;
  color: var(--text-dim); text-align: center;
}
.cal-table td {
  padding: 0.35rem 0; font-size: 12px; text-align: center;
  color: var(--text-secondary); cursor: default;
  transition: all 0.12s; border-radius: 4px;
}
.cal-day:hover:not(.cal-empty) { background: var(--primary-bg); color: var(--primary); }
.cal-today {
  background: var(--primary); color: #fff !important; font-weight: 700; border-radius: 4px;
}
.cal-other { opacity: 0.35; }
.cal-empty { }

.activity-card { padding: 1rem 1.2rem; }
.activity-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.75rem; }
.activity-list { display: flex; flex-direction: column; gap: 0.8rem; }
.activity-time {
  font-size: 11px; color: var(--primary); display: block; margin-bottom: 0.12rem;
  opacity: 0.8;
}
.activity-text { font-size: 12.5px; color: var(--text-secondary); line-height: 1.5; }

.info-card { padding: 1rem 1.2rem; }
.info-list { display: flex; flex-direction: column; gap: 0.5rem; margin-bottom: 0.65rem; }
.info-item {
  display: flex; align-items: center; justify-content: space-between;
  font-size: 12.5px;
}
.info-label { color: var(--text-dim); }
.info-value { color: var(--text-secondary); font-weight: 500; }
.btn-expand-info {
  width: 100%; padding: 0.4rem; font-size: 12px; color: var(--primary);
  background: var(--primary-bg); border: 1px solid var(--border-accent);
  border-radius: 8px; cursor: pointer; transition: all 0.15s; font-weight: 500;
}
.btn-expand-info:hover { background: var(--primary); color: #fff; border-color: var(--primary); }
.info-detail {
  margin-top: 0.65rem; padding: 0.65rem;
  background: var(--bg-body); border-radius: 8px; font-size: 11.5px;
  line-height: 1.7; color: var(--text-muted);
}
.info-detail p { margin-bottom: 0.25rem; }
.info-detail p:last-child { margin-bottom: 0; }

/* ========== 动画 ========== */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ========== 响应式 ========== */
@media (max-width: 1024px) {
  .content-area {
    grid-template-columns: 210px 1fr 230px; gap: 1rem;
    padding: 1.25rem 1rem;
  }
  .post-cover { width: 150px; min-height: 110px; }
}
@media (max-width: 800px) {
  .content-area { grid-template-columns: 1fr; }
  .sidebar-left, .sidebar-right {
    position: static;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
  }
  .post-cover { width: 120px; min-height: 90px; }
  .post-card { flex-wrap: wrap; }
  .post-body { padding: 0.75rem; }
}
@media (max-width: 520px) {
  .sidebar-left, .sidebar-right { grid-template-columns: 1fr; }
  .post-card { flex-direction: column; }
  .post-cover { width: 100%; height: 140px; border-radius: 0 0 var(--radius-lg) var(--radius-lg); }
}

/* ===== 暗色模式覆盖（字体色泽统一）===== */
html[data-theme='dark'] .tab-pill {
  background: rgba(16, 185, 129, 0.12);
}
html[data-theme='dark'] .tab-pill:hover {
  background: rgba(16, 185, 129, 0.2);
}
html[data-theme='dark'] .tab-pill.active {
  background: rgba(5, 150, 105, 0.28);
}
html[data-theme='dark'] .tab-pill-count {
  color: var(--text); opacity: 0.7;
}
html[data-theme='dark'] .meta-item { color: var(--text-secondary); }
html[data-theme='dark'] .meta-svg { opacity: 0.5; }
html[data-theme='dark'] .ann-close:hover {
  background: rgba(248, 113, 113, 0.15);
}
/* 暗色模式标签/摘要文字更清晰 */
html[data-theme='dark'] .post-excerpt { color: var(--text-secondary); }
html[data-theme='dark'] .post-hash-tag {
  color: var(--text-secondary);
  background: rgba(148, 163, 184, 0.12);
  border-color: rgba(148, 163, 184, 0.18);
}
html[data-theme='dark'] .activity-text { color: var(--text-secondary); }
html[data-theme='dark'] .activity-time { opacity: 0.65; }
html[data-theme='dark'] .ann-text { color: var(--text-secondary); }
html[data-theme='dark'] .profile-desc { color: var(--text-secondary); }
html[data-theme='dark'] .post-arrow {
  background: rgba(52, 211, 153, 0.1);
}
/* 分类/标签暗色 */
html[data-theme='dark'] .category-item:hover {
  background: rgba(52, 211, 153, 0.1);
}
html[data-theme='dark'] .cat-name { color: #94a3b8; }
html[data-theme='dark'] .category-item:hover .cat-name { color: var(--primary); }
html[data-theme='dark'] .cloud-tag {
  color: var(--text-secondary);
  background: rgba(148, 163, 184, 0.12);
  border-color: rgba(148, 163, 184, 0.18);
}
html[data-theme='dark'] .info-value { color: var(--text-secondary); }

/* 时间线归档暗色 */
html[data-theme='dark'] .archive-stats { border-color: var(--border-strong); }
html[data-theme='dark'] .timeline-group { border-color: rgba(51, 65, 85, 0.5); }
html[data-theme='dark'] .tl-title { color: #e2e8f0; }
html[data-theme='dark'] .tl-post-item:hover { background: rgba(16,185,129,0.12); }

/* 折叠/展开动画 */
.collapse-tl-enter-active,
.collapse-tl-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
}
.collapse-tl-enter-from,
.collapse-tl-leave-to {
  opacity: 0;
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
}
.collapse-tl-enter-to,
.collapse-tl-leave-from {
  opacity: 1;
  max-height: 800px;
}

/* ========== 分类总览视图（/category） ========== */
.cat-overview-header {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}
.cat-overview-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--primary);
  margin: 0;
}
.cat-overview-sub {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 13px;
  color: var(--text-dim);
  margin: 0;
}
.cat-sub-icon { width: 15px; height: 15px; }

/* 分类卡片网格 */
.cat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1rem;
  margin-top: 0.5rem;
}
.cat-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: var(--bg-card);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-lg);
  padding: 1.4rem 1.4rem;
  cursor: pointer;
  transition: all var(--transition);
  box-shadow: var(--shadow-sm);
  animation: fadeUp 0.4s ease both;
}
.cat-card:hover {
  transform: translateY(-3px);
  border-color: var(--primary-light);
  box-shadow: var(--shadow-md);
}
.cat-icon {
  width: 48px; height: 48px; flex-shrink: 0;
  border-radius: 12px;
  background: var(--primary-bg);
  color: var(--primary);
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;
}
.cat-icon svg { width: 22px; height: 22px; }
.cat-card:hover .cat-icon {
  background: var(--primary);
  color: #fff;
}
.cat-info { flex: 1; min-width: 0; }
.cat-name {
  font-size: 17px; font-weight: 700;
  color: var(--text);
  margin-bottom: 0.2rem;
  transition: color 0.2s;
}
.cat-card:hover .cat-name { color: var(--primary); }
.cat-count {
  font-size: 13px;
  color: var(--text-dim);
}
.cat-arrow {
  width: 34px; height: 34px; flex-shrink: 0;
  border-radius: 50%;
  background: var(--bg-body);
  border: 1px solid var(--border-strong);
  color: var(--text-secondary);
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;
}
.cat-arrow svg { width: 16px; height: 16px; }
.cat-card:hover .cat-arrow {
  background: var(--primary);
  border-color: var(--primary);
  color: #fff;
  transform: translateX(3px);
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* 响应式 */
@media (max-width: 640px) {
  .cat-grid { grid-template-columns: 1fr; }
}

/* ========== 文章详情视图（/posts/:id） ========== */
.detail-loading {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; padding: 4rem 1rem; gap: 1rem; color: var(--text-dim);
}
.loading-spinner {
  width: 36px; height: 36px; border: 3px solid var(--border-strong);
  border-top-color: var(--primary); border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* 字数 + 阅读时间 */
.detail-word-info {
  display: flex; align-items: center; gap: 0.75rem;
  font-size: 13px; color: var(--text-dim);
  padding: 0.5rem 0.2rem;
}
.dwi-item {
  display: inline-flex; align-items: center; gap: 0.3rem;
}
.dwi-icon { width: 14px; height: 14px; stroke: currentColor; opacity: 0.65; }
.dwi-sep { opacity: 0.35; font-size: 11px; }

/* 绿色左边栏标题 */
.detail-title-block {
  display: flex; align-items: stretch;
  padding: 0; margin-bottom: 0.8rem;
}
.detail-title {
  font-size: clamp(1.5rem, 2.8vw, 2rem); font-weight: 800;
  color: var(--text); line-height: 1.35;
  padding: 1.4rem 1.5rem 1.3rem 1.2rem;
  margin: 0;
}

/* meta 行 */
.detail-meta-row {
  display: flex; align-items: center; gap: 0.45rem;
  flex-wrap: wrap; font-size: 13px;
  padding: 0 0.2rem 0.8rem;
  color: var(--text-dim);
}
.dm-item {
  display: inline-flex; align-items: center; gap: 0.25rem;
}
.dm-icon { width: 13px; height: 13px; stroke: currentColor; opacity: 0.6; }
.dm-sep { color: var(--border-strong); font-size: 11px; margin: 0 0.15rem; }
.dm-tag {
  color: var(--primary); font-weight: 500;
}
.dm-tag:not(:last-child)::after {
  content: ' / '; color: var(--text-dim); font-weight: 400;
  margin: 0 0.1rem;
}

/* 封面图 */
.detail-cover {
  border-radius: var(--radius-lg);
  overflow: hidden; margin-bottom: 1rem;
  background: var(--bg-body);
}
.detail-cover img {
  width: 100%; max-height: 400px; object-fit: cover;
  display: block;
}

/* Markdown 正文 */
.detail-body {
  padding: 1.8rem 2rem 2.5rem !important;
  font-size: 15.2px; line-height: 1.85;
  color: var(--text-secondary); word-break: break-word;
}
.detail-body :deep(h2), .detail-body :deep(h3) {
  margin: 1.8em 0 0.75em; color: var(--text); font-weight: 700;
}
.detail-body :deep(h2) {
  font-size: 1.48rem; padding-bottom: 0.35rem;
  border-bottom: 2px solid var(--primary-bg);
}
.detail-body :deep(h3) { font-size: 1.22rem; }
.detail-body :deep(p) { margin: 0 0 1em; }
.detail-body :deep(code) {
  background: #f1f5f9; color: #be123c;
  padding: 0.15em 0.45em; border-radius: 5px; font-size: 13px;
}
.detail-body :deep(pre) {
  background: #1e293b; border-radius: var(--radius);
  padding: 1rem; overflow-x: auto; margin: 1em 0;
}
.detail-body :deep(pre code) { background: none; padding: 0; color: #e2e8f0; }
.detail-body :deep(strong) { color: var(--text); font-weight: 700; }
.detail-body :deep(blockquote) {
  border-left: 4px solid var(--primary);
  padding: 0.6rem 1rem; margin: 1em 0;
  background: var(--primary-bg);
  border-radius: 0 var(--radius) var(--radius) 0;
  color: var(--text-dim);
}
.detail-body :deep(li) { margin-left: 1.5rem; margin-bottom: 0.3rem; }
.detail-body :deep(img) { max-width: 100%; border-radius: var(--radius); margin: 1em 0; }
.detail-body :deep(a) { color: var(--primary); text-decoration: none; }
.detail-body :deep(a:hover) { text-decoration: underline; }
.detail-body :deep(table) { border-collapse: collapse; width: 100%; margin: 1em 0; }
.detail-body :deep(th), .detail-body :deep(td) {
  border: 1px solid var(--border-strong); padding: 0.5rem 0.75rem;
  text-align: left; font-size: 13.5px;
}
.detail-body :deep(th) { background: var(--bg-body); font-weight: 600; }

/* 删除按钮 */
.-detail-actions {
  display: flex; justify-content: flex-end; padding: 0.5rem 0.2rem;
}
.btn-delete {
  padding: 0.5rem 1.3rem; border-radius: 10px;
  background: #fef2f2; color: #dc2626;
  border: 1px solid #fecaca; font-size: 13px; cursor: pointer;
  transition: all 0.2s; font-weight: 500;
}
.btn-delete:hover { background: #dc2626; color: #fff; }

/* 详情暗色模式 */
html[data-theme='dark'] .detail-body code {
  background: rgba(51,65,85,0.5); color: #fca5a5;
}
html[data-theme='dark'] .btn-delete {
  background: rgba(127,29,29,0.3); border-color: rgba(220,38,38,0.3);
}
html[data-theme='dark'] .btn-delete:hover { background: #dc2626; color: #fff; }
html[data-theme='dark'] .detail-body pre { border-color: rgba(255,255,255,0.06); }
html[data-theme='dark'] .dm-icon { opacity: 0.45; }
html[data-theme='dark'] .dwi-icon { opacity: 0.45; }

/* Hero 区域：详情页时副标题显示发布信息 */
html[data-theme='dark'] .hero-area::after {
  background: linear-gradient(180deg,
    rgba(0,0,0,0) 40%,
    rgba(15,23,42,0.6) 75%,
    var(--bg-body) 100%
  );
}

/* ========== 页脚 ========== */
.site-footer {
  text-align: center;
  padding: 2rem 1.5rem 2.5rem;
  margin-top: 0;
  border-top: 1px dashed var(--border);
  max-width: var(--max-width, 1200px);
  margin-left: auto;
  margin-right: auto;
}
.footer-copy {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 0.4rem;
  letter-spacing: 0.3px;
}
.footer-copy strong {
  color: var(--primary);
  font-weight: 600;
}
.footer-motto {
  font-size: 12.5px;
  color: var(--text-dim, #9ca3af);
  font-style: italic;
  letter-spacing: 0.5px;
  opacity: 0.8;
}

/* ========== 标签页 ========== */
.tag-overview-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  padding: 1.2rem 1.4rem;
}
.tag-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.45rem 0.85rem;
  border-radius: 20px;
  background: var(--bg-body, #f8fafc);
  border: 1px solid var(--border, #e2e8f0);
  color: var(--text-primary, #334155);
  font-size: 13px;
  text-decoration: none;
  transition: all 0.2s ease;
  font-weight: 500;
}
.tag-chip:hover {
  background: var(--primary-bg, #f0fdf4);
  color: var(--primary, #059669);
  border-color: var(--primary, #059669);
  transform: translateY(-1px);
}
.tag-chip-count {
  font-size: 11px;
  background: rgba(100,116,139,0.12);
  color: var(--text-secondary, #64748b);
  padding: 0.08rem 0.5rem;
  border-radius: 10px;
  font-weight: 600;
}
.tag-chip:hover .tag-chip-count {
  background: var(--primary, #059669);
  color: #fff;
}

/* Top 10 排行 */
.top10-card {
  padding: 1.3rem 1.5rem;
}
.top10-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary, #1e293b);
  margin-bottom: 1rem;
  border-left: 3.5px solid var(--primary, #059669);
  padding-left: 0.7rem;
}
.top10-list {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
}
.top10-item {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.35rem 0;
}
.top10-rank {
  width: 22px;
  text-align: center;
  font-size: 13px;
  font-weight: 700;
  color: var(--text-dim, #94a3b8);
  flex-shrink: 0;
}
.top10-item:nth-child(1) .top10-rank { color: #ef4444; }
.top10-item:nth-child(2) .top10-rank { color: #f59e0b; }
.top10-item:nth-child(3) .top10-rank { color: #059669; }
.top10-name {
  font-size: 13.5px;
  font-weight: 600;
  color: var(--text-primary, #1e293b);
  min-width: 80px;
  flex-shrink: 0;
}
.top10-bar-wrap {
  flex: 1;
  height: 8px;
  background: rgba(100,116,139,0.1);
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}
.top10-bar {
  height: 100%;
  background: linear-gradient(90deg, var(--primary, #059669), #34d399);
  border-radius: 4px;
  transition: width 0.4s ease;
  min-width: 0;
}
.top10-count {
  font-size: 12px;
  color: var(--primary, #059669);
  font-weight: 600;
  white-space: nowrap;
  flex-shrink: 0;
  min-width: 52px;
  text-align: right;
}

/* ========== AI 聊天样式 ========== */
.ai-chat-wrapper {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 0 !important;
}

/* ---- 聊天顶部 ---- */
.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--border-strong);
  flex-shrink: 0;
}
.chat-header-left {
  display: flex; align-items: center; gap: 0.75rem;
}
.chat-icon { font-size: 26px; }
.chat-header h2 { font-size: 1.05rem; font-weight: 700; color: var(--text); margin: 0; }
.chat-subtitle {
  font-size: 12px; color: var(--text-dim);
  display: flex; align-items: center; gap: 0.35rem; margin-top: 1px;
}
.dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.dot-online { background: var(--success); box-shadow: 0 0 6px var(--success); }
.dot-offline { background: #f59e0b; box-shadow: 0 0 6px #f59e0b; }
.btn-clear {
  padding: 0.35rem 0.9rem; border-radius: 16px;
  border: 1px solid var(--border-strong); background: transparent;
  color: var(--text-muted); font-size: 12px; cursor: pointer; transition: all 0.2s;
}
.btn-clear:hover { border-color: var(--danger); color: var(--danger); }

/* ---- 消息区域 ---- */
.chat-messages {
  flex: 1; overflow-y: auto;
  padding: 1.25rem 1.25rem 0.5rem;
  scroll-behavior: smooth;
  min-height: 360px;
  max-height: calc(100vh - 420px);
}

/* 欢迎语 */
.welcome { text-align: center; padding: 3rem 1rem; animation: fadeUp 0.5s ease; }
.welcome-icon { font-size: 44px; margin-bottom: 1rem; }
.welcome h3 { font-size: 1.2rem; color: var(--text); margin-bottom: 0.45rem; }
.welcome p { font-size: 14px; color: var(--text-muted); margin-bottom: 1.5rem; }
.suggestions { display: flex; flex-wrap: wrap; gap: 0.5rem; justify-content: center; }
.sug-btn {
  padding: 0.45rem 1rem; border-radius: 20px;
  border: 1px solid var(--border-accent); background: var(--primary-bg);
  color: var(--primary-dark); font-size: 13px; cursor: pointer; transition: all 0.2s; font-weight: 500;
}
.sug-btn:hover { background: var(--primary); color: #fff; border-color: var(--primary); }

/* ---- 消息气泡 ---- */
.msg-row { margin-bottom: 1rem; }
.msg-row.user { display: flex; justify-content: flex-end; }
.msg-bubble {
  display: flex; gap: 0.55rem; max-width: 85%; animation: fadeUp 0.3s ease;
}
.msg-bubble.user { flex-direction: row-reverse; }
.msg-avatar {
  width: 32px; height: 32px; flex-shrink: 0; margin-top: 2px;
  display: flex; align-items: center; justify-content: center;
}
.avatar-img { width: 32px; height: 32px; border-radius: 50%; object-fit: cover; border: 1px solid var(--border-strong); }
.avatar-placeholder {
  width: 32px; height: 32px; border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  color: #fff; font-size: 13px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
}
.msg-content {
  padding: 0.65rem 1rem; border-radius: 16px;
  font-size: 14px; line-height: 1.65; word-break: break-word;
}
.msg-bubble.assistant .msg-content {
  background: var(--bg-body); border: 1px solid var(--border-strong);
  border-radius: 4px 16px 16px 16px; box-shadow: none;
  color: var(--text);
}
.msg-bubble.user .msg-content {
  background: var(--primary); color: #fff;
  border-radius: 16px 4px 16px 16px;
}
.user-text { white-space: pre-wrap; }

/* ---- 打字动画 ---- */
.typing { align-items: center; }
.typing-dots { display: flex; gap: 4px; padding: 0.5rem 0.25rem; }
.typing-dots span {
  width: 7px; height: 7px; border-radius: 50%;
  background: var(--text-dim); animation: bounce 1.4s infinite ease-in-out both;
}
.typing-dots span:nth-child(1) { animation-delay: -0.32s; }
.typing-dots span:nth-child(2) { animation-delay: -0.16s; }

/* ---- 输入区域 ---- */
.chat-input-area {
  display: flex; align-items: flex-end; gap: 0.6rem;
  padding: 0.75rem 1.25rem; border-top: 1px solid var(--border-strong);
  flex-shrink: 0;
}
.chat-input {
  flex: 1; padding: 0.65rem 1rem; border-radius: 14px;
  border: 1px solid var(--border-strong);
  background: var(--bg-body); color: var(--text);
  font-size: 14px; font-family: inherit; line-height: 1.5;
  outline: none; resize: none; max-height: 150px; transition: all 0.2s;
}
.chat-input:focus { border-color: var(--primary); box-shadow: 0 0 0 3px rgba(16,185,129,0.1); }
.chat-input::placeholder { color: var(--text-dim); }
.chat-input:disabled { opacity: 0.5; }
.btn-send {
  width: 38px; height: 38px; border-radius: 50%; border: none;
  background: var(--primary); color: #fff; font-size: 18px;
  cursor: pointer; display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; transition: all 0.2s; box-shadow: 0 2px 10px rgba(5,150,105,0.25);
}
.btn-send:hover:not(:disabled) { transform: translateY(-1px); background: var(--primary-dark); box-shadow: 0 4px 14px rgba(5,150,105,0.35); }
.btn-send:disabled { opacity: 0.4; cursor: not-allowed; }
.spinner {
  width: 14px; height: 14px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff; border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

/* Markdown 内容样式 */
.ai-chat-wrapper .markdown-body :deep(p) { margin: 0 0 0.5rem; }
.ai-chat-wrapper .markdown-body :deep(p:last-child) { margin-bottom: 0; }
.ai-chat-wrapper .markdown-body :deep(code) {
  background: var(--primary-bg); color: #be123c; padding: 0.15em 0.4em;
  border-radius: 5px; font-size: 13px; font-family: 'Fira Code', monospace;
}
.ai-chat-wrapper .markdown-body :deep(pre) {
  background: #1e293b; border: 1px solid #334155;
  border-radius: 10px; padding: 0.85rem 1.1rem; overflow-x: auto; margin: 0.5rem 0;
}
.ai-chat-wrapper .markdown-body :deep(pre code) { background: none; padding: 0; color: #e2e8f0; font-size: 13px; }
.ai-chat-wrapper .markdown-body :deep(strong) { color: var(--text); font-weight: 700; }
.ai-chat-wrapper .markdown-body :deep(h2), .ai-chat-wrapper .markdown-body :deep(h3), .ai-chat-wrapper .markdown-body :deep(h4) {
  margin: 0.6rem 0 0.3rem; color: var(--text); font-weight: 700;
}
.ai-chat-wrapper .markdown-body :deep(li) { margin-left: 1.2rem; margin-bottom: 0.15rem; }
.ai-chat-wrapper .markdown-body :deep(blockquote) {
  border-left: 3px solid var(--primary);
  padding: 0.3rem 0 0.3rem 0.75rem; margin: 0.4rem 0;
  color: var(--text-muted); font-style: italic; background: var(--primary-bg);
  border-radius: 0 var(--radius) var(--radius) 0;
}
.ai-chat-wrapper .markdown-body :deep(table) {
  border-collapse: collapse; width: 100%; margin: 0.5rem 0; font-size: 13px;
  border: 1px solid var(--border-strong); border-radius: var(--radius); overflow: hidden;
}
.ai-chat-wrapper .markdown-body :deep(th), .ai-chat-wrapper .markdown-body :deep(td) {
  border: 1px solid var(--border-strong); padding: 0.4rem 0.65rem; text-align: left;
}
.ai-chat-wrapper .markdown-body :deep(th) { background: var(--bg-body); font-weight: 600; color: var(--text); }

/* ===== 暗色模式 AI 聊天适配 ===== */
html[data-theme='dark'] .msg-bubble.assistant .msg-content {
  background: rgba(30, 41, 59, 0.75);
  border-color: rgba(148, 163, 184, 0.12);
}
html[data-theme='dark'] .ai-chat-wrapper .markdown-body :deep(code) {
  background: rgba(5, 150, 105, 0.12); color: #f472b6;
}
html[data-theme='dark'] .ai-chat-wrapper .markdown-body :deep(pre) {
  background: #0f172a; border-color: rgba(148, 163, 184, 0.1);
}
html[data-theme='dark'] .ai-chat-wrapper .markdown-body :deep(blockquote) {
  border-left-color: var(--primary); background: rgba(5, 150, 105, 0.06);
}
html[data-theme='dark'] .welcome h3 { color: #e2e8f0; }
html[data-theme='dark'] .welcome p { color: #94a3b8; }
html[data-theme='dark'] .sug-btn { border-color: rgba(148, 163, 184, 0.2); }

@keyframes fadeUp { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
@keyframes bounce { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); } }
@keyframes spin { to { transform: rotate(360deg); } }

@media (max-width: 768px) {
  .chat-messages { max-height: calc(100vh - 380px); }
  .msg-bubble { max-width: 92%; }
  .suggestions { flex-direction: column; align-items: center; }
}

/* ========== 写文章编辑器 ========== */
.editor-wrap {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.5rem;
}
.editor-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  flex-wrap: wrap;
}
.editor-heading {
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--text);
  margin: 0;
}
.editor-actions-row {
  display: flex;
  gap: 0.6rem;
}
.btn-editor {
  padding: 0.5rem 1.4rem;
  border-radius: 24px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition);
  border: none;
}
.btn-editor-primary {
  background: var(--primary);
  color: white;
  box-shadow: 0 2px 10px rgba(5,150,105,0.25);
}
.btn-editor-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  background: var(--primary-dark);
  box-shadow: 0 4px 14px rgba(5,150,105,0.35);
}
.btn-editor-primary:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
.btn-editor-outline {
  border: 1px solid var(--border-strong);
  background: transparent;
  color: var(--text-secondary);
}
.btn-editor-outline:hover {
  background: var(--bg-body);
  border-color: var(--primary);
  color: var(--primary);
}
.editor-title-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border-radius: 10px;
  border: 1px solid var(--border-strong);
  background: var(--bg-body);
  color: var(--text);
  font-size: 20px;
  font-weight: 700;
  outline: none;
  transition: all var(--transition);
  box-shadow: inset 0 1px 2px rgba(0,0,0,0.03);
}
.editor-title-input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(16,185,129,0.12);
}
.editor-title-input::placeholder { color: var(--text-dim); }
.editor-meta-row {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}
.editor-select,
.editor-extra-input {
  flex: 1;
  min-width: 140px;
  padding: 0.55rem 0.9rem;
  border-radius: 10px;
  border: 1px solid var(--border-strong);
  background: var(--bg-body);
  color: var(--text);
  font-size: 13px;
  outline: none;
  transition: all var(--transition);
  box-shadow: inset 0 1px 2px rgba(0,0,0,0.03);
}
.editor-select:focus,
.editor-extra-input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(16,185,129,0.08);
}
.editor-toolbar {
  display: flex;
  gap: 0.3rem;
  flex-wrap: wrap;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--border-strong);
}
.toolbar-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  border: none;
  background: transparent;
  color: var(--text-muted);
  font-size: 14px;
  cursor: pointer;
  transition: all var(--transition);
  font-weight: 700;
}
.toolbar-btn:hover {
  background: var(--primary-bg);
  color: var(--primary-dark);
}
.editor-textarea {
  width: 100%;
  min-height: 420px;
  padding: 1rem;
  border-radius: 10px;
  border: 1px solid var(--border-strong);
  background: var(--bg-body);
  color: var(--text);
  font-size: 15px;
  font-family: 'Fira Code', 'Cascadia Code', monospace;
  line-height: 1.75;
  outline: none;
  resize: vertical;
  transition: all var(--transition);
  box-shadow: inset 0 1px 2px rgba(0,0,0,0.03);
}
.editor-textarea:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(16,185,129,0.08);
}
.editor-textarea::placeholder { color: var(--text-dim); }

/* 编辑器响应式 */
@media (max-width: 768px) {
  .editor-header-row {
    flex-direction: column;
    align-items: flex-start;
  }
  .editor-actions-row { align-self: flex-end; }
  .editor-meta-row { flex-direction: column; }
  .editor-toolbar { justify-content: flex-start; }
}
</style>

