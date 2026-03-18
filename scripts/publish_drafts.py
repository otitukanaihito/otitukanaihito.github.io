"""
予約投稿スクリプト
drafts/ フォルダ内のHTMLファイルを公開日チェックして blog/ に移動する。

ファイル命名規則: {任意のスラッグ}-YYYY-MM-DD.html
例: new-article-2026-03-24.html
"""

import os
import re
import shutil
from datetime import date, datetime

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRAFTS_DIR = os.path.join(REPO_ROOT, "drafts")
BLOG_DIR = os.path.join(REPO_ROOT, "blog")
SITEMAP_PATH = os.path.join(REPO_ROOT, "sitemap.xml")
BASE_URL = "https://otitukanaihito.github.io"

DATE_PATTERN = re.compile(r"-(\d{4}-\d{2}-\d{2})\.html$")


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

    # </urlset> の直前に挿入
    updated = content.replace("</urlset>", new_entries + "</urlset>")
    with open(SITEMAP_PATH, "w", encoding="utf-8") as f:
        f.write(updated)

    print(f"sitemap.xml を更新しました（{len(published_files)}件追加）")


def main():
    today = date.today()
    print(f"実行日: {today}")

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

    return len(published)


if __name__ == "__main__":
    main()
