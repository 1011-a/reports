(() => {
  const root = document.documentElement;
  const toggle = document.getElementById('theme-toggle');
  if (!toggle) return;

  const apply = (mode) => {
    root.dataset.theme = mode;
    localStorage.setItem('theme', mode);
  };

  toggle.addEventListener('click', () => {
    const next = root.dataset.theme === 'dark' ? 'light' : 'dark';
    apply(next);
  });
})();
