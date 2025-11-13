#!/bin/bash

# Start API Server Script
# This script starts the FastAPI server with streaming support

echo "======================================"
echo "🚀 启动智能搜索助手 API 服务器"
echo "======================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装 Python 3.8+"
    exit 1
fi

# Check if config.py exists
if [ ! -f "config.py" ]; then
    echo "❌ config.py 文件不存在"
    echo "请确保配置文件已正确设置"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🔧 未检测到虚拟环境，正在创建..."
    python3 -m venv venv
    echo "✅ 虚拟环境创建成功"
fi

# Activate virtual environment
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📦 安装/更新依赖包..."
pip install -r requirements.txt --quiet

# Start the server
echo ""
echo "======================================"
echo "✅ 准备就绪，启动服务器..."
echo "======================================"
echo ""
echo "服务器地址: http://localhost:8080"
echo "API 文档: http://localhost:8080/docs"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

python3 api_server.py

