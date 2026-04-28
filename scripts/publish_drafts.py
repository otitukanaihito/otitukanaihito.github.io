"""
予約投稿スクリプト
drafts/ フォルダ内のHTMLファイルを公開日チェックして blog/ に移動する。

ファイル命名規則: {任意のスラッグ}-YYYY-MM-DD.html
例: new-article-2026-03-24.html
"""

import json
import os
import re
import shutil
import subprocess
import sys
from datetime import date, datetime, timezone, timedelta

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRAFTS_DIR = os.path.join(REPO_ROOT, "drafts")
BLOG_DIR = os.path.join(REPO_ROOT, "blog")
SITEMAP_PATH = os.path.join(REPO_ROOT, "sitemap.xml")
ARTICLES_JSON = os.path.join(REPO_ROOT, "scripts", "articles.json")
GENERATE_SCRIPT = os.path.join(REPO_ROOT, "scripts", "generate.py")
BASE_URL = "https://otitukanaihito.github.io"

DATE_PATTERN = re.compile(r"-(\d{4}-\d{2}-\d{2})\.html$")

KNOWN_CATEGORIES = ["AI活用", "AI開発", "自動化", "ナレッジ管理", "福祉×テック", "サイト制作", "ライフスタイル"]


def extract_metadata(filepath, filename):
    """公開済みHTMLから articles.json 用のメタデータを抽出する。"""
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    # title: <title>記事タイトル - オチつかないカンパニー</title>
    title_match = re.search(r"<title>(.*?)\s*[-–]\s*オチつかないカンパニー</title>", content)
    title = title_match.group(1).strip() if title_match else filename

    # og:image → 相対パス（images/xxx.webp など）
    image_match = re.search(r'<meta property="og:image" content="' + re.escape(BASE_URL) + r'/(.*?)"', content)
    image = image_match.group(1) if image_match else "images/blog_ai_thumbnail.webp"

    # category: rounded-full 系クラスを持つ span からテキストを抽出し既知カテゴリと照合
    category = "AI活用"  # デフォルト
    cat_match = re.search(r'rounded-full[^>]*>([^<]+)</span>', content)
    if cat_match:
        extracted = cat_match.group(1).strip()
        if extracted in KNOWN_CATEGORIES:
            category = extracted

    # slug: ファイル名から .html を除いたもの
    slug = filename[:-5]

    # date: ファイル名末尾の日付
    date_match = DATE_PATTERN.search(filename)
    pub_date = date_match.group(1) if date_match else date.today().isoformat()

    return {"slug": slug, "title": title, "date": pub_date, "category": category, "image": image}


def update_articles_json(new_articles):
    """articles.json に新記事を追加し、日付降順で保存する。"""
    with open(ARTICLES_JSON, encoding="utf-8") as f:
        articles = json.load(f)

    existing_slugs = {a["slug"] for a in articles}
    added = 0
    for entry in new_articles:
        if entry["slug"] not in existing_slugs:
            articles.append(entry)
            added += 1
            print(f"  articles.json に追加: {entry['slug']}")

    if added == 0:
        return False

    articles.sort(key=lambda a: a["date"], reverse=True)
    with open(ARTICLES_JSON, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    print(f"articles.json を更新しました（{added}件追加）")
    return True


def get_publish_date(filename):
    """ファイル名から公開日を取得する。見つからなければNoneを返す。"""
    match = DATE_PATTERN.search(filename)
    if not match:
        return None
    try:
        return date.fromisoformat(match.group(1))
    except ValueError:
        return None


def update_sitemap(published_files):
    """公開したファイルをsitemap.xmlに追記する。"""
    if not published_files or not os.path.exists(SITEMAP_PATH):
        return

    today_str = date.today().isoformat()
    new_entries = ""
    for filename in published_files:
        url = f"{BASE_URL}/blog/{filename}"
        new_entries += f"""  <url>
    <loc>{url}</loc>
    <lastmod>{today_str}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>\n"""

    with open(SITEMAP_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # 既存URLと重複しないものだけ追加
    filtered = ""
    for filename in published_files:
        url = f"{BASE_URL}/blog/{filename}"
        if url not in content:
            filtered += f"""  <url>
    <loc>{url}</loc>
    <lastmod>{today_str}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>\n"""
    new_entries = filtered

    if not new_entries:
        print("sitemap.xml: 追加対象なし（重複スキップ）")
        return

    # </urlset> の直前に挿入
    updated = content.replace("</urlset>", new_entries + "</urlset>")
    with open(SITEMAP_PATH, "w", encoding="utf-8") as f:
        f.write(updated)

    print(f"sitemap.xml を更新しました（{len(published_files)}件追加）")


def main():
    JST = timezone(timedelta(hours=9))
    today = datetime.now(JST).date()
    print(f"実行日: {today} (JST)")

    if not os.path.exists(DRAFTS_DIR):
        print("drafts/ フォルダが存在しません。スキップします。")
        return

    draft_files = [f for f in os.listdir(DRAFTS_DIR) if f.endswith(".html")]
    if not draft_files:
        print("drafts/ にファイルがありません。")
        return

    published = []
    skipped = []

    for filename in sorted(draft_files):
        publish_date = get_publish_date(filename)

        if publish_date is None:
            print(f"  スキップ（日付なし）: {filename}")
            skipped.append(filename)
            continue

        if publish_date <= today:
            src = os.path.join(DRAFTS_DIR, filename)
            dst = os.path.join(BLOG_DIR, filename)
            shutil.move(src, dst)
            published.append(filename)
            print(f"  公開: {filename}  （公開日: {publish_date}）")
        else:
            days_left = (publish_date - today).days
            print(f"  待機中: {filename}  （あと{days_left}日）")
            skipped.append(filename)

    print(f"\n公開: {len(published)}件 / 待機: {len(skipped)}件")

    if published:
        update_sitemap(published)

        # articles.json 更新 → generate.py でカード再生成
        new_entries = []
        for filename in published:
            filepath = os.path.join(BLOG_DIR, filename)
            entry = extract_metadata(filepath, filename)
            new_entries.append(entry)

        updated = update_articles_json(new_entries)
        if updated:
            print("generate.py を実行してカードを再生成します...")
            result = subprocess.run(
                [sys.executable, GENERATE_SCRIPT],
                capture_output=True, text=True, encoding="utf-8"
            )
            if result.returncode == 0:
                print(result.stdout.strip())
            else:
                print(f"generate.py エラー: {result.stderr.strip()}")

    return len(published)


if __name__ == "__main__":
    main()
