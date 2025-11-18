"""
Search Tools Module
Provides different search API interfaces (Tavily and DuckDuckGo)
Plus utility tools like time query
"""

from langchain_community.tools import DuckDuckGoSearchRun
from typing import Optional
from datetime import datetime
import pytz

# Use new langchain-tavily package
try:
    from langchain_tavily import TavilySearch
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False
    print("⚠️ langchain-tavily not installed, Tavily search will be unavailable")


def get_search_tool(provider: str = "duckduckgo", api_key: Optional[str] = None):
    """
    Get search tool
    
    Args:
        provider: Search provider ("tavily" or "duckduckgo")
        api_key: Tavily API key (if using Tavily)
    
    Returns:
        Search tool instance
    """
    if provider.lower() == "tavily":
        if not TAVILY_AVAILABLE:
            raise ImportError("Tavily search requires langchain-tavily package. Run: pip install langchain-tavily")
        
        if not api_key:
            raise ValueError("Using Tavily search requires an API key")
        
        # Set environment variable
        import os
        os.environ["TAVILY_API_KEY"] = api_key
        
        # Use new TavilySearch tool
        return TavilySearch(
            max_results=5,
            name="tavily_search",
            description="A search engine tool. Use this tool when you need to answer questions about current events, real-time information, or need to fetch the latest data from the web. The input should be a search query."
        )
    else:
        # DuckDuckGo doesn't need API key, suitable for quick start
        search = DuckDuckGoSearchRun(
            name="duckduckgo_search",
            description="A search engine tool. Use this tool when you need to answer questions about current events, real-time information, or need to fetch the latest data from the web. The input should be a search query."
        )
        return search


class SearchToolWrapper:
    """Search tool wrapper providing unified interface"""
    
    def __init__(self, provider: str = "duckduckgo", api_key: Optional[str] = None):
        self.provider = provider
        self.tool = get_search_tool(provider, api_key)
    
    def search(self, query: str) -> str:
        """Execute search"""
        try:
            return self.tool.run(query)
        except Exception as e:
            return f"Search error: {str(e)}"
    
    def get_tool(self):
        """Get LangChain tool instance"""
        return self.tool


class TimeToolWrapper:
    """时间查询工具"""
    
    def __init__(self):
        pass
    
    def get_current_time(self, timezone: str = "Asia/Shanghai") -> str:
        """
        获取当前时间
        
        Args:
            timezone: 时区，默认为 Asia/Shanghai (中国时间)
                     其他选项: America/New_York, Europe/London, Asia/Tokyo 等
        
        Returns:
            格式化的当前时间字符串
        """
        try:
            # 获取指定时区的当前时间
            tz = pytz.timezone(timezone)
            current_time = datetime.now(tz)
            
            # 格式化输出
            result = {
                "timezone": timezone,
                "datetime": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "date": current_time.strftime("%Y-%m-%d"),
                "time": current_time.strftime("%H:%M:%S"),
                "weekday": current_time.strftime("%A"),
                "year": current_time.year,
                "month": current_time.month,
                "day": current_time.day,
                "hour": current_time.hour,
                "minute": current_time.minute,
                "second": current_time.second,
            }
            
            # 返回友好的格式
            return (
                f"当前时间 ({timezone}):\n"
                f"📅 日期: {result['date']} ({result['weekday']})\n"
                f"🕐 时间: {result['time']}\n"
                f"📆 完整: {result['datetime']}"
            )
            
        except Exception as e:
            return f"获取时间失败: {str(e)}\n请检查时区名称是否正确。"
