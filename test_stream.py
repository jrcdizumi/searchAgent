#!/usr/bin/env python3
"""
测试流式 API 的脚本
"""

import requests
import json
import sys

def test_stream():
    """测试流式端点"""
    url = "http://localhost:8080/api/chat/stream"
    
    data = {
        "message": "你好，请简单介绍一下你自己"
    }
    
    print("🔍 发送请求到流式端点...")
    print(f"📝 消息: {data['message']}\n")
    
    try:
        response = requests.post(
            url,
            json=data,
            stream=True,
            timeout=60
        )
        
        if response.status_code != 200:
            print(f"❌ 错误: HTTP {response.status_code}")
            print(f"详情: {response.text}")
            return False
        
        print("✅ 连接成功，开始接收流式数据...\n")
        print("=" * 60)
        
        event_count = 0
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    event_count += 1
                    try:
                        data = json.loads(line[6:])
                        event_type = data.get('type', 'unknown')
                        
                        if event_type == 'start':
                            print(f"🚀 [{event_type}] {data.get('message', '')}")
                        
                        elif event_type == 'content':
                            print(data.get('content', ''), end='', flush=True)
                        
                        elif event_type == 'search':
                            print(f"\n🔍 [{event_type}] 搜索: {data.get('query', '')} (第{data.get('count', 0)}次)")
                        
                        elif event_type == 'search_complete':
                            print(f"✅ [{event_type}] {data.get('message', '')}")
                        
                        elif event_type == 'done':
                            print(f"\n\n🎉 [{event_type}] {data.get('message', '')}")
                        
                        elif event_type == 'error':
                            print(f"\n❌ [{event_type}] {data.get('message', '')}")
                            return False
                        
                    except json.JSONDecodeError as e:
                        print(f"\n⚠️ JSON 解析错误: {e}")
                        print(f"原始数据: {line}")
        
        print("=" * 60)
        print(f"\n✅ 测试完成! 共接收 {event_count} 个事件")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败: 无法连接到后端服务")
        print("请确保后端服务正在运行: python api_server.py")
        return False
    
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_health():
    """测试健康检查端点"""
    url = "http://localhost:8080/api/health"
    
    print("🏥 测试健康检查端点...")
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 健康检查通过: {data}")
            return True
        else:
            print(f"❌ 健康检查失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("🧪 测试流式 API")
    print("=" * 60 + "\n")
    
    # 测试健康检查
    if not test_health():
        print("\n❌ 后端服务未运行或不健康")
        sys.exit(1)
    
    print()
    
    # 测试流式传输
    if test_stream():
        print("\n✅ 所有测试通过!")
        sys.exit(0)
    else:
        print("\n❌ 测试失败!")
        sys.exit(1)


if __name__ == "__main__":
    main()

