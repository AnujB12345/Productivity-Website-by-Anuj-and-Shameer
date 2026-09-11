self.addEventListener('push', function(event) {
    let data = {};
    try {
        data = event.data.json();
    } catch (e) {
        data = { title: 'Productivity App', body: event.data ? event.data.text() : 'You have a new notification' };
    }

    const options = {
        body: data.body || '',
        data: { url: data.url || '/' },
    };

    event.waitUntil(
        self.registration.showNotification(data.title || 'Productivity App', options)
    );
});

self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    const targetUrl = event.notification.data && event.notification.data.url ? event.notification.data.url : '/';
    event.waitUntil(
        clients.matchAll({ type: 'window' }).then(function(clientList) {
            for (const client of clientList) {
                if (client.url === targetUrl && 'focus' in client) return client.focus();
            }
            if (clients.openWindow) return clients.openWindow(targetUrl);
        })
    );
});