<template>
  <div class="profile-wrap">
    <div class="profile-header">
      <h1 class="profile-title">个人中心</h1>
      <p class="profile-sub">管理你的昵称、头像、简介与登录密码</p>
    </div>

    <!-- 个人资料 -->
    <section class="pf-card">
      <h2 class="pf-card-title">个人资料</h2>

      <!-- 头像 -->
      <div class="pf-avatar-row">
        <div
          class="pf-avatar"
          :style="profile.avatar ? { backgroundImage: 'url(' + profile.avatar + ')' } : {}"
        >
          <span v-if="!profile.avatar">{{ user.initial || 'U' }}</span>
        </div>
        <div class="pf-avatar-actions">
          <button class="pf-btn-ghost" type="button" @click="triggerAvatar" :disabled="uploading">
            {{ uploading ? `上传中 ${uploadProgress}%` : '更换头像' }}
          </button>
          <button
            v-if="profile.avatar"
            class="pf-btn-ghost danger"
            type="button"
            @click="profile.avatar = ''"
          >移除头像</button>
          <p class="pf-hint">支持 jpg/png/gif，复用了文章图片上传通道</p>
          <input
            ref="avatarInput"
            type="file"
            accept="image/*"
            hidden
            @change="onAvatarSelected"
          />
        </div>
      </div>

      <!-- 昵称 -->
      <div class="pf-field">
        <label class="pf-label">昵称</label>
        <input
          class="pf-input"
          v-model="profile.nickname"
          maxlength="20"
          placeholder="展示在评论与导航栏的名字"
        />
      </div>

      <!-- 简介 -->
      <div class="pf-field">
        <label class="pf-label">个人简介</label>
        <textarea
          class="pf-textarea"
          v-model="profile.bio"
          maxlength="200"
          rows="4"
          placeholder="一句话介绍你自己（最多 200 字）"
        ></textarea>
        <div class="pf-count">{{ (profile.bio || '').length }}/200</div>
      </div>

      <button class="pf-btn-primary" type="button" :disabled="savingProfile" @click="saveProfile">
        {{ savingProfile ? '保存中…' : '保存资料' }}
      </button>
    </section>

    <!-- 修改密码 -->
    <section class="pf-card">
      <h2 class="pf-card-title">修改密码</h2>
      <div class="pf-field">
        <label class="pf-label">当前密码</label>
        <input class="pf-input" type="password" v-model="pwd.old_password" placeholder="请输入当前密码" />
      </div>
      <div class="pf-field">
        <label class="pf-label">新密码</label>
        <input class="pf-input" type="password" v-model="pwd.new_password" placeholder="至少 6 位" />
      </div>
      <div class="pf-field">
        <label class="pf-label">确认新密码</label>
        <input class="pf-input" type="password" v-model="pwd.confirm" placeholder="再次输入新密码" />
      </div>
      <button class="pf-btn-primary" type="button" :disabled="savingPwd" @click="savePassword">
        {{ savingPwd ? '保存中…' : '更新密码' }}
      </button>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '../store'
import { useRouter } from 'vue-router'
import { inject } from 'vue'
import { getMe, updateProfile, updatePassword } from '../api/auth'
import { uploadImage } from '../api/posts'

const user = useUserStore()
const router = useRouter()
const toast = inject('toast')

const profile = ref({ nickname: '', bio: '', avatar: '' })
const pwd = ref({ old_password: '', new_password: '', confirm: '' })

const savingProfile = ref(false)
const savingPwd = ref(false)
const uploading = ref(false)
const uploadProgress = ref(0)
const avatarInput = ref(null)

onMounted(async () => {
  // 未登录保护：路由 meta.requiresAuth 但项目暂无全局守卫，这里兜底
  if (!user.isLoggedIn) {
    router.replace('/auth')
    return
  }
  try {
    const data = await getMe()
    profile.value = {
      nickname: data.nickname || '',
      bio: data.bio || '',
      avatar: data.avatar || ''
    }
  } catch (e) {
    toast && toast(e.message || '加载资料失败', 'error')
  }
})

function triggerAvatar() {
  avatarInput.value && avatarInput.value.click()
}

async function onAvatarSelected(e) {
  const file = e.target.files && e.target.files[0]
  if (!file) return
  if (!/^image\//.test(file.type)) {
    toast && toast('请选择图片文件', 'error')
    e.target.value = ''
    return
  }
  if (file.size > 5 * 1024 * 1024) {
    toast && toast('图片不能超过 5MB', 'error')
    e.target.value = ''
    return
  }
  uploading.value = true
  uploadProgress.value = 0
  try {
    const url = await uploadImage(file, (p) => { uploadProgress.value = p })
    profile.value.avatar = url
    toast && toast('头像已上传，记得点“保存资料”', 'success')
  } catch (err) {
    toast && toast(err.message || '头像上传失败', 'error')
  } finally {
    uploading.value = false
    e.target.value = ''
  }
}

async function saveProfile() {
  if (savingProfile.value) return
  savingProfile.value = true
  try {
    await updateProfile({
      nickname: profile.value.nickname || null,
      bio: profile.value.bio || null,
      avatar: profile.value.avatar || null
    })
    // 同步到导航栏（头像 + 昵称）
    user.setProfile({
      nickname: profile.value.nickname || null,
      avatar: profile.value.avatar || null
    })
    toast && toast('资料已更新 ✨', 'success')
  } catch (e) {
    toast && toast(e.message || '保存失败', 'error')
  } finally {
    savingProfile.value = false
  }
}

async function savePassword() {
  if (savingPwd.value) return
  const { old_password, new_password, confirm } = pwd.value
  if (!old_password || !new_password) {
    toast && toast('请填写完整密码信息', 'error')
    return
  }
  if (new_password.length < 6) {
    toast && toast('新密码至少 6 位', 'error')
    return
  }
  if (new_password !== confirm) {
    toast && toast('两次新密码不一致', 'error')
    return
  }
  savingPwd.value = true
  try {
    await updatePassword(old_password, new_password)
    pwd.value = { old_password: '', new_password: '', confirm: '' }
    toast && toast('密码修改成功 🔒', 'success')
  } catch (e) {
    toast && toast(e.message || '修改失败', 'error')
  } finally {
    savingPwd.value = false
  }
}
</script>

<style scoped>
.profile-wrap {
  max-width: 640px;
  margin: 0 auto;
  padding: 96px 1rem 3rem;
}
.profile-header { margin-bottom: 1.75rem; }
.profile-title {
  font-size: 26px; font-weight: 800; color: var(--text);
  margin: 0 0 0.35rem;
}
.profile-sub { font-size: 14px; color: var(--text-muted); margin: 0; }

.pf-card {
  background: var(--bg-card);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-lg);
  padding: 1.75rem;
  margin-bottom: 1.5rem;
  box-shadow: var(--shadow-md);
}
.pf-card-title {
  font-size: 17px; font-weight: 700; color: var(--text);
  margin: 0 0 1.25rem;
}

.pf-avatar-row {
  display: flex; align-items: center; gap: 1.25rem;
  margin-bottom: 1.5rem;
}
.pf-avatar {
  width: 72px; height: 72px; border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  background-size: cover; background-position: center;
  display: flex; align-items: center; justify-content: center;
  font-size: 24px; font-weight: 700; color: #fff;
  flex-shrink: 0; overflow: hidden;
  border: 2px solid rgba(255,255,255,0.8);
  box-shadow: var(--shadow-sm);
}
.pf-avatar-actions { display: flex; flex-direction: column; gap: 0.5rem; }
.pf-hint { font-size: 12px; color: var(--text-dim); margin: 0.25rem 0 0; }

.pf-field { margin-bottom: 1.1rem; }
.pf-label {
  display: block; font-size: 13px; color: var(--text-secondary);
  margin-bottom: 0.4rem; font-weight: 500;
}
.pf-input, .pf-textarea {
  width: 100%; padding: 0.65rem 0.9rem;
  border-radius: 10px; border: 1px solid var(--border-strong);
  background: var(--bg-body); color: var(--text); font-size: 14px;
  outline: none; transition: all var(--transition);
  font-family: inherit; resize: vertical;
  box-shadow: inset 0 1px 2px rgba(0,0,0,0.03);
}
.pf-input:focus, .pf-textarea:focus {
  border-color: var(--primary); box-shadow: 0 0 0 3px rgba(16,185,129,0.12);
}
.pf-input::placeholder, .pf-textarea::placeholder { color: var(--text-dim); }
.pf-count { text-align: right; font-size: 12px; color: var(--text-dim); margin-top: 0.3rem; }

.pf-btn-primary {
  width: 100%; padding: 0.72rem; border-radius: 12px; border: none;
  background: var(--primary); color: white; font-size: 15px; font-weight: 700;
  cursor: pointer; transition: all var(--transition); letter-spacing: 0.5px;
  margin-top: 0.25rem; box-shadow: 0 4px 14px rgba(5,150,105,0.28);
}
.pf-btn-primary:hover:not(:disabled) {
  background: var(--primary-dark); transform: translateY(-1px);
  box-shadow: 0 6px 18px rgba(5,150,105,0.35);
}
.pf-btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }

.pf-btn-ghost {
  align-self: flex-start; padding: 0.45rem 0.9rem;
  border-radius: 9px; border: 1px solid var(--border-strong);
  background: var(--bg-body); color: var(--text-secondary);
  font-size: 13px; font-weight: 500; cursor: pointer;
  transition: all var(--transition);
}
.pf-btn-ghost:hover:not(:disabled) { border-color: var(--primary); color: var(--primary); }
.pf-btn-ghost:disabled { opacity: 0.6; cursor: not-allowed; }
.pf-btn-ghost.danger { color: var(--danger); border-color: rgba(239,68,68,0.3); }
.pf-btn-ghost.danger:hover { background: #fef2f2; }

@media (max-width: 640px) {
  .pf-card { padding: 1.25rem; }
}
</style>
