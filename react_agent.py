"""
ReAct Agent Implementation
Using function calling for intelligent tool usage
Compatible with new LangChain version
"""

from typing import Optional, List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from search_tools import SearchToolWrapper, TimeToolWrapper
from memory_manager import MemoryManager
import json
import re


class SearchAgent:
    """Search-based intelligent agent using function calling"""
    
    SYSTEM_PROMPT = """You are a helpful AI assistant with access to tools that help you provide accurate and timely information.

Available Tools:
1. search_web: Use when you need latest information, news, prices, weather, or any real-time data from the internet
2. get_current_time: Use when you need to know the current date, time, or day of the week

IMPORTANT Guidelines for Tool Usage:

Time Tool - Use get_current_time when:
- User asks about current time: "现在几点？" "What time is it?"
- User asks about current date: "今天几号？" "What's today's date?"
- User asks about day of week: "今天星期几？" "What day is it?"
- User mentions "today", "now", "latest", "newest", "recent", "this week", "this month"
- User asks about time in different timezones: "纽约现在几点？"
- ANY query about current/latest information: ALWAYS get time first, then search
  * "What is the latest iPhone?" → Get time first, then search "latest iPhone [date]"
  * "今天有什么新闻？" → Get time first, then search "[date] news"
  * "Recent AI developments" → Get time first, then search "AI developments [date]"

Search Tool - Use search_web when:
- Need latest news, current events, or recent information
- Need real-time data like prices, weather, stock prices
- User asks about something you don't have up-to-date knowledge about
- User explicitly asks to search or look up information

Direct Answer - Answer directly when:
- Question is about general knowledge that doesn't change
- Simple math, definitions, or common facts
- Personal opinions or creative tasks

Always use tools proactively when needed to provide accurate, current information.
Respond naturally in the same language as the user's question."""
    
    def __init__(
        self,
        openai_api_key: str,
        search_provider: str = "duckduckgo",
        tavily_api_key: Optional[str] = None,
        model_name: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_memory_length: int = 10,
        verbose: bool = True,
        openai_base_url: Optional[str] = None
    ):
        """
        Initialize search agent
        
        Args:
            openai_api_key: OpenAI API key
            search_provider: Search provider ("duckduckgo" or "tavily")
            tavily_api_key: Tavily API key (if using Tavily)
            model_name: Model name to use
            temperature: Temperature parameter
            max_memory_length: Maximum memory length
            verbose: Whether to show detailed logs
            openai_base_url: API base URL (optional, for proxy or custom endpoint)
        """
        # Initialize LLM
        llm_params = {
            "api_key": openai_api_key,
            "model": model_name,
            "temperature": temperature
        }
        if openai_base_url:
            llm_params["base_url"] = openai_base_url
        
        self.llm = ChatOpenAI(**llm_params)
        
        # Initialize search tool
        self.search_tool = SearchToolWrapper(
            provider=search_provider,
            api_key=tavily_api_key
        )
        
        # Initialize time tool
        self.time_tool = TimeToolWrapper()
        
        # Initialize memory manager
        self.memory_manager = MemoryManager(
            max_length=max_memory_length,
            memory_type="buffer",
            llm=self.llm,
            save_to_file=True
        )
        
        self.verbose = verbose
        
        # Define tools for function calling
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_web",
                    "description": "Search the web for real-time information. Use this when you need current events, latest news, weather, prices, or any information that changes over time.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query. Should be concise keywords or a clear question."
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_current_time",
                    "description": """Get the current date and time in a specific timezone. 
                    
USE THIS TOOL when:
- User asks "现在几点？" "What time is it?" "几点了？"
- User asks "今天几号？" "What's the date?" "今天是几月几号？"
- User asks "今天星期几？" "What day is it today?" "今天周几？"
- User mentions ANY time-related words: "today", "now", "latest", "newest", "recent", "current", "this week", "this month"
- User asks about "latest" or "newest" products/events/news
- You need current date context for accurate searching

CRITICAL: For ANY "latest/newest/recent" query, ALWAYS call this FIRST, then use the date in your search!

EXAMPLES that MUST trigger this tool:
- "现在几点了？" → Call get_current_time()
- "今天是几号？" → Call get_current_time()
- "What is the latest iPhone?" → Call get_current_time() FIRST, then search "latest iPhone November 2025"
- "What is the latest iPhone now?" → Call get_current_time() FIRST, then search
- "今天有什么新闻？" → Call get_current_time() FIRST, then search "[date] news"
- "Recent AI developments" → Call get_current_time() FIRST, then search "AI developments November 2025"
- "纽约现在几点？" → Call get_current_time(timezone="America/New_York")
- "Newest features in iOS" → Call get_current_time() FIRST
- "Current Bitcoin price" → Call get_current_time() FIRST

RULE: If query contains "latest/newest/recent/now/today/current" → ALWAYS get time FIRST!""",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "timezone": {
                                "type": "string",
                                "description": "Timezone name. Common values: 'Asia/Shanghai' (China/Beijing), 'America/New_York' (US East), 'America/Los_Angeles' (US West), 'Europe/London' (UK), 'Asia/Tokyo' (Japan), 'Europe/Paris' (France). Default is 'Asia/Shanghai'.",
                                "default": "Asia/Shanghai"
                            }
                        },
                        "required": []
                    }
                }
            }
        ]
    
    def _parse_text_tool_call(self, content: str) -> Optional[str]:
        """
        Parse text-format tool calls as fallback
        Handles formats like: <tool_call>search_web<arg_key>query</arg_key><arg_value>...</arg_value></tool_call>
        """
        if not content or '<tool_call>' not in content:
            return None
        
        try:
            # Pattern 1: XML-style format
            match = re.search(r'<tool_call>search_web.*?<arg_value>(.*?)</arg_value>', content, re.DOTALL)
            if match:
                return match.group(1).strip()
            
            # Pattern 2: Simple format
            match = re.search(r'<tool_call>\s*search_web\s*\(.*?query\s*[=:]\s*["\']([^"\']+)["\']', content, re.DOTALL)
            if match:
                return match.group(1).strip()
            
            # Pattern 3: JSON-like format in tool_call
            match = re.search(r'<tool_call>.*?"query"\s*:\s*"([^"]+)"', content, re.DOTALL)
            if match:
                return match.group(1).strip()
                
        except Exception as e:
            if self.verbose:
                print(f"⚠️ Failed to parse text tool call: {e}")
        
        return None
    
    def query(self, user_input: str, max_iterations: int = 5) -> str:
        """
        Process user query with function calling
        
        Args:
            user_input: User's input question
            max_iterations: Maximum number of iterations for function calling
        
        Returns:
            Agent's response
        """
        try:
            # Get conversation history
            chat_history = self.memory_manager.get_memory()
            
            # Add user message to memory
            self.memory_manager.add_user_message(user_input)
            
            # Build messages
            messages = [
                SystemMessage(content=self.SYSTEM_PROMPT),
            ]
            
            # Add recent conversation history
            for msg in chat_history[-6:]:  # Last 3 rounds
                messages.append(msg)
            
            # Add current user question
            messages.append(HumanMessage(content=user_input))
            
            # Iterative function calling loop
            iteration = 0
            search_count = 0
            max_searches = 2  # Allow max 2 searches per query
            
            while iteration < max_iterations:
                iteration += 1
                
                if self.verbose and iteration > 1:
                    print(f"\n🔄 Iteration {iteration}")
                
                # Call LLM with tools (time tool doesn't count towards search limit)
                response = self.llm.invoke(
                    messages,
                    tools=self.tools,
                    tool_choice="auto"
                )
                
                # Check if model wants to call a function (structured format)
                search_performed = False
                
                if hasattr(response, 'tool_calls') and response.tool_calls:
                    # Process structured tool calls
                    for tool_call in response.tool_calls:
                        if tool_call['name'] == 'search_web' and search_count < max_searches:
                            args = tool_call['args']
                            search_query = args.get('query', '')
                            
                            if self.verbose:
                                print(f"\n🔍 Search #{search_count + 1} (structured)")
                                print(f"📝 Query: {search_query}")
                            
                            # Execute search
                            search_results = self.search_tool.search(search_query)
                            
                            if self.verbose:
                                print(f"✅ Search completed")
                            
                            # Add assistant message with tool call
                            messages.append(response)
                            
                            # Add tool response
                            messages.append(
                                ToolMessage(
                                    content=f"Search results: {search_results}",
                                    tool_call_id=tool_call['id']
                                )
                            )
                            
                            search_count += 1
                            search_performed = True
                            break
                        
                        elif tool_call['name'] == 'search_web' and search_count >= max_searches:
                            # Max searches reached, skip this search
                            if self.verbose:
                                print(f"\n⚠️ Max searches ({max_searches}) reached, skipping search")
                            # Don't add tool call to messages, let model continue without it
                            break
                        
                        elif tool_call['name'] == 'get_current_time':
                            # Time tool doesn't count towards search limit
                            args = tool_call['args']
                            timezone = args.get('timezone', 'Asia/Shanghai')
                            
                            if self.verbose:
                                print(f"\n🕐 Getting current time")
                                print(f"📍 Timezone: {timezone}")
                            
                            # Execute time query
                            time_result = self.time_tool.get_current_time(timezone)
                            
                            if self.verbose:
                                print(f"✅ Time retrieved")
                            
                            # Add assistant message with tool call
                            messages.append(response)
                            
                            # Add tool response
                            messages.append(
                                ToolMessage(
                                    content=time_result,
                                    tool_call_id=tool_call['id']
                                )
                            )
                            
                            search_performed = True
                            break
                
                # Fallback: Check for text-format tool calls
                elif search_count < max_searches and response.content:
                    search_query = self._parse_text_tool_call(response.content)
                    
                    if search_query:
                        if self.verbose:
                            print(f"\n🔍 Search #{search_count + 1} (text format)")
                            print(f"📝 Query: {search_query}")
                        
                        # Execute search
                        search_results = self.search_tool.search(search_query)
                        
                        if self.verbose:
                            print(f"✅ Search completed")
                        
                        # Add response and search results
                        messages.append(response)
                        messages.append(
                            AIMessage(content=f"\nSearch results: {search_results}\n\nBased on these results, please provide the answer:")
                        )
                        
                        search_count += 1
                        search_performed = True
                
                # If search was performed, continue to next iteration
                if search_performed:
                    continue
                
                # No more tool calls, model has final answer
                final_response = response.content
                
                # Add AI response to memory
                self.memory_manager.add_ai_message(final_response)
                
                return final_response
            
            # Max iterations reached
            if self.verbose:
                print(f"\n⚠️ Max iterations ({max_iterations}) reached")
            
            # Try to get a response without tools
            final_response = self.llm.invoke(messages).content
            self.memory_manager.add_ai_message(final_response)
            return final_response
            
        except Exception as e:
            error_msg = f"Error processing query: {str(e)}"
            if self.verbose:
                print(error_msg)
                import traceback
                traceback.print_exc()
            return f"Sorry, an error occurred while processing your request: {str(e)}"
    
    def chat(self, user_input: str) -> Dict[str, Any]:
        """
        Chat interface, returns more detailed information
        
        Args:
            user_input: User input
        
        Returns:
            Dictionary containing response and metadata
        """
        response = self.query(user_input)
        
        return {
            "response": response,
            "memory_length": len(self.memory_manager.get_memory()),
            "timestamp": self._get_timestamp()
        }
    
    def clear_memory(self):
        """Clear conversation memory"""
        self.memory_manager.clear_memory()
        if self.verbose:
            print("Conversation memory cleared")
    
    def get_memory_summary(self) -> str:
        """Get memory summary"""
        return self.memory_manager.get_context_string()
    
    @staticmethod
    def _get_timestamp() -> str:
        """Get timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def create_search_agent(
    openai_api_key: str,
    search_provider: str = "duckduckgo",
    tavily_api_key: Optional[str] = None,
    openai_base_url: Optional[str] = None,
    **kwargs
) -> SearchAgent:
    """
    Factory function to create search agent
    
    Args:
        openai_api_key: OpenAI API key
        search_provider: Search provider
        tavily_api_key: Tavily API key
        openai_base_url: OpenAI API base URL (optional)
        **kwargs: Other parameters
    
    Returns:
        SearchAgent instance
    """
    return SearchAgent(
        openai_api_key=openai_api_key,
        search_provider=search_provider,
        tavily_api_key=tavily_api_key,
        openai_base_url=openai_base_url,
        **kwargs
    )
