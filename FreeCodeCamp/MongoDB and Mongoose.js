{/*Install and Set Up Mongoose*/}
//Add mongodb and mongoose to the project’s package.json. Then, require mongoose as mongoose in myApp.js. 
//Store your MongoDB Atlas database URI in a private .env file as MONGO_URI. Surround the the URI with single or double quotes,
//and make sure no space exists between both the variable and the =, and the value and =. 
//Connect to the database using the following syntax:
//mongoose.connect(<Your URI>, { useNewUrlParser: true, useUnifiedTopology: true });
//MY URI = mongodb+srv://paulocilas:<password>@cluster0-testing.j5x1d.mongodb.net/<dbname>?retryWrites=true&w=majority

//.env
GLITCH_DEBUGGER=true
SECRET=
MADE_WITH=
MONGO_URI=mongodb+srv:/\/paulocilas:Eumeamo46@cluster0-testing.j5x1d.mongodb.net/Cluster0-testing?retryWrites=true&w=majority

//package.json
"dependencies": {
    "express": "^4.12.4",
    "body-parser": "^1.15.2",
    "mongodb": "^3.0.0",
    "mongoose": "^5.6.5"
  },

//myApp.js
const mongoose = require('mongoose');
mongoose.connect(process.env.MONGO_URI);

{/*Create a Model*/}
//CRUD part I-CREATE

//ASsign Mongoose Schema to a variable
const Schema = mongoose.Schema;

//building schema you can use either of three options for name validation
//name: String
//name: {type: String}
//name: {type: String, required: true}//preferred

//Create Person schema
const personSchema = new Schema({
    name: { type: String, required: true },
    age: Number, 
    favoriteFoods: [String]
});

//Create Person model from the schema
const Person = mongoose.model("Person", personSchema);

{/*Create and Save a Record of a Model*/}
//Install & set up mongoose
const mongoose = require('mongoose');
mongoose.connect(process.env.MONGO_URI);//this the file containing MONGO_URI address.

//Create a model of a person, using schema 
var personSchema = new mongoose.Schema({
    name:String,
    age:Number,
    favoriteFoods:[String]
});
//Create a new person, including their attributes and save the new person you created
var Person = mongoose.model('Person', personSchema);
//Put your new person inside the createAndSavePerson function.
var createAndSavePerson = function(done) {
    var pauloCilas = new Person({name:"Paulo Cilas", age: 32, favoriteFoods: ["Juice", "pizza"]});
    pauloCilas.save(function(err, data){
        if (err) return console.error(err);
        done(null, data)
    });
};

{/*Create Many Records with model.create()*/}
var arrayOfPeople = [
    {name: "Guto", age:29, favoriteFoods:["hamburger", "coca"]}, 
    {name: "Letta", age: 33, favoriteFoods:["candy","cake"]},
    {name: "Luisa", age: 30, favoriteFoods:["Shirimp", "fish"]}
  ];
//create many People with `Model.create()`
var createManyPeople = function(arrayOfPeople, done){
    Person.create(arrayOfPeople, function(err, people){
        if (err) return console.log(err);
        done(null, people);
    });
};

{/*Use model.find() to Search your database*/}
var findPeopleByName = function(personName, done) {
    Person.find({name: personName}, function(err, match){
        if (err) return console.log(err);
        done(null, match);
    });
};

{/*Use model.findOne() to return a single matching document from your database*/}
var findOneByFood = function(food, done){
    Person.findOne({favoriteFoods: food}, function(err, match){
        if (err) return console.log(err);
        done(null, match)
    });
};

{/*Use model.findById() to Search your database by _id*/}
var findPersonById = function(personId, done) {
    Person.findById(personId, function (err, data) {
      if (err) return console.log(err);
      done(null, data);
    });
  };

  {/*Perform classic updates by running find, edit, then save*/}
  const findEditThenSave = (personId, done) => {
      const foodToAdd = "hamburger";
        Person.findById(personId, (err, person) => {
            if (err) return console.log(err);
            person.favoriteFoods.push(foodTAdd);
        person.save((err, updatedPerson) => {
            if (err) return console.log(err);
            done(null, updatedPerson)
        })
    })
  }

  {/*Perform new updates on a document using model.findOneAndUpdate()*/}
  const findAndUpdate = (personName, done) => {
      const ageToSet = 20;
      Person.findOneAndUpdate({name:personName}, {age:ageToSet}, {new:True}, (err, person) =>{
          if (err) return console.log(err);
          done(null, person);
      })
  };

  {/*Delete One Document Using model.findByIdAndRemove*/}
  const removeById = (personId, done) => {
      Person.findByIdAndRemove(personId, (err, removeDoc)=>{
          if (err) return console.log(err);
          done(null, removeDoc);
      });
  };


{/*Delete Many Documents with model.remove()*/}
const removeManyPeople = (done) => {
    const nameToRemove = "Mary";
  
    Person.remove({name:nameToRemove}, (err, removeDocs)=>{
      if (err) return console.log(err);
      done(null, removeDocs);
    })
  };

  {/*Chain Search Query Helpers to narrow search results*/}
  const queryChain = (done) => {
      const foodToSearch = "burrito";

      Person.find({favoriteFoods:foodToSearch})
      .sort({name:1})
      .limit(2)
      .select({age:0})
      .exec((err, data)=>{
          if(err) return console.log(err);
          done(null, data);
      })
  };
