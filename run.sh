#!/bin/bash

# 知乎爬虫启动脚本
# 使用方法:
# ./run.sh login                    # 首次运行，登录并保存cookie
# ./run.sh check                    # 检查登录状态
# ./run.sh article [用户名]         # 爬取文章
# ./run.sh answer [用户名]          # 爬取回答
# ./run.sh think [用户名]           # 爬取想法
# ./run.sh all [用户名]             # 爬取所有内容
#
# [用户名] 是可选参数，格式为知乎个人主页URL中的标识，如 zhang-san
# 不指定用户名时爬取登录用户自己的内容

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 激活虚拟环境
source venv/bin/activate

# 检查登录状态的函数
check_login() {
    if [ ! -f "cookie/cookie_zhihu.pkl" ]; then
        echo "❌ 错误: 未找到登录 cookie"
        echo ""
        echo "请先运行登录命令:"
        echo "  ./run.sh login"
        echo ""
        exit 1
    fi
}

# 获取用户名参数（如果提供）
TARGET_USER="$2"
USER_ARG=""
if [ -n "$TARGET_USER" ]; then
    USER_ARG="--target_user $TARGET_USER"
fi

# 根据参数执行不同操作
case "$1" in
    login)
        echo "首次登录，保存cookie..."
        python crawler.py
        ;;
    check)
        echo "检查登录状态..."
        python check_login.py
        ;;
    article)
        check_login
        if [ -n "$TARGET_USER" ]; then
            echo "爬取指定用户的文章: $TARGET_USER"
        else
            echo "爬取自己的文章..."
        fi
        python crawler.py --article --MarkDown --links_scratch $USER_ARG
        ;;
    answer)
        check_login
        if [ -n "$TARGET_USER" ]; then
            echo "爬取指定用户的回答: $TARGET_USER"
        else
            echo "爬取自己的回答..."
        fi
        python crawler.py --answer --MarkDown --links_scratch $USER_ARG
        ;;
    think)
        check_login
        if [ -n "$TARGET_USER" ]; then
            echo "爬取指定用户的想法: $TARGET_USER"
        else
            echo "爬取自己的想法..."
        fi
        python crawler.py --think --links_scratch $USER_ARG
        ;;
    all)
        check_login
        if [ -n "$TARGET_USER" ]; then
            echo "爬取指定用户的所有内容: $TARGET_USER"
        else
            echo "爬取自己的所有内容（想法、文章、回答）..."
        fi
        python crawler.py --think --article --answer --MarkDown --links_scratch $USER_ARG
        ;;
    *)
        echo "使用方法:"
        echo "  ./run.sh login                - 首次运行，登录并保存cookie"
        echo "  ./run.sh check                - 检查登录状态"
        echo "  ./run.sh article [用户名]     - 爬取文章（保存为Markdown和PDF）"
        echo "  ./run.sh answer [用户名]      - 爬取回答（保存为Markdown和PDF）"
        echo "  ./run.sh think [用户名]       - 爬取想法（保存为文本）"
        echo "  ./run.sh all [用户名]         - 爬取所有内容"
        echo ""
        echo "参数说明:"
        echo "  [用户名] - 可选，指定要爬取的知乎用户（个人主页URL中的标识）"
        echo "           - 例如: zhang-san (对应 https://www.zhihu.com/people/zhang-san)"
        echo "           - 不指定时爬取登录用户自己的内容"
        echo ""
        echo "示例:"
        echo "  ./run.sh login                    # 首次登录"
        echo "  ./run.sh article                  # 爬取自己的文章"
        echo "  ./run.sh article zhang-san        # 爬取 zhang-san 的文章"
        echo "  ./run.sh all li-si                # 爬取 li-si 的所有内容"
        echo ""
        echo "首次使用请先运行: ./run.sh login"
        exit 1
        ;;
esac
