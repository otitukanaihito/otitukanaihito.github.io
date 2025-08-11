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
      link.style.right = '20px';
      link.style.bottom = '20px';
      link.style.zIndex = '9999';
      link.style.padding = '10px 14px';
      link.style.borderRadius = '999px';
      link.style.background = 'linear-gradient(135deg,#4f46e5,#7c3aed)';
      link.style.color = '#fff';
      link.style.fontWeight = '700';
      link.style.boxShadow = '0 10px 30px rgba(79,70,229,.35)';
      link.style.textDecoration = 'none';
      link.style.transition = 'transform .2s ease, box-shadow .2s ease';
      link.onmouseenter = function(){
        link.style.transform = 'translateY(-2px)';
        link.style.boxShadow = '0 14px 40px rgba(79,70,229,.45)';
      };
      link.onmouseleave = function(){
        link.style.transform = 'translateY(0)';
        link.style.boxShadow = '0 10px 30px rgba(79,70,229,.35)';
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


