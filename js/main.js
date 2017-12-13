var firebase = require('firebase');
var configFile = require('./config.js');
var pyshell = require('python-shell');

 firebase.initializeApp(configFile.config);  //initialize Firebase
 console.log("Please check in");
 
 var cardID;
 rfid = new pyshell('main.py');
 rfid.on('message', function(message)

 {
  cardID = message; 
  console.log("CardID:" + cardID);
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
      
    } else 
     {
      console.log("Not logged in");
     }
  });
}
 
 function checkIfCardIsActive(cardID) 
{
  database.ref('cardinfo/' + cardID).once('value').then(function(snapshot)
  {
    var cardStatus = (snapshot.val().status);
    var uuid = (snapshot.val().uuid);
    if (cardStatus !== 'active') //check if card is activated by the administrator
    {
      throw new Error('Card is not active!');
    } 

    else 
    {
      checkIfUserIsResponder(uuid);
      console.log("Checked in succesfully");  
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
      throw new Error('User is not a responder');
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
  });
}