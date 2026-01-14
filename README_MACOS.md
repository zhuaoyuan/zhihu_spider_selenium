# 知乎爬虫 macOS 使用指南

## 项目简介

这是一个用于爬取知乎个人主页的工具，可以保存：
- **想法（Pins）**：保存为文本和图片
- **文章（Articles）**：保存为 Markdown 和 PDF，包含数学公式、代码和图片
- **回答（Answers）**：保存为 Markdown 和 PDF，包含数学公式、代码和图片

## 环境要求

- macOS 系统（已支持 Intel 和 M1/M2 芯片）
- Python 3.x（已配置虚拟环境）
- Microsoft Edge 浏览器（用于自动化爬取）

## 已完成的配置

✅ Python 虚拟环境已创建  
✅ 依赖包已安装（numpy, selenium, beautifulsoup4）  
✅ 启动脚本已创建  
✅ 代码已修复（去除硬编码配置）  

## 使用步骤

### 1. 安装 Microsoft Edge 浏览器

如果还没有安装 Edge 浏览器，请先安装：

```bash
# 使用 Homebrew 安装
brew install --cask microsoft-edge

# 或者访问官网下载
# https://www.microsoft.com/edge
```

### 2. 首次登录（必须）

首次使用需要登录知乎并保存 cookie：

```bash
./run.sh login
```

运行后会：
1. 自动下载适合您系统的浏览器驱动
2. 打开 Edge 浏览器并跳转到知乎登录页面
3. **手动输入账号密码并登录**
4. 登录成功后，**不要操作浏览器**，程序会自动保存 cookie
5. Cookie 保存后会自动开始检查环境

**注意**：
- 如果驱动下载后提示需要授权，请按照提示执行 `chmod +x` 命令
- 登录时可以选择密码登录或短信登录
- 登录后看到 cookie_zhihu.pkl 文件表示成功

### 3. 开始爬取

登录成功后，可以选择爬取不同的内容：

#### 爬取文章
```bash
./run.sh article
```

#### 爬取回答
```bash
./run.sh answer
```

#### 爬取想法
```bash
./run.sh think
```

#### 爬取所有内容
```bash
./run.sh all
```

### 4. 查看结果

爬取的内容会保存在以下目录：

- `article/` - 文章内容（Markdown 和 PDF）
- `answer/` - 回答内容（Markdown 和 PDF）
- `think/` - 想法内容（文本和图片）
- `log/` - 运行日志

每个目录下会按照日期和标题创建子目录，包含：
- PDF 文件
- Markdown 文件（带 `_formula_` 后缀，支持数学公式）
- 图片文件（编号为 0.jpg, 1.jpg...）
- 时间和 IP 属地信息文本文件

## 高级用法

### 自定义参数

如果需要自定义参数，可以直接使用 Python 命令：

```bash
# 激活虚拟环境
source venv/bin/activate

# 自定义睡眠时间（默认6秒）
python crawler.py --article --MarkDown --sleep_time 10

# 不重新爬取链接（使用已保存的 article.txt 或 answers.txt）
python crawler.py --article --MarkDown

# 查看所有参数
python crawler.py --help
```

### 参数说明

- `--think` - 爬取想法
- `--article` - 爬取文章
- `--answer` - 爬取回答
- `--MarkDown` - 保存 Markdown 格式
- `--links_scratch` - 重新爬取所有链接
- `--sleep_time` - 设置爬取间隔时间（秒），默认 6 秒
- `--computer_time_sleep` - 电脑运行速度的延迟时间，默认 0

### 增量爬取

如果已经爬取过，又发布了新内容：

1. **少量新内容**：手动编辑 `article/article.txt` 或 `answer/answers.txt`，添加新链接，然后运行：
   ```bash
   source venv/bin/activate
   python crawler.py --article --MarkDown  # 不加 --links_scratch
   ```

2. **大量新内容**：重命名旧的 txt 文件，让程序重新爬取所有链接：
   ```bash
   mv article/article.txt article/article_backup.txt
   ./run.sh article  # 会自动跳过已爬取的内容
   ```

## 常见问题

### 1. 浏览器驱动问题

如果提示权限错误：
```bash
chmod +x msedgedriver/msedgedriver
```

### 2. Cookie 失效

如果爬取时提示需要登录，说明 cookie 已失效：
```bash
rm cookie/cookie_zhihu.pkl
./run.sh login  # 重新登录
```

### 3. 网络问题

- 确保网络连接正常
- 爬取时设置了延迟（默认6秒），避免给知乎服务器压力
- 建议在深夜运行，网络较好且避免影响知乎其他用户

### 4. SSL 证书问题

已使用清华镜像源和 HTTP 协议解决，无需额外配置。

### 5. 爬取速度

- 想法：每篇约 6秒 × 图片数量
- 回答：每篇约 30 秒
- 文章：每篇约 33 秒

## 注意事项

1. **遵守知乎服务条款**：仅用于个人备份，不要用于商业用途
2. **控制爬取频率**：默认延迟 6 秒，避免给服务器压力
3. **保护隐私**：cookie 文件包含登录信息，注意保密
4. **浏览器窗口**：爬取时不要最小化浏览器窗口，不要手动操作
5. **数据备份**：爬取的内容建议定期备份

## 目录结构

```
zhihu_spider_selenium/
├── crawler.py          # 主程序
├── run.sh             # 启动脚本
├── venv/              # Python 虚拟环境
├── msedgedriver/      # 浏览器驱动
├── cookie/            # 保存的 cookie
├── article/           # 爬取的文章
├── answer/            # 爬取的回答
├── think/             # 爬取的想法
└── log/               # 运行日志
```

## 技术支持

- 原项目地址：https://github.com/ZouJiu1/zhihu_spider_selenium
- 更新日志：2024-12-24 添加 macOS 支持

## 更新说明

本版本已针对 macOS 进行优化：
- ✅ 支持 Intel 芯片 Mac
- ✅ 支持 M1/M2 芯片 Mac（Apple Silicon）
- ✅ 自动下载适配的浏览器驱动
- ✅ 修复证书验证问题
- ✅ 优化安装流程
