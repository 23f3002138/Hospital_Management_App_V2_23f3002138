
const CACHE_NAME = 'hospital-management-v1'
const urlsToCache = [
  '/',
  '/static/css/app.css',
  '/static/js/app.js',
  '/static/js/chunk-vendors.js'
]

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        return cache.addAll(urlsToCache)
      })
  )
})

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        
        return response || fetch(event.request)
      })
  )
})
