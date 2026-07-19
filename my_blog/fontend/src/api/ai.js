import { post } from './request'

/**
 * 发送消息给 AI，获取回复（非流式，兼容旧逻辑）
 * @param {string} message - 用户输入的消息
 * @param {Array} history - 可选，历史对话 [{role:'user'|'assistant', content}]
 * @returns {Promise<{reply: string}>}
 */
export function chatWithAI(message, history = []) {
  return post('/ai/chat', { message, history })
}

/**
 * 流式对话：调用 /api/ai/chat，每收到一个 token 回调 onToken
 * 后端以 SSE 格式返回：data: {"reply":"..."}\n\n
 *
 * 错误分类（抛出带 code 字段的 Error）：
 *   - 'NETWORK'  网络故障 / 后端未启动（fetch 失败）
 *   - 'AUTH'     401 登录失效，需重新登录
 *   - 'SERVER'   5xx 服务异常
 *   - 'STREAM'   流传输中途业务报错（已部分输出）
 *
 * @param {string} message
 * @param {Array} history
 * @param {(token: string) => void} onToken 每收到一段文本触发
 */
export async function chatWithAIStream(message, history = [], onToken) {
  const token = localStorage.getItem('blog_token')

  // 1) 网络层错误（后端没起 / 断网）→ NETWORK
  let resp
  try {
    resp = await fetch('/api/ai/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({ message, history }),
    })
  } catch (networkErr) {
    const err = new Error('网络异常，已进入演示模式')
    err.code = 'NETWORK'
    throw err
  }

  // 2) HTTP 状态错误
  if (!resp.ok) {
    let msg = `HTTP ${resp.status}`
    try {
      const errBody = await resp.json()
      msg = errBody.message || msg
    } catch (e) { /* ignore */ }
    const err = new Error(msg)
    err.code = resp.status === 401 ? 'AUTH' : 'SERVER'
    throw err
  }

  // 3) 读取 SSE 流
  const reader = resp.body.getReader()
  const decoder = new TextDecoder('utf-8')
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })

    // 按 SSE 分隔符 `\n\n` 切分事件
    let sep
    while ((sep = buffer.indexOf('\n\n')) !== -1) {
      const chunk = buffer.slice(0, sep)
      buffer = buffer.slice(sep + 2)
      const line = chunk.trim()
      if (line.startsWith('data:')) {
        const payload = line.slice(5).trim()
        try {
          const json = JSON.parse(payload)
          if (json.reply) onToken(json.reply)
          if (json.error) {
            const err = new Error(json.error)
            err.code = 'STREAM'
            throw err
          }
        } catch (e) {
          // 只有 JSON 解析错误才忽略；业务错误(STREAM)重新抛出
          if (e.code === 'STREAM') throw e
        }
      }
    }
  }
}
