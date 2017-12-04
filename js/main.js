var firebase = require('firebase');
var configFile = require('./config.js');

//initialize Firebase

  firebase.initializeApp(configFile.config);

  console.log("API: Tricycle firebase");
  firebase.auth().signInWithEmailAndPassword(configFile.email, configFile.pass).catch(function(error) {
    
    // Handle Errors here.
    var errorCode = error.code;
    var errorMessage = error.message;
  
    console.log("authError Here:");
    console.log(errorCode);
    console.log(errorMessage);
    // ...
  });



