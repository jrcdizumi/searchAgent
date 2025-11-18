import { useState, useRef, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeHighlight from 'rehype-highlight'
import './App.css'
import 'highlight.js/styles/github-dark.css'

interface Message {
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
}

interface StreamEvent {
  type: 'start' | 'content' | 'search' | 'search_complete' | 'done' | 'error'
  content?: string
  message?: string
  query?: string
  count?: number
}

// LocalStorage 键名
const STORAGE_KEY = 'chat_history'

function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [streamingContent, setStreamingContent] = useState('')
  const [searchStatus, setSearchStatus] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const abortControllerRef = useRef<AbortController | null>(null)

  // 从 localStorage 加载历史对话
  useEffect(() => {
    try {
      const savedMessages = localStorage.getItem(STORAGE_KEY)
      if (savedMessages) {
        const parsed = JSON.parse(savedMessages)
        // 将时间戳字符串转换回 Date 对象
        const messagesWithDates = parsed.map((msg: any) => ({
          ...msg,
          timestamp: new Date(msg.timestamp)
        }))
        setMessages(messagesWithDates)
        console.log('✅ 已加载历史对话:', messagesWithDates.length, '条消息')
      }
    } catch (error) {
      console.error('❌ 加载历史对话失败:', error)
      // 如果数据损坏，清除它
      localStorage.removeItem(STORAGE_KEY)
    }
  }, [])

  // 保存消息到 localStorage（当消息变化时）
  useEffect(() => {
    if (messages.length > 0) {
      try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(messages))
        console.log('💾 已保存对话历史')
      } catch (error) {
        console.error('❌ 保存对话历史失败:', error)
      }
    }
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, streamingContent])

  const handleStreamResponse = async (userMessage: Message) => {
    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)
    setStreamingContent('')
    setSearchStatus('')

    // Create abort controller for this request
    abortControllerRef.current = new AbortController()

    try {
      const response = await fetch('/api/chat/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage.content,
        }),
        signal: abortControllerRef.current.signal,
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      if (!reader) {
        throw new Error('无法读取响应流')
      }

      let accumulatedContent = ''

      while (true) {
        const { done, value } = await reader.read()

        if (done) {
          break
        }

        const chunk = decoder.decode(value, { stream: true })
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data: StreamEvent = JSON.parse(line.slice(6))

              switch (data.type) {
                case 'start':
                  setSearchStatus(data.message || '开始处理...')
                  break

                case 'content':
                  if (data.content) {
                    accumulatedContent += data.content
                    setStreamingContent(accumulatedContent)
                  }
                  break

                case 'search':
                  setSearchStatus(
                    `🔍 正在搜索 (${data.count}/2): ${data.query}`
                  )
                  break

                case 'search_complete':
                  setSearchStatus(data.message || '搜索完成')
                  break

                case 'done':
                  // Finalize the message
                  const assistantMessage: Message = {
                    role: 'assistant',
                    content: accumulatedContent,
                    timestamp: new Date(),
                  }
                  setMessages(prev => [...prev, assistantMessage])
                  setStreamingContent('')
                  setSearchStatus('')
                  break

                case 'error':
                  throw new Error(data.message || '处理请求时出错')
              }
            } catch (e) {
              console.warn('解析 SSE 数据失败:', e)
            }
          }
        }
      }
    } catch (error: any) {
      if (error.name === 'AbortError') {
        console.log('请求已取消')
        setStreamingContent('')
        setSearchStatus('')
      } else {
        console.error('流式传输失败:', error)
        const errorMessage: Message = {
          role: 'system',
          content: `抱歉，处理请求时出现错误：${error.message}。请检查后端服务是否正常运行。`,
          timestamp: new Date(),
        }
        setMessages(prev => [...prev, errorMessage])
      }
    } finally {
      setIsLoading(false)
      abortControllerRef.current = null
    }
  }

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    }

    setInput('')

    // Use streaming by default
    await handleStreamResponse(userMessage)
  }

  const handleStop = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      setIsLoading(false)
      setStreamingContent('')
      setSearchStatus('')
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const clearChat = () => {
    // 显示确认对话框
    if (messages.length > 0) {
      const confirmed = window.confirm(
        '确定要清空所有对话记录吗？\n\n这将删除本地保存的所有历史对话，此操作不可恢复。'
      )
      if (!confirmed) {
        return
      }
    }

    // 清空状态
    setMessages([])
    setStreamingContent('')
    setSearchStatus('')
    
    // 清空 localStorage
    localStorage.removeItem(STORAGE_KEY)
    console.log('🗑️ 已清空本地对话历史')
    
    // 调用 API 清空后端记忆
    fetch('/api/clear', { method: 'POST' })
      .then(() => console.log('✅ 已清空后端记忆'))
      .catch((error) => console.error('❌ 清空后端记忆失败:', error))
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-left">
          <h1>🔍 智能搜索助手</h1>
          {messages.length > 0 && (
            <span className="message-count">
              {messages.length} 条消息
            </span>
          )}
        </div>
        <button 
          onClick={clearChat} 
          className="clear-btn" 
          title="清空对话"
          disabled={messages.length === 0 && !streamingContent}
        >
          清空历史
        </button>
      </header>

      <div className="chat-container">
        <div className="messages">
          {messages.length === 0 && !streamingContent ? (
            <div className="welcome">
              <h2>👋 欢迎使用智能搜索助手</h2>
              <p>我可以帮您搜索和解答各种问题，支持实时流式回复</p>
              <p className="storage-hint">
                💾 对话历史会自动保存到本地，下次打开自动恢复
              </p>
              <div className="suggestions">
                <button onClick={() => setInput('今天的天气如何？')}>
                  今天的天气如何？
                </button>
                <button onClick={() => setInput('最新的科技新闻')}>
                  最新的科技新闻
                </button>
                <button onClick={() => setInput('推荐一些学习资源')}>
                  推荐一些学习资源
                </button>
              </div>
            </div>
          ) : (
            <>
              {messages.map((msg, index) => (
                <div key={index} className={`message ${msg.role}`}>
                  <div className="message-avatar">
                    {msg.role === 'user'
                      ? '👤'
                      : msg.role === 'assistant'
                      ? '🤖'
                      : '⚠️'}
                  </div>
                  <div className="message-content">
                    <div className="message-text">
                      {msg.role === 'user' || msg.role === 'system' ? (
                        msg.content
                      ) : (
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          rehypePlugins={[rehypeHighlight]}
                        >
                          {msg.content}
                        </ReactMarkdown>
                      )}
                    </div>
                    <div className="message-time">
                      {msg.timestamp.toLocaleTimeString('zh-CN', {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </div>
                  </div>
                </div>
              ))}

              {/* Streaming content */}
              {streamingContent && (
                <div className="message assistant streaming">
                  <div className="message-avatar">🤖</div>
                  <div className="message-content">
                    <div className="message-text">
                      <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        rehypePlugins={[rehypeHighlight]}
                      >
                        {streamingContent}
                      </ReactMarkdown>
                      <span className="cursor-blink">▊</span>
                    </div>
                    {searchStatus && (
                      <div className="search-status">{searchStatus}</div>
                    )}
                  </div>
                </div>
              )}

              {/* Loading indicator without streaming content */}
              {isLoading && !streamingContent && (
                <div className="message assistant">
                  <div className="message-avatar">🤖</div>
                  <div className="message-content">
                    <div className="typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                    {searchStatus && (
                      <div className="search-status">{searchStatus}</div>
                    )}
                  </div>
                </div>
              )}
            </>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="input-container">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="输入您的问题... (Enter 发送，Shift+Enter 换行)"
            rows={1}
            disabled={isLoading}
          />
          {isLoading ? (
            <button onClick={handleStop} className="stop-btn">
              停止
            </button>
          ) : (
            <button
              onClick={handleSend}
              disabled={!input.trim()}
              className="send-btn"
            >
              发送
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

export default App
