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


var server = app.listen(HTTP_PORT, function()
{
       var host = server.address().address;
       var port = server.address().port;
       console.log("app listening at http://%s:%s", host, port);
   });
   
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

