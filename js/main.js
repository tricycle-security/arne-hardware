var firebase = require('firebase');
//var firebase = require('firebase/database');
//var firebase = require('firebase/auth');
var configFile = require('./config.js');

  firebase.initializeApp(configFile.config); //initialize Firebase

  firebase.auth().signInWithEmailAndPassword(configFile.email, configFile.pass).catch(function(error) 
  {
  // Handle Errors here.
    var errorCode = error.code;
    var errorMessage = error.message;
  
    console.log("authError Here:");
    console.log(errorCode);
    console.log(errorMessage);
    // ...
  });

  uuid = 'EJyIfXPnAjebmaQXNlAjuqv0BBl1' //uuid of Hans Hoogerwerf
  var database = firebase.database(); //get reference to the database service

  function checkIfUserIsResponder(uuid) 
{

  database.ref('userinfo/' + 'userstatus/' + uuid + '/responder').once('value').then(function(snapshot)
  {
    var responder = (snapshot.val());
    if (responder !== true) 
    {
      Throw ("User is not a responder");
    }

    else 
    {
      console.log("You are checked in!");
    }
  });
};

  function changeStatus(uuid) //write the status data to the Firbase Database. 
  {
    database.ref('currentstatus/'+ uuid).set( 
    {

      uuid: uuid,
      onLocation: true
      
    });
  }

  firebase.auth().onAuthStateChanged(function(user) 
  {
    if (user!=null)   {

      console.log("Logged in succesfully"); //check if authtication succeeded
      checkIfUserIsResponder(uuid);
      changeStatus(uuid); //send if user is checked in or checked out
    
    } else {
      console.log("Not logged in");
    }


  });



