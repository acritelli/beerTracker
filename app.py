from flask import Flask, render_template, request
from pymongo import MongoClient
from secrets import randbits
from shortuuid import uuid
from flask_pymongo import PyMongo

# client = MongoClient()

# db = client.beerexpo
# collection = db.beers

# for record in collection.find():
#     print(record['name'])
#     for beer in record['beers']:
#         print("\t", beer)
        

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'beerexpo'
mongo = PyMongo(app)

# Sign up page
# Accept an email, generate a random URL, store user info in Mongo, send an email with the URL
@app.route('/')
def landingPage():
    return render_template('signup.html')

@app.route('/signup', methods = ['POST'])
def signup():
    # Check to see if this is a valid email address

    # Generate a UUID, verify not already in database

    # Init the user object with all breweries (may want to consider an "edit" flag to show if they've had something or not)

    # Send an email with the link

    # Redirect user to their page (template should recommend they bookmark)

    # Check to see if a valid UUID was submitted, check if exists
    print(request.form)
    return(uuid())

@app.route('/users/<uuid>')
def user(uuid):
    str = "Your uuid is " + uuid
    return(str)
    

@app.route('/beers')
def hello():
    default_breweries = list(mongo.db.defBeers.find())
    return render_template('test.html', breweries=default_breweries)

# User page
# Grab all defualt beer info from Mongo. Grab beer info from user collection. foreach, If beer is in user collection, display that info. Else, display defaults.

# Edit rating
# Accept JSON of beer info. Get Mongo for user. If the entry exists, update it. If not, add it.

# Get beer report
# Generate a full report of the beer for a user from Mongo. Downloadable as CSV

if __name__ == '__main__':
    app.run(debug=True)