from flask import Flask, render_template, request, redirect, jsonify, make_response
from shortuuid import uuid
from flask_pymongo import PyMongo
from bson.json_util import dumps
from csv import writer
from io import StringIO
import config
        

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'beerexpo'

if(config.MONGO_USERNAME):
    app.config['MONGO_USERNAME'] = config.MONGO_USERNAME
if(config.MONGO_PASSWORD):
    app.config['MONGO_PASSWORD'] = config.MONGO_PASSWORD
mongo = PyMongo(app)

# Sign up page
# Accept a name, generate a random URL, store user info in Mongo
@app.route('/')
def landingPage():
    return render_template('signup.html')

@app.route('/signup', methods = ['POST'])
def signup():

    # Generate a UUID, verify not already in database
    url = uuid()
    if(mongo.db.users.find_one(({'url': url }))):
        # TODO: Need to return some sort of error here
        print('Duplicate uuid found')
        return('Error')

    # Init the user object
    newUser = {
        'url': url,
        'name': request.form['name'],
        'beer': {}
    }
    mongo.db.users.insert_one(newUser)

    # Redirect user to their page (template should recommend they bookmark)
    redirectStr = '/users/' + url
    return redirect(redirectStr)

@app.route('/users/<url>')
def user(url):
    # Display template
    return render_template('userPage.html', url=url)

# Returns a user object with a list of all beers (including those not yet rated)
@app.route('/users/<url>/getBeers')
def getBeers(url):
    # Grab user based on url (uuid) and all default beers
    user = mongo.db.users.find_one(({'url': url}))
    defBeers = mongo.db.defBeers.find()

    # Check to see if a user has rated a beer. If they haven't, add to user object to be returned
    for brewery in defBeers:
        if (not brewery['name'] in user['beer']):
            user['beer'][brewery['name']] = {}
        for beer in brewery['beers']:
            if (not beer in user['beer'][brewery['name']]):
                user['beer'][brewery['name']][beer] = {'rating':'', 'notes':''}

    return dumps(user)

@app.route('/users/<url>/editRating', methods = ['POST'])
def editRating(url):
    # TODO: more efficient query and update, return more robust errors...

    # Remove . and $ characters from brewery and beer, since they're keys in Mongo
    brewery = request.form['brewery']
    brewery = brewery.replace('.', '')
    brewery = brewery.replace('$', '')
    beer = request.form['beer']
    beer = beer.replace('.', '')
    beer = beer.replace('$', '')

    rating = request.form['rating']
    notes = request.form['tastingNotes']
    if (request.form['mustTry'] == 'true'):
        mustTry = True
    else:
        mustTry = False
   

    user = mongo.db.users.find_one({'url': url})

    # Account for new breweries/beers
    if (not brewery in user['beer']):
        user['beer'][brewery] = {}
    if (not beer in user['beer'][brewery]):
        user['beer'][brewery][beer] = {'rating':'', 'notes':''}

    user['beer'][brewery][beer]['rating'] = rating
    user['beer'][brewery][beer]['notes'] = notes
    user['beer'][brewery][beer]['mustTry'] = mustTry

    mongo.db.users.update({'url' : url}, user)
    return('success')

@app.route('/users/<url>/downloadRatings')
def downloadRatings(url):
    stringIO = StringIO()
    csv = writer(stringIO)
    csv.writerow(['Brewery', 'Beer', 'Rating', 'Notes'])
    user = mongo.db.users.find_one({'url': url})
    for brewery in user['beer']:
        for beer in user['beer'][brewery]:
            row = [brewery, beer, user['beer'][brewery][beer]['rating'], user['beer'][brewery][beer]['notes']]
            csv.writerow(row)
    output = make_response(stringIO.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=beerRatings.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@app.route('/beers')
def hello():
    default_breweries = list(mongo.db.defBeers.find())
    return render_template('test.html', breweries=default_breweries)

if __name__ == '__main__':
    app.run(debug=True)