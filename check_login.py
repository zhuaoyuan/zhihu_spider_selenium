#!/usr/bin/env python3
"""
检查登录状态和 cookie 是否有效
"""

import os
import pickle
import sys

def check_cookie():
    """检查 cookie 文件是否存在"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cookie_dir = os.path.join(script_dir, 'cookie')
    cookie_path = os.path.join(cookie_dir, 'cookie_zhihu.pkl')
    
    print("=" * 50)
    print("检查登录状态...")
    print("=" * 50)
    
    if not os.path.exists(cookie_dir):
        print("❌ Cookie 目录不存在")
        print(f"   预期路径: {cookie_dir}")
        print("\n需要首次登录，请运行: ./run.sh login")
        return False
    
    if not os.path.exists(cookie_path):
        print("❌ Cookie 文件不存在")
        print(f"   预期路径: {cookie_path}")
        print("\n需要首次登录，请运行: ./run.sh login")
        return False
    
    print(f"✅ Cookie 文件存在: {cookie_path}")
    
    # 尝试读取 cookie
    try:
        with open(cookie_path, 'rb') as f:
            cookies = pickle.load(f)
        print(f"✅ Cookie 文件有效，包含 {len(cookies)} 个 cookie")
        
        # 显示 cookie 的创建时间
        import time
        file_time = os.path.getmtime(cookie_path)
        from datetime import datetime
        create_time = datetime.fromtimestamp(file_time)
        print(f"   Cookie 创建时间: {create_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 检查 cookie 是否太旧（超过7天）
        age_days = (time.time() - file_time) / 86400
        if age_days > 7:
            print(f"⚠️  Cookie 已经 {age_days:.1f} 天，可能已失效")
            print("   建议重新登录: ./run.sh login")
        else:
            print(f"   Cookie 年龄: {age_days:.1f} 天")
        
        return True
    except Exception as e:
        print(f"❌ 读取 Cookie 文件失败: {e}")
        print("   Cookie 文件可能损坏，请重新登录")
        return False

def main():
    print("\n🔍 知乎爬虫登录状态检查\n")
    
    cookie_ok = check_cookie()
    
    print("\n" + "=" * 50)
    print("检查结果")
    print("=" * 50)
    
    if cookie_ok:
        print("✅ 登录状态正常")
        print("\n可以开始爬取:")
        print("  ./run.sh article   # 爬取文章")
        print("  ./run.sh answer    # 爬取回答")
        print("  ./run.sh think     # 爬取想法")
    else:
        print("❌ 需要登录")
        print("\n请先运行登录命令:")
        print("  ./run.sh login")
        print("\n登录后会:")
        print("  1. 打开浏览器到知乎登录页")
        print("  2. 手动输入账号密码并登录")
        print("  3. 自动保存 cookie")
        print("  4. 之后就可以自动爬取了")
    
    print("=" * 50)
    print()
    
    return 0 if cookie_ok else 1

if __name__ == "__main__":
    sys.exit(main())
