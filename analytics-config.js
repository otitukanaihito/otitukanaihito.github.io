// Google Analytics 4 設定ファイル
// このファイルを編集して実際の測定IDを設定してください

const ANALYTICS_CONFIG = {
    // Google Analytics 4 の測定IDをここに設定
    // 例: 'G-XXXXXXXXXX'
    MEASUREMENT_ID: 'G-WBGJLRYXKS',
    
    // カスタム設定
    CUSTOM_CONFIG: {
        'anonymize_ip': true,
        'cookie_flags': 'SameSite=None;Secure',
        'send_page_view': true,
        'custom_map': {
            'custom_parameter_1': 'visitor_type',
            'custom_parameter_2': 'page_category'
        }
    },
    
    // イベント設定
    EVENTS: {
        PAGE_VIEW: 'page_view',
        USER_ENGAGEMENT: 'user_engagement',
        CLICK: 'click',
        SCROLL: 'scroll',
        FORM_SUBMIT: 'form_submit'
    },
    
    // カスタムイベントパラメータ
    CUSTOM_PARAMETERS: {
        VISITOR_TYPE: 'visitor_type',
        PAGE_CATEGORY: 'page_category',
        AFFILIATE_TYPE: 'affiliate_type',
        PRODUCT_NAME: 'product_name'
    }
};

// 設定をグローバルに公開
window.ANALYTICS_CONFIG = ANALYTICS_CONFIG;

// Google Analytics 初期化関数
function initializeAnalytics() {
    if (typeof gtag !== 'undefined') {
        gtag('config', ANALYTICS_CONFIG.MEASUREMENT_ID, ANALYTICS_CONFIG.CUSTOM_CONFIG);
        console.log('Google Analytics 4 が初期化されました');
    } else {
        console.warn('Google Analytics が読み込まれていません');
    }
}

// 測定IDの解決（優先順位: URLパラメータ > window変数 > localStorage > 設定ファイル）
function resolveMeasurementId() {
    try {
        const params = new URLSearchParams(window.location.search);
        const fromQuery = params.get('ga');
        if (fromQuery && /^G-[A-Z0-9]+$/.test(fromQuery)) {
            return fromQuery;
        }
    } catch (_) {}

    if (typeof window.GA_MEASUREMENT_ID === 'string' && /^G-[A-Z0-9]+$/.test(window.GA_MEASUREMENT_ID)) {
        return window.GA_MEASUREMENT_ID;
    }

    try {
        const ls = localStorage.getItem('GA_MEASUREMENT_ID');
        if (ls && /^G-[A-Z0-9]+$/.test(ls)) {
            return ls;
        }
    } catch (_) {}

    return ANALYTICS_CONFIG.MEASUREMENT_ID;
}

// GAスクリプトを動的に読み込み、初期化を実行
function loadGoogleAnalytics() {
    const id = resolveMeasurementId();
    if (!id || id === 'GA_MEASUREMENT_ID') {
        console.warn('GA測定IDが未設定です。`analytics-config.js` または localStorage("GA_MEASUREMENT_ID")、URLパラメータ ?ga=G-XXXX で指定してください。');
        return;
    }

    // 重複読み込み防止
    if (document.getElementById('ga4-loader')) {
        return;
    }

    // dataLayer と gtag の定義
    window.dataLayer = window.dataLayer || [];
    window.gtag = function(){ dataLayer.push(arguments); };
    gtag('js', new Date());

    // 設定ファイル上のIDを上書き
    ANALYTICS_CONFIG.MEASUREMENT_ID = id;

    // スクリプト挿入
    const s = document.createElement('script');
    s.async = true;
    s.id = 'ga4-loader';
    s.src = `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(id)}`;
    document.head.appendChild(s);

    // 初期化
    s.addEventListener('load', () => {
        initializeAnalytics();
        // 既定の page_view を送信
        try {
            gtag('event', ANALYTICS_CONFIG.EVENTS.PAGE_VIEW, {
                'page_title': document.title,
                'page_location': window.location.href
            });
        } catch (e) {}
    });
}

// カスタムイベント送信関数
function sendCustomEvent(eventName, parameters = {}) {
    if (typeof gtag !== 'undefined') {
        gtag('event', eventName, parameters);
        console.log('イベント送信:', eventName, parameters);
    }
}

// ページビューイベント送信
function sendPageView(pageTitle, pageLocation) {
    sendCustomEvent(ANALYTICS_CONFIG.EVENTS.PAGE_VIEW, {
        'page_title': pageTitle,
        'page_location': pageLocation || window.location.href
    });
}

// ユーザーエンゲージメントイベント送信
function sendUserEngagement(engagementTime = 1000) {
    sendCustomEvent(ANALYTICS_CONFIG.EVENTS.USER_ENGAGEMENT, {
        'engagement_time_msec': engagementTime
    });
}

// クリックイベント送信
function sendClickEvent(eventCategory, eventLabel, customParameters = {}) {
    sendCustomEvent(ANALYTICS_CONFIG.EVENTS.CLICK, {
        'event_category': eventCategory,
        'event_label': eventLabel,
        ...customParameters
    });
}

// アフィリエイトクリックイベント送信
function sendAffiliateClick(productName, affiliateType) {
    sendClickEvent('affiliate', productName, {
        [ANALYTICS_CONFIG.CUSTOM_PARAMETERS.AFFILIATE_TYPE]: affiliateType,
        [ANALYTICS_CONFIG.CUSTOM_PARAMETERS.PRODUCT_NAME]: productName
    });
}

// 訪問者分析データ取得関数（シミュレーション）
function getVisitorAnalytics() {
    return {
        currentVisitors: Math.floor(Math.random() * 50) + 10,
        todayPageviews: Math.floor(Math.random() * 500) + 200,
        monthlyVisitors: Math.floor(Math.random() * 5000) + 2000,
        avgSessionDuration: Math.floor(Math.random() * 5) + 2,
        geographicDistribution: {
            '日本': 85,
            'アメリカ': 8,
            'その他': 7
        },
        deviceDistribution: {
            'デスクトップ': 45,
            'モバイル': 40,
            'タブレット': 15
        },
        browserDistribution: {
            'Chrome': 60,
            'Safari': 25,
            'Firefox': 10,
            'Edge': 5
        }
    };
}

// グローバル関数として公開
window.initializeAnalytics = initializeAnalytics;
window.loadGoogleAnalytics = loadGoogleAnalytics;
window.sendCustomEvent = sendCustomEvent;
window.sendPageView = sendPageView;
window.sendUserEngagement = sendUserEngagement;
window.sendClickEvent = sendClickEvent;
window.sendAffiliateClick = sendAffiliateClick;
window.getVisitorAnalytics = getVisitorAnalytics; 