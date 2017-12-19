var http = require('http');
var fs = require('fs');


// Loading the index file . html displayed to the client
var server = http.createServer(function(req, res) {
    fs.readFile('html/index.html', 'utf-8', function(error, content) {
        res.writeHead(200, {"Content-Type": "text/html"});
        res.end(content);
    });
});



module.exports.sendStatus = function sendStatus(message) {
var io = require('socket.io').listen(server); // Loading socket.io
io.sockets.on('connection', function (socket) { 
  console.log('A client is connected!'); // When a client connects, we note it in the console
  var incremental = 0;
  setInterval(function () {
      console.log('message from main:', message);
      
      socket.emit('update-value', message); // Emit on the opened socket.
      incremental++;
  }, 1000);
  //socket.emit('message', { content: 'You are connected!' });
});

}
server.listen(8080);
