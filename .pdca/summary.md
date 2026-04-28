# レビュさん 指摘パターン集

## 繰り返し指摘（要注意）
- [HIGH] インラインstyle属性（1回目）→ CSSクラスに切り出す

## スコア推移
| 日付 | ファイル | スコア |
|------|---------|--------|
| 2026-04-29 | index.html / generate.py / publish.yml | 3/5 |

## 直近の指摘ログ
### 2026-04-29 - index.html / generate.py / publish.yml（スコア: 3/5）
- [HIGH] generate.py: `image_tag()` が死にコード → 削除する
- [HIGH] index.html 105行目: インラインstyle → brutalist.cssにクラス化
- [MEDIUM] get_article_description(): フォールバック正規表現が冗長 → 1パターンに統一
- [MEDIUM] publish.yml: コミットメッセージ日付がUTC → `TZ=Asia/Tokyo date` に変更
- [LOW] サイトロゴ href="index.html" → href="/" に変更
