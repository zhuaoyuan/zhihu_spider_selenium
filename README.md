# 爬取知乎的内容

- 原项目地址：https://github.com/ZouJiu1/zhihu_spider_selenium

2026-01-14对项目做了在mac intel上的适配，支持自定义用户名。其余机型未测试过。

### macOS 环境


**环境要求**

- macOS 系统（已支持 Intel）
- Python 3.x（已配置虚拟环境）
- Microsoft Edge 浏览器（用于自动化爬取）

---

## 快速开始

### macOS 用户

#### 0️⃣ 环境配置
```bash
# 安装edge
brew install --cask microsoft-edge

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级 pip、安装依赖
python -m pip install --upgrade pip
pip install --trusted-host pypi.tuna.tsinghua.edu.cn -i http://pypi.tuna.tsinghua.edu.cn/simple -r requirement.txt

```


#### 1️⃣ 首次登录

```bash
cd path/to/zhihu_spider_selenium
./run.sh login
```

**重要提示：**
- 浏览器会自动打开知乎登录页面
- 手动输入账号密码并登录
- 登录后**不要操作浏览器**，等待程序自动保存 cookie
- 如果提示需要给驱动添加执行权限，按提示运行 `chmod +x` 命令

#### 2️⃣ 开始爬取

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

#### 3️⃣ 查看结果

爬取的内容保存在：
- `article/` - 文章
- `answer/` - 回答
- `think/` - 想法
- `log/` - 运行日志

### Windows 用户

#### 1、登录

运行以下内容，这一步是**手动**操作，需要人工输入账号和密码，然后点击登录就行，登录以后会自动保存好cookie，以后爬取时就不用重复登录了，保存的cookie在这个目录的**cookie**，产生的档案是**cookie_zhihu.pkl**

```bash
python crawler.py
```

运行以后会弹出一个浏览器，自动打开知乎页面以后就可以开始登录，下图所示就是登录页面，两类登录方式都可以，只要能登录就行，**点击登录以后，不要再操作页面，键盘或鼠标都不可以，登录以后查看目录cookie是否保存好cookie_zhihu.pkl，保存好就会开始爬取了。**

<img src="./showimg/login.png" width="29%"/>

---

## 详细使用说明

### 每项单独爬取

爬取一旦开始就自动运行了，爬取窗口一般不能最小化，可以做其他事情的

**爬取知乎想法**

默认的爬取每篇想法的睡眠时间是 **6s*图片的数量** 以上

```bash
python crawler.py --think --links_scratch
```

**爬取知乎回答**

默认的爬取每篇回答的睡眠时间是**16s**以上，这边实际爬取耗时平均是每篇 **30s**每个图片需要6s, --MarkDown控制是否保存markdown格式的网页内容

若是PDF看起来版式太大，调小参数就可以printop.scale，不是特殊情况一般不用调整

```bash
python crawler.py --answer --MarkDown --links_scratch
```

**爬取知乎的article**

默认的爬取每篇article的睡眠时间是**16s**以上，这边实际爬取130多篇，耗时平均是每篇 **33.096s**每个图片需要6s

```bash
python crawler.py --article --MarkDown --links_scratch
```

### 三项一起爬取的

```bash
python crawler.py --think --article --answer --MarkDown --links_scratch
```

### 参数详细解释

- `--links_scratch`：重命名*.txt，然后爬取所有的article链接+标题，或者所有的回答链接+标题。article\article.txt和answer\answers.txt都保存了链接和标题

- `--MarkDown`：保存markdown格式的article或者回答的

- `--think`：是否爬取想法的

- `--article`：是否爬取article的

- `--answer`：是否爬取回答的

所以，爬取所有的article或者回答的链接，需要加--links_scratch，会重命名article.txt或者answers.txt，然后生成answers.txt或者article.txt，并爬取txt的网址

```bash
python crawler.py --think --article --answer --MarkDown --links_scratch
python crawler.py --answer --MarkDown --links_scratch
python crawler.py --article --MarkDown --links_scratch
python crawler.py --think --MarkDown --links_scratch
```

直接爬取当前article.txt或者answers.txt的网址，则需要删除--links_scratch

```bash
python crawler.py --think --article --answer --MarkDown
python crawler.py --answer --MarkDown
python crawler.py --article --MarkDown
python crawler.py --think --MarkDown
```

### 又发布了一篇，只爬取写的这篇

第一次可以全部爬取，等所有article或者回答或者想法都已经爬取好以后，此时若是又写了一篇或者几篇，而且想爬取到本地，可以将**article/article.txt**这个档案重命名到**article/article_2023_06_20.txt**，或者重命名answer.txt，然后将写好的article或者回答的网址和标题按照之前档案的格式再create一个article.txt/answer.txt档案，运行爬取程序就可以了的，**此时需要去掉选项--links_scratch避免爬取所有链接**，想法会跳过已经爬取好的时间，所以可以按照上面的方式运行，此时只会爬取article.txt/answer.txt的网址

<img src="./showimg/add1.png" width="90%"/>

也就是

```bash
python crawler.py --think --article --answer --MarkDown
或者
python crawler.py --answer --MarkDown
或者
python crawler.py --article --MarkDown
或者
python crawler.py --think --MarkDown
```

若是过了很长很长时间，发布了很多篇，此时一篇一篇加入不太方便，可以直接将**article/article.txt**这个档案重命名到**article/article_2023_06_20.txt**，或者重命名answer.txt，然后运行爬取程序即可，**需要加入选项--links_scratch爬取所有链接**，上面提到了已经爬取过的不会重复爬取，所以实际只会爬取最近写好的article或者回答，想法则会直接跳过已经爬取的内容。

### 目录

**think**：该目录存放爬取到的想法内容
**article**：该目录存放article的website以及爬取到的内容
**answer**：该目录存放回答的website以及爬取到的内容

---

## 🚀 快速示例：指定用户爬取

### 场景 1：爬取自己的内容（原有功能）

```bash
cd path/to/zhihu_spider_selenium

# 首次使用，先登录
./run.sh login

# 爬取自己的所有内容
./run.sh all
```

**结果**：爬取你自己的文章、回答、想法，保存到对应目录。

---

### 场景 2：爬取指定用户的文章

#### 步骤 1：找到用户名

假设你想爬取知乎用户"张三"的文章：

1. 访问该用户的知乎主页
2. 查看浏览器地址栏：`https://www.zhihu.com/people/zhang-san-123`
3. 提取用户名：`zhang-san-123`

#### 步骤 2：执行爬取

```bash
cd path/to/zhihu_spider_selenium

# 确保已登录
./run.sh check

# 爬取指定用户的文章
./run.sh article zhang-san-123
```

**输出示例**：
```
============================================================
将爬取指定用户的内容: zhang-san-123
知乎主页: https://www.zhihu.com/people/zhang-san-123
============================================================
```

**结果**：爬取 `zhang-san-123` 的所有公开文章，保存到 `article/` 目录。

---

### 场景 3：爬取多个用户的回答

```bash
cd path/to/zhihu_spider_selenium

# 爬取用户 A 的回答
./run.sh answer zhang-san

# 爬取用户 B 的回答
./run.sh answer li-si

# 爬取用户 C 的回答
./run.sh answer wang-wu
```

**结果**：三个用户的回答都保存在 `answer/` 目录下，按时间和标题自动分类。

---

### 场景 4：爬取知乎大V的所有内容

假设你想爬取某个知乎大V（例如：excited-vczh）的所有内容：

```bash
cd path/to/zhihu_spider_selenium

# 爬取该用户的所有内容（文章+回答+想法）
./run.sh all excited-vczh
```

**结果**：
- `article/` - 该用户的所有文章（Markdown + PDF）
- `answer/` - 该用户的所有回答（Markdown + PDF）  
- `think/` - 该用户的所有想法（文本 + 图片）

---

### 场景 5：使用 Python 命令自定义参数

```bash
cd path/to/zhihu_spider_selenium
source venv/bin/activate

# 爬取指定用户的文章，增加睡眠时间到 10 秒
python crawler.py --article --MarkDown --links_scratch \
                  --target_user zhang-san \
                  --sleep_time 10

# 只爬取指定用户的回答
python crawler.py --answer --MarkDown --links_scratch \
                  --target_user li-si

# 爬取指定用户的所有内容
python crawler.py --think --article --answer --MarkDown --links_scratch \
                  --target_user wang-wu
```

---

### 对比：爬取自己 vs 爬取他人

| 场景 | 命令 | 说明 |
|------|------|------|
| 爬取自己的文章 | `./run.sh article` | 不指定用户名 |
| 爬取张三的文章 | `./run.sh article zhang-san` | 指定用户名 |
| 爬取自己的所有内容 | `./run.sh all` | 不指定用户名 |
| 爬取李四的所有内容 | `./run.sh all li-si` | 指定用户名 |

---

### 实际案例

#### 案例 1：备份知名用户的精华回答

```bash
# 假设你想备份轮子哥（excited-vczh）的回答
./run.sh answer excited-vczh

# 结果：所有回答保存为 Markdown 和 PDF 格式
# 包括数学公式、代码块、图片等
```

#### 案例 2：学习某领域专家的文章

```bash
# 假设你想学习某个领域专家的所有文章
./run.sh article some-expert-name

# 结果：可以离线阅读，方便做笔记和学习
```

#### 案例 3：收藏多个用户的精彩内容

```bash
# 创建批量脚本
cat > crawl_favorite_users.sh << 'EOF'
#!/bin/bash
cd path/to/zhihu_spider_selenium

echo "开始爬取收藏的用户..."

# 用户列表
users=(
    "excited-vczh"
    "magi-elen"
    "another-user"
)

# 依次爬取每个用户的所有内容
for user in "${users[@]}"; do
    echo "=========================================="
    echo "爬取用户: $user"
    echo "=========================================="
    ./run.sh all "$user"
    echo "休息 60 秒..."
    sleep 60
done

echo "全部完成！"
EOF

# 添加执行权限
chmod +x crawl_favorite_users.sh

# 执行批量爬取
./crawl_favorite_users.sh
```

---

### 常见用户名格式

知乎用户名（URL 标识）通常是以下格式之一：

#### 格式 1：中文拼音 + 数字
```
zhang-san-123
li-si-456
wang-wu-789
```

#### 格式 2：英文昵称
```
john-doe
awesome-coder
tech-writer
```

#### 格式 3：随机字符串
```
a1b2c3d4e5f6
user-12ab34cd
zhihu-56ef78gh
```

#### 格式 4：特殊用户（知乎官方、认证用户等）
```
excited-vczh        # 轮子哥
magi-elen          # 知名用户
he-xie-shi         # 知乎编辑
```

---

### 注意事项速查

#### ✅ 可以做的：
- 爬取任何公开主页用户的公开内容
- 同时保存 Markdown 和 PDF 格式
- 批量爬取多个用户
- 自定义爬取参数

#### ❌ 不能做的：
- 爬取私密内容
- 爬取需要关注才能看的内容
- 同时并发爬取多个用户（需要依次爬取）
- 不登录就爬取（会被限制）

#### ⚠️ 注意事项：
1. **必须先登录**（使用自己的账号）
2. **遵守爬取频率**（默认 6 秒间隔）
3. **仅用于个人学习和备份**
4. **不要用于商业用途**

---

## 高级用法

### 自定义参数

如果需要自定义参数，可以直接使用 Python 命令：

```bash
# 激活虚拟环境（macOS）
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
- `--target_user` - 指定要爬取的用户名（不指定则爬取自己的内容）

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

---

## 常见问题

### 问题 1：提示用户不存在

**原因**：用户名错误或用户已注销

**解决**：
1. 重新访问该用户主页，确认 URL 是否正确
2. 确认该用户账号是否还存在

### 问题 2：爬取内容为空

**原因**：
- 该用户没有发布相应类型的内容
- 该用户设置了隐私保护

**解决**：
1. 先用浏览器访问该用户主页，确认是否有内容
2. 检查该用户的隐私设置

### 问题 3：Cookie 失效

**现象**：提示需要登录

**解决**：
```bash
rm cookie/cookie_zhihu.pkl
./run.sh login  # macOS
# 或
python crawler.py  # Windows
```

### 问题 4：浏览器驱动问题

如果提示权限错误（macOS）：
```bash
chmod +x msedgedriver/msedgedriver
```

### 问题 5：网络问题

- 确保网络连接正常
- 爬取时设置了延迟（默认6秒），避免给知乎服务器压力
- 建议在深夜运行，网络较好且避免影响知乎其他用户

### 问题 6：SSL 证书问题

已使用清华镜像源和 HTTP 协议解决，无需额外配置。

### 问题 7：爬取速度

- 想法：每篇约 6秒 × 图片数量
- 回答：每篇约 30 秒
- 文章：每篇约 33 秒

---

## 注意事项

1. **需要较好的网速**，本机网速测验是下载100Mbps，上传60Mbps，低点也可以的，不是太慢太卡就行[https://www.speedtest.cn/](https://www.speedtest.cn/)

2. **爬取时设置了睡眠时间**，避免给知乎服务器带来太大压力，可以日间调试好，然后深夜运行爬取人少，给其他小伙伴更好的用户体验，避免知乎顺着网线过来找人，默认**6**s

3. **若是一直停在登录页面**，可能是之前保存的cookie失效了，需要再次登录保存cookie

4. **遵守知乎服务条款**：仅用于个人备份，不要用于商业用途

5. **保护隐私**：cookie 文件包含登录信息，注意保密

6. **浏览器窗口**：爬取时不要最小化浏览器窗口，不要手动操作

7. **数据备份**：爬取的内容建议定期备份

---

## 目录结构

```
zhihu_spider_selenium/
├── crawler.py          # 主程序
├── run.sh             # 启动脚本（macOS）
├── venv/              # Python 虚拟环境（macOS）
├── msedgedriver/      # 浏览器驱动
├── cookie/            # 保存的 cookie
├── article/           # 爬取的文章
├── answer/            # 爬取的回答
├── think/             # 爬取的想法
└── log/               # 运行日志
```

---

## 验证结果

爬取完成后，检查结果：

```bash
# 查看爬取的文章
ls -lh article/

# 查看爬取的回答
ls -lh answer/

# 查看爬取的想法
ls -lh think/

# 查看运行日志
ls -lt log/
tail -50 log/[最新日志文件]
```

---

## 帮助命令

```bash
# 查看所有可用命令（macOS）
./run.sh

# 查看 Python 参数说明
source venv/bin/activate  # macOS
python crawler.py --help

# 检查登录状态（macOS）
./run.sh check

# 测试环境
source venv/bin/activate  # macOS
python test_env.py
```

---

**开始使用：**

```bash
cd path/to/zhihu_spider_selenium

# 方式 1：爬取自己的内容
./run.sh all

# 方式 2：爬取指定用户的内容
./run.sh all [用户名]
```

🎉 祝使用愉快！
