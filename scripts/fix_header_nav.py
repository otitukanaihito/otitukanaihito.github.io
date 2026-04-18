"""
高優先度3件の一括修正スクリプト
1. ←ホームボタンのモバイル被り → back-home.js修正（別途）
2. ヘッダーロゴの折り返し → text-2xlをレスポンシブに
3. ナビ構成の不一致 → 全17記事を5項目に統一
"""
import os
import re

BLOG_DIR = os.path.join(os.path.dirname(__file__), '..', 'blog')

OLD_LOGO_CLASS = 'text-2xl font-black tracking-wider text-gray-900 hover:text-indigo-600 transition-colors duration-300'
NEW_LOGO_CLASS = 'text-sm md:text-2xl font-black tracking-wider whitespace-nowrap text-gray-900 hover:text-indigo-600 transition-colors duration-300'

OLD_NAV = (
    '<a href="../index.html#blog" class="text-gray-700 hover:text-indigo-600 transition-colors duration-300">ブログ</a>\n'
    '                <a href="../index.html#affiliate" class="text-gray-700 hover:text-indigo-600 transition-colors duration-300">おすすめツール</a>\n'
    '                <a href="../index.html#services" class="text-gray-700 hover:text-indigo-600 transition-colors duration-300">サービス</a>\n'
    '                <a href="../index.html#about" class="text-gray-700 hover:text-indigo-600 transition-colors duration-300">プロフィール</a>'
)

NEW_NAV = (
    '<a href="../index.html#blog" class="text-gray-700 hover:text-indigo-600 transition-colors duration-300">ブログ</a>\n'
    '                <a href="../categories.html" class="text-gray-700 hover:text-indigo-600 transition-colors duration-300">カテゴリー</a>\n'
    '                <a href="../index.html#affiliate" class="text-gray-700 hover:text-indigo-600 transition-colors duration-300">おすすめツール</a>\n'
    '                <a href="../index.html#about" class="text-gray-700 hover:text-indigo-600 transition-colors duration-300">プロフィール</a>\n'
    '                <a href="../index.html#contact" class="text-gray-700 hover:text-indigo-600 transition-colors duration-300">お問い合わせ</a>'
)

files = [f for f in os.listdir(BLOG_DIR) if f.endswith('.html')]
files.sort()

for fname in files:
    path = os.path.join(BLOG_DIR, fname)
    with open(path, encoding='utf-8') as f:
        content = f.read()

    original = content
    content = content.replace(OLD_LOGO_CLASS, NEW_LOGO_CLASS)
    content = content.replace(OLD_NAV, NEW_NAV)

    if content != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        changed = []
        if OLD_LOGO_CLASS not in content:
            changed.append('ロゴ修正')
        if OLD_NAV not in content:
            changed.append('ナビ修正')
        print(f'OK {fname}: {", ".join(changed)}')
    else:
        print(f'  {fname}: 変更なし')

print('\n完了')
