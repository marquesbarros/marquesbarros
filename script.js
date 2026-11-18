(() => {
  const button = document.querySelector('.menu-toggle');
  const menu = document.getElementById('site-menu');
  if (button && menu) {
    // Collapse only after keyboard and pointer controls are operational.
    const setOpen = open => {
      button.setAttribute('aria-expanded', String(open));
      menu.classList.toggle('is-open', open);
    };
    button.addEventListener('click', () => setOpen(button.getAttribute('aria-expanded') !== 'true'));
    menu.addEventListener('click', event => {
      const link = event.target.closest('a');
      if (!link) return;
      const wasOpen = button.getAttribute('aria-expanded') === 'true';
      setOpen(false);
      if (wasOpen && link.hash && link.pathname === location.pathname) {
        document.getElementById(decodeURIComponent(link.hash.slice(1)))?.focus({ preventScroll: true });
      }
    });
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && button.getAttribute('aria-expanded') === 'true') {
        setOpen(false);
        button.focus();
      }
    });
    document.addEventListener('click', event => {
      if (!event.target.closest('.site-header')) setOpen(false);
    });
    window.matchMedia('(min-width: 901px)').addEventListener('change', () => setOpen(false));
    document.documentElement.classList.add('js-nav');
  }
  if (!('IntersectionObserver' in window) || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const observer = new IntersectionObserver((entries, obs) => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('is-visible');
      obs.unobserve(entry.target);
    });
  }, { threshold: 0.08 });
  document.querySelectorAll('.reveal').forEach(item => observer.observe(item));
})();
