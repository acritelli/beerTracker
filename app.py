from flask import Flask, render_template, request, redirect
from shortuuid import uuid
from flask_pymongo import PyMongo
from flask_mail import Mail, Message

# client = MongoClient()

# db = client.beerexpo
# collection = db.beers

# for record in collection.find():
#     print(record['name'])
#     for beer in record['beers']:
#         print("\t", beer)
        

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'beerexpo'
app.config['MAIL_DEFAULT_SENDER'] = 'expotracker'
mongo = PyMongo(app)
mail = Mail(app)

# Sign up page
# Accept an email, generate a random URL, store user info in Mongo, send an email with the URL
@app.route('/')
def landingPage():
    return render_template('signup.html')

@app.route('/signup', methods = ['POST'])
def signup():
    # TODO: Check to see if this is a valid email address

    # Generate a UUID, verify not already in database
    url = uuid()
    if(mongo.db.users.find_one(({'url': url }))):
        # TODO: Need to return some sort of error here
        print('Duplicate uuid found')
        return('Error')

    # Init the user object with all breweries (may want to consider an "edit" flag to show if they've had something or not)
    newUser = {
        'url': url,
        'name': request.form['name'],
        'beer': {}
    }
    for brewery in mongo.db.defBeers.find():
        newUser['beer'][brewery['name']] = {}
        for beer in brewery['beers']:
            newUser['beer'][brewery['name']][beer] = {}
            newUser['beer'][brewery['name']][beer]['rating'] = ""
            newUser['beer'][brewery['name']][beer]['notes'] = ""
    mongo.db.users.insert_one(newUser)

    # Send an email with the link
    # msg = Message("Your unique URL is: ", recipients=[request.form['email']])
    # mail.send(msg)

    # Redirect user to their page (template should recommend they bookmark)
    redirectStr = '/users/' + url
    return redirect(redirectStr)

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