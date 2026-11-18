(() => {
  const items = document.querySelectorAll('.reveal, .reveal-image');
  if (!('IntersectionObserver' in window)) {
    items.forEach(item => item.classList.add('is-visible'));
    return;
  }
  const observer = new IntersectionObserver((entries, obs) => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      entry.target.classList.add('is-visible');
      obs.unobserve(entry.target);
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -5% 0px' });
  items.forEach(item => observer.observe(item));
})();

(async () => {
  const img = document.getElementById('riima-screenshot');
  if (!img) return;
  try {
    const files = Array.from({ length: 11 }, (_, i) =>
      './assets/riima-interface/chunk-' + String(i).padStart(2, '0') + '.txt'
    );
    const parts = await Promise.all(files.map(url => fetch(url).then(r => {
      if (!r.ok) throw new Error('RIIMA screenshot chunk failed: ' + url);
      return r.text();
    })));
    const binary = atob(parts.join(''));
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
    img.src = URL.createObjectURL(new Blob([bytes], { type: 'image/webp' }));
  } catch (error) {
    console.error(error);
    img.alt = 'Captura da interface do RIIMA indisponível.';
  }
})();


(async () => {
  const img = document.getElementById('saa-targets-figure');
  if (!img) return;
  try {
    const files = Array.from({ length: 4 }, (_, i) =>
      './assets/saa-targets/chunk-' + String(i).padStart(2, '0') + '.txt'
    );
    const parts = await Promise.all(files.map(url => fetch(url).then(r => {
      if (!r.ok) throw new Error('SAA figure chunk failed: ' + url);
      return r.text();
    })));
    const binary = atob(parts.join(''));
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
    img.src = URL.createObjectURL(new Blob([bytes], { type: 'image/webp' }));
  } catch (error) {
    console.error(error);
    img.alt = 'Figura da Anomalia Magnética do Atlântico Sul indisponível.';
  }
})();
