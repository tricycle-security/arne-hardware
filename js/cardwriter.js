var firebase = require('firebase');
var configFile = require('./configcardwriter.js');
var cardID = "CTcvQXcsS72fTest";
firebase.initializeApp(configFile.config);  //initialize Firebase
initializeAndAuthenticate();

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
 validiateAuthtentication();
}


function validiateAuthtentication()
{ 
  console.log("Validating Authentication...");
  firebase.auth().onAuthStateChanged(function(user) 
  {
    if (user!=null)  
    {
      console.log("CardWriter Logged in succesfully"); //check if authtication succeeded
      writeCard(cardID);
    } 
    else 
     {
      return;
     }
  });
}


function writeCard(cardID) //write the status data to the Firbase Database. 
{
  database.ref('cardinfo/' + cardID).set(
    {
      status: "inactive",
      uuid: "none" //for set function it is mandotory to write to all database values even if it does'nt change    
    }
  );
}

