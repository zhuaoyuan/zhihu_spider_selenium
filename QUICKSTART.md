# 快速开始指南

## ✅ 环境已配置完成！

所有必要的依赖包已安装，项目已准备就绪。

## 🚀 立即开始使用

### 1️⃣ 安装 Edge 浏览器（如果还没有）

```bash
# 使用 Homebrew 安装
brew install --cask microsoft-edge

# 或访问官网下载
# https://www.microsoft.com/edge
```

### 2️⃣ 首次登录

```bash
cd /Users/zhuaoyuan/cursor-workspace/knowledge-base/scripts/zhihu_spider_selenium
./run.sh login
```

**重要提示：**
- 浏览器会自动打开知乎登录页面
- 手动输入账号密码并登录
- 登录后**不要操作浏览器**，等待程序自动保存 cookie
- 如果提示需要给驱动添加执行权限，按提示运行 `chmod +x` 命令

### 3️⃣ 开始爬取

登录成功后，选择要爬取的内容：

```bash
# 爬取文章（保存为 Markdown 和 PDF）
./run.sh article

# 爬取回答（保存为 Markdown 和 PDF）
./run.sh answer

# 爬取想法（保存为文本）
./run.sh think

# 爬取所有内容
./run.sh all
```

### 4️⃣ 查看结果

爬取的内容保存在：
- `article/` - 文章
- `answer/` - 回答
- `think/` - 想法
- `log/` - 运行日志

## 📖 更多信息

- 详细使用指南：查看 `README_MACOS.md`
- 运行环境测试：`source venv/bin/activate && python test_env.py`
- 查看帮助：`source venv/bin/activate && python crawler.py --help`

## 🔧 配置说明

### 当前配置

- ✅ Python 虚拟环境：`venv/`
- ✅ 已安装依赖：numpy, selenium, beautifulsoup4, requests
- ✅ 系统平台：Intel Mac (macOS)
- ✅ 启动脚本：`run.sh`

### 爬取参数

默认配置：
- 爬取间隔：6 秒（可通过 `--sleep_time` 参数修改）
- 保存格式：PDF + Markdown（支持数学公式）
- 重复爬取：自动跳过已爬取内容

## ⚠️ 注意事项

1. **首次运行**会自动下载浏览器驱动（约 10-20MB）
2. **爬取速度**较慢是正常的（每篇文章/回答约 30 秒），这是为了避免给知乎服务器压力
3. **Cookie 有效期**有限，如果提示需要登录，运行 `./run.sh login` 重新登录
4. **不要最小化浏览器**，不要手动操作爬取窗口
5. **保护隐私**：cookie 文件包含登录信息，注意保密

## 🐛 故障排除

### 驱动权限问题
```bash
chmod +x msedgedriver/msedgedriver
```

### Cookie 失效
```bash
rm cookie/cookie_zhihu.pkl
./run.sh login
```

### 重新安装依赖
```bash
source venv/bin/activate
pip install --trusted-host pypi.tuna.tsinghua.edu.cn -i http://pypi.tuna.tsinghua.edu.cn/simple -r requirement.txt
```

## 📝 示例输出

爬取的文章/回答会保存为如下结构：

```
article/
└── 2023-05-03_18_37_泰勒公式推导方式二_IP_属地上海/
    ├── 泰勒公式推导方式二_formula_.md  # Markdown 格式（含数学公式）
    ├── 泰勒公式推导方式二.pdf           # PDF 格式
    ├── 2023-05-03_18_37・IP_属地上海.txt  # 元信息
    └── 0.jpg, 1.jpg...                  # 图片
```

## 🎯 高级用法

### 自定义参数
```bash
source venv/bin/activate

# 增加爬取间隔到 10 秒
python crawler.py --article --MarkDown --sleep_time 10

# 只爬取已保存的链接列表（不重新获取）
python crawler.py --article --MarkDown
```

### 增量更新
如果发布了新文章但不想重新爬取所有内容：

1. 手动添加新文章链接到 `article/article.txt`
2. 运行：`python crawler.py --article --MarkDown`（不加 `--links_scratch`）

## 🙏 致谢

- 原项目：https://github.com/ZouJiu1/zhihu_spider_selenium
- macOS 适配：2024-12-24

---

**开始使用：** `./run.sh login`
