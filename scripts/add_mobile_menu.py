"""
blog/ 全記事にモバイルハンバーガーメニューを追加
- ヘッダーにハンバーガーボタン追加
- mobile-menu ドロップダウン追加
- toggleMenu() 関数を back-home.js の前に挿入
"""
import os

BLOG_DIR = os.path.join(os.path.dirname(__file__), '..', 'blog')

HAMBURGER_BTN = '''            <div class="md:hidden">
                <button onclick="toggleMenu()" class="text-gray-700" aria-label="メニューを開く">
                    <svg id="menu-icon" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <line x1="3" y1="6" x2="21" y2="6"></line>
                        <line x1="3" y1="12" x2="21" y2="12"></line>
                        <line x1="3" y1="18" x2="21" y2="18"></line>
                    </svg>
                    <svg id="close-icon" class="w-6 h-6 hidden" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
            </div>'''

MOBILE_MENU = '''        <div id="mobile-menu" class="md:hidden bg-white px-6 pb-4 hidden">
            <nav class="flex flex-col space-y-4">
                <a href="../index.html#blog" class="text-gray-700 hover:text-indigo-600">ブログ</a>
                <a href="../categories.html" class="text-gray-700 hover:text-indigo-600">カテゴリー</a>
                <a href="../index.html#affiliate" class="text-gray-700 hover:text-indigo-600">おすすめツール</a>
                <a href="../index.html#about" class="text-gray-700 hover:text-indigo-600">プロフィール</a>
                <a href="../index.html#contact" class="text-gray-700 hover:text-indigo-600">お問い合わせ</a>
            </nav>
        </div>'''

TOGGLE_SCRIPT = '''    <script>
        function toggleMenu() {
            var mobileMenu = document.getElementById('mobile-menu');
            var menuIcon = document.getElementById('menu-icon');
            var closeIcon = document.getElementById('close-icon');
            if (mobileMenu.classList.contains('hidden')) {
                mobileMenu.classList.remove('hidden');
                menuIcon.classList.add('hidden');
                closeIcon.classList.remove('hidden');
            } else {
                mobileMenu.classList.add('hidden');
                menuIcon.classList.remove('hidden');
                closeIcon.classList.add('hidden');
            }
        }
    </script>
'''

OLD_NAV_END = '            </nav>\n        </div>\n    </header>'
NEW_NAV_END = f'{HAMBURGER_BTN}\n        </div>\n{MOBILE_MENU}\n    </header>'

OLD_BACKHOME = '    <script src="../back-home.js"></script>'
NEW_BACKHOME = f'{TOGGLE_SCRIPT}    <script src="../back-home.js"></script>'

OLD_BODY_END = '</body>'
NEW_BODY_END = f'{TOGGLE_SCRIPT}    <script src="../back-home.js"></script>\n</body>'

files = sorted(f for f in os.listdir(BLOG_DIR) if f.endswith('.html'))
ok, skip = [], []

for fname in files:
    path = os.path.join(BLOG_DIR, fname)
    with open(path, encoding='utf-8') as f:
        content = f.read()

    if 'toggleMenu' in content:
        skip.append(fname)
        continue

    if OLD_NAV_END not in content:
        print(f'SKIP (nav pattern not found): {fname}')
        skip.append(fname)
        continue

    content = content.replace(OLD_NAV_END, NEW_NAV_END, 1)

    if OLD_BACKHOME in content:
        content = content.replace(OLD_BACKHOME, NEW_BACKHOME, 1)
    else:
        content = content.replace(OLD_BODY_END, NEW_BODY_END, 1)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    ok.append(fname)

print(f'OK: {len(ok)}件')
for f in ok:
    print(f'  {f}')
if skip:
    print(f'SKIP: {len(skip)}件')
    for f in skip:
        print(f'  {f}')
