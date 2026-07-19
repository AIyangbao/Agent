/**
 * 简易 Markdown 渲染器
 * 支持：标题、粗体、斜体、代码块、行内代码、列表、引用、表格
 */
export function renderMarkdown(text) {
  if (!text) return ''
  let html = text
    // 转义 HTML
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    // 代码块 ```...```
    .replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
    // 行内代码 `...`
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    // 粗体 **...**
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    // 斜体 *...*
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    // 表格（简易支持）
    .replace(/^\|(.+)\|$/gm, (line) => {
      const cells = line.split('|').filter(c => c.trim())
      if (cells.every(c => /^[-:]+$/.test(c.trim()))) return ''
      return '<tr>' + cells.map(c => `<td>${c.trim()}</td>`).join('') + '</tr>'
    })
    // 无序列表
    .replace(/^[-*] (.+)$/gm, '<li>$1</li>')
    // 有序列表
    .replace(/^\d+\. (.+)$/gm, '<li>$1</li>')
    // 引用 >
    .replace(/^&gt; (.+)$/gm, '<blockquote>$1</blockquote>')
    // 标题 ### ...
    .replace(/^### (.+)$/gm, '<h4>$1</h4>')
    .replace(/^## (.+)$/gm, '<h3>$1</h3>')
    .replace(/^# (.+)$/gm, '<h2>$1</h2>')
    // 换行
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br>')

  return '<p>' + html + '</p>'
}
