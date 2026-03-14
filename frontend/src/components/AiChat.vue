<template>
  <div class="ai-chat-root" :class="{ 'theme-dark': dark }">
    <header class="chat-head">
      <div class="head-left">
        <div class="badge">AI</div>
        <div>
          <h3>AI 导师</h3>
          <p>引导式提示，不直接给完整答案</p>
        </div>
        <span class="online-dot">在线</span>
      </div>

      <button type="button" class="collapse-btn" @click="isExpanded = !isExpanded">
        {{ isExpanded ? '收起' : '展开' }}
      </button>
    </header>

    <section v-show="isExpanded" class="chat-body">
      <div ref="messagesContainer" class="messages">
        <div v-if="messages.length === 0" class="empty-state">
          <div class="empty-badge">Tutor</div>
          <h4>开始提问</h4>
          <p>你可以问思路、边界条件、复杂度、调试方向，我会按步骤引导。</p>
        </div>

        <div
          v-for="message in messages"
          :key="message.id"
          class="message-row"
          :class="{ user: message.role === 'user', assistant: message.role === 'assistant' }"
        >
          <article class="message-bubble">
            <p class="role-tag" v-if="message.role === 'assistant'">AI 导师</p>
            <pre>{{ message.content }}</pre>
          </article>
        </div>

        <div v-if="isLoading" class="message-row assistant">
          <article class="message-bubble typing">
            <p class="role-tag">AI 导师</p>
            <div class="typing-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </article>
        </div>
      </div>

      <footer class="chat-input-wrap">
        <textarea
          v-model="inputMessage"
          :disabled="isLoading"
          placeholder="输入你的问题，按 Enter 发送，Shift + Enter 换行"
          rows="2"
          @keydown.enter.exact.prevent="sendMessage"
        ></textarea>
        <button
          type="button"
          :disabled="isLoading || !inputMessage.trim()"
          class="send-btn"
          @click="sendMessage"
        >
          {{ isLoading ? '发送中...' : '发送' }}
        </button>
      </footer>
    </section>
  </div>
</template>

<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const configuredBaseUrl = (import.meta.env.VITE_API_BASE_URL || '').trim()
const API_BASE_URL = import.meta.env.DEV
  ? ''
  : configuredBaseUrl.replace(/\/+$/, '')

const props = defineProps({
  problemDescription: {
    type: String,
    default: ''
  },
  currentCode: {
    type: String,
    default: ''
  },
  dark: {
    type: Boolean,
    default: false
  }
})

const isExpanded = ref(true)
const messages = ref([])
const inputMessage = ref('')
const isLoading = ref(false)
const messagesContainer = ref(null)

let messageId = 0
let activeController = null

const createMessage = (role, content) => {
  messageId += 1
  return {
    id: `${role}-${messageId}`,
    role,
    content
  }
}

const scrollToBottom = () => {
  if (!messagesContainer.value) return
  requestAnimationFrame(() => {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  })
}

const appendWelcomeMessage = () => {
  if (!props.problemDescription) return
  if (messages.value.length > 0) return
  messages.value.push(
    createMessage(
      'assistant',
      '题目描述和你的代码已加载。你可以先问：当前思路哪里可能有漏洞？边界条件应该补哪些？复杂度是否可优化？'
    )
  )
}

const sendMessage = async () => {
  if (!inputMessage.value.trim() || isLoading.value) return

  const userMessage = inputMessage.value.trim()
  inputMessage.value = ''
  messages.value.push(createMessage('user', userMessage))

  await nextTick()
  scrollToBottom()

  isLoading.value = true
  activeController = new AbortController()

  const assistantMessage = createMessage('assistant', '')
  messages.value.push(assistantMessage)

  try {
    const response = await fetch(`${API_BASE_URL}/api/ai/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        problem_description: props.problemDescription,
        current_code: props.currentCode,
        user_message: userMessage
      }),
      signal: activeController.signal
    })

    if (!response.ok || !response.body) {
      throw new Error('请求失败')
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const events = buffer.split('\n\n')
      buffer = events.pop() || ''

      for (const event of events) {
        const lines = event.split('\n')
        for (const line of lines) {
          if (!line.startsWith('data:')) continue
          const text = line.slice(5).trimStart()
          if (!text || text === '[DONE]') continue
          assistantMessage.content += text
        }
      }

      await nextTick()
      scrollToBottom()
    }

    if (!assistantMessage.content.trim()) {
      assistantMessage.content = '当前没有收到有效内容，请重试一次。'
    }
  } catch (error) {
    if (error?.name === 'AbortError') return
    console.error('AI 对话失败:', error)
    assistantMessage.content = '当前服务暂时不可用，请稍后重试。'
  } finally {
    activeController = null
    isLoading.value = false
    await nextTick()
    scrollToBottom()
  }
}

watch(
  () => props.problemDescription,
  () => {
    appendWelcomeMessage()
  }
)

onMounted(() => {
  appendWelcomeMessage()
})

onBeforeUnmount(() => {
  if (activeController) {
    activeController.abort()
    activeController = null
  }
})
</script>

<style scoped>
.ai-chat-root {
  --chat-bg: rgba(255, 255, 255, 0.92);
  --chat-soft: rgba(253, 249, 242, 0.92);
  --chat-line: #ddcfbc;
  --chat-line-soft: #eadfd0;
  --chat-text: #2f271f;
  --chat-sub: #7b6d5b;
  --chat-muted: #998a74;
  --chat-user-bg: linear-gradient(145deg, #83552b 0%, #ab7543 100%);
  --chat-user-text: #fff;
  --chat-assistant-bg: rgba(255, 255, 255, 0.88);
  --chat-assistant-border: #dbcab4;
  --chat-send-bg: linear-gradient(145deg, #83552b 0%, #ab7543 100%);
  --chat-send-shadow: 0 10px 20px rgba(105, 68, 35, 0.24);
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--chat-bg);
  color: var(--chat-text);
}

.ai-chat-root.theme-dark {
  --chat-bg: rgba(23, 29, 39, 0.94);
  --chat-soft: rgba(20, 26, 36, 0.94);
  --chat-line: #313b4a;
  --chat-line-soft: #26303f;
  --chat-text: #ecf0f7;
  --chat-sub: #a8b1bf;
  --chat-muted: #8a94a6;
  --chat-user-bg: linear-gradient(145deg, #8f6337 0%, #bf8856 100%);
  --chat-user-text: #fff;
  --chat-assistant-bg: rgba(18, 24, 33, 0.95);
  --chat-assistant-border: #344153;
  --chat-send-bg: linear-gradient(145deg, #8f6337 0%, #bf8856 100%);
  --chat-send-shadow: 0 10px 20px rgba(10, 14, 20, 0.4);
}

.chat-head {
  padding: 10px 12px;
  border-bottom: 1px solid var(--chat-line);
  background: var(--chat-soft);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.head-left {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.badge {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.12em;
  color: #fff;
  background: var(--chat-user-bg);
  flex-shrink: 0;
}

.head-left h3 {
  font-size: 13px;
  font-weight: 700;
}

.head-left p {
  font-size: 11px;
  color: var(--chat-sub);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 240px;
}

.online-dot {
  height: 22px;
  padding: 0 9px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  color: #2b744a;
  background: rgba(75, 166, 116, 0.18);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.collapse-btn {
  border: 1px solid var(--chat-line);
  background: transparent;
  color: var(--chat-sub);
  border-radius: 9px;
  height: 30px;
  padding: 0 10px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.collapse-btn:hover {
  color: var(--chat-text);
  border-color: var(--chat-muted);
}

.chat-body {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.messages {
  flex: 1;
  min-height: 0;
  overflow: auto;
  padding: 12px;
  display: grid;
  gap: 10px;
}

.messages::-webkit-scrollbar {
  width: 6px;
}

.messages::-webkit-scrollbar-thumb {
  background: var(--chat-line);
  border-radius: 999px;
}

.empty-state {
  border: 1px dashed var(--chat-line);
  border-radius: 12px;
  min-height: 140px;
  display: grid;
  place-items: center;
  text-align: center;
  gap: 8px;
  padding: 16px;
  color: var(--chat-sub);
}

.empty-badge {
  border-radius: 999px;
  border: 1px solid var(--chat-line);
  padding: 0 10px;
  height: 24px;
  display: inline-flex;
  align-items: center;
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--chat-muted);
}

.empty-state h4 {
  font-size: 14px;
  color: var(--chat-text);
}

.empty-state p {
  font-size: 12px;
  line-height: 1.6;
  max-width: 340px;
}

.message-row {
  display: flex;
}

.message-row.user {
  justify-content: flex-end;
}

.message-row.assistant {
  justify-content: flex-start;
}

.message-bubble {
  width: min(90%, 420px);
  border-radius: 12px;
  padding: 10px 12px;
  border: 1px solid var(--chat-assistant-border);
  background: var(--chat-assistant-bg);
  box-shadow: 0 8px 18px rgba(45, 35, 24, 0.08);
  animation: bubble-in 0.18s ease;
}

.message-row.user .message-bubble {
  border: none;
  background: var(--chat-user-bg);
  color: var(--chat-user-text);
  box-shadow: var(--chat-send-shadow);
}

.role-tag {
  font-size: 10px;
  color: var(--chat-muted);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-bottom: 4px;
}

.message-row.user .role-tag {
  color: rgba(255, 255, 255, 0.78);
}

.message-bubble pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 13px;
  line-height: 1.55;
  font-family: inherit;
}

.typing {
  display: grid;
  gap: 6px;
}

.typing-dots {
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.typing-dots span {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--chat-muted);
  animation: pulse 1s ease-in-out infinite;
}

.typing-dots span:nth-child(2) {
  animation-delay: 0.15s;
}

.typing-dots span:nth-child(3) {
  animation-delay: 0.3s;
}

.chat-input-wrap {
  border-top: 1px solid var(--chat-line);
  background: var(--chat-soft);
  padding: 10px;
  display: grid;
  gap: 8px;
}

.chat-input-wrap textarea {
  width: 100%;
  border: 1px solid var(--chat-line);
  border-radius: 10px;
  background: var(--chat-bg);
  color: var(--chat-text);
  resize: none;
  outline: none;
  padding: 9px 10px;
  font-size: 13px;
  line-height: 1.5;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.chat-input-wrap textarea::placeholder {
  color: var(--chat-muted);
}

.chat-input-wrap textarea:focus {
  border-color: var(--chat-muted);
  box-shadow: 0 0 0 3px rgba(153, 138, 116, 0.12);
}

.chat-input-wrap textarea:disabled {
  opacity: 0.7;
}

.send-btn {
  justify-self: end;
  border: 0;
  border-radius: 10px;
  height: 34px;
  min-width: 92px;
  padding: 0 12px;
  background: var(--chat-send-bg);
  color: #fff;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: var(--chat-send-shadow);
  transition: transform 0.2s ease, opacity 0.2s ease;
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-1px);
}

.send-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

@keyframes bubble-in {
  from {
    opacity: 0;
    transform: translateY(4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes pulse {
  0%,
  100% {
    transform: translateY(0);
    opacity: 0.45;
  }
  50% {
    transform: translateY(-2px);
    opacity: 1;
  }
}

@media (max-width: 720px) {
  .head-left p,
  .online-dot {
    display: none;
  }

  .message-bubble {
    width: 100%;
  }
}
</style>
