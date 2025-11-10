# ⚡ 快速开始指南

## 3分钟启动您的搜索增强代理

### 🎯 前提条件

- Python 3.8+
- OpenAI API密钥（从 https://platform.openai.com/api-keys 获取）

### 📝 三步启动

#### 1️⃣ 运行安装脚本

```bash
chmod +x setup.sh
./setup.sh
```

#### 2️⃣ 配置API密钥

```bash
# 编辑配置文件
nano config.py

# 填入您的OpenAI API密钥
OPENAI_API_KEY = "sk-your-openai-api-key"
```

#### 3️⃣ 启动程序

```bash
source venv/bin/activate
python main.py
```

### 🎮 开始对话

```
🧑 您: 2024年最新的AI技术趋势是什么？

🤖 助手: [自动搜索网络并给出答案]
```

### 💡 示例问题

试试这些问题：

```
- 今天的天气怎么样？
- Python 3.12有哪些新特性？
- 2024年诺贝尔奖得主是谁？
- 解释一下量子计算
- 最新的Tesla车型有哪些？
```

### 🔧 常用命令

在程序中输入：
- `/clear` - 清空对话历史
- `/memory` - 查看对话历史
- `/help` - 显示帮助
- `/quit` - 退出

### 📚 编程使用

创建一个Python文件：

```python
from react_agent import create_search_agent
import config

# 创建代理
agent = create_search_agent(
    openai_api_key=config.OPENAI_API_KEY,
    search_provider="duckduckgo"
)

# 提问
response = agent.query("LangChain是什么？")
print(response)
```

运行：

```bash
python your_script.py
```

### 🎯 多轮对话示例

```python
agent.query("介绍一下机器学习")
agent.query("它有哪些应用？")  # 自动记住上下文
agent.query("推荐一些学习资源")  # 继续对话
```

### ⚙️ 自定义配置

编辑 `config.py`：

```python
# 使用更强大的模型
MODEL_NAME = "gpt-4"

# 调整创造性
TEMPERATURE = 0.3  # 0=确定性，1=创造性

# 调整记忆长度
MAX_MEMORY_LENGTH = 20  # 保存20轮对话

# 切换搜索引擎
SEARCH_PROVIDER = "tavily"  # 需要Tavily API密钥

# 使用代理或自定义API端点（可选）
OPENAI_BASE_URL = "https://your-proxy.com/v1"
```

### 🔍 搜索引擎选择

**DuckDuckGo（默认）：**
- ✅ 完全免费
- ✅ 无需API密钥
- ✅ 快速开始

**Tavily（推荐生产环境）：**
- ✅ 更好的搜索质量
- ✅ 结构化结果
- ✅ 更快的响应
- ⚠️ 需要API密钥（免费额度：1000次/月）

### 🚀 运行示例程序

```bash
python example.py
```

包含4个完整示例：
1. 基础使用
2. 多轮对话
3. 自定义配置
4. 记忆管理

### 🐛 遇到问题？

**API密钥错误：**
```bash
# 检查config.py中的密钥格式
OPENAI_API_KEY = "sk-..."  # 应该以sk-开头
```

**模块未找到：**
```bash
# 确保激活虚拟环境
source venv/bin/activate
pip install -r requirements.txt
```

**搜索失败：**
```bash
# 检查网络连接
# 或在config.py中切换搜索提供商
SEARCH_PROVIDER = "tavily"
```

### 📖 更多信息

- 完整文档：`README.md`
- 安装指南：`INSTALL.md`
- 示例代码：`example.py`

### 💰 成本预估

使用 `gpt-3.5-turbo`：
- 每1000个token约 $0.002
- 典型对话（包含搜索）：约500-1000 tokens
- **成本：约 $0.001-0.002 每次对话**

使用 `gpt-4`：
- 成本约为gpt-3.5的30倍
- 更好的理解和推理能力

**DuckDuckGo搜索：** 完全免费
**Tavily搜索：** 免费1000次/月

### 🎓 工作原理

```
用户问题 → ReAct代理
           ├─ 思考：是否需要搜索？
           ├─ 行动：调用搜索工具
           ├─ 观察：获取搜索结果
           ├─ 思考：综合信息
           └─ 回答：最终答案

所有对话 → 记忆管理器 → 持久化存储
```

### ✨ 特色功能

1. **智能决策**：自动判断是否需要搜索
2. **上下文记忆**：记住之前的对话
3. **实时信息**：获取最新的网络数据
4. **灵活配置**：支持多种模型和搜索引擎
5. **易于扩展**：可添加自定义工具

### 🎯 最佳实践

1. **使用gpt-3.5-turbo测试**，满意后再升级到gpt-4
2. **DuckDuckGo足够日常使用**，生产环境考虑Tavily
3. **定期清空记忆**（`/clear`）以获得更好的性能
4. **明确的问题**能得到更好的答案

### 🚀 现在开始！

```bash
# 1. 安装
./setup.sh

# 2. 配置
nano config.py

# 3. 运行
source venv/bin/activate
python main.py
```

**就这么简单！开始享受您的智能搜索代理吧！** 🎉

---

需要帮助？查看 `README.md` 或 `INSTALL.md`

