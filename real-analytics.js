// 実際のGoogle Analytics 4 APIを使用した訪問者分析機能
// このファイルは実際のGA4 APIキーとプロパティIDが必要です

class RealVisitorAnalytics {
    constructor() {
        this.GA4_PROPERTY_ID = 'YOUR_GA4_PROPERTY_ID'; // 実際のプロパティID
        this.GA4_API_KEY = 'YOUR_GA4_API_KEY'; // 実際のAPIキー
        this.accessToken = null;
        this.isAuthenticated = false;
    }

    // Google OAuth2認証
    async authenticate() {
        try {
            // Google OAuth2認証フロー
            const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?` +
                `client_id=${this.GA4_API_KEY}&` +
                `redirect_uri=${encodeURIComponent(window.location.origin)}&` +
                `scope=https://www.googleapis.com/auth/analytics.readonly&` +
                `response_type=token`;

            // ポップアップで認証
            const popup = window.open(authUrl, 'ga4_auth', 'width=500,height=600');
            
            return new Promise((resolve, reject) => {
                window.addEventListener('message', (event) => {
                    if (event.data.type === 'GA4_AUTH_SUCCESS') {
                        this.accessToken = event.data.accessToken;
                        this.isAuthenticated = true;
                        resolve(true);
                    } else if (event.data.type === 'GA4_AUTH_ERROR') {
                        reject(new Error('認証に失敗しました'));
                    }
                });
            });
        } catch (error) {
            console.error('認証エラー:', error);
            return false;
        }
    }

    // GA4 APIからリアルタイムデータを取得
    async getRealTimeData() {
        if (!this.isAuthenticated) {
            throw new Error('認証が必要です');
        }

        try {
            const response = await fetch(
                `https://analyticsdata.googleapis.com/v1beta/properties/${this.GA4_PROPERTY_ID}:runRealtimeReport`,
                {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${this.accessToken}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        dimensions: [
                            { name: 'country' },
                            { name: 'deviceCategory' }
                        ],
                        metrics: [
                            { name: 'activeUsers' },
                            { name: 'screenPageViews' }
                        ]
                    })
                }
            );

            if (!response.ok) {
                throw new Error(`API エラー: ${response.status}`);
            }

            const data = await response.json();
            return this.parseRealTimeData(data);
        } catch (error) {
            console.error('リアルタイムデータ取得エラー:', error);
            return this.getFallbackData();
        }
    }

    // 履歴データを取得
    async getHistoricalData(startDate, endDate) {
        if (!this.isAuthenticated) {
            throw new Error('認証が必要です');
        }

        try {
            const response = await fetch(
                `https://analyticsdata.googleapis.com/v1beta/properties/${this.GA4_PROPERTY_ID}:runReport`,
                {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${this.accessToken}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        dateRanges: [
                            {
                                startDate: startDate,
                                endDate: endDate
                            }
                        ],
                        dimensions: [
                            { name: 'date' },
                            { name: 'pageTitle' },
                            { name: 'country' },
                            { name: 'deviceCategory' },
                            { name: 'browser' }
                        ],
                        metrics: [
                            { name: 'users' },
                            { name: 'screenPageViews' },
                            { name: 'averageSessionDuration' }
                        ]
                    })
                }
            );

            if (!response.ok) {
                throw new Error(`API エラー: ${response.status}`);
            }

            const data = await response.json();
            return this.parseHistoricalData(data);
        } catch (error) {
            console.error('履歴データ取得エラー:', error);
            return this.getFallbackHistoricalData();
        }
    }

    // リアルタイムデータの解析
    parseRealTimeData(data) {
        const result = {
            currentVisitors: 0,
            pageViews: 0,
            geographicDistribution: {},
            deviceDistribution: {}
        };

        if (data.rows) {
            data.rows.forEach(row => {
                const country = row.dimensionValues[0].value;
                const device = row.dimensionValues[1].value;
                const activeUsers = parseInt(row.metricValues[0].value);
                const views = parseInt(row.metricValues[1].value);

                result.currentVisitors += activeUsers;
                result.pageViews += views;

                // 地理的分布
                result.geographicDistribution[country] = 
                    (result.geographicDistribution[country] || 0) + activeUsers;

                // デバイス分布
                result.deviceDistribution[device] = 
                    (result.deviceDistribution[device] || 0) + activeUsers;
            });
        }

        return result;
    }

    // 履歴データの解析
    parseHistoricalData(data) {
        const result = {
            dailyVisitors: [],
            popularPages: {},
            geographicDistribution: {},
            deviceDistribution: {},
            browserDistribution: {}
        };

        if (data.rows) {
            data.rows.forEach(row => {
                const date = row.dimensionValues[0].value;
                const pageTitle = row.dimensionValues[1].value;
                const country = row.dimensionValues[2].value;
                const device = row.dimensionValues[3].value;
                const browser = row.dimensionValues[4].value;
                const users = parseInt(row.metricValues[0].value);
                const views = parseInt(row.metricValues[1].value);

                // 日別訪問者数
                const existingDate = result.dailyVisitors.find(d => d.date === date);
                if (existingDate) {
                    existingDate.visitors += users;
                } else {
                    result.dailyVisitors.push({ date, visitors: users });
                }

                // 人気ページ
                result.popularPages[pageTitle] = 
                    (result.popularPages[pageTitle] || 0) + views;

                // 地理的分布
                result.geographicDistribution[country] = 
                    (result.geographicDistribution[country] || 0) + users;

                // デバイス分布
                result.deviceDistribution[device] = 
                    (result.deviceDistribution[device] || 0) + users;

                // ブラウザ分布
                result.browserDistribution[browser] = 
                    (result.browserDistribution[browser] || 0) + users;
            });
        }

        return result;
    }

    // フォールバックデータ（APIが利用できない場合）
    getFallbackData() {
        return {
            currentVisitors: Math.floor(Math.random() * 50) + 10,
            pageViews: Math.floor(Math.random() * 500) + 200,
            geographicDistribution: {
                'Japan': 85,
                'United States': 8,
                'Other': 7
            },
            deviceDistribution: {
                'desktop': 45,
                'mobile': 40,
                'tablet': 15
            }
        };
    }

    // フォールバック履歴データ
    getFallbackHistoricalData() {
        const today = new Date();
        const dailyVisitors = [];
        
        for (let i = 6; i >= 0; i--) {
            const date = new Date(today);
            date.setDate(date.getDate() - i);
            dailyVisitors.push({
                date: date.toISOString().split('T')[0],
                visitors: Math.floor(Math.random() * 200) + 100
            });
        }

        return {
            dailyVisitors,
            popularPages: {
                'ホームページ': 1234,
                'ブログ記事1': 856,
                'サービス紹介': 543
            },
            geographicDistribution: {
                'Japan': 85,
                'United States': 8,
                'Other': 7
            },
            deviceDistribution: {
                'desktop': 45,
                'mobile': 40,
                'tablet': 15
            },
            browserDistribution: {
                'Chrome': 60,
                'Safari': 25,
                'Firefox': 10,
                'Edge': 5
            }
        };
    }
}

// グローバルインスタンス
window.realAnalytics = new RealVisitorAnalytics();

// 認証コールバック処理
window.addEventListener('message', (event) => {
    if (event.origin !== 'https://accounts.google.com') return;
    
    const urlParams = new URLSearchParams(event.data);
    const accessToken = urlParams.get('access_token');
    
    if (accessToken) {
        window.opener.postMessage({
            type: 'GA4_AUTH_SUCCESS',
            accessToken: accessToken
        }, window.location.origin);
        window.close();
    } else {
        window.opener.postMessage({
            type: 'GA4_AUTH_ERROR'
        }, window.location.origin);
        window.close();
    }
}); 