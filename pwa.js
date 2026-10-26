'use strict';
(() => {
  const button = document.querySelector('.pwa-install');
  const dialog = document.querySelector('#install-dialog');
  let installPrompt = null;
  const standalone = window.matchMedia('(display-mode: standalone)');
  const installed = () => standalone.matches || window.navigator.standalone === true;
  function update() { if (button) button.hidden = installed(); }
  window.addEventListener('beforeinstallprompt', event => {
    event.preventDefault(); installPrompt = event; update();
  });
  window.addEventListener('appinstalled', () => { installPrompt = null; if (dialog?.open) dialog.close(); update(); });
  standalone.addEventListener('change', update);
  button?.addEventListener('click', async () => {
    if (installPrompt) {
      const prompt = installPrompt; installPrompt = null;
      try { await prompt.prompt(); await prompt.userChoice; } catch (_) { dialog.showModal(); }
    } else dialog.showModal();
  });
  dialog?.querySelector('[data-install-close]').addEventListener('click', () => dialog.close());
  dialog?.addEventListener('click', event => { if (event.target === dialog) { const rect = dialog.getBoundingClientRect(); if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close(); } });
  update();
  if ('serviceWorker' in navigator) window.addEventListener('load', () => {
    navigator.serviceWorker.register('sw.js', { scope: './', updateViaCache: 'none' }).catch(() => { /* The website still works if offline support is unavailable. */ });
  });
})();
