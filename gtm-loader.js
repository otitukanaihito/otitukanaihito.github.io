// Google Tag Manager (GTM) deferred loader
// How to override container ID:
// 1) URL parameter: ?gtm=GTM-XXXX
// 2) window.GTM_CONTAINER_ID = 'GTM-XXXX'
// 3) localStorage.setItem('GTM_CONTAINER_ID','GTM-XXXX')
// Default below is set based on user's provided container ID.

(function(){
  'use strict';

  function resolveGtmId(){
    try {
      var params = new URLSearchParams(window.location.search);
      var fromQuery = params.get('gtm');
      if (fromQuery && /^GTM-[A-Z0-9]+$/.test(fromQuery)) return fromQuery;
    } catch (_) {}

    if (typeof window.GTM_CONTAINER_ID === 'string' && /^GTM-[A-Z0-9]+$/.test(window.GTM_CONTAINER_ID)) {
      return window.GTM_CONTAINER_ID;
    }

    try {
      var ls = localStorage.getItem('GTM_CONTAINER_ID');
      if (ls && /^GTM-[A-Z0-9]+$/.test(ls)) return ls;
    } catch (_) {}

    // Default container ID provided by the user (can be changed safely)
    return 'GTM-MDWZM4DL';
  }

  function loadGtm(containerId){
    if (!containerId || !/^GTM-[A-Z0-9]+$/.test(containerId)) {
      console.warn('GTM container ID is invalid or missing.');
      return;
    }

    if (document.getElementById('gtm-loader-script')) return; // avoid duplicate

    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({ 'gtm.start': new Date().getTime(), event: 'gtm.js' });

    var s = document.createElement('script');
    s.id = 'gtm-loader-script';
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtm.js?id=' + encodeURIComponent(containerId);
    document.head.appendChild(s);

    // Optional: inject noscript fallback placeholder (not functional without full iframe)
  }

  try {
    loadGtm(resolveGtmId());
  } catch(e) {
    console.warn('Failed to load GTM:', e);
  }
})();


