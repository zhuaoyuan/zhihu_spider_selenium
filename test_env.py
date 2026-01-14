#!/usr/bin/env python3
"""
环境测试脚本 - 检查项目是否可以正常运行
"""

import sys
import os

def test_imports():
    """测试所有依赖包是否可以正常导入"""
    print("=" * 50)
    print("测试 Python 包导入...")
    print("=" * 50)
    
    packages = [
        ('numpy', 'NumPy'),
        ('selenium', 'Selenium'),
        ('bs4', 'BeautifulSoup4'),
        ('pickle', 'Pickle'),
        ('json', 'JSON'),
        ('requests', 'Requests'),
        ('argparse', 'Argparse'),
        ('datetime', 'Datetime'),
        ('time', 'Time'),
        ('os', 'OS'),
        ('platform', 'Platform'),
    ]
    
    all_success = True
    for module_name, display_name in packages:
        try:
            __import__(module_name)
            print(f"✅ {display_name:20} - 导入成功")
        except ImportError as e:
            print(f"❌ {display_name:20} - 导入失败: {e}")
            all_success = False
    
    return all_success

def test_selenium_driver():
    """测试 Selenium 驱动配置"""
    print("\n" + "=" * 50)
    print("测试 Selenium WebDriver...")
    print("=" * 50)
    
    try:
        from selenium import webdriver
        from selenium.webdriver.edge.service import Service
        from selenium.webdriver import EdgeOptions
        
        print("✅ Selenium WebDriver 模块导入成功")
        
        # 检查驱动文件
        script_dir = os.path.dirname(os.path.abspath(__file__))
        driver_dir = os.path.join(script_dir, 'msedgedriver')
        
        if 'darwin' in sys.platform:
            driver_path = os.path.join(driver_dir, 'msedgedriver')
        else:
            driver_path = os.path.join(driver_dir, 'msedgedriver.exe')
        
        if os.path.exists(driver_path):
            print(f"✅ 浏览器驱动已存在: {driver_path}")
            if 'darwin' in sys.platform:
                # 检查执行权限
                import stat
                st = os.stat(driver_path)
                if st.st_mode & stat.S_IXUSR:
                    print("✅ 驱动文件有执行权限")
                else:
                    print("⚠️  驱动文件没有执行权限，请运行: chmod +x " + driver_path)
        else:
            print(f"ℹ️  浏览器驱动不存在，首次运行时会自动下载")
            print(f"   预期路径: {driver_path}")
        
        return True
    except Exception as e:
        print(f"❌ Selenium WebDriver 测试失败: {e}")
        return False

def test_directories():
    """测试项目目录结构"""
    print("\n" + "=" * 50)
    print("测试项目目录结构...")
    print("=" * 50)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dirs = ['article', 'answer', 'think', 'cookie', 'log', 'msedgedriver']
    
    all_ok = True
    for dir_name in dirs:
        dir_path = os.path.join(script_dir, dir_name)
        if os.path.exists(dir_path):
            print(f"✅ {dir_name:15} 目录已存在")
        else:
            print(f"ℹ️  {dir_name:15} 目录不存在（运行时会自动创建）")
    
    return True

def test_platform():
    """测试系统平台"""
    print("\n" + "=" * 50)
    print("系统信息...")
    print("=" * 50)
    
    import platform
    
    print(f"操作系统: {sys.platform}")
    print(f"系统版本: {platform.platform()}")
    print(f"处理器: {platform.processor()}")
    print(f"Python 版本: {sys.version}")
    
    if 'darwin' in sys.platform:
        if 'arm' in platform.processor():
            print("✅ 检测到 Apple Silicon (M1/M2) Mac")
        else:
            print("✅ 检测到 Intel Mac")
    elif 'win' in sys.platform:
        print("✅ 检测到 Windows 系统")
    elif 'linux' in sys.platform:
        print("✅ 检测到 Linux 系统")
    
    return True

def main():
    print("\n")
    print("🔧 知乎爬虫环境检测")
    print("=" * 50)
    
    results = []
    
    # 运行所有测试
    results.append(("Python 包导入", test_imports()))
    results.append(("Selenium 驱动", test_selenium_driver()))
    results.append(("项目目录", test_directories()))
    results.append(("系统平台", test_platform()))
    
    # 总结
    print("\n" + "=" * 50)
    print("测试总结")
    print("=" * 50)
    
    all_passed = all(result[1] for result in results)
    
    for test_name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name:20} {status}")
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有测试通过！环境配置成功！")
        print("\n下一步：")
        print("  1. 确保已安装 Microsoft Edge 浏览器")
        print("  2. 运行 ./run.sh login 进行首次登录")
        print("  3. 查看 README_MACOS.md 了解详细使用方法")
    else:
        print("⚠️  部分测试未通过，请检查上述错误信息")
    print("=" * 50)
    print()
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
