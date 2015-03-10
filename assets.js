// assets to be used by the 'hapi-assets' module based on process.env.NODE_ENV
module.exports = {
    development: {
        js: ['/js/test-one.js', '/js/test-two.js'],
        css: ['/css/reset.css', '/css/styles.css']
    },
    production: {
        js: ['js/scripts.js'],
        css: ['/css/styles.css']
    }
};