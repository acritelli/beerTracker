from flask import Flask, render_template
from pymongo import MongoClient
from secrets import randbits
from shortuuid import uuid
# from flask_pymongo import PyMongo

# client = MongoClient()

# db = client.beerexpo
# collection = db.beers

# for record in collection.find():
#     print(record['name'])
#     for beer in record['beers']:
#         print("\t", beer)
        

app = Flask(__name__)

# Sign up page
# Accept an email, generate a random URL, store user info in Mongo, send an email with the URL
@app.route('/')
def landingPage():
    return render_template('signup.html')

@app.route('/signup')
def signup():
    # Check to see if a valid UUID was submitted, check if exists
    return(uuid())

@app.route('/users/<uuid>')
def user(uuid):
    str = "Your uuid is " + uuid
    return(str)
    


def hello():
    client = MongoClient()
    db = client.beerexpo
    default_breweries = list(db.defBeers.find())
    return render_template('test.html', breweries=default_breweries)

# User page
# Grab all defualt beer info from Mongo. Grab beer info from user collection. foreach, If beer is in user collection, display that info. Else, display defaults.

# Edit rating
# Accept JSON of beer info. Get Mongo for user. If the entry exists, update it. If not, add it.

# Get beer report
# Generate a full report of the beer for a user from Mongo. Downloadable as CSV

if __name__ == '__main__':
    app.run(debug=True)