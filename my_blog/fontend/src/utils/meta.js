/**
 * 轻量页面元信息管理（SPA 动态设置 SEO / 社交分享卡片）。
 * 不依赖 vue-meta，直接操作 document.head，适配本项目单组件多视图结构。
 */

const SITE_NAME = 'Firefly 的博客'
const SITE_DESC = '记录学习与项目心得 · In Code We Trust'

function upsertMeta(selector, attr, key, content) {
  let el = document.head.querySelector(selector)
  if (!el) {
    el = document.createElement('meta')
    if (attr) el.setAttribute(attr, key)
    document.head.appendChild(el)
  }
  el.setAttribute('content', content)
  return el
}

function removeMeta(selector) {
  const el = document.head.querySelector(selector)
  if (el) el.remove()
}

// 把可能是相对路径的图片地址补全为绝对 URL（社交平台要求 OG 图片为绝对地址）
function toAbsolute(url) {
  if (!url) return ''
  try {
    return new URL(url, window.location.origin).href
  } catch (e) {
    return url
  }
}

/**
 * 设置当前页面 meta（标题 / 描述 / Open Graph / Twitter Card）。
 * @param {Object} o
 * @param {string} [o.title]      文章标题（会自动拼接站点名）
 * @param {string} [o.description] 描述（建议 <=150 字）
 * @param {string} [o.image]       分享卡片封面图（相对/绝对均可，内部补全）
 * @param {string} [o.url]         页面地址（默认当前页）
 * @param {string} [o.type]        og:type，文章用 article，站点用 website
 */
export function setMeta({ title, description, image, url, type = 'article' } = {}) {
  const fullTitle = title ? `${title} · ${SITE_NAME}` : SITE_NAME
  document.title = fullTitle

  upsertMeta('meta[name="description"]', 'name', 'description', description || SITE_DESC)

  // Open Graph
  upsertMeta('meta[property="og:type"]', 'property', 'og:type', type)
  upsertMeta('meta[property="og:title"]', 'property', 'og:title', title || SITE_NAME)
  upsertMeta('meta[property="og:description"]', 'property', 'og:description', description || SITE_DESC)
  upsertMeta('meta[property="og:site_name"]', 'property', 'og:site_name', SITE_NAME)
  if (url) upsertMeta('meta[property="og:url"]', 'property', 'og:url', url)

  const absImg = toAbsolute(image || '')
  if (absImg) {
    upsertMeta('meta[property="og:image"]', 'property', 'og:image', absImg)
    upsertMeta('meta[name="twitter:image"]', 'name', 'twitter:image', absImg)
  } else {
    removeMeta('meta[property="og:image"]')
    removeMeta('meta[name="twitter:image"]')
  }

  // Twitter Card
  upsertMeta('meta[name="twitter:card"]', 'name', 'twitter:card', absImg ? 'summary_large_image' : 'summary')
  upsertMeta('meta[name="twitter:title"]', 'name', 'twitter:title', title || SITE_NAME)
  upsertMeta('meta[name="twitter:description"]', 'name', 'twitter:description', description || SITE_DESC)
}

// 恢复为站点首页默认 meta
export function resetMeta() {
  setMeta({ type: 'website' })
}
