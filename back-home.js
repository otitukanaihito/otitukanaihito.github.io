// Back to Home floating button for blog pages
(function () {
  try {
    document.addEventListener('DOMContentLoaded', function () {
      // Avoid adding on the homepage
      if (location.pathname.endsWith('/index.html') || location.pathname === '/' ) return;

      var link = document.createElement('a');
      link.href = '../index.html';
      link.textContent = '← ホーム';
      link.setAttribute('aria-label', 'ホームに戻る');
      link.style.position = 'fixed';
      link.style.right = '16px';
      link.style.bottom = window.innerWidth < 768 ? '72px' : '20px';
      link.style.zIndex = '9999';
      window.addEventListener('resize', function() {
        link.style.bottom = window.innerWidth < 768 ? '72px' : '20px';
      });
      link.style.padding = '9px 14px';
      link.style.borderRadius = '0';
      link.style.background = '#111111';
      link.style.color = '#FAFAF7';
      link.style.fontFamily = "'IBM Plex Mono', monospace";
      link.style.fontSize = '0.7rem';
      link.style.fontWeight = '700';
      link.style.textTransform = 'uppercase';
      link.style.letterSpacing = '0.08em';
      link.style.border = '3px solid #111111';
      link.style.boxShadow = '4px 4px 0px #111111';
      link.style.textDecoration = 'none';
      link.style.transition = 'box-shadow 0.12s, transform 0.12s';
      link.onmouseenter = function(){
        link.style.background = '#FF4D3D';
        link.style.boxShadow = '6px 6px 0px #111111';
        link.style.transform = 'translate(-2px,-2px)';
      };
      link.onmouseleave = function(){
        link.style.background = '#111111';
        link.style.boxShadow = '4px 4px 0px #111111';
        link.style.transform = 'translate(0,0)';
      };
      document.body.appendChild(link);

      // Keyboard shortcut: Alt+H to return home
      document.addEventListener('keydown', function (e) {
        if (e.altKey && (e.key === 'h' || e.key === 'H')) {
          window.location.href = '../index.html';
        }
      });
    });
  } catch (e) {
    // no-op
  }
})();


