// Largely modeled on https://scotch.io/tutorials/build-a-restufl-api-using-node-and-express-4

// Things related to the node web server
var express = require('express');
var app = express();

var fs = require('fs');         // Filesystem access
var assert = require('assert');
var HTTP_PORT = 3000;

// Mongoose is a json schema, one of the two major ones. 
// There's another undergoing IETF standardization, json.schema
var mongoose = require('mongoose');

// Mongo database driver
var MongoClient = require('mongodb').MongoClient;
var robodataDatabase;

// BodyParser allows us to get data from a POST
var bodyParser = require('body-parser');
app.use(bodyParser.urlencoded({extended:true}));
app.use(bodyParser.json());


// router object, which ties URLs to pieces of code that will be run
var router = express.Router();

// Middleware to use for all requests. In this
// case, all requests get some primitive logging
router.use(function(req, res, next)
{
   console.log("request came in and was logged. Forwarded on.");
   next();
});

//--------- SET UP ROUTES --------
// Route /test (or /api/test when we call app.use below)
// to the function here

// Handle a post operation
router.route('/mission')
        // ====== POST verb
        .post(function(req, res)
        {
          console.log("got api post");
          var obj = {};
          obj.name = req.body.name;
          // commit to database
          res.json({message:"post done"});
        })
        
        // ===== GET verb
        .get(function(req, res)
        {
          console.log("got api get");
          var obj = {};
          obj.name = req.body.name;
          // commit to database
          res.json({message:"get done"});
        })
        
        // ===== PUT verb
       .put(function (req, res)
        {
          console.log("got API PUT:", req.body.name);
          var obj = {};
          res.json({message:"put request"});
        })
        
        // ===== DELETE verb
       .delete(function(req, res)
        {
          console.log("got API DELETE:", req.body.name);
          var obj = {};
          res.json({message:"Delete request"});
        })
        
        // ===== Catch-all for something not otherwise handled
       .all(function(req, res, next)
        {
            console.log("Catch-all. Should do some sort of error here");
            res.json({message:"Unexpected, unhandled verb"});
        });

/**
router.get("/mission", function(req, res)
{
    var verb = req.method;
   res.json({message:'router working', 'verb':verb}); 
   
});
*/

// Register the routes
app.use("/REST", router);

// Mongoose schema
var Schema = mongoose.Schema();

/*
var sortieSchema = new mongoose.Schema(
        {
            name: {type:String, default:"robot_sortie_archive"},
            version: {type:String, default:"1.0"}
        });
*/

// Makes default, no auth connection to localhost on 27017
// to the database robodata
var url = "mongodb://localhost:27017/robodata";
MongoClient.connect(url, function(err, db)
{
    robodataDatabase = db;
    console.log("got db connection");
});

/**
 * Uses the already-created robodatabase connection to retrieve
 * a collection, and then write data to it.
 * @param String collectionName name of collection to write to
 * @param String data json data to write to the collection
 * @returns {undefined}
 */
function writeToDatabase(collectionName, data)
{
   var missionCollection = robodataDatabase.collection("robot_missions");
   missionCollection.insert(data);
}


/**
 * Start the web server listening
 * @type type
 */
var server = app.listen(HTTP_PORT, function()
{
       var host = server.address().address;
       var port = server.address().port;
       console.log("app listening at http://%s:%s", host, port);
   });
  

/**
 * When the web client goes to /listUsers this function is fired.
 */
app.get('/listUsers', function(req, res)
{
   fs.readFile(__dirname + '/' + "SortieFormat.json", "utf8", function(err, data)
   {
       //console.log("data is:", data);
       jsonData = JSON.parse(data);
       writeToDatabase("robot_missions", jsonData);
       
       res.end(data);
   });
});

