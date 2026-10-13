self.addEventListener('push', (event) => {
    const data = event.data ? event.data.json() : {};
    event.waitUntil(self.registration.showNotification(data.title || 'New update', {
        body: data.body || 'Open your notifications to see the update.',
        tag: 'account-updates',
        data: { url: '/notifications/' },
    }));
});
self.addEventListener('notificationclick', (event) => {
    event.notification.close();
    event.waitUntil(self.clients.openWindow('/notifications/'));
});
