// Teleprompter Yahir · service worker
// App (index, iconos): guardada para abrir sin internet y se actualiza sola en segundo plano.
// scripts.json: siempre se intenta bajar fresco; si no hay internet, usa la última copia.
const V = 'tp-v1';
const SHELL = ['./', 'index.html', 'manifest.webmanifest', 'icon-192.png', 'icon-512.png', 'icon-180.png'];
const JSON_KEY = new Request('scripts.json');

self.addEventListener('install', e => {
  e.waitUntil(caches.open(V).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== V).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;
  if (url.pathname.endsWith('/scripts.json')){
    e.respondWith((async () => {
      const cache = await caches.open(V);
      try{
        const fresh = await fetch(req, {cache: 'no-store'});
        if (fresh.ok) await cache.put(JSON_KEY, fresh.clone());
        return fresh;
      }catch(err){
        const hit = await cache.match(JSON_KEY);
        if (hit){
          const h = new Headers(hit.headers); h.set('x-tp-cache', '1');
          return new Response(await hit.blob(), {status: 200, headers: h});
        }
        throw err;
      }
    })());
    return;
  }
  e.respondWith((async () => {
    const cache = await caches.open(V);
    const hit = await cache.match(req, {ignoreSearch: true});
    const net = fetch(req).then(r => { if (r.ok) cache.put(req, r.clone()); return r; }).catch(() => null);
    return hit || (await net) || new Response('Sin conexión', {status: 503});
  })());
});
