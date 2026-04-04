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

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTICLES_JSON = os.path.join(REPO_ROOT, "scripts", "articles.json")
INDEX_HTML = os.path.join(REPO_ROOT, "index.html")
CATEGORIES_HTML = os.path.join(REPO_ROOT, "categories.html")

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


def image_tag(image_path, alt, extra_class=""):
    """画像パスに応じて picture または img タグを生成する。"""
    base_class = "w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
    if extra_class:
        base_class = f"{base_class} {extra_class}"

    if image_path.endswith(".webp"):
        png_path = image_path[:-5] + ".png"
        return (
            f'<picture>\n'
            f'                                <source srcset="{image_path}" type="image/webp">\n'
            f'                                <img src="{png_path}" alt="{alt}" width="640" height="640" loading="lazy" decoding="async" class="{base_class}">\n'
            f'                            </picture>'
        )
    else:
        return (
            f'<img src="{image_path}" alt="{alt}" width="640" height="640" loading="lazy" decoding="async" class="{base_class}">'
        )


def make_index_card(article):
    """index.html 用のカードHTMLを生成する。"""
    color = CATEGORY_META.get(article["category"], {}).get("color", "indigo")
    img = image_tag(article["image"], article["title"])
    return (
        f'                    <div class="bg-white rounded-2xl shadow-xl overflow-hidden group transform hover:-translate-y-2 transition-transform duration-300">\n'
        f'                        <div class="overflow-hidden h-48">\n'
        f'                            {img}\n'
        f'                        </div>\n'
        f'                        <div class="p-6">\n'
        f'                            <div class="flex items-center mb-3">\n'
        f'                                <span class="text-sm font-semibold text-{color}-600 bg-{color}-100 px-3 py-1 rounded-full">{article["category"]}</span>\n'
        f'                                <span class="text-sm text-gray-500 ml-auto">{article["date"]}</span>\n'
        f'                            </div>\n'
        f'                            <h3 class="text-lg font-bold text-gray-800 hover:text-indigo-600 transition-colors">\n'
        f'                                <a href="blog/{article["slug"]}.html">{article["title"]}</a>\n'
        f'                            </h3>\n'
        f'                        </div>\n'
        f'                    </div>'
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
    cards = [make_index_card(a) for a in articles]
    return "\n".join(cards)


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
    replacement = f"{start_marker}\n{new_content}\n                {end_marker}"
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


def main():
    articles = load_articles()
    print(f"記事数: {len(articles)}件")

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
