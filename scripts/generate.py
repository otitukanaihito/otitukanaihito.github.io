"""
ブログカード自動生成スクリプト
articles.json を読み込んで index.html と categories.html のカード部分を再生成する。

使い方:
  cd otitukanaihito.github.io
  python scripts/generate.py

記事追加手順:
  1. scripts/articles.json に1エントリ追加（日付降順）
  2. python scripts/generate.py を実行
"""

import json
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTICLES_JSON = os.path.join(REPO_ROOT, "scripts", "articles.json")
INDEX_HTML = os.path.join(REPO_ROOT, "index.html")
CATEGORIES_HTML = os.path.join(REPO_ROOT, "categories.html")
BLOG_DIR = os.path.join(REPO_ROOT, "blog")
SITEMAP_PATH = os.path.join(REPO_ROOT, "sitemap.xml")
BASE_URL = "https://otitukanaihito.github.io"

# カテゴリー設定（表示順・色・アイコン）
CATEGORY_META = {
    "AI活用":       {"color": "purple", "icon": "🤖", "id": "ai-usage"},
    "AI開発":       {"color": "indigo", "icon": "💻", "id": "ai-dev"},
    "自動化":       {"color": "indigo", "icon": "⚙️",  "id": "automation"},
    "ナレッジ管理": {"color": "violet", "icon": "🧠", "id": "knowledge"},
    "福祉×テック":  {"color": "teal",   "icon": "🏥", "id": "welfare-tech"},
    "サイト制作":   {"color": "blue",   "icon": "🌐", "id": "web"},
    "ライフスタイル": {"color": "amber", "icon": "☀️", "id": "lifestyle"},
}


def load_articles():
    with open(ARTICLES_JSON, encoding="utf-8") as f:
        return json.load(f)


def get_article_description(slug):
    """blog/{slug}.html の <meta name="description"> を抽出する。"""
    filepath = os.path.join(BLOG_DIR, f"{slug}.html")
    if not os.path.exists(filepath):
        return ""
    with open(filepath, encoding="utf-8") as f:
        content = f.read()
    m = re.search(r'<meta name="description"[^>]*content="(.*?)"', content, re.DOTALL)
    return m.group(1) if m else ""


def make_index_card(article, description=""):
    """index.html 用のカードHTMLを生成する（brutalistデザイン対応）。"""
    return (
        f'          <!-- {article["slug"]} -->\n'
        f'          <a href="blog/{article["slug"]}.html" class="article-card">\n'
        f'            <img src="{article["image"]}" alt="{article["title"]}" class="article-card-img" loading="lazy">\n'
        f'            <div class="article-card-body">\n'
        f'              <div class="article-card-meta">\n'
        f'                <span class="article-card-tag">{article["category"]}</span>\n'
        f'                <span>{article["date"]}</span>\n'
        f'              </div>\n'
        f'              <h3>{article["title"]}</h3>\n'
        f'              <p>{description}</p>\n'
        f'            </div>\n'
        f'          </a>'
    )


def make_category_card(article):
    """categories.html 用のカードHTMLを生成する。"""
    color = CATEGORY_META.get(article["category"], {}).get("color", "indigo")
    return (
        f'        <a href="blog/{article["slug"]}.html"\n'
        f'           class="block bg-white rounded-xl shadow-sm border border-gray-100 p-5 hover:shadow-md hover:-translate-y-1 transition-all duration-300">\n'
        f'          <div class="flex items-center gap-2 mb-2">\n'
        f'            <span class="text-xs font-semibold text-{color}-600 bg-{color}-100 px-2 py-0.5 rounded-full">{article["category"]}</span>\n'
        f'            <span class="text-xs text-gray-400 ml-auto">{article["date"]}</span>\n'
        f'          </div>\n'
        f'          <h3 class="font-bold text-gray-800 leading-snug">{article["title"]}</h3>\n'
        f'        </a>'
    )


def generate_index_cards(articles):
    cards = [make_index_card(a, get_article_description(a["slug"])) for a in articles]
    return "\n\n".join(cards)


def generate_category_sections(articles):
    """カテゴリー別セクションHTMLを生成する。"""
    # カテゴリーごとに記事をまとめる（CATEGORY_META の順序で）
    grouped = {cat: [] for cat in CATEGORY_META}
    for a in articles:
        cat = a["category"]
        if cat not in grouped:
            grouped[cat] = []
        grouped[cat].append(a)

    total = len(articles)
    active_cats = [cat for cat in CATEGORY_META if grouped.get(cat)]
    cat_count = len(active_cats)

    sections = []
    # 件数行
    sections.append(f'    <p class="text-gray-500 mb-12">全 {total} 記事 ／ {cat_count} カテゴリー</p>')

    for cat_name in CATEGORY_META:
        cat_articles = grouped.get(cat_name, [])
        if not cat_articles:
            continue
        meta = CATEGORY_META[cat_name]
        color = meta["color"]
        icon = meta["icon"]
        cat_id = meta["id"]
        n = len(cat_articles)

        cat_cards = "\n".join(make_category_card(a) for a in cat_articles)
        section = (
            f'\n    <!-- {cat_name} -->\n'
            f'    <section id="{cat_id}" class="mb-14">\n'
            f'      <div class="flex items-center gap-3 mb-6">\n'
            f'        <span class="text-2xl">{icon}</span>\n'
            f'        <h2 class="text-2xl font-bold text-gray-800">{cat_name}</h2>\n'
            f'        <span class="ml-auto text-sm text-{color}-600 bg-{color}-100 px-3 py-1 rounded-full font-semibold">{n}記事</span>\n'
            f'      </div>\n'
            f'      <div class="grid md:grid-cols-2 gap-6">\n'
            f'{cat_cards}\n'
            f'      </div>\n'
            f'    </section>'
        )
        sections.append(section)

    return "\n".join(sections) + "\n"


def replace_between(content, start_marker, end_marker, new_content):
    """start_marker と end_marker の間を new_content で置き換える。"""
    pattern = re.compile(
        re.escape(start_marker) + r".*?" + re.escape(end_marker),
        re.DOTALL
    )
    replacement = f"{start_marker}\n\n{new_content}\n\n          {end_marker}"
    result, count = pattern.subn(replacement, content)
    if count == 0:
        raise ValueError(f"マーカーが見つかりません: {start_marker!r}")
    return result


def replace_between_categories(content, start_marker, end_marker, new_content):
    """categories.html 用 — インデントが異なるため別関数。"""
    pattern = re.compile(
        re.escape(start_marker) + r".*?" + re.escape(end_marker),
        re.DOTALL
    )
    replacement = f"{start_marker}\n{new_content}\n  {end_marker}"
    result, count = pattern.subn(replacement, content)
    if count == 0:
        raise ValueError(f"マーカーが見つかりません: {start_marker!r}")
    return result


def verify_consistency(articles):
    """blog/*.html / articles.json / sitemap.xml の整合性を検証する。
    欠落・余剰があれば標準エラーに報告して非ゼロで終了。
    """
    json_slugs = {a["slug"] for a in articles}
    fs_slugs = {f[:-5] for f in os.listdir(BLOG_DIR) if f.endswith(".html")}

    # drafts/ に居る未公開slugは許容する
    drafts_dir = os.path.join(REPO_ROOT, "drafts")
    draft_slugs = set()
    if os.path.isdir(drafts_dir):
        draft_slugs = {f[:-5] for f in os.listdir(drafts_dir) if f.endswith(".html")}

    missing_files = json_slugs - fs_slugs - draft_slugs   # JSONに有るがファイルもdraftも無し
    orphan_files = fs_slugs - json_slugs    # ファイルは有るがJSON未登録

    sitemap_slugs = set()
    if os.path.exists(SITEMAP_PATH):
        with open(SITEMAP_PATH, encoding="utf-8") as f:
            sm = f.read()
        for m in re.finditer(r"<loc>" + re.escape(BASE_URL) + r"/blog/([^<]+)\.html</loc>", sm):
            sitemap_slugs.add(m.group(1))

    sitemap_missing = fs_slugs - sitemap_slugs   # ファイル有るがsitemap未掲載
    sitemap_ghost = sitemap_slugs - fs_slugs     # sitemap有るがファイル無し

    errors = []
    if missing_files:
        errors.append(f"articles.jsonに有るがファイル無し: {sorted(missing_files)}")
    if orphan_files:
        errors.append(f"ファイル有るがarticles.json未登録: {sorted(orphan_files)}")
    if sitemap_missing:
        errors.append(f"ファイル有るがsitemap.xml未掲載: {sorted(sitemap_missing)}")
    if sitemap_ghost:
        errors.append(f"sitemap.xml有るがファイル無し: {sorted(sitemap_ghost)}")

    if errors:
        print("整合性チェック失敗:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)
    print("整合性チェック OK（articles.json/blog/sitemap.xml 一致）")


def main():
    articles = load_articles()
    print(f"記事数: {len(articles)}件")
    verify_consistency(articles)

    # --- index.html を更新 ---
    with open(INDEX_HTML, encoding="utf-8") as f:
        index_content = f.read()

    index_cards = generate_index_cards(articles)
    index_content = replace_between(
        index_content,
        "<!-- BLOG-CARDS-START -->",
        "<!-- BLOG-CARDS-END -->",
        index_cards,
    )
    with open(INDEX_HTML, "w", encoding="utf-8") as f:
        f.write(index_content)
    print("index.html を更新しました")

    # --- categories.html を更新 ---
    with open(CATEGORIES_HTML, encoding="utf-8") as f:
        cat_content = f.read()

    cat_sections = generate_category_sections(articles)
    cat_content = replace_between_categories(
        cat_content,
        "<!-- CATEGORIES-START -->",
        "<!-- CATEGORIES-END -->",
        cat_sections,
    )
    with open(CATEGORIES_HTML, "w", encoding="utf-8") as f:
        f.write(cat_content)
    print("categories.html を更新しました")


if __name__ == "__main__":
    main()
