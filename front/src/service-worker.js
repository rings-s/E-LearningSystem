import { version } from '$app/env';
import { immutable, assets } from '$app/manifest';

const CACHE = `cache-${version}`;
const ASSETS = [...immutable, ...assets].map((file) => file.path);

self.addEventListener('install', (event) => {
	event.waitUntil(caches.open(CACHE).then((cache) => cache.addAll(ASSETS)));
});

self.addEventListener('activate', (event) => {
	event.waitUntil(
		caches.keys().then(async (keys) => {
			for (const key of keys) {
				if (key !== CACHE) await caches.delete(key);
			}
		})
	);
});
