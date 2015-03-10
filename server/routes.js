var controllers = require('./controllers');

module.exports = [{
  method: 'GET',
  path: '/',
  config: controllers.base.home
}, {
  method: 'GET',
  path: '/about',
  config: controllers.base.about
}, {
  method: 'GET',
  path: '/{path*}',
  config: controllers.base.missing
}, {
  method: 'GET',
  path: '/partials/{path*}',
  config: controllers.assets.partials
}, {
  method: 'GET',
  path: '/images/{path*}',
  config: controllers.assets.images
}, {
  method: 'GET',
  path: '/css/{path*}',
  config: controllers.assets.css
}, {
  method: 'GET',
  path: '/js/{path*}',
  config: controllers.assets.js
}];