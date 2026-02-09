// Admin panel JS (no inline scripts due to strict CSP on /admin)
(function () {
  function ready(fn) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', fn);
    } else {
      fn();
    }
  }

  ready(function () {
    // ===== Mobile nav drawer =====
    var body = document.body;
    var btn = document.querySelector('.nav-toggle');
    var drawer = document.getElementById('navDrawer');
    var overlay = document.querySelector('.nav-overlay');

    function setOpen(open) {
      if (!body) return;
      body.setAttribute('data-nav-open', open ? '1' : '0');
      if (drawer) drawer.setAttribute('aria-hidden', open ? 'false' : 'true');
      if (btn) btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    }

    if (btn && drawer && overlay) {
      btn.addEventListener('click', function () {
        var isOpen = body.getAttribute('data-nav-open') === '1';
        setOpen(!isOpen);
      });

      document.querySelectorAll('[data-nav-close]').forEach(function (el) {
        el.addEventListener('click', function () {
          setOpen(false);
        });
      });

      drawer.querySelectorAll('a').forEach(function (a) {
        a.addEventListener('click', function () {
          setOpen(false);
        });
      });

      document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') setOpen(false);
      });

      setOpen(false);
    }

    // ===== Confirmations (CSP-safe) =====
    document.addEventListener(
      'submit',
      function (e) {
        var form = e.target;
        if (!form || !form.getAttribute) return;
        var msg = form.getAttribute('data-confirm');
        if (!msg) return;
        if (!window.confirm(msg)) {
          e.preventDefault();
          e.stopPropagation();
        }
      },
      true
    );

    // ===== Users page: client-side search =====
    var input = document.getElementById('userSearch');
    if (input) {
      input.addEventListener('input', function () {
        var q = (input.value || '').trim().toLowerCase();
        var items = document.querySelectorAll('#userList [data-search]');
        items.forEach(function (el) {
          var hay = el.getAttribute('data-search') || '';
          var ok = !q || hay.indexOf(q) !== -1;
          el.style.display = ok ? '' : 'none';
        });
      });
    }
  });
})();

