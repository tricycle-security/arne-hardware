var http = require('http');
var fs = require('fs');
var server = http.createServer(function(req, res) {
    fs.readFile('html/index.html', 'utf-8', function(error, content) {
        res.writeHead(200, {"Content-Type": "text/html"});
        res.end(content);
    });
});

function sendStatus(message) {
var io = require('socket.io').listen(server); // Loading socket.io
io.sockets.on('connection', function (socket) { 
console.log('A client is connected!'); // When a client connects, we note it in the console
  
    console.log('message from main:', message);
    
    socket.emit('message', message); // Emit on the opened socket.

//socket.emit('message', { content: 'You are connected!' });
 });
}
server.listen(8080);
