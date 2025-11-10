#!/bin/bash

# 搜索增强代理安装脚本

echo "🚀 开始安装搜索增强代理..."
echo ""

# 检查Python版本
echo "📌 检查Python版本..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Python版本: $python_version"

# 创建虚拟环境
echo ""
echo "📦 创建虚拟环境..."
if [ -d "venv" ]; then
    echo "   虚拟环境已存在，跳过创建"
else
    python3 -m venv venv
    echo "   ✅ 虚拟环境创建成功"
fi

# 激活虚拟环境
echo ""
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 升级pip
echo ""
echo "⬆️  升级pip..."
pip install --upgrade pip

# 安装依赖
echo ""
echo "📚 安装依赖包..."
pip install -r requirements.txt

# 创建配置文件
echo ""
echo "⚙️  设置配置文件..."
if [ ! -f "config.py" ]; then
    cp config.example.py config.py
    echo "   ✅ 已创建 config.py"
    echo "   ⚠️  请编辑 config.py 并填入您的API密钥"
else
    echo "   config.py 已存在，跳过创建"
fi

echo ""
echo "=" 
echo "✅ 安装完成！"
echo ""
echo "📖 下一步："
echo "   1. 编辑 config.py 文件，填入您的OpenAI API密钥"
echo "   2. 激活虚拟环境: source venv/bin/activate"
echo "   3. 运行程序: python main.py"
echo "   4. 或运行示例: python example.py"
echo ""
echo "💡 提示："
echo "   - 使用DuckDuckGo搜索不需要额外的API密钥"
echo "   - 如需使用Tavily搜索，请在 https://tavily.com 获取API密钥"
echo ""

