{/*create an Express app object*/}
var express = require('express');
var app = express();

module.exports = app;

{/*Start a working Express Server*/}
// In express, routes takes the following structure: app.METHOD(PATH, HANDLER). 
//METHOD is an http method in lowercase.
//PATH is a relative path on the server (it can be a string, or even a regular expression).
//HANDLER is a function that Express calls when the route is matched. -- take the form function(req,res){...} ** where req is the request object, and res is the response object
var express = require ('express');
var app = express();
app.get("/", (req, res) => {
    res.send("Hello Express");
});
module.exports = app;

{/*Serve an HTML File*/}
var express = require ('express');
var app = express();
app.get("/", function (req, res) {
    res.sendFile (__dirname + "/views/index.html");
});
module.exports = app;

{/*Serve Static Assets*/}
//middleware -> express.static(path), where path parameter is the absolute path of the folder containing the assets.
//middleware are functions that intercept route handlers, adding some kind of information.
//middleware needs to be mounted using the method app.use(path, middlewareFunction) (first path argument is optional - without it, middleware is executed for all requests)
var express = require('express');
var app = express();

app.get("/", function(req, res) {
    res.sendFile(__dirname + "/views/index.html")
});
app.use(express.static(__dirname+"/public")); //or Assets at the /assets route -> app.use("/assets", express.static(__dirname + "/public"));
module.exports = app;

{/*Serve JSON on a Specific Route*/}
var express = require('express');
var app = express();

app.get("/json", function(req, res) {
    res.json({
        message: "Hello json"
    });
});
module.exports = app;

{/*Use the .env File*/}
//The .env file is a hidden file that is used to pass environment variables to your application.
//Environment variables are accessible from the app as process.env.VAR_NAME. 
//process.env object is a global Node object, and variables are passed as strings. 
//The .env is a shell file, so you don't need to wrap names or values in quotes. 
//There cannot be space around the equals sign when you are assigning values to variables, e.g. VAR_NAME=value.

//.env file created with:
MESSAGE_STYLE=uppercase

//myApp.js
var express =require ('express');
var app = express();
app.get("/json", (req, res) => {
    let data = {"message": "Hello json"};
    if (Process.env.MESSAGE_STYLE === 'uppercase'){
        data.message = data.massage.toUpperCase();
    }
    res.json(data);
});
module.exports = app;

{/*Implement a Root-Level Request Logger Middleware*/}
//express.static() middleware function are functions that take 3 arguments: request object, response object, next function in the application's request-response cycle
var express = require('express');
var app = express();

app.use("/", function(req, res, next) {
    console.log(req.method+" "+req.path+" - "+req.ip)
    next();
});
module.exports = app;

{/*Chain Middleware to Create a Time Server*/}
//Middleware can be mounted at a specific rout using app.METHOD(path, middlewareFunction)
var express = require('express');
var app = express();

app.get('/now', function(req, res, next){
    req.time = new Date().toString();
    next();
}, function(req, res){
    res.send({
        time: req.time
    });
});
module.exports = app;

{/*Get Route Parameter Input from the Client*/}
var express = require('express');
var app = express();

app.get('/:word/echo', function(req, res, next){
    res.send({
        echo: req.params.word
    });
});
module.exports = app;

{/*Get Query Parameter Input from the Client*/}
//Another common way to get input from the client is by encoding the data after the route path. using a query string;
//The query string is delimited by a question mark (?), and includes field=value couples; separated by an ampersand(&);
//Express can parse the data from the query string, and populate the object <req.query>;
//example: 
//route_path: '/library' 
//actual_request_URL: '/library?userId=546&bookId=6754'
//req.query: {userId: '546', bookId: '6754'}
var express = require('express');
var app = express();

app.get('/name', function(req, res){
    var firstName = req.query.first;
    var lastName = req.query.last;
    // OR you can destructure and rename the keys
    //var { first: firstName, last: lastName } = req.query;
    res.json({
        name: `${firstName} ${lastName}`
    });
});

{/*Use body-parser to Parse POST Requests*/}
//learn how to handle POST requests (without a database for now)
//In these kind of requests (POST), the data doesn't appear in the URL, it is hidden in the request body.
//The body is a part of the HTTP request, also called the payload
//Body is encoded like the query string. This is the default format used by HTML forms.
//To parse the data coming from POST requests, you have to install the <body-parser> package.

//In order to import the body-parser, add the following line at the top of your file:
var bodyParser = require("body-parser");
var express = require('express');
var app = express();

//body-parser returns with:
app.use(bodyParser.urlencoded({extended: false}));
//In order to parse JSON data sent in the POST request, we used middleware as shown below. The data received in the request is available in the <req.body> object
app.use(bodyParser.json());

{/*Get data from POST requests*/}
var express = require('express');
var bodyParser = require("body-parser");
var app = express();
app.use(bodyParser.urlencoded({extended: false}));
app.use(bodyParser.json());

app.get("/", function(req, res) {
    res.sendFile(__dirname + "/views/index.html")
});
app.use(express.static(__dirname+"/public")); //or Assets at the /assets route -> app.use("/assets", express.static(__dirname + "/public"));

app.get('/name', function(req, res){
    var firstName = req.query.first;
    var lastName = req.query.last;
    // OR you can destructure and rename the keys
    //var { first: firstName, last: lastName } = req.query;
    res.json({
        name: `${firstName} ${lastName}`
    });
});
app.post("/name", function(req, res) {
    //Handle the data in the request
    var string = req.body.first + " " + req.body.last;
    res.json({name: string});
});
module.exports = app;