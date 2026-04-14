# 项目命令列表

本文档汇总本仓库内常用入口与参数，与 `README.md` 一致处不再赘述细节。

---

## 环境与依赖

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirement.txt
```

前置说明：

- Python 3.10+
- `login` 子命令需要 Microsoft Edge，以及仓库默认路径下的 EdgeDriver：`msedgedriver/msedgedriver`
- Cookie 默认保存路径：`cookie/cookie_zhihu.pkl`

---

## 推荐入口：`./run.sh`

脚本使用 `venv/bin/python`；若虚拟环境不存在会先报错退出。

| 命令 | 说明 |
|------|------|
| `./run.sh login` | 打开浏览器手动登录知乎并保存 cookie |
| `./run.sh check` | 检查 cookie 是否可用（内部调用 `crawler.py check-cookie`） |
| `./run.sh update-data [--output-dir DIR]` | 扫描 `data/user` 与 `data/column`，按目录内最近日期增量抓取 |
| `./run.sh user <username> <contents...> [--time-begin "YYYY-MM-DD [HH:MM[:SS]]"] [--output-dir DIR]` | 抓取用户内容；`contents` 为 `pins` / `posts` / `answers` 的一个或多个 |
| `./run.sh column <column_id> [--time-begin "..."] [--output-dir DIR]` | 抓取专栏文章 |
| `./run.sh` 或未知子命令 | 打印用法并退出（非 0） |

示例：

```bash
./run.sh login
./run.sh check
./run.sh update-data
./run.sh update-data --output-dir data

./run.sh user xi-bi-tang posts answers
./run.sh user xi-bi-tang pins --time-begin "2026-01-01 00:00:00"

./run.sh column c_1494255546366226432
./run.sh column c_1494255546366226432 --time-begin "2026-01-01 00:00:00"
```

---

## 底层入口：`venv/bin/python crawler.py`

子命令一览：

| 子命令 | 作用 |
|--------|------|
| `login` | 浏览器登录并保存 cookie |
| `check-cookie` | 请求轻量接口验证 cookie |
| `update-data` | 批量增量更新 `data` 下已有用户与专栏 |
| `crawl` | 单次抓取（用户或专栏二选一） |
| （未指定子命令） | 打印帮助，退出码 1 |

### `login`

```bash
venv/bin/python crawler.py login \
  [--driver-path msedgedriver/msedgedriver] \
  [--cookie-path cookie/cookie_zhihu.pkl] \
  [--wait-seconds 600]
```

### `check-cookie`

```bash
venv/bin/python crawler.py check-cookie [--cookie-path cookie/cookie_zhihu.pkl]
```

### `update-data`

```bash
venv/bin/python crawler.py update-data \
  [--cookie-path cookie/cookie_zhihu.pkl] \
  [--output-dir data]
```

### `crawl`

```bash
# 用户模式（必须同时提供 --user 与 --contents）
venv/bin/python crawler.py crawl \
  --user <用户名> \
  --contents pins posts answers \
  [--time-begin "YYYY-MM-DD [HH:MM[:SS]]"] \
  [--output-dir data] \
  [--cookie-path cookie/cookie_zhihu.pkl]

# 专栏模式（提供 --column-id，不要传 --contents）
venv/bin/python crawler.py crawl \
  --column-id <专栏ID，如 c_1494255546366226432> \
  [--time-begin "..."] \
  [--output-dir data] \
  [--cookie-path cookie/cookie_zhihu.pkl]
```

约束：

- `--user` 与 `--column-id` 必须且只能选一个
- 用户模式必须带 `--contents`（可选值：`pins`、`posts`、`answers`，可多选）
- 专栏模式不要带 `--contents`

---

## 辅助脚本：`scripts/copy_newest_md.py`

将 `data/column` 与 `data/user` 下、文件名以 `YYYYMMDD_` 开头且日期 **大于等于** 起始日的 `.md` 复制到扁平目录 `data/newest_{起始}_{实际最大日期}/`。

```bash
python3 scripts/copy_newest_md.py <fromdate> [--data-root data] [--dry-run]
```

- `fromdate`：起始日期，格式 `YYYYMMDD`（含当天）
- `--data-root`：数据根目录，默认 `data`
- `--dry-run`：只打印将要复制的路径，不实际复制

示例：

```bash
python3 scripts/copy_newest_md.py 20260323
python3 scripts/copy_newest_md.py 20260323 --data-root data --dry-run
```

---

## 对照说明

- `./run.sh check` 等价于 `venv/bin/python crawler.py check-cookie`
- `./run.sh user` / `column` / `update-data` 只是把参数转给 `crawler.py crawl` 或 `update-data`

本仓库主流程以 `crawler.py` 与 `run.sh` 为准；`msedgedriver/` 下的历史副本脚本不作为标准入口列出。
