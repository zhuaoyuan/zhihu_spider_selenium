# 知乎内容爬虫（当前可用版）

本项目用于抓取知乎公开内容，支持：
- 按用户抓取：`pins`、`posts`、`answers`
- 按专栏抓取：`column_id` 下全部文章
- 按时间过滤：仅抓取晚于 `time_begin` 的内容
- 输出为 Markdown，目录结构清晰

当前实现基于 `cookie + Zhihu v4 API`，已替换旧版页面 DOM 抓取逻辑。

---

## 1. 功能概览

- 用户模式：`--user <用户名> --contents <pins/posts/answers...>`
- 专栏模式：`--column-id <专栏ID>`
- 时间过滤：`--time-begin "YYYY-MM-DD [HH:MM[:SS]]"`（可空）
- 进度打印：按分页和写入批次输出进度
- 去重：按内容 `id` 去重，避免重复落盘

---

## 2. 环境要求

- Python 3.10+
- 已安装依赖（见 `requirement.txt`）
- Microsoft Edge（仅 `login` 子命令需要）
- EdgeDriver：默认路径 `msedgedriver/msedgedriver`

安装依赖示例：

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirement.txt
```

---

## 3. 快速开始

### 3.1 首次登录并保存 cookie

```bash
./run.sh login
# 或
venv/bin/python crawler.py login
```

说明：
- 会打开浏览器到知乎登录页
- 手动登录后程序会自动保存 cookie 到 `cookie/cookie_zhihu.pkl`

### 3.2 检查 cookie 是否可用

```bash
./run.sh check
# 或
venv/bin/python crawler.py check-cookie
```

---

## 4. 使用方式

## 4.1 推荐入口（run.sh）

### 用户内容抓取

```bash
./run.sh user <username> <contents...> [--time-begin "YYYY-MM-DD HH:MM:SS"] [--output-dir DIR]
```

示例：

```bash
./run.sh user xi-bi-tang posts answers
./run.sh user xi-bi-tang pins --time-begin "2026-01-01 00:00:00"
```

### 专栏抓取

```bash
./run.sh column <column_id> [--time-begin "YYYY-MM-DD HH:MM:SS"] [--output-dir DIR]
```

示例：

```bash
./run.sh column c_1494255546366226432
./run.sh column c_1494255546366226432 --time-begin "2026-01-01 00:00:00"
```

---

## 4.2 底层入口（crawler.py）

```bash
venv/bin/python crawler.py login
venv/bin/python crawler.py check-cookie

# 用户模式
venv/bin/python crawler.py crawl \
  --user xi-bi-tang \
  --contents pins posts answers \
  --time-begin "2026-01-01 00:00:00" \
  --output-dir data

# 专栏模式
venv/bin/python crawler.py crawl \
  --column-id c_1494255546366226432 \
  --time-begin "2026-01-01 00:00:00" \
  --output-dir data
```

---

## 5. 参数说明

`crawler.py crawl` 参数：

- `--user`：知乎用户名，例如 `xi-bi-tang`
- `--contents`：用户内容类型，可选 `pins` `posts` `answers`（可多选）
- `--column-id`：专栏 ID，例如 `c_1494255546366226432`
- `--time-begin`：仅抓取晚于该时间的内容，默认空（抓全部）
- `--output-dir`：输出根目录，默认 `data`
- `--cookie-path`：cookie 文件路径，默认 `cookie/cookie_zhihu.pkl`

约束：
- `--user` 与 `--column-id` 必须二选一
- 使用 `--user` 时必须传 `--contents`
- 使用 `--column-id` 时不需要 `--contents`

---

## 6. 输出目录结构

默认输出目录为 `data`。

### 用户模式

```text
data/
  xi-bi-tang/
    posts/
      0001_xxx.md
    answers/
      0001_xxx.md
    pins/
      0001_xxx.md
```

### 专栏模式

```text
data/
  宏观洞察/
    0001_xxx.md
    0002_xxx.md
```

说明：专栏目录名默认使用“专栏标题”；若标题不可用则回退为 `column_id`。

每个 Markdown 文件包含：
- 标题
- 元信息（id、url、created、updated）
- 正文内容

---

## 7. 进度输出示例

抓取时会打印类似日志：

```text
[xi-bi-tang/answers] page=1, items=20, saved=0
[xi-bi-tang/answers] page=2, items=20, saved=20
[xi-bi-tang/answers] 已写入 40/419
```

含义：
- `page`：当前分页
- `items`：该页返回条数
- `saved`：当前累计有效条数（去重后）
- `已写入`：落盘进度

---

## 8. 常见问题

### Q1：报 403 / 风控限制怎么办？
- 先执行 `./run.sh check` 确认 cookie 有效
- cookie 失效时重新 `./run.sh login`
- 避免短时间高频重复抓取

### Q2：为什么页面上看到有内容，但抓取结果很少？
- 知乎接口返回与页面展示可能不完全一致
- 若配置了 `--time-begin`，旧内容会被过滤

### Q3：如何只抓最近内容？
- 使用 `--time-begin`，例如：

```bash
./run.sh user xi-bi-tang posts answers --time-begin "2026-03-01 00:00:00"
```

---

## 9. 合规与使用建议

- 请仅抓取你有权访问的公开内容
- 请遵守目标网站服务条款与当地法律法规
- 建议控制频率，避免对目标服务造成压力

---

## 10. 变更说明（相对旧版）

- 已移除旧版 `--think/--article/--answer` 风格参数
- 已移除旧版按页面 DOM 大量解析的主流程
- 统一为子命令模式：`login` / `check-cookie` / `crawl`
- `run.sh` 同步改为新接口
