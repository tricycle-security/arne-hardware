var firebase = require('firebase');
var configFile = require('./config.js');
var html = require('./server.js');

/*
html1="./html/pleasecheckin.html"
html2="./html/checkedin.html"
html3="./html/checkedout.html"
*/
//html.startWebserver();
html.sendStatus('Please check in');
firebase.initializeApp(configFile.config);  //initialize Firebase

 console.log("Please check in");
 var cardID = "EkbgGG7UodDNotGb"
 initializeAndAuthenticate(); 

 /*var pyshell = require('python-shell');
 rfid = new pyshell('main.py');
 rfid.on('message', function(message)

 {
  cardID = message; 
  console.log("CardID:" + cardID);
  

 });
*/
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
{ console.log("Checking if card is active....")
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
      if (onLocation==true) {
      console.log("Succesfully checked in!") 
      html.sendStatus('Succesfully checked in!'); 
    }
    else {
      console.log("Succesfully checked out!")
      html.sendStatus('Succesfully checked out!'); 
    }
  });
}