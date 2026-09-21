import axios from 'axios' // 导入 Axios

const api = axios.create({ // 创建 Axios 实例
  baseURL: '/api', // 设置 API 基础路径
  timeout: 10000 // 设置请求超时时间
})

export const orderAPI = { // 定义订单接口
  async list() { // 获取订单列表
    const response = await api.get('/order/list') // 请求订单接口
    return response.data // 返回响应数据
  }
}

export const ticketAPI = { // 定义工单接口
  async list() { // 获取工单列表
    const response = await api.get('/ticket/list') // 请求工单接口
    return response.data // 返回响应数据
  }
}

export const faqAPI = { // 定义 FAQ 接口
  async suggest(query, limit = 5) { // 获取问题联想
    const response = await api.get('/faq/suggest', { // 请求联想接口
      params: { // 设置查询参数
        query, // 用户输入内容
        limit // 返回数量限制
      }
    })

    return response.data // 返回响应数据
  },

  async hot(limit = 5) { // 获取首页热门问题
    const response = await api.get('/faq/hot', { // 请求热门问题接口
      params: { // 设置查询参数
        limit // 返回数量限制
      }
    })

    return response.data // 返回响应数据
  }
}

export const healthAPI = { // 定义健康检查接口
  async check() { // 检查服务状态
    const response = await api.get('/health') // 请求健康检查接口
    return response.data // 返回响应数据
  }
}

export const chatAPI = { // 定义聊天接口
  async sendStreamMessage( // 定义流式聊天方法
    query, // 用户问题
    sessionId, // 会话 ID
    onMessage, // 消息回调
    onError, // 错误回调
    onDone // 完成回调
  ) {
    try { // 捕获请求异常
      const response = await fetch('/api/chat', { // 请求聊天接口
        method: 'POST', // 使用 POST 方法
        headers: { // 设置请求头
          'Content-Type': 'application/json' // 指定 JSON 格式
        },
        body: JSON.stringify({ // 构造请求数据
          query, // 用户问题
          session_id: sessionId // 会话 ID
        })
      })

      if (!response.ok) { // 判断请求是否成功
        throw new Error(`请求失败：${response.status}`) // 抛出请求错误
      }

      if (!response.body) { // 判断是否支持流式响应
        throw new Error('浏览器不支持流式响应') // 抛出流式响应错误
      }

      const reader = response.body.getReader() // 获取响应读取器
      const decoder = new TextDecoder('utf-8') // 创建 UTF-8 解码器

      let buffer = '' // 保存未处理的数据

      while (true) { // 持续读取响应
        const { value, done } = await reader.read() // 读取一段数据

        if (done) { // 判断是否读取完成
          break // 结束循环
        }

        buffer += decoder.decode(value, { // 解码当前数据
          stream: true // 保持流式解码状态
        })

        const events = buffer.split('\n\n') // 按空行分割 SSE 事件
        buffer = events.pop() || '' // 保留未完整事件

        for (const event of events) { // 遍历完整事件
          const line = event // 获取事件中的 data 行
            .split('\n') // 按行分割
            .find(item => item.startsWith('data:')) // 查找 data 数据

          if (!line) { // 判断是否存在数据行
            continue // 跳过当前事件
          }

          const jsonText = line.slice(5).trim() // 获取 JSON 内容

          if (!jsonText) { // 判断 JSON 内容是否为空
            continue // 跳过当前事件
          }

          const data = JSON.parse(jsonText) // 解析 JSON 数据

          if (data.type === 'token') { // 判断是否为文本片段
            onMessage(data.content || '') // 回调文本内容
          }

          if (data.type === 'error') { // 判断是否为错误消息
            onError(data.error || '服务器发生错误') // 回调错误信息
          }
        }
      }

      onDone() // 通知流式响应完成
    } catch (error) { // 捕获请求异常
      onError(error.message || '网络请求失败') // 回调错误信息
    }
  }
}