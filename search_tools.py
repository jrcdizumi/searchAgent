"""
Search Tools Module
Provides different search API interfaces (Tavily and DuckDuckGo)
"""

from langchain_community.tools import DuckDuckGoSearchRun
from typing import Optional

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
