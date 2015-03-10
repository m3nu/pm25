'use strict';

var Hapi = require('hapi');
var Bcrypt = require('bcrypt');

var path = require('path');

var settings = require('./config/default');

var routes = require('./server/routes');
var plugins = require('./plugins');

var server = new Hapi.Server({
  connections: {
    routes: {
      cors: settings.cors
    }
  }
});
server.connection({
  port: settings.port,
  host: settings.host
});

server.views({
  engines: {
    html: require('swig')
  },
  path: './server/views'
});


// Export the server to be required elsewhere.
module.exports = server;

var users = {
    fotoverite: {
        username: 'fotoverite',
        password: '$2a$10$QKxFLqmDdcY6I7n27O7id.tqT.d1wWLnz.dbSiIXqWmkP17npcXXK',   // 'secret'
        name: 'Matthew Bergman',
        id: '2133d32a'
    }
};

var validate = function (username, password, callback) {

    var user = users[username];
    if (!user) {
        return callback(null, false);
    }

    Bcrypt.compare(password, user.password, function (err, isValid) {

        callback(err, isValid, { id: user.id, name: user.name });
    });
};



var setup = function(done) {


  //Register all plugins
  server.register(plugins, function(err) {
    if (err) {
      throw err; // something bad happened loading a plugin
    }
  });

  server.auth.strategy('simple', 'basic', { validateFunc: validate });

   // Add the server routes
  server.route(routes);
  done();

};

var start = function() {
  server.start(function() {
    server.log('info', 'Server running at: ' + server.info.uri);
  });
};

// If someone runs: "node server.js" then automatically start the server
if (path.basename(process.argv[1], '.js') == path.basename(__filename, '.js')) {
  setup(function() {
    start();
  });
}