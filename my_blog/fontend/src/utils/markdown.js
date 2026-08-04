/**
 * 简易 Markdown 渲染器（接入 highlight.js 做代码高亮）
 * 支持：标题、粗体、斜体、代码块（语法高亮）、行内代码、列表、引用、表格
 */
import hljs from 'highlight.js/lib/common'
import 'highlight.js/styles/atom-one-dark.css'
import katex from 'katex'
import 'katex/dist/katex.min.css'

function escapeHtml(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

// 标题转锚点 id：小写、空白转连字符、保留中文与字母数字，去除其它符号
function slugify(text) {
  return (text || '')
    .toLowerCase()
    .trim()
    .replace(/\s+/g, '-')
    .replace(/[^\w\u4e00-\u9fa5-]/g, '')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '')
}

function safeUrl(url) {
  const u = (url || '').trim()
  // 仅允许 http/https/相对路径/data:image，阻断 javascript: 等危险协议
  if (/^(https?:|\/|data:image\/)/i.test(u)) return u
  if (/^[^a-z]+:/i.test(u)) return ''
  return u
}

// 渲染 LaTeX 数学公式为 HTML（KaTeX）。throwOnError:false 时公式语法错误只标红不抛异常。
function renderMath(expr, displayMode) {
  try {
    return katex.renderToString(expr.trim(), { displayMode, throwOnError: false })
  } catch (e) {
    return `<code class="math-error">${escapeHtml(expr)}</code>`
  }
}

function renderInline(text) {
  // 先抽取数学公式，避免 & < > 被转义、* 被当成斜体而破坏公式
  const mathStore = []
  let s = text
  // 块级 $$...$$
  s = s.replace(/\$\$([\s\S]+?)\$\$/g, (_, expr) => {
    const token = `\u0000M${mathStore.length}\u0000`
    mathStore.push(renderMath(expr, true))
    return token
  })
  // 行内 $...$
  s = s.replace(/\$([^$\n]+?)\$/g, (_, expr) => {
    const token = `\u0000M${mathStore.length}\u0000`
    mathStore.push(renderMath(expr, false))
    return token
  })
  // 仅转义非公式文本（占位符 \u0000M\d+\u0000 不被 escapeHtml 影响）
  s = escapeHtml(s)
  s = s
    // 行内代码 `...`
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    // 图片 ![alt](url) → 原生懒加载 + 可点击放大
    .replace(/!\[([^\]]*)\]\(([^)\s]+)\)/g, (_, alt, url) => {
      const safe = safeUrl(url)
      if (!safe) return ''
      return `<img src="${safe}" alt="${alt}" loading="lazy" class="md-image" referrerpolicy="no-referrer">`
    })
    // 链接 [text](url) → 新窗口打开
    .replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, (_, label, url) => {
      const safe = safeUrl(url)
      if (!safe) return escapeHtml(label)
      return `<a href="${safe}" target="_blank" rel="noopener noreferrer">${label}</a>`
    })
    // 粗体 **...**
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    // 斜体 *...*
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    // 表格（简易支持）
    .replace(/^\|(.+)\|$/gm, (line) => {
      const cells = line.split('|').filter((c) => c.trim())
      if (cells.every((c) => /^[-:]+$/.test(c.trim()))) return ''
      return '<tr>' + cells.map((c) => `<td>${c.trim()}</td>`).join('') + '</tr>'
    })
    // 无序列表
    .replace(/^[-*] (.+)$/gm, '<li>$1</li>')
    // 有序列表
    .replace(/^\d+\. (.+)$/gm, '<li>$1</li>')
    // 引用 >
    .replace(/^&gt; (.+)$/gm, '<blockquote>$1</blockquote>')
    // 标题 ### ...（给标题加 id，供目录锚定；注意顺序先长后短）
    .replace(/^### (.+)$/gm, (_, c) => `<h4 id="${slugify(c.trim())}">${c}</h4>`)
    .replace(/^## (.+)$/gm, (_, c) => `<h3 id="${slugify(c.trim())}">${c}</h3>`)
    .replace(/^# (.+)$/gm, (_, c) => `<h2 id="${slugify(c.trim())}">${c}</h2>`)
    // 换行
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br>')
  // 回填公式渲染结果
  return s.replace(/\u0000M(\d+)\u0000/g, (_, i) => mathStore[+i])
}

export function renderMarkdown(text) {
  if (!text) return ''
  // 先按代码块切分，避免被转义/行内规则破坏；代码块用 hljs 高亮
  const parts = text.split(/```(\w*)\n([\s\S]*?)```/g)
  let out = ''
  for (let i = 0; i < parts.length; i += 3) {
    const before = parts[i]
    if (before) out += '<p>' + renderInline(before) + '</p>'
    const lang = parts[i + 1]
    const code = parts[i + 2]
    if (code !== undefined) {
      const langLower = (lang || '').toLowerCase()
      let highlighted
      try {
        highlighted =
          langLower && hljs.getLanguage(langLower)
            ? hljs.highlight(code, { language: langLower }).value
            : hljs.highlightAuto(code).value
      } catch (e) {
        highlighted = escapeHtml(code)
      }
      const cls = langLower ? ` class="hljs language-${langLower}"` : ' class="hljs"'
      out += `<pre><code${cls}>${highlighted}</code></pre>`
    }
  }
  return out
}

/**
 * 给已渲染的 Markdown 容器内的代码块增强：加行号 + 复制按钮。
 * 因为代码块通过 v-html 渲染，无法在模板里绑事件，这里直接操作真实 DOM。
 * 幂等：已处理过的 pre 会跳过（避免 watch 重复触发时双重包裹）。
 */
export function enhanceCodeBlocks(root) {
  if (!root || typeof document === 'undefined') return
  const blocks = root.querySelectorAll('pre > code')
  blocks.forEach((codeEl) => {
    const pre = codeEl.parentElement
    if (!pre || pre.parentElement?.classList.contains('code-block')) return

    // 行号：高亮后的 HTML 按行包裹。hljs 的换行都在 span 之外，按 \n 切分安全。
    let html = codeEl.innerHTML
    let lines = html.split('\n')
    if (lines.length && lines[lines.length - 1] === '') lines.pop()
    codeEl.innerHTML = lines
      .map((l) => `<span class="code-line">${l || ' '}</span>`)
      .join('\n')

    // 外层包裹 + 头部（语言标签 + 复制按钮）
    const wrapper = document.createElement('div')
    wrapper.className = 'code-block'
    const header = document.createElement('div')
    header.className = 'code-header'
    const m = codeEl.className.match(/language-([\w-]+)/)
    const lang = m ? m[1] : 'text'
    header.innerHTML =
      `<span class="code-lang">${escapeHtml(lang)}</span>` +
      `<button type="button" class="code-copy">复制</button>`
    pre.parentNode.insertBefore(wrapper, pre)
    wrapper.appendChild(header)
    wrapper.appendChild(pre)

    const btn = header.querySelector('.code-copy')
    btn.addEventListener('click', () => {
      const text = codeEl.textContent
      const ok = () => {
        btn.textContent = '已复制 ✓'
        btn.classList.add('copied')
        setTimeout(() => {
          btn.textContent = '复制'
          btn.classList.remove('copied')
        }, 1500)
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(ok).catch(() => fallbackCopy(text, ok))
      } else {
        fallbackCopy(text, ok)
      }
    })
  })
}

// 剪贴板 API 不可用时的降级方案（如非 HTTPS 的本地环境）
function fallbackCopy(text, done) {
  const ta = document.createElement('textarea')
  ta.value = text
  ta.style.position = 'fixed'
  ta.style.top = '-9999px'
  ta.style.opacity = '0'
  document.body.appendChild(ta)
  ta.focus()
  ta.select()
  try {
    document.execCommand('copy')
    done()
  } catch (e) {
    /* ignore */
  }
  document.body.removeChild(ta)
}

/**
 * 从 Markdown 源提取标题目录（TOC）。
 * 跳过代码块内的 # 注释，支持 # / ## / ### 三级。
 * 返回 [{ level, text, id }]，id 与 renderMarkdown 渲染的标题 id 完全一致。
 */
export function extractToc(text) {
  if (!text) return []
  const toc = []
  const parts = text.split(/```(\w*)\n([\s\S]*?)```/g)
  const seen = {}
  for (let i = 0; i < parts.length; i += 3) {
    const before = parts[i]
    if (!before) continue
    for (const line of before.split('\n')) {
      const m = /^(#{1,3})\s+(.+?)\s*$/.exec(line)
      if (!m) continue
      const level = m[1].length
      const raw = m[2].trim()
      if (!raw) continue
      let id = slugify(raw)
      if (!id) continue
      if (seen[id]) {
        seen[id] += 1
        id = `${id}-${seen[id]}`
      } else {
        seen[id] = 1
      }
      const display = raw.replace(/[*_`]/g, '').trim()
      toc.push({ level, text: display, id })
    }
  }
  return toc
}

// 图片灯箱单例（点击 md-image 放大查看）
let lightbox = null
function ensureLightbox() {
  if (lightbox) return lightbox
  lightbox = document.createElement('div')
  lightbox.id = 'md-lightbox'
  lightbox.className = 'md-lightbox'
  lightbox.innerHTML = '<img class="md-lightbox-img" alt="preview">'
  lightbox.addEventListener('click', () => lightbox.classList.remove('open'))
  document.body.appendChild(lightbox)
  return lightbox
}

/**
 * 给已渲染的 Markdown 容器内的图片绑定点击放大（lightbox）。
 * 与 enhanceCodeBlocks 同理，v-html 渲染内容无法在模板绑事件，直接操作真实 DOM。
 * 幂等：已绑定的图片跳过。
 */
export function enhanceImages(root) {
  if (!root || typeof document === 'undefined') return
  const lb = ensureLightbox()
  const lbImg = lb.querySelector('.md-lightbox-img')
  const imgs = root.querySelectorAll('img.md-image')
  imgs.forEach((img) => {
    if (img.dataset.zoomReady) return
    img.dataset.zoomReady = '1'
    img.addEventListener('click', () => {
      const src = img.currentSrc || img.src
      if (!src) return
      lbImg.src = src
      lbImg.alt = img.alt || ''
      lb.classList.add('open')
    })
  })
}
