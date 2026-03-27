#!/usr/bin/env python3
"""Zhihu crawler (user posts/answers/pins + column articles)."""

from __future__ import annotations

import argparse
import html
import json
import os
import pickle
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver import EdgeOptions


BASE_DIR = Path(__file__).resolve().parent
COOKIE_PATH = BASE_DIR / "cookie" / "cookie_zhihu.pkl"
DEFAULT_OUTPUT_DIR = BASE_DIR / "data"
USER_GROUP_DIR = "user"
COLUMN_GROUP_DIR = "column"
DEFAULT_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)


@dataclass
class CrawlItem:
    id: str
    title: str
    url: str
    created_ts: int | None
    updated_ts: int | None
    html_content: str
    raw: dict


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def sanitize_filename(name: str, max_len: int = 120) -> str:
    text = re.sub(r"[\\/:*?\"<>|\n\r\t]+", "_", name).strip(" .")
    text = re.sub(r"\s+", " ", text)
    if not text:
        text = "untitled"
    return text[:max_len].rstrip(" .")


def ts_to_iso(ts: int | None) -> str:
    if not ts:
        return ""
    return datetime.fromtimestamp(ts).isoformat(timespec="seconds")


def normalize_timestamp(value) -> int | None:
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def ts_to_yyyymmdd(ts: int | None) -> str:
    if not ts:
        return ""
    return datetime.fromtimestamp(ts).strftime("%Y%m%d")


def pick_item_date_prefix(item: CrawlItem) -> str:
    prefix = ts_to_yyyymmdd(item.created_ts) or ts_to_yyyymmdd(item.updated_ts)
    if prefix:
        return prefix
    return datetime.now().strftime("%Y%m%d")


def parse_time_begin(value: str | None) -> datetime | None:
    if not value:
        return None
    value = value.strip()
    fmts = [
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d",
        "%Y/%m/%d %H:%M",
        "%Y/%m/%d %H:%M:%S",
    ]
    for fmt in fmts:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"无法解析 time_begin: {value}") from exc


def load_cookie_from_pickle(cookie_path: Path) -> list[dict]:
    if not cookie_path.exists():
        raise FileNotFoundError(f"cookie 不存在: {cookie_path}")
    with cookie_path.open("rb") as f:
        return pickle.load(f)


def build_session(cookie_path: Path, user_agent: str = DEFAULT_UA) -> requests.Session:
    cookies = load_cookie_from_pickle(cookie_path)
    sess = requests.Session()
    sess.headers.update(
        {
            "User-Agent": user_agent,
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://www.zhihu.com/",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
    )
    for c in cookies:
        name = c.get("name")
        value = c.get("value")
        if not name:
            continue
        sess.cookies.set(
            name,
            value,
            domain=c.get("domain"),
            path=c.get("path", "/"),
        )
    return sess


def setup_edge(driver_path: str, headless: bool = False) -> webdriver.Edge:
    service = Service(executable_path=driver_path)
    options = EdgeOptions()
    options.add_argument("lang=zh-CN,zh,en-US,en")
    options.add_argument("disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    if headless:
        options.add_argument("--headless=new")
    driver = webdriver.Edge(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver


def save_cookie(driver: webdriver.Edge, path: Path) -> None:
    ensure_dir(path.parent)
    with path.open("wb") as f:
        pickle.dump(driver.get_cookies(), f)


def login_and_save_cookie(driver_path: str, cookie_path: Path, wait_seconds: int = 600) -> None:
    driver = setup_edge(driver_path=driver_path, headless=False)
    try:
        driver.get("https://www.zhihu.com/")
        print("请在浏览器中完成登录。登录成功后不要手动关闭窗口。")
        deadline = time.time() + wait_seconds
        while time.time() < deadline:
            if driver.find_elements(By.CSS_SELECTOR, "#Popover15-toggle"):
                save_cookie(driver, cookie_path)
                print(f"登录 cookie 已保存: {cookie_path}")
                return
            time.sleep(3)
        raise TimeoutError("等待登录超时，请重试。")
    finally:
        driver.quit()


def html_to_markdown(fragment: str) -> str:
    if not fragment:
        return ""
    soup = BeautifulSoup(fragment, "html.parser")

    for br in soup.find_all("br"):
        br.replace_with("\n")

    for a in soup.find_all("a"):
        href = a.get("href") or ""
        text = a.get_text(" ", strip=True) or href
        a.replace_with(f"[{text}]({href})")

    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-original") or ""
        alt = img.get("alt") or "image"
        img.replace_with(f"\n![{alt}]({src})\n")

    lines: list[str] = []
    for node in soup.contents:
        if getattr(node, "name", None) in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            level = int(node.name[1])
            lines.append(f"{'#' * level} {node.get_text(' ', strip=True)}")
        elif getattr(node, "name", None) in {"p", "div", "li", "blockquote"}:
            txt = node.get_text(" ", strip=True)
            if txt:
                lines.append(txt)
        else:
            txt = str(node).strip()
            if txt:
                lines.append(BeautifulSoup(txt, "html.parser").get_text(" ", strip=True))

    out = "\n\n".join(line for line in lines if line)
    out = html.unescape(out)
    out = re.sub(r"\n{3,}", "\n\n", out)
    return out.strip()


def pin_content_to_markdown(pin: dict) -> str:
    parts: list[str] = []
    for block in pin.get("content") or []:
        btype = block.get("type")
        if btype == "text":
            text_html = block.get("content") or block.get("own_text") or ""
            text = html_to_markdown(text_html)
            if text:
                parts.append(text)
        elif btype == "image":
            url = block.get("original_url") or block.get("url")
            if url:
                parts.append(f"![]({url})")
    return "\n\n".join(parts).strip()


def request_json(session: requests.Session, url: str) -> dict:
    r = session.get(url, timeout=20)
    if r.status_code != 200:
        raise RuntimeError(f"请求失败 {r.status_code}: {url}\n{r.text[:300]}")
    obj = r.json()
    if isinstance(obj, dict) and obj.get("error"):
        raise RuntimeError(f"接口返回错误: {json.dumps(obj['error'], ensure_ascii=False)}")
    return obj


def should_keep(item_dt: datetime | None, time_begin: datetime | None) -> bool:
    if time_begin is None:
        return True
    if item_dt is None:
        return True
    return item_dt > time_begin


def pick_title_from_html(content: str, max_len: int = 60) -> str:
    if not content:
        return ""
    soup = BeautifulSoup(content, "html.parser")
    for tag in ["h1", "h2", "h3", "p", "div"]:
        for node in soup.find_all(tag):
            text = node.get_text(" ", strip=True)
            if text:
                return text[:max_len]
    text = soup.get_text(" ", strip=True)
    return text[:max_len] if text else ""


def is_bad_title(title: str) -> bool:
    if not title:
        return True
    text = title.strip()
    if not text:
        return True
    if re.fullmatch(r"\d+", text):
        return True
    if re.fullmatch(r"article[_-]?\d+", text, flags=re.IGNORECASE):
        return True
    return False


def normalize_answer(item: dict) -> CrawlItem:
    answer_id = str(item.get("id"))
    q_title = (item.get("question") or {}).get("title") or "untitled_answer"
    title = f"{q_title} - answer_{answer_id}"
    url = (item.get("url") or "").replace("api/v4/answers", "question")
    if "/question/" in url and "/answer/" not in url:
        url = f"https://www.zhihu.com/question/{(item.get('question') or {}).get('id', '')}/answer/{answer_id}"
    created = normalize_timestamp(item.get("created_time"))
    updated = normalize_timestamp(item.get("updated_time"))
    return CrawlItem(
        id=answer_id,
        title=title,
        url=url,
        created_ts=created,
        updated_ts=updated,
        html_content=item.get("content") or "",
        raw=item,
    )


def normalize_article(item: dict) -> CrawlItem:
    article_obj = item.get("article") if isinstance(item.get("article"), dict) else {}
    target_obj = item.get("target") if isinstance(item.get("target"), dict) else {}
    source = article_obj or target_obj or item

    article_id = str(
        source.get("id")
        or item.get("id")
        or target_obj.get("id")
        or article_obj.get("id")
        or ""
    ).strip()

    raw_title = str(
        source.get("title")
        or item.get("title")
        or source.get("excerpt_title")
        or item.get("excerpt_title")
        or ""
    ).strip()
    title = raw_title
    if is_bad_title(title):
        title = str(source.get("excerpt_title") or item.get("excerpt_title") or "").strip()
    if is_bad_title(title):
        title = pick_title_from_html(str(source.get("content") or item.get("content") or ""))
    if is_bad_title(title):
        title = str(source.get("excerpt") or item.get("excerpt") or "").strip()[:60]
    if is_bad_title(title):
        title = f"article_{article_id}"

    url = str(
        source.get("url")
        or item.get("url")
        or source.get("share_url")
        or item.get("share_url")
        or ""
    ).strip()
    if not url and article_id:
        url = f"https://zhuanlan.zhihu.com/p/{article_id}"

    created = normalize_timestamp(
        (
        source.get("created")
        or item.get("created")
        or source.get("created_time")
        or item.get("created_time")
        )
    )
    updated = normalize_timestamp(
        (
        source.get("updated")
        or item.get("updated")
        or source.get("updated_time")
        or item.get("updated_time")
        )
    )

    return CrawlItem(
        id=article_id,
        title=title,
        url=url,
        created_ts=created,
        updated_ts=updated,
        html_content=source.get("content") or item.get("content") or "",
        raw=item,
    )


def normalize_pin(item: dict) -> CrawlItem:
    pin_id = str(item.get("id"))
    title = item.get("excerpt_title") or f"pin_{pin_id}"
    url = item.get("url") or f"/pins/{pin_id}"
    if url.startswith("/"):
        url = f"https://www.zhihu.com{url}"
    return CrawlItem(
        id=pin_id,
        title=title,
        url=url,
        created_ts=normalize_timestamp(item.get("created")),
        updated_ts=normalize_timestamp(item.get("updated")),
        html_content=pin_content_to_markdown(item),
        raw=item,
    )


def fetch_paginated(
    session: requests.Session,
    first_url: str,
    normalizer,
    time_begin: datetime | None,
    progress_label: str,
) -> list[CrawlItem]:
    url = first_url
    out: list[CrawlItem] = []
    seen_ids: set[str] = set()
    page = 0
    while url:
        page += 1
        obj = request_json(session, url)
        data = obj.get("data") or []
        paging = obj.get("paging") or {}

        print(f"[{progress_label}] page={page}, items={len(data)}, saved={len(out)}")

        stop_due_time = False
        for raw in data:
            item = normalizer(raw)
            if item.id in seen_ids:
                continue
            item_dt = datetime.fromtimestamp(item.created_ts) if item.created_ts else None
            if not should_keep(item_dt, time_begin):
                stop_due_time = True
                continue
            seen_ids.add(item.id)
            out.append(item)

        next_url = paging.get("next")
        is_end = bool(paging.get("is_end"))

        if stop_due_time:
            print(f"[{progress_label}] 命中 time_begin，停止翻页。")
            break
        if is_end or not next_url:
            break
        url = next_url.replace("http://", "https://")
        time.sleep(0.4)
    return out


def render_item_md(item: CrawlItem) -> str:
    content = item.html_content
    if "<" in content and ">" in content:
        body = html_to_markdown(content)
    else:
        body = content.strip()

    meta = [
        f"# {item.title}",
        "",
        f"- id: {item.id}",
        f"- url: {item.url}",
        f"- created: {ts_to_iso(item.created_ts)}",
        f"- updated: {ts_to_iso(item.updated_ts)}",
        "",
        "---",
        "",
        body,
        "",
    ]
    return "\n".join(meta)


def build_item_filename(item: CrawlItem) -> str:
    date_prefix = pick_item_date_prefix(item)
    safe = sanitize_filename(item.title)
    return f"{date_prefix}_{safe}_{item.id}.md"


def parse_md_meta(path: Path) -> dict[str, str]:
    meta: dict[str, str] = {}
    try:
        with path.open("r", encoding="utf-8") as f:
            for _ in range(40):
                line = f.readline()
                if not line:
                    break
                line = line.strip()
                if line == "---":
                    break
                m = re.match(r"^-?\s*(id|url|created|updated)\s*:\s*(.*)$", line)
                if m:
                    meta[m.group(1)] = m.group(2).strip()
    except Exception:
        return meta
    return meta


def extract_id_from_filename(path: Path) -> str | None:
    m = re.search(r"_([A-Za-z0-9-]+)\.md$", path.name)
    if not m:
        return None
    return m.group(1)


def extract_date_iso_from_filename(path: Path) -> str:
    m = re.match(r"^(20\d{6})_", path.name)
    if not m:
        return ""
    try:
        dt = datetime.strptime(m.group(1), "%Y%m%d")
    except ValueError:
        return ""
    return dt.isoformat(timespec="seconds")


def infer_item_url_from_path(path: Path, item_id: str) -> str:
    if not item_id:
        return ""
    parts = path.parts
    if "column" in parts:
        return f"https://zhuanlan.zhihu.com/p/{item_id}"
    if "user" in parts:
        if "posts" in parts:
            return f"https://zhuanlan.zhihu.com/p/{item_id}"
        if "pins" in parts:
            return f"https://www.zhihu.com/pin/{item_id}"
        if "answers" in parts:
            return f"https://www.zhihu.com/answer/{item_id}"
    return ""


def parse_dt_loose(value: str) -> datetime | None:
    if not value:
        return None
    text = value.strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        pass
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y/%m/%d %H:%M:%S", "%Y/%m/%d"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def backfill_md_meta_file(path: Path) -> bool:
    try:
        raw = path.read_text(encoding="utf-8")
    except Exception:
        return False

    lines = raw.splitlines()
    if not lines:
        return False

    title = ""
    first = lines[0].strip()
    if first.startswith("# "):
        title = first[2:].strip()
    if not title:
        title = path.stem

    split_idx = None
    for i, line in enumerate(lines):
        if line.strip() == "---":
            split_idx = i
            break
    if split_idx is None:
        return False

    meta = parse_md_meta(path)
    item_id = meta.get("id", "").strip() or (extract_id_from_filename(path) or "")
    created = meta.get("created", "").strip() or extract_date_iso_from_filename(path)
    updated = meta.get("updated", "").strip() or created
    url = meta.get("url", "").strip() or infer_item_url_from_path(path, item_id)

    body_lines = lines[split_idx + 1 :]
    while body_lines and not body_lines[0].strip():
        body_lines = body_lines[1:]
    body = "\n".join(body_lines).rstrip()

    rebuilt = "\n".join(
        [
            f"# {title}",
            "",
            f"- id: {item_id}",
            f"- url: {url}",
            f"- created: {created}",
            f"- updated: {updated}",
            "",
            "---",
            "",
            body,
            "",
        ]
    )
    if rebuilt == raw:
        return False
    path.write_text(rebuilt, encoding="utf-8")
    return True


def backfill_md_meta_dir(dir_path: Path) -> int:
    fixed = 0
    for path in dir_path.glob("*.md"):
        if backfill_md_meta_file(path):
            fixed += 1
    return fixed


def fetch_user_identity(session: requests.Session, user_ref: str) -> tuple[str, str]:
    obj = request_json(session, f"https://www.zhihu.com/api/v4/members/{user_ref}")
    url_token = str(obj.get("url_token") or "").strip()
    display_name = str(obj.get("name") or "").strip()
    if not url_token or not display_name:
        raise RuntimeError(f"无法识别用户身份: {user_ref}")
    return url_token, display_name


def format_user_dir_name(display_name: str, url_token: str) -> str:
    safe_display_name = sanitize_filename(display_name)
    return f"{safe_display_name}_{url_token}"


def parse_user_dir_name(name: str) -> tuple[str | None, str | None]:
    if "_" not in name:
        return None, None
    display_name, url_token = name.rsplit("_", 1)
    if not display_name or not url_token:
        return None, None
    return display_name, url_token


def build_existing_id_index(output_dir: Path) -> dict[str, Path]:
    out: dict[str, Path] = {}
    for path in output_dir.glob("*.md"):
        iid = extract_id_from_filename(path)
        if iid:
            out[iid] = path
            continue
        meta = parse_md_meta(path)
        iid = (meta.get("id") or "").strip()
        if iid:
            out[iid] = path
    return out


def dump_item_md(item: CrawlItem, output_dir: Path, existing_by_id: dict[str, Path]) -> Path:
    filename = build_item_filename(item)
    path = output_dir / filename
    path.write_text(render_item_md(item), encoding="utf-8")
    old_path = existing_by_id.get(item.id)
    if old_path and old_path != path and old_path.exists():
        old_path.unlink()
    existing_by_id[item.id] = path
    return path


def write_items(items: list[CrawlItem], out_dir: Path, progress_label: str) -> None:
    ensure_dir(out_dir)
    existing_by_id = build_existing_id_index(out_dir)
    for idx, item in enumerate(items, start=1):
        dump_item_md(item, out_dir, existing_by_id)
        if idx % 10 == 0 or idx == len(items):
            print(f"[{progress_label}] 已写入 {idx}/{len(items)}")


def parse_column_dir_name(name: str) -> tuple[str, str | None]:
    m = re.match(r"^(.*)_((?:c|p)_\d+)$", name)
    if not m:
        return name, None
    return m.group(1), m.group(2)


def format_column_dir_name(column_title: str, column_id: str) -> str:
    safe_title = sanitize_filename(column_title) if column_title else column_id
    if safe_title.endswith(f"_{column_id}"):
        return safe_title
    return f"{safe_title}_{column_id}"


def extract_latest_date_from_filenames(dir_path: Path) -> datetime | None:
    latest: datetime | None = None
    for path in dir_path.glob("*.md"):
        m = re.match(r"^(20\d{6})_", path.name)
        if not m:
            continue
        try:
            dt = datetime.strptime(m.group(1), "%Y%m%d")
        except ValueError:
            continue
        if latest is None or dt > latest:
            latest = dt
    return latest


def latest_created_from_dir(dir_path: Path) -> datetime | None:
    latest: datetime | None = None
    for path in dir_path.glob("*.md"):
        meta = parse_md_meta(path)
        dt = parse_dt_loose(meta.get("created", "")) or parse_dt_loose(meta.get("updated", ""))
        if dt is None:
            continue
        if latest is None or dt > latest:
            latest = dt
    if latest is not None:
        return latest
    return extract_latest_date_from_filenames(dir_path)


def crawl_user(
    session: requests.Session,
    username: str,
    contents: Iterable[str],
    output_root: Path,
    time_begin: datetime | None,
) -> None:
    url_token, display_name = fetch_user_identity(session=session, user_ref=username)
    user_dir_name = format_user_dir_name(display_name, url_token)

    spec = {
        "answers": {
            "url": f"https://www.zhihu.com/api/v4/members/{url_token}/answers?limit=20&offset=0&include=data[*].content,question",
            "normalizer": normalize_answer,
            "subdir": "answers",
        },
        "posts": {
            "url": f"https://www.zhihu.com/api/v4/members/{url_token}/articles?limit=20&offset=0&include=data[*].content",
            "normalizer": normalize_article,
            "subdir": "posts",
        },
        "pins": {
            "url": f"https://www.zhihu.com/api/v4/members/{url_token}/pins?limit=20&offset=0",
            "normalizer": normalize_pin,
            "subdir": "pins",
        },
    }

    for content_type in contents:
        cfg = spec[content_type]
        items = fetch_paginated(
            session=session,
            first_url=cfg["url"],
            normalizer=cfg["normalizer"],
            time_begin=time_begin,
            progress_label=f"{url_token}/{content_type}",
        )
        out_dir = output_root / USER_GROUP_DIR / user_dir_name / cfg["subdir"]
        write_items(items, out_dir, f"{url_token}/{content_type}")
        print(f"[{url_token}/{content_type}] 完成，文件数: {len(items)}，目录: {out_dir}")


def crawl_column(
    session: requests.Session,
    column_id: str,
    output_root: Path,
    time_begin: datetime | None,
) -> None:
    column_meta_url = f"https://www.zhihu.com/api/v4/columns/{column_id}"
    column_meta = request_json(session, column_meta_url)
    column_title = (column_meta.get("title") or "").strip()
    column_dir_name = format_column_dir_name(column_title, column_id)

    url = f"https://www.zhihu.com/api/v4/columns/{column_id}/items?limit=20&offset=0"
    items = fetch_paginated(
        session=session,
        first_url=url,
        normalizer=normalize_article,
        time_begin=time_begin,
        progress_label=f"column/{column_title or column_id}",
    )
    out_dir = output_root / COLUMN_GROUP_DIR / column_dir_name
    write_items(items, out_dir, f"column/{column_title or column_id}")
    print(f"[column/{column_title or column_id}] 完成，文件数: {len(items)}，目录: {out_dir}")


def update_all_data(session: requests.Session, output_root: Path) -> None:
    if not output_root.exists():
        print(f"输出目录不存在，跳过: {output_root}")
        return

    user_root = output_root / USER_GROUP_DIR
    column_root = output_root / COLUMN_GROUP_DIR

    if user_root.exists():
        for user_dir in sorted(p for p in user_root.iterdir() if p.is_dir()):
            display_name, url_token = parse_user_dir_name(user_dir.name)
            if not display_name or not url_token:
                print(f"[update] 跳过用户目录（目录名应为 displayname_urltoken）: {user_dir}")
                continue
            content_subdirs = [kind for kind in ("pins", "posts", "answers") if (user_dir / kind).is_dir()]
            for kind in content_subdirs:
                subdir = user_dir / kind
                fixed = backfill_md_meta_dir(subdir)
                if fixed:
                    print(f"[repair] user={display_name}, content={kind}, 已修复元数据文件: {fixed}")
                latest_dt = latest_created_from_dir(subdir)
                time_begin = latest_dt if latest_dt else None
                time_begin_text = time_begin.strftime("%Y-%m-%d %H:%M:%S") if time_begin else "None"
                print(f"[update] user={display_name}, token={url_token}, content={kind}, time_begin={time_begin_text}")
                crawl_user(
                    session=session,
                    username=url_token,
                    contents=[kind],
                    output_root=output_root,
                    time_begin=time_begin,
                )

    if column_root.exists():
        for col_dir in sorted(p for p in column_root.iterdir() if p.is_dir()):
            title_part, column_id = parse_column_dir_name(col_dir.name)
            if not column_id:
                print(f"[update] 跳过专栏目录（目录名未包含 column_id）: {col_dir}")
                continue
            fixed = backfill_md_meta_dir(col_dir)
            if fixed:
                print(f"[repair] column={title_part}, column_id={column_id}, 已修复元数据文件: {fixed}")
            latest_dt = latest_created_from_dir(col_dir)
            time_begin = latest_dt if latest_dt else None
            time_begin_text = time_begin.strftime("%Y-%m-%d %H:%M:%S") if time_begin else "None"
            print(f"[update] column={title_part}, column_id={column_id}, time_begin={time_begin_text}")
            crawl_column(
                session=session,
                column_id=column_id,
                output_root=output_root,
                time_begin=time_begin,
            )

    if not user_root.exists() and not column_root.exists():
        print(f"[update] 未发现 {USER_GROUP_DIR}/ 或 {COLUMN_GROUP_DIR}/ 目录: {output_root}")
        print("[update] 请先按新目录结构整理数据后再执行批量更新。")
        return


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="知乎内容爬虫（用户内容 / 专栏）")
    sub = parser.add_subparsers(dest="command")

    p_login = sub.add_parser("login", help="打开浏览器手动登录并保存 cookie")
    p_login.add_argument("--driver-path", default=str(BASE_DIR / "msedgedriver" / "msedgedriver"))
    p_login.add_argument("--cookie-path", default=str(COOKIE_PATH))
    p_login.add_argument("--wait-seconds", type=int, default=600)

    p_crawl = sub.add_parser("crawl", help="执行爬取")
    p_crawl.add_argument("--user", help="知乎用户名，例如 xi-bi-tang")
    p_crawl.add_argument("--contents", nargs="+", choices=["pins", "posts", "answers"], help="用户内容类型")
    p_crawl.add_argument("--column-id", help="专栏 id，例如 c_1494255546366226432")
    p_crawl.add_argument("--time-begin", default="", help="仅保留晚于该时间的内容")
    p_crawl.add_argument("--cookie-path", default=str(COOKIE_PATH))
    p_crawl.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))

    p_check = sub.add_parser("check-cookie", help="检查 cookie 是否可用（请求一个轻量接口）")
    p_check.add_argument("--cookie-path", default=str(COOKIE_PATH))

    p_update = sub.add_parser("update-data", help="扫描 data 目录并按最近日期增量更新全部内容")
    p_update.add_argument("--cookie-path", default=str(COOKIE_PATH))
    p_update.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))

    return parser


def validate_crawl_args(args: argparse.Namespace) -> None:
    has_user = bool(args.user)
    has_column = bool(args.column_id)
    if has_user == has_column:
        raise ValueError("crawl 模式下必须且只能传入 --user 或 --column-id 其中之一")
    if has_user and not args.contents:
        raise ValueError("使用 --user 时必须传入 --contents")
    if has_column and args.contents:
        raise ValueError("使用 --column-id 时不需要 --contents")


def check_cookie(cookie_path: Path) -> None:
    sess = build_session(cookie_path)
    url = "https://www.zhihu.com/api/v4/me"
    try:
        obj = request_json(sess, url)
    except Exception as exc:
        print(f"cookie 不可用: {exc}")
        raise SystemExit(1)
    print("cookie 可用")
    print(f"当前账号: {obj.get('name', '')} ({obj.get('url_token', '')})")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    if args.command == "login":
        login_and_save_cookie(
            driver_path=args.driver_path,
            cookie_path=Path(args.cookie_path),
            wait_seconds=args.wait_seconds,
        )
        return 0

    if args.command == "check-cookie":
        check_cookie(Path(args.cookie_path))
        return 0

    if args.command == "update-data":
        sess = build_session(Path(args.cookie_path))
        output_root = Path(args.output_dir)
        ensure_dir(output_root)
        update_all_data(session=sess, output_root=output_root)
        return 0

    if args.command == "crawl":
        try:
            validate_crawl_args(args)
            time_begin = parse_time_begin(args.time_begin)
        except ValueError as exc:
            print(str(exc))
            return 1

        sess = build_session(Path(args.cookie_path))
        output_root = Path(args.output_dir)
        ensure_dir(output_root)

        if args.user:
            crawl_user(
                session=sess,
                username=args.user,
                contents=args.contents,
                output_root=output_root,
                time_begin=time_begin,
            )
        else:
            crawl_column(
                session=sess,
                column_id=args.column_id,
                output_root=output_root,
                time_begin=time_begin,
            )
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
