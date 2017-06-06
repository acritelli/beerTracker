from flask import Flask, render_template, request, redirect, jsonify, make_response
from shortuuid import uuid
from flask_pymongo import PyMongo
from bson.json_util import dumps
from csv import writer
from io import StringIO
        

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'beerexpo'
app.config['MAIL_DEFAULT_SENDER'] = 'expotracker'
mongo = PyMongo(app)

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
    # TODO: handling for periods in beer name?
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

@app.route('/users/<url>')
def user(url):
    # Display template
    return render_template('userPage.html', url=url)

# TODO: alphabetical order
@app.route('/users/<url>/getBeers')
def getBeers(url):
    # Grab all beer info from user entry based on UUID.
    user = mongo.db.users.find_one(({'url': url}))
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

    user = mongo.db.users.find_one({'url': url})

    # Account for new breweries/beers
    if (not brewery in user['beer']):
        user['beer'][brewery] = {}
    if (not beer in user['beer'][brewery]):
        user['beer'][brewery][beer] = {'rating':'', 'notes':''}

    user['beer'][brewery][beer]['rating'] = rating
    user['beer'][brewery][beer]['notes'] = notes

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

@app.route('/about')
def about():
    return render_template('about.html')
    
    

@app.route('/beers')
def hello():
    default_breweries = list(mongo.db.defBeers.find())
    return render_template('test.html', breweries=default_breweries)


# Edit rating
# Accept JSON of beer info. Get Mongo for user. If the entry exists, update it. If not, add it.

# Get beer report
# Generate a full report of the beer for a user from Mongo. Downloadable as CSV

if __name__ == '__main__':
    app.run(debug=True)