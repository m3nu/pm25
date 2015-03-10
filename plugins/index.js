var path = require('path');
var assets = require(path.normalize(__dirname + '/../') + 'assets');
module.exports = [
  //set up good to log every kind of event. Change according to your needs.
  {
    register: require('good'),
    options: {
      reporters: [{
        reporter: require('good-console'),
        args: [{
          log: '*',
          request: '*',
          ops: '*',
          error: '*'
        }]
      }]
    }
  }, {
    register: require('hapi-assets'),
    options: assets
  }, {
    register: require('hapi-named-routes')
  }, {
    register: require('hapi-cache-buster')
  }, {
    register: require('hapi-auth-basic')
  }
  //require additional plugins here
];