# 訪問者分析機能 セットアップガイド

## 概要（概要）

このブログサイトに訪問者分析機能（訪問者分析機能）を実装しました。リアルタイム訪問者数、地理的分布、ページビュー統計などを確認できます。

## 実装済み機能（実装済み機能）

### 1. リアルタイム訪問者カウンター（リアルタイム訪問者カウンター）
- 現在の訪問者数表示
- 総訪問者数表示
- 30秒ごとの自動更新

### 2. 訪問者分析ダッシュボード（訪問者分析ダッシュボード）
- 詳細な統計情報
- グラフ表示（Chart.js使用）
- 地理的分布
- デバイス・ブラウザ情報

### 3. Google Analytics 4連携（Google Analytics 4連携）
- ページビュートラッキング
- カスタムイベント送信
- プライバシー保護設定

## セットアップ手順（セットアップ手順）

### ステップ1: Google Analytics 4の設定

1. **Google Analyticsアカウント作成**
   - [Google Analytics](https://analytics.google.com/) にアクセス
   - アカウントを作成

2. **プロパティ作成**
   - 「管理」→「プロパティ作成」
   - プロパティ名: 「オチつかないカンパニー」
   - データストリーム: Webサイト
   - 測定IDを取得（例: G-XXXXXXXXXX）

3. **測定IDの設定**
   - `analytics-config.js` ファイルを開く
   - `MEASUREMENT_ID` を実際の測定IDに変更
   ```javascript
   MEASUREMENT_ID: 'G-XXXXXXXXXX', // 実際の測定IDに変更
   ```

### ステップ2: HTMLファイルの更新

1. **index.htmlの更新**
   - 既に実装済み
   - リアルタイムカウンターが表示される

2. **visitor-analytics.htmlの確認**
   - 詳細分析ページが利用可能

### ステップ3: プライバシーポリシーの更新

1. **privacy-policy.htmlの確認**
   - 分析機能の説明を追加済み
   - 必要に応じて内容を調整

## 使用方法（使用方法）

### リアルタイムカウンターの確認
1. ホームページ（index.html）にアクセス
2. ヒーローセクションにカウンターが表示される
3. 「詳細分析を見る」リンクから詳細ページへ

### 詳細分析の確認
1. ナビゲーションの「訪問者分析」をクリック
2. または `visitor-analytics.html` に直接アクセス
3. 各種統計情報とグラフを確認

## カスタマイズ（カスタマイズ）

### カウンターの更新頻度変更
```javascript
// index.html の updateVisitorCounter 関数内
setInterval(updateVisitorCounter, 30000); // 30秒 → 変更可能
```

### グラフの色やスタイル変更
```javascript
// visitor-analytics.html の Chart.js 設定内
backgroundColor: [
    'rgb(99, 102, 241)', // 色を変更
    'rgb(34, 197, 94)',
    'rgb(251, 146, 60)'
]
```

### カスタムイベントの追加
```javascript
// analytics-config.js に新しい関数を追加
function sendCustomAnalyticsEvent(eventName, parameters) {
    sendCustomEvent(eventName, parameters);
}
```

## プライバシーとコンプライアンス（プライバシーとコンプライアンス）

### 実装済みの保護機能
- IPアドレスの匿名化
- セキュアCookie設定
- データ保持期間の制限
- オプトアウト機能

### 法的要件
- GDPR準拠
- CCPA準拠
- 日本の個人情報保護法準拠

## トラブルシューティング（トラブルシューティング）

### よくある問題

1. **カウンターが表示されない**
   - JavaScriptが有効になっているか確認
   - ブラウザのコンソールでエラーを確認

2. **Google Analyticsが動作しない**
   - 測定IDが正しく設定されているか確認
   - ネットワーク接続を確認

3. **グラフが表示されない**
   - Chart.jsライブラリが読み込まれているか確認
   - インターネット接続を確認

### デバッグ方法
```javascript
// ブラウザのコンソールで実行
console.log('Analytics Config:', window.ANALYTICS_CONFIG);
console.log('Visitor Analytics:', getVisitorAnalytics());
```

## 今後の拡張予定（今後の拡張予定）

- リアルタイムチャット機能
- 訪問者フィードバック機能
- A/Bテスト機能
- より詳細な分析レポート

## サポート（サポート）

問題や質問がある場合は、以下の方法でサポートを受けられます：

1. GitHubのIssuesページ
2. ブログのコメント欄
3. お問い合わせフォーム

---

**注意**: この機能は教育・学習目的で実装されています。実際の商用利用の際は、適切な法的アドバイスを受けてください。 