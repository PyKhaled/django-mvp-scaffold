(() => {
  const control = document.getElementById('notification-control');
  if (!control) return;
  const toggle = document.getElementById('notifications-toggle');
  const count = document.getElementById('notification-count');
  const items = document.getElementById('notification-items');
  let pending = false;
  async function refresh() {
    if (pending || document.hidden) return;
    pending = true;
    try {
      const response = await fetch(control.dataset.previewUrl, {
        credentials: 'same-origin', headers: {Accept: 'application/json'},
      });
      if (!response.ok || response.redirected) return;
      const data = await response.json();
      count.textContent = data.unread_count;
      count.hidden = data.unread_count === 0;
      toggle.setAttribute('aria-label', data.unread_count ? `Notifications, ${data.unread_count} unread` : 'Notifications');
      // HTML comes from our authenticated, autoescaped server template.
      // Preserve focused actions while someone is using the dropdown.
      if (!items.contains(document.activeElement)) items.innerHTML = data.html;
    } catch (_) {
      // Keep the existing preview usable when the connection is unavailable.
    } finally {
      pending = false;
    }
  }
  control.addEventListener('show.bs.dropdown', refresh);
  document.addEventListener('visibilitychange', () => { if (!document.hidden) refresh(); });
  window.setInterval(refresh, 30000);
})();
