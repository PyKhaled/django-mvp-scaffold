const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

const handlers = {};
const elements = {
  'notification-control': {
    dataset: {previewUrl: '/notifications/preview/'},
    addEventListener: (event, handler) => { handlers[event] = handler; },
  },
  'notifications-toggle': {setAttribute: (key, value) => { elements.label = value; }},
  'notification-count': {textContent: '1', hidden: false},
  'notification-items': {innerHTML: 'original', contains: (value) => value === 'focused-item'},
};
let interval;
let payload = {unread_count: 3, html: 'updated'};
let redirected = false;
let offline = false;
let calls = 0;
const document = {
  hidden: false, activeElement: null,
  getElementById: (id) => elements[id],
  addEventListener: (event, handler) => { handlers[event] = handler; },
};
vm.runInNewContext(fs.readFileSync('product/static/js/notifications.js', 'utf8'), {
  document,
  window: {setInterval: (handler, delay) => {
    assert.equal(delay, 30000);
    interval = handler;
  }},
  fetch: async (url, options) => {
    calls += 1;
    assert.equal(url, '/notifications/preview/');
    assert.equal(options.credentials, 'same-origin');
    if (offline) throw new Error('offline');
    return {ok: true, redirected, json: async () => payload};
  },
});
(async () => {
  await handlers['show.bs.dropdown']();
  assert.equal(elements['notification-count'].textContent, 3);
  assert.equal(elements.label, 'Notifications, 3 unread');
  assert.equal(elements['notification-items'].innerHTML, 'updated');

  document.activeElement = 'focused-item';
  payload = {unread_count: 0, html: 'new'};
  await interval();
  assert.equal(elements['notification-count'].hidden, true);
  assert.equal(elements.label, 'Notifications');
  assert.equal(elements['notification-items'].innerHTML, 'updated');

  document.hidden = true;
  const before = calls;
  await interval();
  assert.equal(calls, before);
  document.hidden = false;
  document.activeElement = null;

  redirected = true;
  await interval();
  assert.equal(elements['notification-items'].innerHTML, 'updated');
  redirected = false;
  offline = true;
  await interval();
  assert.equal(elements['notification-items'].innerHTML, 'updated');
  offline = false;
  handlers.visibilitychange();
  await new Promise(setImmediate);
  assert.equal(elements['notification-items'].innerHTML, 'new');
  console.log('Notification refresh passed: count, focus, hidden tab, login redirect, offline recovery.');
})().catch((error) => { console.error(error); process.exitCode = 1; });
