var firebase = require('firebase');
var configFile = require('./config.js');
var pyshell = require('python-shell');

firebase.initializeApp(configFile.config); 
var uuid;
 rfid = new pyshell('main.py');

 rfid.on('message', function(message)

 {
  uuid = message; 
  console.log("CardID:" + uuid);
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
 // uuid = 'EkbgGG7UodDNotGb' //uuid of Hans Hoogerwerf
  var database = firebase.database(); //get reference to the database service

  function checkIfCardIsActive(uuid) 
{
  database.ref('cardinfo/' + uuid + '/status').once('value').then(function(snapshot)
  {
    var uuidcheck = (snapshot.val());
    console.log(uuidcheck);
    if (uuidcheck !== 'active')
    {
      throw new Error('Card is not active!');
    } 
    
    else 
    {
      changeStatus(uuid); //send if user is checked in or checked out
      console.log("Checked in succesfully");  
    }
  });
}

  function changeStatus(uuid) //write the status data to the Firbase Database. 
  {
    database.ref('currentstatus/'+ uuid).set( 
    {
      uuid: uuid,
      onLocation: false
      
    });
  }
function validiateAuthtentication(uuid)
{ 
  console.log("Validating Authentication...");
  firebase.auth().onAuthStateChanged(function(user) 
  {
    if (user!=null)  
    {
      console.log("Logged in succesfully"); //check if authtication succeeded
      checkIfCardIsActive();
      
    } else 
     {
      console.log("Not logged in");
     }
  });
}

