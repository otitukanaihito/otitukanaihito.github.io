"""
migrate.py — Neo-Brutalist Zine migration
既存 blog/*.html を新テンプレート (_templates/article.html) に変換する。
本文コンテンツ・OGP・構造化データはすべて保持。

Usage:
  python scripts/migrate.py           # dry-run (差分表示のみ)
  python scripts/migrate.py --apply   # 実際に上書き
"""

import sys
import os
import json
import re
from pathlib import Path

# Windows console UTF-8 対応
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from bs4 import BeautifulSoup, Comment

ROOT = Path(__file__).parent.parent
BLOG_DIR = ROOT / "blog"
TEMPLATE_FILE = ROOT / "_templates" / "article.html"

DRY_RUN = "--apply" not in sys.argv

# ── カテゴリ表示名 → ID マッピング ──────────────────────────
CATEGORY_ID_MAP = {
    "AI開発":     "ai",
    "自動化":     "automation",
    "福祉":       "welfare",
    "育児・時短": "parenting",
    "健康・育児": "parenting",
    "Obsidian":   "obsidian",
    "GitHub":     "github",
    "仕事術":     "work",
    "副業":       "sidework",
    "動画":       "video",
}

def extract_text(el):
    """BeautifulSoup要素のテキストをトリムして返す。"""
    if el is None:
        return ""
    return el.get_text(strip=True)

def get_meta(soup, **kwargs):
    tag = soup.find("meta", kwargs)
    if tag:
        return tag.get("content", "").strip()
    return ""

def get_ld_json(soup, type_name):
    """指定した @type を持つ ld+json ブロックを返す。"""
    for script in soup.find_all("script", {"type": "application/ld+json"}):
        try:
            data = json.loads(script.string)
            if data.get("@type") == type_name:
                return data
        except Exception:
            continue
    return {}

def extract_category_from_breadcrumb(soup):
    """BreadcrumbList から カテゴリ名とIDを取得する。"""
    data = get_ld_json(soup, "BreadcrumbList")
    items = data.get("itemListElement", [])
    # position 2 がカテゴリ
    for item in items:
        if item.get("position") == 2:
            name = item.get("name", "")
            url = item.get("item", "")
            cat_id = url.split("#")[-1] if "#" in url else ""
            return name, cat_id
    return "", ""

def extract_category_from_banner(soup):
    """記事バナー内のカテゴリバッジを探す（フォールバック）。"""
    # pattern: <span class="... bg-*-500 ...px-3 py-1 rounded-full">カテゴリ</span>
    for span in soup.find_all("span"):
        cls = " ".join(span.get("class", []))
        if "rounded-full" in cls and "text-white" in cls:
            text = extract_text(span)
            if text:
                return text
    return ""

def extract_article_header_info(soup):
    """
    バナーdivから date / category / h1 / subtitle を抽出。
    新テンプレートではグラデーションバナーを廃止するため、これらを取り出す。
    """
    date = ""
    category = ""
    h1 = ""
    subtitle = ""

    # バナーを探す: relative h-64 or h-72 と bg-gradient を持つdiv
    banner = None
    for div in soup.find_all("div"):
        cls = " ".join(div.get("class", []))
        if "relative" in cls and ("h-64" in cls or "h-72" in cls or "h-96" in cls):
            banner = div
            break

    if banner:
        # date: 最初の <span class="text-sm text-white ml-*"> または 数字パターン
        for span in banner.find_all("span"):
            text = extract_text(span)
            if re.match(r"\d{4}-\d{2}-\d{2}", text):
                date = text
                break

        # category: rounded-full かつ bg-*-* のspan
        for span in banner.find_all("span"):
            cls = " ".join(span.get("class", []))
            if "rounded-full" in cls and "text-white" in cls:
                category = extract_text(span)
                break

        # h1
        h1_tag = banner.find("h1")
        if h1_tag:
            h1 = extract_text(h1_tag)

        # subtitle: p.text-lg.text-gray-200
        for p in banner.find_all("p"):
            cls = " ".join(p.get("class", []))
            if "text-lg" in cls:
                subtitle = extract_text(p)
                break

    # フォールバック: main h1
    if not h1:
        main_h1 = soup.find("h1")
        if main_h1:
            h1 = extract_text(main_h1)

    return date, category, h1, subtitle

def extract_prose_content(soup):
    """
    記事の本文HTML（prose divのinnerHTML）を抽出する。
    related articles セクション・フッター・ヘッダーは含まない。
    新フォーマット(prose div)と旧フォーマット(section.section)の両方に対応。
    """
    # 新フォーマット: prose クラスを持つ div
    prose = soup.find("div", class_="prose")
    if prose:
        return prose.decode_contents()

    # 旧フォーマット: div.container > section.section or section.card の構造
    containers = soup.find_all("div", class_="container")
    for container in containers:
        sections = container.find_all("section", class_=re.compile(r"section|card"))
        if sections:
            parts = []
            for section in sections:
                h2 = section.find("h2")
                if h2:
                    parts.append(f"<h2>{h2.get_text(strip=True)}</h2>")
                    h2.decompose()
                for child in section.children:
                    if hasattr(child, "decode_contents"):
                        inner = child.decode_contents().strip()
                        if inner:
                            parts.append(str(child))
                    elif str(child).strip():
                        parts.append(str(child))
            if parts:
                return "\n".join(parts)

    # フォールバック: p-8 div
    article_tag = soup.find("article")
    if article_tag:
        inner = article_tag.find("div", class_=re.compile(r"p-8"))
        if inner:
            related = inner.find("div", class_=re.compile(r"mt-12|border-t"))
            if related:
                related.decompose()
            return inner.decode_contents()

    return "<p>（本文抽出エラー）</p>"

def build_article(template, meta):
    """テンプレートにメタデータを埋め込んでHTMLを返す。"""
    result = template
    for key, value in meta.items():
        result = result.replace("{{" + key + "}}", value)
    return result

def migrate_file(html_path: Path, template: str, apply: bool) -> bool:
    """1ファイルを変換する。成功なら True を返す。"""
    try:
        raw = html_path.read_text(encoding="utf-8")
        soup = BeautifulSoup(raw, "html.parser")
    except Exception as e:
        print(f"  [ERROR] parse failed: {e}")
        return False

    # ── メタデータ抽出 ──────────────────────────────────────

    # title: "記事タイトル - サイト名" → 記事タイトルだけ
    title_tag = soup.find("title")
    full_title = title_tag.string.strip() if title_tag else ""
    og_title = get_meta(soup, property="og:title") or full_title.split(" - ")[0]
    title_meta = og_title + " - オチつかないカンパニー"

    description = get_meta(soup, **{"name": "description"})
    keywords    = get_meta(soup, **{"name": "keywords"})
    og_image    = get_meta(soup, property="og:image")
    canonical   = ""
    canonical_tag = soup.find("link", rel="canonical")
    if canonical_tag:
        canonical = canonical_tag.get("href", "")
    if not canonical:
        filename = html_path.name
        canonical = f"https://otitukanaihito.github.io/blog/{filename}"

    # structured data
    posting = get_ld_json(soup, "BlogPosting")
    date = posting.get("datePublished", "")

    # カテゴリ（パンくず優先）
    cat_name, cat_id = extract_category_from_breadcrumb(soup)

    # バナーから h1 / subtitle / date / category (フォールバック)
    banner_date, banner_cat, h1, subtitle = extract_article_header_info(soup)

    if not date:
        date = banner_date
    if not cat_name:
        cat_name = banner_cat
    if not cat_id:
        cat_id = CATEGORY_ID_MAP.get(cat_name, "general")

    # 本文抽出
    content = extract_prose_content(soup)

    # ── テンプレート埋め込み ────────────────────────────────
    meta = {
        "TITLE_META":    title_meta,
        "DESCRIPTION":   description,
        "KEYWORDS":      keywords,
        "CANONICAL_URL": canonical,
        "OG_TITLE":      og_title,
        "OG_IMAGE":      og_image,
        "DATE":          date,
        "CATEGORY":      cat_name,
        "CATEGORY_ID":   cat_id,
        "H1":            h1,
        "SUBTITLE":      subtitle,
        "CONTENT":       content,
    }

    new_html = build_article(template, meta)

    if apply:
        html_path.write_text(new_html, encoding="utf-8")
        print(f"  [OK] {html_path.name}")
    else:
        # dry-run: 主要な抽出結果を表示
        print(f"  title:    {og_title[:60]}")
        print(f"  date:     {date}  category: {cat_name} ({cat_id})")
        print(f"  h1:       {h1[:60]}")
        print(f"  subtitle: {subtitle[:60]}")
        print(f"  content:  {len(content)} chars")

    return True


def main():
    if not TEMPLATE_FILE.exists():
        print(f"[ERROR] テンプレートが見つかりません: {TEMPLATE_FILE}")
        sys.exit(1)

    template = TEMPLATE_FILE.read_text(encoding="utf-8")
    html_files = sorted(BLOG_DIR.glob("*.html"))

    if not html_files:
        print("[INFO] blog/*.html が見つかりませんでした。")
        sys.exit(0)

    mode = "APPLY" if not DRY_RUN else "DRY-RUN"
    print(f"=== migrate.py [{mode}] -- {len(html_files)} files ===\n")

    success = 0
    for path in html_files:
        print(f"[{'WRITE' if not DRY_RUN else 'CHECK'}] {path.name}")
        if migrate_file(path, template, apply=not DRY_RUN):
            success += 1
        print()

    print(f"=== 完了: {success}/{len(html_files)} files ===")
    if DRY_RUN:
        print("※ 実際に書き換えるには --apply を付けて再実行してください。")


if __name__ == "__main__":
    main()
