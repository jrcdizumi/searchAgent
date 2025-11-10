"""
搜索增强智能代理 (Search-Augmented Agent)

一个基于LangChain和ReAct框架的智能代理，能够通过实时网络搜索来回答用户问题。

主要特性：
- ReAct框架：推理和行动循环
- 实时搜索：DuckDuckGo、Tavily支持
- 对话记忆：持久化对话历史
- 灵活配置：多种模型和搜索引擎

快速开始：
    from react_agent import create_search_agent
    import config
    
    agent = create_search_agent(
        openai_api_key=config.OPENAI_API_KEY,
        search_provider="duckduckgo"
    )
    
    response = agent.query("你的问题")
    print(response)
"""

__version__ = "1.0.0"
__author__ = "Search Agent Team"

from react_agent import SearchAgent, create_search_agent
from search_tools import SearchToolWrapper, get_search_tool
from memory_manager import MemoryManager

__all__ = [
    'SearchAgent',
    'create_search_agent',
    'SearchToolWrapper',
    'get_search_tool',
    'MemoryManager',
]

