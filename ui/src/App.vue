<template>
  <div class="app-container">
    <!-- 左侧聊天区域 -->
    <section class="chat-panel">
      <!-- 聊天标题 -->
      <header class="chat-header">
        <div>
          <h1>🛍️ 电商售后智能客服</h1>
          <p>为您提供订单、退换货、物流及售后服务</p>
        </div>

        <el-tag type="success" effect="light">
          在线
        </el-tag>
      </header>

      <!-- 消息区域 -->
      <div ref="chatContainer" class="message-list">
        <!-- 消息 -->
        <div
          v-for="(message, index) in messages"
          :key="index"
          class="message-row"
          :class="message.role"
        >
          <div class="message-avatar">
            {{ message.role === 'user' ? '我' : 'AI' }}
          </div>

          <div class="message-content">
            <div class="message-name">
              {{ message.role === 'user' ? '我' : '售后客服' }}
            </div>

            <div class="message-bubble">
              {{ message.content || '正在输入……' }}
            </div>
          </div>
        </div>

        <!-- 空消息提示 -->
        <div
          v-if="messages.length === 0"
          class="empty-chat"
        >
          暂无聊天记录
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="input-area">
        <!-- 首页常见问题 -->
        <div
          v-if="showHotFaqs && hotFaqs.length > 0"
          class="hot-faqs"
        >
          <div class="hot-faq-title">
            💡 常见问题
          </div>

          <div class="hot-faq-list">
            <button
              v-for="question in hotFaqs"
              :key="question"
              class="hot-faq-button"
              @click="selectHotFaq(question)"
            >
              {{ question }}
            </button>
          </div>
        </div>
        <!-- 售后问题输入框 -->
        <el-input
          v-model="inputMessage"
          type="textarea"
          :rows="4"
          resize="none"
          placeholder="请输入您的售后问题，例如：我的订单能退吗？"
          :disabled="sending"
          @input="handleInput"
          @keydown.enter.exact.prevent="sendMessage"
        />

        <!-- Redis 高频问题联想 -->
        <div
          v-if="showFaqSuggestions"
          class="faq-suggestions"
        >
          <div class="faq-title">
            <span>💡 您可能想问</span>

            <el-button
              text
              size="small"
              class="faq-close-button"
              @click="closeFaqSuggestions"
            >
              ×
            </el-button>
          </div>

          <div
            v-for="suggestion in faqSuggestions"
            :key="suggestion"
            class="faq-suggestion-item"
            @click="selectFaqSuggestion(suggestion)"
          >
            {{ suggestion }}
          </div>
        </div>

        <div class="input-footer">
          <span class="input-tip">
            Enter 发送，Shift + Enter 换行
          </span>

          <el-button
            type="primary"
            :loading="sending"
            :disabled="!inputMessage.trim()"
            @click="sendMessage"
          >
            {{ sending ? '发送中' : '发送' }}
          </el-button>
        </div>
      </div>
    </section>

    <!-- 右侧区域 -->
    <section class="right-panel">
      <!-- 我的订单 -->
      <div class="side-panel order-panel">
        <div class="panel-header">
          <div>
            <h2>📦 我的订单</h2>
            <span>{{ orders.length }} 笔订单</span>
          </div>

          <el-button
            text
            type="primary"
            @click="loadOrders"
          >
            刷新
          </el-button>
        </div>

        <div class="panel-content">
          <!-- 有订单 -->
          <div
            v-if="orders.length > 0"
            class="data-list"
          >
            <div
              v-for="order in orders"
              :key="order.order_no"
              class="order-item"
            >
              <div class="item-top">
                <span class="order-no">
                  {{ order.order_no }}
                </span>

                <el-tag
                  size="small"
                  :type="getOrderStatusType(order.status)"
                >
                  {{ order.status }}
                </el-tag>
              </div>

              <div class="product-name">
                {{ order.product_name }}
              </div>

              <div class="item-info">
                <span>
                  下单时间：{{ order.order_time }}
                </span>

                <strong>
                  {{ formatAmount(order.amount) }}
                </strong>
              </div>

              <div
                v-if="order.tracking_no"
                class="tracking-info"
              >
                物流单号：{{ order.tracking_no }}
              </div>
            </div>
          </div>

          <!-- 暂无订单 -->
          <div
            v-else
            class="empty-panel"
          >
            <div class="empty-icon">📦</div>
            <p>暂无订单数据</p>
            <span>
              当前暂无可展示的订单
            </span>
          </div>
        </div>
      </div>

      <!-- 售后工单 -->
      <div class="side-panel ticket-panel">
        <div class="panel-header">
          <div>
            <h2>📝 售后工单</h2>
            <span>{{ tickets.length }} 个工单</span>
          </div>

          <el-button
            text
            type="primary"
            @click="loadTickets"
          >
            刷新
          </el-button>
        </div>

        <div class="panel-content">
          <!-- 有工单 -->
          <div
            v-if="tickets.length > 0"
            class="data-list"
          >
            <div
              v-for="ticket in tickets"
              :key="ticket.ticket_no"
              class="ticket-item"
            >
              <div class="item-top">
                <span class="ticket-no">
                  {{ ticket.ticket_no }}
                </span>

                <el-tag
                  size="small"
                  :type="getTicketStatusType(ticket.status)"
                >
                  {{ ticket.status }}
                </el-tag>
              </div>

              <div class="ticket-order">
                订单号：{{ ticket.order_no }}
              </div>

              <div class="ticket-issue">
                {{ ticket.issue }}
              </div>

              <div
                v-if="ticket.created_at"
                class="ticket-time"
              >
                创建时间：{{ ticket.created_at }}
              </div>
            </div>
          </div>

          <!-- 暂无工单 -->
          <div
            v-else
            class="empty-panel"
          >
            <div class="empty-icon">📝</div>
            <p>暂无售后工单</p>
            <span>
              需要人工处理的问题会创建售后工单
            </span>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
<script setup>
import { nextTick, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  chatAPI,
  orderAPI,
  ticketAPI,
  faqAPI
} from './api/index.js'

// 当前会话 ID
const sessionId = `customer_${Date.now()}`

// 用户输入内容
const inputMessage = ref('')

// 是否正在发送
const sending = ref(false)

// 聊天消息容器
const chatContainer = ref(null)

// 聊天消息
const messages = ref([
  {
    role: 'assistant',
    content:
      '您好，我是电商售后智能客服，请问有什么可以帮助您？'
  }
])

// 订单数据
const orders = ref([])

// 售后工单数据
const tickets = ref([])

// 滚动到聊天底部
const scrollToBottom = async () => {
  await nextTick()

  if (chatContainer.value) {
    chatContainer.value.scrollTop =
      chatContainer.value.scrollHeight
  }
}

// 加载订单
const loadOrders = async () => {
  try {
    const result = await orderAPI.list()

    if (result.success) {
      orders.value = result.orders || []
    }
  } catch (error) {
    ElMessage.error('订单数据加载失败')
  }
}

// 加载工单
const loadTickets = async () => {
  try {
    const result = await ticketAPI.list()

    if (result.success) {
      tickets.value = result.tickets || []
    }
  } catch (error) {
    ElMessage.error('售后工单加载失败')
  }
}

// 加载首页常见问题
const loadHotFaqs = async () => {
  try {
    const result = await faqAPI.hot(4)

    if (result.success) {
      hotFaqs.value = result.suggestions || []
    }
  } catch (error) {
    hotFaqs.value = []
  }
}

// Redis 售后问题联想
const faqSuggestions = ref([])

// 首页快捷问题
const hotFaqs = ref([])

// 是否显示首页快捷问题
const showHotFaqs = ref(true)

// 是否显示联想列表
const showFaqSuggestions = ref(false)

// 联想请求定时器
let faqTimer = null

// 联想请求编号，用于避免旧请求覆盖新结果
let faqRequestId = 0

// 处理输入框内容变化
const handleInput = () => {
  // 清除上一次延迟请求
  if (faqTimer) {
    clearTimeout(faqTimer)
  }

  // 获取当前输入内容
  const query = inputMessage.value.trim()

  // 少于两个字符时不显示联想
  if (query.length < 2) {
    faqSuggestions.value = []
    showFaqSuggestions.value = false
    return
  }

  // 延迟 200ms 再查询，避免连续输入时频繁请求
  faqTimer = setTimeout(async () => {
    // 当前请求编号加一
    const requestId = ++faqRequestId

    try {
      // 调用 Redis 联想接口
      const result = await faqAPI.suggest(query, 5)

      // 如果已经有更新的请求，则丢弃当前结果
      if (requestId !== faqRequestId) {
        return
      }

      // 保存联想结果
      faqSuggestions.value = result.success
        ? result.suggestions || []
        : []

      // 有结果才显示联想框
      showFaqSuggestions.value =
        faqSuggestions.value.length > 0
    } catch (error) {
      // 请求失败时隐藏联想框
      faqSuggestions.value = []
      showFaqSuggestions.value = false
    }
  }, 200)
}

const selectFaqSuggestion = (suggestion) => {
  // 当前输入发生变化，使之前的联想请求失效
  faqRequestId++

  // 清除延迟请求
  if (faqTimer) {
    clearTimeout(faqTimer)
  }

  // 将候选问题填入输入框
  inputMessage.value = suggestion

  // 隐藏联想框
  faqSuggestions.value = []
  showFaqSuggestions.value = false
}

// 点击首页快捷问题
const selectHotFaq = (question) => {
  // 将问题填入输入框
  inputMessage.value = question

  // 清空正在显示的联想结果
  faqSuggestions.value = []
  showFaqSuggestions.value = false
}

// 手动关闭当前联想框
const closeFaqSuggestions = () => {
  // 让已经发出的旧请求失效
  faqRequestId++

  // 清除尚未执行的延迟请求
  if (faqTimer) {
    clearTimeout(faqTimer)
  }

  // 清空联想结果
  faqSuggestions.value = []

  // 隐藏联想框
  showFaqSuggestions.value = false
}

// 发送消息
const sendMessage = async () => {
  const query = inputMessage.value.trim()

  // 空消息不发送
  if (!query || sending.value) {
    return
  }

  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: query
  })

  // 清空输入框
  inputMessage.value = ''

  // 设置发送状态
  sending.value = true

  // 先创建一个空的 AI 消息
  messages.value.push({
    role: 'assistant',
    content: ''
  })

  // 获取当前 AI 消息
  const assistantMessage =
    messages.value[messages.value.length - 1]

  await scrollToBottom()

  // 调用后端 SSE 接口
  await chatAPI.sendStreamMessage(
    query,
    sessionId,

    // 收到一个 token
    async (content) => {
      assistantMessage.content += content
      await scrollToBottom()
    },

    // 请求发生错误
    (error) => {
      assistantMessage.content =
        `抱歉，服务暂时出现问题：${error}`

      sending.value = false

      ElMessage.error(error)
    },

    // SSE 正常结束
    async () => {
      sending.value = false

      // 刷新右侧数据
      await loadOrders()
      await loadTickets()

      await scrollToBottom()
    }
  )
}

// 格式化金额
const formatAmount = (amount) => {
  return `¥${Number(amount || 0).toFixed(2)}`
}

// 订单状态对应 Element Plus 标签类型
const getOrderStatusType = (status) => {
  const statusMap = {
    '已完成': 'success',
    '已发货': 'primary',
    '运输中': 'warning',
    '待发货': 'info',
    '已取消': 'danger'
  }

  return statusMap[status] || 'info'
}

// 工单状态对应 Element Plus 标签类型
const getTicketStatusType = (status) => {
  const statusMap = {
    '待处理': 'warning',
    '处理中': 'primary',
    '已完成': 'success',
    '已升级': 'danger'
  }

  return statusMap[status] || 'info'
}

// 页面加载时获取数据
onMounted(async () => {
  await loadOrders()
  await loadTickets()
  await loadHotFaqs()
  await scrollToBottom()
})
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.app-container {
  width: 100%;
  height: 100vh;
  display: grid;
  grid-template-columns: minmax(0, 1.8fr) minmax(360px, 1fr);
  gap: 16px;
  padding: 16px;
  background: #f5f7fa;
  overflow: hidden;
}

/* ==================== 左侧聊天区域 ==================== */

.chat-panel {
  min-width: 0;
  min-height: 0;
  display: flex;
  flex-direction: column;
  background: #ffffff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.chat-header {
  height: 78px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  border-bottom: 1px solid #ebeef5;
}

.chat-header h1 {
  margin: 0 0 4px;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.chat-header p {
  margin: 0;
  font-size: 13px;
  color: #909399;
}

.message-list {
  flex: 1;
  min-height: 0;
  padding: 24px;
  overflow-y: auto;
}

.message-row {
  display: flex;
  gap: 10px;
  margin-bottom: 22px;
}

.message-row.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #409eff;
  color: #ffffff;
  font-size: 13px;
  font-weight: 600;
}

.message-row.user .message-avatar {
  background: #67c23a;
}

.message-content {
  max-width: 72%;
}

.message-name {
  margin-bottom: 6px;
  font-size: 12px;
  color: #909399;
}

.message-row.user .message-name {
  text-align: right;
}

.message-bubble {
  padding: 11px 14px;
  border-radius: 10px;
  background: #f2f6fc;
  color: #303133;
  font-size: 14px;
  line-height: 1.7;
  white-space: pre-wrap;
  word-break: break-word;
}

.message-row.user .message-bubble {
  background: #409eff;
  color: #ffffff;
}

.empty-chat {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
}

/* 输入区域 */

.input-area {
  position: relative;
  flex-shrink: 0;
  padding: 16px;
  border-top: 1px solid #ebeef5;
  background: #ffffff;
}

.input-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
}

.input-tip {
  font-size: 12px;
  color: #a8abb2;
}

.faq-suggestions {
  position: absolute;
  left: 16px;
  right: 16px;

  /* 整个联想框放到输入区域上方 */
  bottom: calc(100% + 8px);

  z-index: 100;
  max-height: 280px;
  overflow-y: auto;
  padding: 8px 0;

  background: #ffffff;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.12);
}

/* 联想标题 */
.faq-title {
  display: flex;
  align-items: center;
  justify-content: space-between;

  height: 36px;
  padding: 0 8px 0 14px;

  font-size: 12px;
  color: #909399;

  border-bottom: 1px solid #f0f0f0;
}

/* 关闭按钮 */
.faq-close-button {
  padding: 4px 8px;
  font-size: 16px;
  color: #909399;
}

/* 鼠标悬停关闭按钮 */
.faq-close-button:hover {
  color: #409eff;
}

/* 联想问题 */
.faq-suggestion-item {
  padding: 10px 14px;
  font-size: 13px;
  color: #303133;
  cursor: pointer;
  transition: background 0.2s;
}

/* 鼠标悬停 */
.faq-suggestion-item:hover {
  background: #f5f7fa;
  color: #409eff;
}

/* ==================== 右侧区域 ==================== */

.right-panel {
  min-width: 0;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.side-panel {
  min-height: 0;
  display: flex;
  flex-direction: column;
  background: #ffffff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.order-panel {
  flex: 1;
}

.ticket-panel {
  flex: 1;
}

.panel-header {
  height: 68px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 18px;
  border-bottom: 1px solid #ebeef5;
}

.panel-header h2 {
  margin: 0 0 3px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.panel-header span {
  font-size: 12px;
  color: #909399;
}

.panel-content {
  flex: 1;
  min-height: 0;
  padding: 14px;
  overflow-y: auto;
}

/* ==================== 数据列表 ==================== */

.data-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.order-item,
.ticket-item {
  padding: 13px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  transition: 0.2s;
}

.order-item:hover,
.ticket-item:hover {
  border-color: #c6e2ff;
  background: #f8fbff;
}

.item-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.order-no,
.ticket-no {
  font-size: 12px;
  color: #606266;
  font-weight: 500;
}

.product-name {
  margin: 10px 0;
  font-size: 14px;
  color: #303133;
  font-weight: 500;
}

.item-info {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  font-size: 12px;
  color: #909399;
}

.item-info strong {
  color: #f56c6c;
  font-size: 14px;
}

.tracking-info {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}

.ticket-order {
  margin-top: 10px;
  font-size: 12px;
  color: #606266;
}

.ticket-issue {
  margin-top: 8px;
  font-size: 13px;
  line-height: 1.6;
  color: #303133;
}

.ticket-time {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}

/* ==================== 空状态 ==================== */

.empty-panel {
  width: 100%;
  height: 100%;
  min-height: 180px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.empty-icon {
  margin-bottom: 12px;
  font-size: 38px;
}

.empty-panel p {
  margin: 0 0 6px;
  font-size: 14px;
  color: #606266;
}

.empty-panel span {
  font-size: 12px;
  color: #a8abb2;
}

/* ==================== 首页常见问题 ==================== */

.hot-faqs {
  margin-bottom: 10px;
}

.hot-faq-title {
  margin-bottom: 8px;
  font-size: 12px;
  color: #909399;
}

.hot-faq-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.hot-faq-button {
  padding: 7px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 16px;
  background: #ffffff;
  color: #606266;
  font-size: 12px;
  line-height: 1.4;
  cursor: pointer;
  transition: all 0.2s;
}

.hot-faq-button:hover {
  border-color: #409eff;
  color: #409eff;
  background: #f0f7ff;
}

/* ==================== 滚动条 ==================== */

.message-list::-webkit-scrollbar,
.panel-content::-webkit-scrollbar {
  width: 6px;
}

.message-list::-webkit-scrollbar-thumb,
.panel-content::-webkit-scrollbar-thumb {
  background: #dcdfe6;
  border-radius: 3px;
}
</style>