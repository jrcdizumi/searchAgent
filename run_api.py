#!/usr/bin/env python3
"""
简化的 API 服务器启动脚本
不使用 reload 模式，避免多进程问题
"""

import sys
import uvicorn

# 添加当前目录到路径
sys.path.insert(0, '/Users/dian.chen/Documents/searchAgent')

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 启动智能搜索助手 API 服务器")
    print("=" * 60)
    print("📍 服务器地址: http://localhost:8080")
    print("📚 API 文档: http://localhost:8080/docs")
    print("=" * 60)
    print("\n⏳ 正在初始化 Agent（首次启动可能需要几秒钟）...\n")
    
    try:
        uvicorn.run(
            "api_server:app",
            host="0.0.0.0",
            port=8080,
            reload=False,  # 关闭 reload 避免多进程
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n👋 服务器已停止")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        sys.exit(1)

