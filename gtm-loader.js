// Google Tag Manager (GTM) deferred loader
// How to override container ID:
// 1) URL parameter: ?gtm=GTM-XXXX
// 2) window.GTM_CONTAINER_ID = 'GTM-XXXX'
// 3) localStorage.setItem('GTM_CONTAINER_ID','GTM-XXXX')
// Default below is set based on user's provided container ID.

(function(){
  'use strict';

  // Security: Disallow overriding via URL or localStorage to prevent arbitrary container injection
  function resolveGtmId(){
    var DEFAULT_ID = 'GTM-MDWZM4DL';
    var ALLOWLIST = [DEFAULT_ID];

    // Optional: allow explicit runtime override ONLY if it matches allowlist
    if (typeof window.GTM_CONTAINER_ID === 'string' && /^GTM-[A-Z0-9]+$/.test(window.GTM_CONTAINER_ID)) {
      if (ALLOWLIST.indexOf(window.GTM_CONTAINER_ID) !== -1) {
        return window.GTM_CONTAINER_ID;
      }
    }

    return DEFAULT_ID;
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



