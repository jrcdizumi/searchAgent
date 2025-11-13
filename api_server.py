"""
FastAPI Server with Streaming Support
Provides REST API with Server-Sent Events (SSE) streaming
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, AsyncIterator
import json
import asyncio
import sys
from react_agent import create_search_agent

# Load configuration
try:
    import config
except ImportError:
    print("❌ config.py file not found")
    sys.exit(1)

# Initialize FastAPI app
app = FastAPI(title="Search Agent API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance
agent = None


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str
    stream: Optional[bool] = False


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
    memory_length: int
    timestamp: str


@app.on_event("startup")
async def startup_event():
    """Initialize agent on startup"""
    global agent
    
    print("🔧 Initializing agent...")
    
    try:
        agent = create_search_agent(
            openai_api_key=config.OPENAI_API_KEY,
            search_provider=config.SEARCH_PROVIDER,
            tavily_api_key=getattr(config, 'TAVILY_API_KEY', None),
            openai_base_url=getattr(config, 'OPENAI_BASE_URL', None),
            model_name=getattr(config, 'MODEL_NAME', 'gpt-3.5-turbo'),
            temperature=getattr(config, 'TEMPERATURE', 0.7),
            max_memory_length=getattr(config, 'MAX_MEMORY_LENGTH', 10),
            verbose=True
        )
        print("✅ Agent initialized successfully!")
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        sys.exit(1)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Search Agent API",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/api/chat (POST)",
            "stream": "/api/chat/stream (POST)",
            "memory": "/api/memory (GET)",
            "clear": "/api/clear (POST)"
        }
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "agent_ready": agent is not None}


@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Chat endpoint - Non-streaming response
    
    Request body:
        - message: User's message
        - stream: Whether to use streaming (optional, default: False)
    """
    if agent is None:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    # If streaming is requested, redirect to stream endpoint
    if request.stream:
        return await chat_stream(request)
    
    try:
        # Call agent to get response
        result = agent.chat(request.message.strip())
        return ChatResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


async def generate_stream(message: str) -> AsyncIterator[str]:
    """
    Generate streaming response
    
    Yields SSE formatted data chunks
    """
    try:
        # Send initial event
        yield f"data: {json.dumps({'type': 'start', 'message': '开始处理您的问题...'})}\n\n"
        await asyncio.sleep(0.1)
        
        # 使用简化的方法：直接调用 agent 的 query 方法并逐字返回
        # agent.query() 内部会处理记忆管理和搜索逻辑
        try:
            # 使用线程池异步调用同步的 query 方法，避免阻塞事件循环
            response_text = await asyncio.to_thread(agent.query, message)
            
            # 将响应逐字流式发送到前端
            for char in response_text:
                yield f"data: {json.dumps({'type': 'content', 'content': char})}\n\n"
                await asyncio.sleep(0.02)  # 控制输出速度，创建打字机效果
                
        except Exception as inner_e:
            # 如果出错，发送错误事件
            error_msg = f"处理出错: {str(inner_e)}"
            yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"
            return
        
        # Send completion event
        yield f"data: {json.dumps({'type': 'done', 'message': '回答完成'})}\n\n"
        
    except Exception as e:
        # Send error event
        error_msg = f"Error: {str(e)}"
        yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"


@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Chat endpoint - Streaming response using Server-Sent Events
    
    Request body:
        - message: User's message
    """
    if agent is None:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    return StreamingResponse(
        generate_stream(request.message.strip()),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.get("/api/memory")
async def get_memory():
    """Get conversation memory"""
    if agent is None:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    try:
        memory_summary = agent.get_memory_summary()
        memory_list = agent.memory_manager.get_memory()
        
        return {
            "summary": memory_summary,
            "length": len(memory_list),
            "messages": [
                {
                    "role": msg.__class__.__name__.replace("Message", "").lower(),
                    "content": msg.content
                }
                for msg in memory_list
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting memory: {str(e)}")


@app.post("/api/clear")
async def clear_memory():
    """Clear conversation memory"""
    if agent is None:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    try:
        agent.clear_memory()
        return {"message": "Memory cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing memory: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("🚀 Starting Search Agent API Server")
    print("=" * 60)
    print("Server will run at: http://localhost:8080")
    print("API Documentation: http://localhost:8080/docs")
    print("=" * 60)
    print()
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8080,
        reload=False,  # 关闭 reload 避免多进程问题
        log_level="info"
    )

