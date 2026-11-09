// Teleprompter Yahir · service worker
// App (index, iconos): con internet siempre baja la versión más nueva; sin internet abre la copia guardada.
// scripts.json: siempre se intenta bajar fresco; si no hay internet, usa la última copia.
const V = 'tp-v11';
const SHELL = ['./', 'index.html', 'manifest.webmanifest', 'icon-192.png', 'icon-512.png', 'icon-180.png', 'icon-512-maskable.png',
  'fonts/inter.woff2', 'fonts/manrope.woff2', 'fonts/space-grotesk.woff2', 'fonts/sora.woff2', 'fonts/orbitron.woff2',
  'fonts/oswald.woff2', 'fonts/playfair-display.woff2', 'fonts/lora.woff2', 'fonts/jetbrains-mono.woff2'];
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
    const isShell = req.mode === 'navigate' || /\.(html|webmanifest|js)$/.test(url.pathname) || url.pathname.endsWith('/');
    const net = fetch(req, isShell ? {cache: 'no-cache'} : undefined).then(r => { if (r.ok) cache.put(req, r.clone()); return r; }).catch(() => null);
    if (isShell){
      /* red primero (máx. 3 s) para que los cambios de diseño lleguen enseguida; si falla, copia guardada */
      const fresh = await Promise.race([net, new Promise(res => setTimeout(() => res(null), 3000))]);
      return fresh || hit || (await net) || new Response('Sin conexión', {status: 503});
    }
    return hit || (await net) || new Response('Sin conexión', {status: 503});
  })());
});
