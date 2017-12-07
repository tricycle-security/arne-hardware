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
     throw new Error('User is not a responder'); // This is messy I know will make catch and try block. 
     console.log("You are not a user!");
    }

    else 
    {
      changeStatus(uuid); //send if user is checked in or checked out
      console.log("Checked in succesfully");
    }
  });
};

  function changeStatus(uuid) //write the status data to the Firbase Database. 
  {
    database.ref('currentstatus/'+ uuid).set( 
    {

      uuid: uuid,
      onLocation: false
      
    });
  }

  firebase.auth().onAuthStateChanged(function(user) 
  {
    if (user!=null)   {
      console.log("Logged in succesfully"); //check if authtication succeeded
      checkIfUserIsResponder(uuid);
      
    
    } else {
      console.log("Not logged in");
    }
  });



