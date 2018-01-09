var firebase = require('firebase');
var configFile = require('./config.js');
var pyshell = require('python-shell');
var http = require('http');
var fs = require('fs');

var server = http.createServer(function(req, res) {
    fs.readFile('index.html', 'utf-8', function(error, content) {
        res.writeHead(200, {"Content-Type": "text/html"});
        res.end(content);
    });
});
var io = require('socket.io').listen(server);
server.listen(8080);

io.on('connection', function(socket) 
{
  socket.emit('sendStatus', {messages: 'Please check in' });

function resetCheckedIn() {
  socket.emit('sendStatus', {messages: 'Please check in' });

}

var resetMessage;
function checkedIn() {
  clearTimeout(resetMessage)
  resetMessage = setTimeout(resetCheckedIn, 2000)
}

firebase.initializeApp(configFile.config);  //initialize Firebase

 console.log("Please check in");
 var cardID;
 rfid = new pyshell('main.py');
 rfid.on('message', function(message)
 {
    if (message == "E1" || message == "E2") {
    console.log('Card is not valid' + 'Errorcode:' + message)
    return; 
 }
    cardID = message;
    var obj = JSON.parse(message)
    if (obj.payload=="Unknown Card" || obj.payload==" No Authentication") 
      {
        console.log(obj.payload)
        return;
      }
    cardID = obj.payload; 
    initializeAndAuthenticate(); 

 });

var database = firebase.database(); //get reference to the database service
function initializeAndAuthenticate() 
{

  firebase.auth().signInWithEmailAndPassword(configFile.email, configFile.pass).catch(function(error)

  { // Handle Errors here.
    var errorCode = error.code;
    var errorMessage = error.message;

    console.log("authError Here:");
    console.log(errorCode);
    console.log(errorMessage);
  });
 console.log("Authenticating...");
 validiateAuthtentication();
}

function validiateAuthtentication()
{ 
  console.log("Validating Authentication...");
  firebase.auth().onAuthStateChanged(function(user) 
  {
    if (user!=null)  
    {
      console.log("Logged in succesfully"); //check if authtication succeeded
      checkIfCardIsActive(cardID);
      return;  
    } 
  });
}
 
 function checkIfCardIsActive(cardID) 
{
  //socket.emit('sendStatus', { messages: 'Checking if card is active....'});  
  //console.log("Checking if card is active....")
  database.ref('cardinfo/' + cardID).once('value').then(function(snapshot)
  {
    var cardStatus = (snapshot.val().status);
    var uuid = (snapshot.val().uuid);
    if (cardStatus !== 'active') //check if card is activated by the administrator
    {
      console.log("Card is not active"); 
    } 

    else 
    {
      console.log("Checking if user is Responder..."); 
      checkIfUserIsResponder(uuid);   
    }
  });
}

function checkIfUserIsResponder(uuid)  //It is important that a user is a responder, because only responders can check in (to get alerts)
{
  database.ref('userinfo/' + 'userstatus/' + uuid + '/responder').once('value').then(function(snapshot)
  {
    var responder = (snapshot.val());
    if (responder !== true) 
    {
      console.log("You are not authorized to check in!"); 
    }

    else 
    {
      changeStatus(uuid);
    }
  });  
};
 
function changeStatus(uuid) //write the status data to the Firbase Database. 
{
  database.ref('currentstatus/' + uuid).once('value').then(function(snapshot) 
  {
    var onLocation = !(snapshot.val().onLocation);
      database.ref('currentstatus/'+ uuid).set( 
      {
        onLocation: onLocation,
        uuid: uuid //for set function it is mandotory to write to all database values even if it does'nt change    
      });
      if (onLocation==true) 
      {
        console.log("Succesfully checked in!")
        database.ref('userinfo/' + 'usergeninfo/' + uuid + '/fname').once('value').then(function(snapshot)
        { 
          var fname = (snapshot.val()); 
          socket.emit('sendStatus', { messages: 'Welcome\xa0' + fname });
          console.log('Welkom\xa0' + fname);
          checkedIn()
          return;
        });    
      }
    else 
      {
        console.log("Succesfully checked out!")
        database.ref('userinfo/' + 'usergeninfo/' + uuid + '/fname').once('value').then(function(snapshot)
        {
          var fname2 = (snapshot.val()); 
          socket.emit('sendStatus', { messages: 'Good bye\xa0' + fname2 + "!"});
          console.log('Good bye\xa0' + fname2 + "!");
          checkedIn()
          return;

        });   
      } 
  });
 }
}); //close bracket for emit function