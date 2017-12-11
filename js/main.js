var firebase = require('firebase');
var configFile = require('./config.js');
var pyshell = require('python-shell');

 firebase.initializeApp(configFile.config); 
 console.log("Please check in");
 var cardID;
 rfid = new pyshell('main.py');
 rfid.on('message', function(message)

 {
  cardID = message; 
  console.log("CardID:" + cardID);
  initializeAndAuthenticate(); 

 });

function initializeAndAuthenticate() 
{
  //initialize Firebase
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
 // cardID = 'EkbgGG7UodDNotGb' //cardID of Hans Hoogerwerf
 var database = firebase.database(); //get reference to the database service

 function checkIfCardIsActive(cardID) 
{
  database.ref('cardinfo/' + cardID + '/status').once('value').then(function(snapshot)
  
  {
    var cardIDcheck = (snapshot.val());
    console.log(cardIDcheck);
    if (cardIDcheck !== 'active') //check if card is activated by the administrator
    {
      throw new Error('Card is not active!');
    } 

    else 
    {
      changeStatus(cardID); //send if user is checked in or checked out
      console.log("Checked in succesfully");  
    }
  });
}
  function changeStatus(cardID) //write the status data to the Firbase Database. 
  {
    database.ref('currentstatus/'+ cardID).set( 
    {
      cardID: cardID,
      onLocation: true
      
    });
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

