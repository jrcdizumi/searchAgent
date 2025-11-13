# 🤖 搜索增强智能代理 (Search-Augmented Agent)

一个基于LangChain和ReAct框架的智能代理，能够通过实时网络搜索来回答用户问题，克服大语言模型训练数据的时效性限制。

## 🆕 新功能：流式传输 Web UI

现在支持**实时流式响应**和**现代化 Web 界面**！

🌟 **快速体验流式界面：**
```bash
# 启动后端 API
./start_server.sh

# 启动前端（新终端窗口）
cd frontend && npm run dev

# 访问 http://localhost:3000
```

📚 **详细文档：**
- 🚀 [流式传输快速启动](STREAMING_QUICKSTART.md)
- 📡 [API 使用指南](API_GUIDE.md)
- 🌊 [流式传输详解](README_STREAMING.md)

## ✨ 主要特性

- 🧠 **ReAct框架**: 使用Reasoning and Acting范式进行推理和决策
- 🔍 **实时搜索**: 支持多种搜索引擎（DuckDuckGo、Tavily）
- 🌊 **流式传输**: Server-Sent Events (SSE) 实时流式输出 ⭐ **NEW**
- 💻 **Web界面**: React + TypeScript 现代化前端 ⭐ **NEW**
- 📡 **REST API**: FastAPI 构建的高性能 API 服务 ⭐ **NEW**
- 💾 **对话记忆**: 保存对话历史，支持上下文相关的多轮对话
- 🔧 **灵活配置**: 支持多种LLM模型和搜索提供商
- 📝 **持久化存储**: 对话历史自动保存到文件
- 🎯 **易于使用**: 提供命令行界面、Web界面和编程接口

## 📋 项目结构

```
searchAgent/
├── api_server.py           # 🌟 FastAPI 服务器（支持流式传输）
├── start_server.sh         # 🌟 API 服务器启动脚本
├── main.py                 # 命令行交互界面
├── react_agent.py          # ReAct 代理核心实现
├── search_tools.py         # 搜索工具封装
├── memory_manager.py       # 记忆管理模块
├── config.py               # 配置文件
├── requirements.txt        # Python 依赖
│
├── frontend/               # 🌟 React + TypeScript 前端
│   ├── src/
│   │   ├── App.tsx        # 主应用（支持流式接收）
│   │   ├── App.css        # 样式文件
│   │   └── main.tsx       # 入口文件
│   ├── package.json
│   └── vite.config.ts
│
└── docs/                   # 📚 文档
    ├── STREAMING_QUICKSTART.md  # 流式传输快速启动
    ├── API_GUIDE.md             # API 使用指南
    └── README_STREAMING.md      # 流式传输详解
```

## 🚀 快速开始

### ⭐ 推荐：使用 Web 界面 + 流式传输

#### 1. 启动后端 API 服务

```bash
# 一键启动（推荐）
chmod +x start_server.sh
./start_server.sh

# 或手动启动
python api_server.py
```

后端将运行在 http://localhost:8000

#### 2. 启动前端界面

打开**新的终端窗口**：

```bash
cd frontend
npm install  # 首次运行需要
npm run dev
```

前端将运行在 http://localhost:3000

#### 3. 开始使用

在浏览器打开 http://localhost:3000 即可体验流式对话！

📖 **详细教程**：查看 [流式传输快速启动指南](STREAMING_QUICKSTART.md)

---

### 方法1: 使用安装脚本（命令行版本）

```bash
# 运行安装脚本
chmod +x setup.sh
./setup.sh

# 编辑配置文件，填入API密钥
nano config.py

# 运行程序
source venv/bin/activate
python main.py
```

### 方法2: 手动安装

#### 1. 创建虚拟环境

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate
```

#### 2. 安装依赖

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 3. 配置API密钥

```bash
# 复制配置示例文件
cp config.example.py config.py

# 编辑config.py，填入您的OpenAI API密钥
nano config.py
```

需要配置的内容：

```python
# 必需：OpenAI API密钥
OPENAI_API_KEY = "sk-your-openai-api-key"

# 可选：选择搜索提供商
SEARCH_PROVIDER = "duckduckgo"  # 或 "tavily"

# 可选：如果使用Tavily，需要填入Tavily API密钥
TAVILY_API_KEY = "your-tavily-api-key"
```

**获取API密钥：**
- OpenAI API: https://platform.openai.com/api-keys
- Tavily API: https://tavily.com （可选，提供更好的搜索结果）

#### 4. 运行程序

```bash
# 交互式命令行界面
python main.py

# 或运行示例程序
python example.py
```

## 💻 使用方法

### 交互式命令行界面

运行 `python main.py` 后，您可以：

```
🧑 您: 2024年巴黎奥运会有哪些新增项目？

🤖 助手: [代理会自动搜索并给出答案]
```

**可用命令：**
- `/clear` - 清空对话历史
- `/memory` - 查看对话历史
- `/help` - 显示帮助信息
- `/quit` - 退出程序

### 编程接口

```python
from react_agent import create_search_agent
import config

# 创建代理
agent = create_search_agent(
    openai_api_key=config.OPENAI_API_KEY,
    search_provider="duckduckgo",
    verbose=True
)

# 单次查询
response = agent.query("Python 3.12有哪些新特性？")
print(response)

# 带元数据的查询
result = agent.chat("介绍一下LangChain")
print(result['response'])
print(f"记忆长度: {result['memory_length']}")

# 清空记忆
agent.clear_memory()
```

## 🎯 示例场景

### 1. 实时信息查询

```python
agent.query("今天北京的天气怎么样？")
agent.query("最新的AI技术进展是什么？")
agent.query("2024年诺贝尔奖得主是谁？")
```

### 2. 多轮上下文对话

```python
agent.query("介绍一下量子计算")
agent.query("它有哪些实际应用？")  # 记住上文的"量子计算"
agent.query("目前有哪些公司在研发？")  # 继续上下文
```

### 3. 混合知识回答

对于一般性问题，代理会使用自身知识；当需要最新信息时，会自动调用搜索工具。

```python
agent.query("什么是机器学习？")  # 使用内置知识
agent.query("2024年最流行的机器学习框架是什么？")  # 使用搜索
```

## 🔧 配置选项

### config.py 配置说明

```python
# OpenAI配置
OPENAI_API_KEY = "your-key"
OPENAI_BASE_URL = None  # 可选，用于代理或自定义端点
MODEL_NAME = "gpt-3.5-turbo"  # 或 "gpt-4"
TEMPERATURE = 0.7  # 0-1，越高越创造性

# 搜索配置
SEARCH_PROVIDER = "duckduckgo"  # 或 "tavily"
TAVILY_API_KEY = "your-key"  # 仅Tavily需要

# 记忆配置
MAX_MEMORY_LENGTH = 10  # 保存的对话轮次
```

### 搜索提供商对比

| 特性 | DuckDuckGo | Tavily |
|------|-----------|---------|
| API密钥 | ❌ 不需要 | ✅ 需要 |
| 搜索质量 | ⭐⭐⭐ 良好 | ⭐⭐⭐⭐ 优秀 |
| 速度 | 快 | 非常快 |
| 结构化结果 | 否 | 是 |
| 免费额度 | 无限 | 1000次/月 |

**推荐：**
- 快速开始/测试：使用 DuckDuckGo
- 生产环境：使用 Tavily

### 自定义 API 端点

如果您需要使用代理或第三方兼容 OpenAI API 的服务，可以配置 `OPENAI_BASE_URL`：

```python
# 使用代理
OPENAI_BASE_URL = "https://your-proxy.com/v1"

# 使用Azure OpenAI
OPENAI_BASE_URL = "https://your-resource.openai.azure.com"

# 使用其他兼容服务（如本地部署的模型）
OPENAI_BASE_URL = "http://localhost:8000/v1"
```

**常见使用场景：**
- 🌐 **网络代理**：在无法直接访问 OpenAI API 的地区使用
- ☁️ **Azure OpenAI**：使用 Azure 提供的 OpenAI 服务
- 🏢 **企业代理**：通过公司内部代理访问
- 🔧 **本地模型**：使用兼容 OpenAI API 的本地部署模型
- 🧪 **测试环境**：使用 mock API 进行测试

**示例：**

```python
# 在代码中使用
agent = create_search_agent(
    openai_api_key="your-key",
    openai_base_url="https://your-proxy.com/v1",
    search_provider="duckduckgo"
)
```

## 📚 技术架构

### ReAct框架

ReAct (Reasoning and Acting) 是一种让LLM在推理过程中与外部工具交互的框架：

```
问题 → 思考 → 行动 → 观察 → 思考 → ... → 最终答案
```

**工作流程：**
1. **问题**：用户输入问题
2. **思考**：代理分析问题，决定下一步
3. **行动**：调用搜索工具（如需要）
4. **观察**：获取搜索结果
5. **重复**：继续思考和行动，直到得出答案
6. **最终答案**：综合所有信息给出回答

### 核心组件

```
SearchAgent (react_agent.py)
    ├── LLM (ChatOpenAI)
    ├── SearchTool (search_tools.py)
    │   ├── DuckDuckGo
    │   └── Tavily
    ├── MemoryManager (memory_manager.py)
    │   ├── ConversationBufferMemory
    │   └── 持久化存储
    └── AgentExecutor
```

## 🛠️ 高级用法

### 自定义提示模板

```python
from react_agent import SearchAgent

# 自定义ReAct提示
custom_prompt = """你是一个专业的研究助手..."""

agent = SearchAgent(
    openai_api_key="your-key",
    # ... 其他参数
)
# 修改agent.REACT_PROMPT_TEMPLATE
```

### 添加自定义工具

```python
from langchain.tools import Tool

def calculator(expr: str) -> str:
    return str(eval(expr))

calc_tool = Tool(
    name="calculator",
    func=calculator,
    description="用于数学计算"
)

# 添加到agent.tools
agent.tools.append(calc_tool)
```

### 使用不同的记忆类型

```python
from memory_manager import MemoryManager

# 摘要记忆（节省token）
memory = MemoryManager(
    memory_type="summary",
    llm=llm
)
```

## 📊 性能优化

### 减少API调用成本

1. **使用更便宜的模型**：`gpt-3.5-turbo` 比 `gpt-4` 便宜很多
2. **限制记忆长度**：减少 `MAX_MEMORY_LENGTH`
3. **使用免费搜索**：DuckDuckGo 完全免费
4. **降低温度**：`TEMPERATURE=0` 获得更确定的结果，减少重试

### 提高响应速度

1. **使用Tavily搜索**：比DuckDuckGo更快
2. **减少最大迭代次数**：修改 `max_iterations` 参数
3. **关闭详细日志**：`verbose=False`

## 🐛 故障排除

### 常见问题

**1. ImportError: No module named 'langchain'**
```bash
# 确保激活了虚拟环境
source venv/bin/activate
pip install -r requirements.txt
```

**2. OpenAI API错误**
```bash
# 检查API密钥是否正确
# 检查是否有足够的余额
# 检查网络连接
```

**3. 搜索失败**
```bash
# DuckDuckGo可能被限流，稍后重试
# 或切换到Tavily
```

**4. 记忆文件损坏**
```bash
# 删除chat_history.json重新开始
rm chat_history.json
```

## 📖 更多示例

查看 `example.py` 文件获取更多使用示例：

```bash
python example.py
```

包含的示例：
- 基础使用
- 带记忆的多轮对话
- 自定义配置
- 清空记忆

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 🔗 相关资源

- [LangChain文档](https://python.langchain.com/)
- [ReAct论文](https://arxiv.org/abs/2210.03629)
- [OpenAI API文档](https://platform.openai.com/docs)
- [Tavily API文档](https://docs.tavily.com/)

## 💡 项目亮点

这个项目展示了：

1. ✅ **ReAct框架实现** - 完整的推理和行动循环
2. ✅ **工具集成** - 无缝集成多个搜索API
3. ✅ **记忆管理** - 持久化对话历史
4. ✅ **错误处理** - 完善的异常处理机制
5. ✅ **可扩展性** - 易于添加新工具和功能
6. ✅ **生产就绪** - 包含配置管理、日志、文档

## 📞 支持

如有问题，请提交Issue或查看文档。

---

**开始构建你的智能搜索代理吧！** 🚀

