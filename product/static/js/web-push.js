(() => {
    const panel = document.getElementById('web-push-controls');
    if (!panel) return;
    const status = panel.querySelector('[role="status"]');
    const enable = panel.querySelector('[data-enable]');
    const disable = panel.querySelector('[data-disable]');
    const supported = window.isSecureContext && 'serviceWorker' in navigator && 'PushManager' in window && 'Notification' in window;
    if (!supported) {
        status.textContent = 'Browser notifications are unavailable in this browser or connection.';
        enable.disabled = disable.disabled = true;
        return;
    }
    const save = async (data) => {
        const response = await fetch(panel.dataset.subscription, {
            method: 'POST', credentials: 'same-origin',
            headers: {'Content-Type': 'application/json', 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value},
            body: JSON.stringify(data),
        });
        if (!response.ok) throw new Error('Could not save browser notification settings.');
    };
    enable.addEventListener('click', async () => {
        enable.disabled = true;
        try {
            const permission = await Notification.requestPermission();
            if (permission !== 'granted') throw new Error('Allow notifications in your browser settings to enable delivery.');
            const response = await fetch(panel.dataset.config, {credentials: 'same-origin'});
            if (!response.ok) throw new Error('Could not load notification configuration.');
            const config = await response.json();
            if (!config.public_key) throw new Error('Browser notifications are not configured yet.');
            const registration = await navigator.serviceWorker.register(panel.dataset.worker, {scope: '/'});
            await navigator.serviceWorker.ready;
            let subscription = await registration.pushManager.getSubscription();
            if (!subscription) {
                const encoded = config.public_key.replace(/-/g, '+').replace(/_/g, '/');
                const binary = atob(encoded + '='.repeat((4 - encoded.length % 4) % 4));
                subscription = await registration.pushManager.subscribe({userVisibleOnly: true, applicationServerKey: Uint8Array.from(binary, c => c.charCodeAt(0))});
            }
            await save(subscription.toJSON());
            status.textContent = 'This browser is enabled. Choose categories below and save your preferences.';
        } catch (error) { status.textContent = error.message; }
        finally { enable.disabled = false; }
    });
    disable.addEventListener('click', async () => {
        disable.disabled = true;
        try {
            const registration = await navigator.serviceWorker.getRegistration('/');
            const subscription = registration && await registration.pushManager.getSubscription();
            if (subscription) {
                await save({remove: true, endpoint: subscription.endpoint});
                await subscription.unsubscribe();
            }
            status.textContent = 'This browser is disabled.';
        } catch (error) { status.textContent = error.message; }
        finally { disable.disabled = false; }
    });
})();
