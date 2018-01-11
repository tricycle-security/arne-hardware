var firebase = require('firebase');
var configFile = require('./configcardwriter.js');
var pyshell = require('python-shell');

firebase.initializeApp(configFile.config);  //initialize Firebase
initializeAndAuthenticate();
validiateAuthtentication();

var cardID;
rfid = new pyshell('prepare.py');
rfid.on('message', function(message)
{
  checkIfMessageIsJson(message);
  if (message == "E1" || message == "E2")
  {
    console.log('Card is not valid')
    return; 
  }

  cardID = message;
  var obj = JSON.parse(message)
  if (obj.payload=="failed")
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
        console.log("CardWriter Logged in succesfully"); //check if authtentication succeeded
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
    });
}
 
function checkIfMessageIsJson(message) 
{
  try 
  {
      JSON.parse(message);
  } catch (e)
  {
      return false;
  }
  return true;
}