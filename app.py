from flask import Flask, render_template, request, redirect, jsonify, make_response, url_for
from shortuuid import uuid
from flask_pymongo import PyMongo
from bson.json_util import dumps
from csv import writer
from io import StringIO
import config
from copy import deepcopy
        

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

@app.route('/about')
def aboutPage():
    return render_template('about.html')

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

@app.route('/users/<uuid>')
def user(uuid, selectedBrewery=None, selectedBeer=None):
    templateVars = {}
    templateVars['activePage'] = 'Dashboard'
    templateVars['url'] =  uuid
    templateVars['action'] = 'displayAll'

    if 'selectedBrewery' in request.args and 'selectedBeer' in request.args:
        templateVars['selectedBrewery'] = request.args['selectedBrewery']
        templateVars['selectedBeer'] = request.args['selectedBeer']

    # Display template
    return render_template('userPage.html', templateVars=templateVars)

@app.route('/users/<uuid>/mustTryBeers')
def mustTryBeers(uuid):
    templateVars = {}
    templateVars['activePage'] = 'mustTryBeers'
    templateVars['url'] =  uuid
    templateVars['action'] = 'displayMustTry'
    return render_template('userPage.html', templateVars=templateVars)

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

# Get must try beers. May fold this into regular getBeers at some point
@app.route('/users/<url>/getMustTryBeers')
def getMustTryBeers(url):
    user = mongo.db.users.find_one(({'url': url}))
    # Make a copy so that we can delete items in loop (can't change size of a dict in a loop)
    mustTryBeers = deepcopy(user)

    # Iterate over user's beers and delete any that aren't must try from the copy mustTryBeers
    # We do this to a copy (and return the copy) because we can't alter the dict size in a loop
    for brewery in user['beer']:
        for beer in user['beer'][brewery]:
            if 'mustTry' in user['beer'][brewery][beer] and not user['beer'][brewery][beer]['mustTry']:
                print(brewery + beer + ' not a must try')
                del mustTryBeers['beer'][brewery][beer]
        # If brewery dictionary is now empty (all have been deleted), then remove the brewery
        if not mustTryBeers['beer'][brewery]:
            del mustTryBeers['beer'][brewery]
    return dumps(mustTryBeers)

@app.route('/users/<url>/editRating', methods = ['POST'])
def editRating(url):
    print(request.form)
    # TODO: more efficient query and update, return more robust errors...

    # Account for other brewery/beer
    if request.form['brewerySelector'] == 'Other':
        brewery = request.form['otherBreweryName']
    else:
        brewery = request.form['brewerySelector']
    if request.form['beerSelector'] == 'Other':
        beer = request.form['otherBeerName']
    else:
        beer = request.form['beerSelector']

    # Remove . and $ characters from brewery and beer, since they're keys in Mongo
    brewery = brewery.replace('.', '')
    brewery = brewery.replace('$', '')
    beer = beer.replace('.', '')
    beer = beer.replace('$', '')

    rating = request.form['rating']
    notes = request.form['tastingNotes']
    mustTry = False
    if 'mustTry' in request.form:
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
    return(redirect(url_for('user', uuid=url, selectedBrewery=brewery, selectedBeer=beer)))

@app.route('/users/<uuid>/downloadRatings')
def downloadRatings(uuid):
    stringIO = StringIO()
    csv = writer(stringIO)
    csv.writerow(['Brewery', 'Beer', 'Rating', 'Notes', 'Must Try'])
    user = mongo.db.users.find_one({'url': uuid})
    for brewery in sorted(user['beer']):
        for beer in sorted(user['beer'][brewery]):
            row = [brewery, beer]

            # Check to see if keys exist for a user, if not fill with a blank
            if 'rating' in user['beer'][brewery][beer]:
                row.append(user['beer'][brewery][beer]['rating'])
            else:
                row.append('')

            if 'notes' in user['beer'][brewery][beer]:
                row.append(user['beer'][brewery][beer]['notes'])
            else:
                row.append('')

            if 'mustTry' in user['beer'][brewery][beer]:
                row.append(user['beer'][brewery][beer]['mustTry'])
            else:
                row.append('')
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