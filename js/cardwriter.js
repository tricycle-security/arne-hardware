var firebase = require('firebase');
var configFile = require('./configcardwriter.js');

firebase.initializeApp(configFile.config);  //initialize Firebase
initializeAndAuthenticate();
validiateAuthtentication();

var cardID;
rfid = new pyshell('preparecard.py');
rfid.on('message', function(message)
{
 if (message == "E1" || message == "E2") {
 console.log('Card is not valid')
 return; 
}
 cardID = message;
 var obj = JSON.parse(message)
 if (obj.payload=="Unknown Card" || obj.payload==" No Authentication") 
 {
   console.log(obj.payload)
   return;
 }
 cardID=obj.payload; 
 console.log("CardID:" + cardID);
 writeCardToFirebase(cardID); 

});


var database = firebase.database();
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
 
}

function validiateAuthtentication()
{ 
  console.log("Validating Authentication...");
  firebase.auth().onAuthStateChanged(function(user) 
  {
    if (user!=null)  
    {
      console.log("CardWriter Logged in succesfully"); //check if authtication succeeded
      
    } 
    else 
     {
      return;
     }
  });
}
function writeCardToFirebase(cardID) //write cardID to Firebase
{
  database.ref('cardinfo/' + cardID).set(
    {
      status: "inactive",
      uuid: "none" // in the webapplication this value will be generated
    }
  );
}

