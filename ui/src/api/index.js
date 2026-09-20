import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

export const orderAPI = {
  async list() {
    const response = await api.get('/order/list')
    return response.data
  }
}

export const ticketAPI = {
  async list() {
    const response = await api.get('/ticket/list')
    return response.data
  }
}

export const faqAPI = {
  async suggest(query, limit = 5) {
    const response = await api.get('/faq/suggest', {
      params: {
        query,
        limit
      }
    })

    return response.data
  },

  async hot(limit = 5) {
    const response = await api.get('/faq/hot', {
      params: {
        limit
      }
    })

    return response.data
  }
}

export const healthAPI = {
  async check() {
    const response = await api.get('/health')
    return response.data
  }
}

export const chatAPI = {
  async sendStreamMessage(
    query,
    sessionId,
    onMessage,
    onError,
    onDone
  ) {
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          query,
          session_id: sessionId
        })
      })

      if (!response.ok) {
        throw new Error(`请求失败：${response.status}`)
      }

      if (!response.body) {
        throw new Error('浏览器不支持流式响应')
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder('utf-8')

      let buffer = ''

      while (true) {
        const { value, done } = await reader.read()

        if (done) {
          break
        }

        buffer += decoder.decode(value, {
          stream: true
        })

        const events = buffer.split('\n\n')
        buffer = events.pop() || ''

        for (const event of events) {
          const line = event
            .split('\n')
            .find(item => item.startsWith('data:'))

          if (!line) {
            continue
          }

          const jsonText = line.slice(5).trim()

          if (!jsonText) {
            continue
          }

          const data = JSON.parse(jsonText)

          if (data.type === 'token') {
            onMessage(data.content || '')
          }

          if (data.type === 'error') {
            onError(data.error || '服务器发生错误')
          }
        }
      }

      onDone()
    } catch (error) {
      onError(error.message || '网络请求失败')
    }
  }
}