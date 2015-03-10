'use strict';

var fs = require('fs');
var path = require('path');
var root = path.resolve(__dirname, '../../');

module.exports = {
  home: {
    handler: function(request, reply) {
      var jsonFile = path.resolve(root, 'html/forecast/beijing.json');
      fs.readFile(jsonFile, 'utf8', function(err, data) {
        if (err) {
          return console.log(err);
        }
        console.log(data);
        reply.view('home', {
          title: 'Super Informative About Page',
          json: data
        });
      });

    },
    id: 'home'
  },
  about: {
    handler: function(request, reply) {
      reply.view('about', {
        title: 'Super Informative About Page'
      });
    },
    id: 'about'
  },
  missing: {
    handler: function(request, reply) {
      reply.view('404', {
        title: 'Total Bummer 404 Page'
      }).code(404);
    },
    id: '404'
  }

};