// サーバーサイド訪問者分析機能（Node.js/Express使用例）
// このファイルはサーバーサイドで実行されます

const express = require('express');
const { google } = require('googleapis');
const cors = require('cors');
const app = express();

// ミドルウェア設定
app.use(cors());
app.use(express.json());

// Google Analytics 4設定
const GA4_CONFIG = {
    propertyId: 'YOUR_GA4_PROPERTY_ID',
    clientId: 'YOUR_CLIENT_ID',
    clientSecret: 'YOUR_CLIENT_SECRET',
    refreshToken: 'YOUR_REFRESH_TOKEN'
};

// Google Analytics 4認証
async function getGA4Client() {
    const oauth2Client = new google.auth.OAuth2(
        GA4_CONFIG.clientId,
        GA4_CONFIG.clientSecret,
        'http://localhost:3000/auth/callback'
    );

    oauth2Client.setCredentials({
        refresh_token: GA4_CONFIG.refreshToken
    });

    return google.analyticsdata({
        version: 'v1beta',
        auth: oauth2Client
    });
}

// リアルタイム訪問者数取得API
app.get('/api/analytics/realtime', async (req, res) => {
    try {
        const analytics = await getGA4Client();
        
        const response = await analytics.properties.runRealtimeReport({
            property: `properties/${GA4_CONFIG.propertyId}`,
            requestBody: {
                dimensions: [
                    { name: 'country' },
                    { name: 'deviceCategory' }
                ],
                metrics: [
                    { name: 'activeUsers' },
                    { name: 'screenPageViews' }
                ]
            }
        });

        const data = response.data;
        const result = parseRealTimeData(data);
        
        res.json(result);
    } catch (error) {
        console.error('リアルタイムデータ取得エラー:', error);
        res.status(500).json({
            error: 'データ取得に失敗しました',
            fallback: getFallbackRealTimeData()
        });
    }
});

// 履歴データ取得API
app.get('/api/analytics/historical', async (req, res) => {
    try {
        const { startDate, endDate } = req.query;
        const analytics = await getGA4Client();
        
        const response = await analytics.properties.runReport({
            property: `properties/${GA4_CONFIG.propertyId}`,
            requestBody: {
                dateRanges: [
                    {
                        startDate: startDate || '7daysAgo',
                        endDate: endDate || 'today'
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
            }
        });

        const data = response.data;
        const result = parseHistoricalData(data);
        
        res.json(result);
    } catch (error) {
        console.error('履歴データ取得エラー:', error);
        res.status(500).json({
            error: 'データ取得に失敗しました',
            fallback: getFallbackHistoricalData()
        });
    }
});

// ページビュー記録API
app.post('/api/analytics/pageview', (req, res) => {
    const { page, referrer, userAgent, ip } = req.body;
    
    // データベースにページビューを記録
    recordPageView({
        page,
        referrer,
        userAgent,
        ip,
        timestamp: new Date(),
        sessionId: req.session?.id || generateSessionId()
    });
    
    res.json({ success: true });
});

// リアルタイムデータ解析
function parseRealTimeData(data) {
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

            result.geographicDistribution[country] = 
                (result.geographicDistribution[country] || 0) + activeUsers;
            result.deviceDistribution[device] = 
                (result.deviceDistribution[device] || 0) + activeUsers;
        });
    }

    return result;
}

// 履歴データ解析
function parseHistoricalData(data) {
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

            // 分布データ
            result.geographicDistribution[country] = 
                (result.geographicDistribution[country] || 0) + users;
            result.deviceDistribution[device] = 
                (result.deviceDistribution[device] || 0) + users;
            result.browserDistribution[browser] = 
                (result.browserDistribution[browser] || 0) + users;
        });
    }

    return result;
}

// フォールバックデータ
function getFallbackRealTimeData() {
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

function getFallbackHistoricalData() {
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

// ページビュー記録（データベース実装例）
function recordPageView(data) {
    // ここでデータベースに記録
    // 例: MongoDB, PostgreSQL, SQLite等
    console.log('ページビュー記録:', data);
}

// セッションID生成
function generateSessionId() {
    return Math.random().toString(36).substring(2, 15) + 
           Math.random().toString(36).substring(2, 15);
}

// サーバー起動
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`訪問者分析サーバーが起動しました: http://localhost:${PORT}`);
});

module.exports = app; 