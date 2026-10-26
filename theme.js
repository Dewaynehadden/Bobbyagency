/* Apply preference before styles load to avoid a bright flash on dark visits. */
(() => {
  const key = 'bobbyagency-theme';
  const system = window.matchMedia('(prefers-color-scheme: dark)');
  let preference;
  try { preference = localStorage.getItem(key); } catch (_) { /* Storage may be disabled. */ }
  if (!['light', 'dark'].includes(preference)) preference = null;
  function apply(theme) {
    document.documentElement.dataset.theme = theme;
    document.documentElement.style.colorScheme = theme;
    const button = document.querySelector('.theme-toggle');
    if (button) {
      const dark = theme === 'dark';
      button.setAttribute('aria-pressed', String(dark));
      button.setAttribute('aria-label', `Switch to ${dark ? 'day' : 'night'} mode`);
      button.title = `Switch to ${dark ? 'day' : 'night'} mode`;
      button.querySelector('.theme-symbol').textContent = dark ? '☀' : '☾';
    }
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.content = theme === 'dark' ? '#10141d' : '#faf8f3';
  }
  apply(preference || (system.matches ? 'dark' : 'light'));
  document.addEventListener('DOMContentLoaded', () => {
    apply(document.documentElement.dataset.theme);
    document.querySelector('.theme-toggle')?.addEventListener('click', () => {
      preference = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
      try { localStorage.setItem(key, preference); } catch (_) { /* Keep the choice for this visit. */ }
      apply(preference);
    });
  });
  system.addEventListener('change', event => { if (!preference) apply(event.matches ? 'dark' : 'light'); });
  window.addEventListener('storage', event => {
    if (event.key === key) {
      preference = ['light', 'dark'].includes(event.newValue) ? event.newValue : null;
      apply(preference || (system.matches ? 'dark' : 'light'));
    }
  });
})();
