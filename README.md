# About

A website that provides an interface to record ratings and tasting notes at beer tasting events. First used at the Rochester Real Beer Expo, with plans to add features and use it for the Flower City Brewers Fest.

![screenshot](/static/img/screenshot.png)

# Features
 
* All announced beers already added
* Track ratings and tasting notes
* Download your ratings as an Excel spreadsheet after the event
* Ability to add breweries and beers not listed
* Ability to mark a beer as "must try" so that you can only view a list of the beers that you absolutely want to taste
* Free sign-up, with no account creation required

# Why not just use Untappd?

Untappd is awesome! I just find it tedious to try searching for beers while I'm at beer tasting events. I usually end up carrying around a slip of paper to take notes on (and see others doing the same). Additionally, there are those who do not use Untappd.

Currently, you can export your notes in an Excel file and manually enter them into Untappd. 

# Installation

BeerTracker runs on a CentOS, MongoDB, and Python stack. I use Gunicorn as the WSGI server and NGINX for a reverse-proxy. Supervisord keeps the gunicorn workers running. The instructions below assume CentOS 7.

All of the instructions below also assume a standalone server dedicated to BeerTracker. MongoDB, NGINX, and Supervisord are certainly more than capable of hosting multiple applications, but I just assume that BeerTracker will be the only app on these servers. Therefore, configurations for multiple sites or databases are now covered below.

## Download the latest version of BeerTracker

Install the EPEL repository: `yum install -y epel-release`

Install Python 3: `yum install -y python34 python34-pip`

Install git: `yum install -y git`

Grab the latest version of the code: `git clone https://github.com/acritelli/beerTracker.git /beerTracker`

Change to the app directory: `cd /beerTracker`

Install virtualenv: `pip3 install virtualenv`

Create a Python virtual environment: `virtualenv -p python3 venv`

Use the Python version in the virtual environment: `source /beerTracker/venv/bin/activate`

Install all of the Python prerequisites: `pip install -r requirements.txt`

## Install and configure MongoDB

The instructions below are for MongoDB 3.4. You should consult the [official installation instructions](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-red-hat/) to ensure that you are installing the latest version according to MongoDB's best practices.

Install vim: `yum install -y vim`

Edit the MongoDB repository file according to the official installation instructions (found above): `vim /etc/yum.repos.d/mongodb-org-3.4.repo`

Install MongoDB: `yum install -y mongodb-org`

Start the MongoDB service: `systemctl start mongod`

Set the MongoDB service to automatically start on system boot: `systemctl enable mongod`

Add an administrative user:

```
use admin
db.createUser(
  {
    user: "admin",
    pwd: "supersecretpassword",
    roles: [ { role: "userAdminAnyDatabase", db: "admin" } ]
  }
)
```
Add a user that can access the beerexpo collection:

```
use beerexpo
db.createUser(
  {
    user: "beerTracker",
    pwd: "supersecretapppassword",
    roles: [ { role: "userAdminAnyDatabase", db: "beerexpo" } ]
  }
)
```

Enable authorization in /etc/mongod.conf by adding the following:

```
security:
  authorization: enabled
```

Restart mongo: `systemctl restart mongod`

Edit /beerTracker/config.py.sample to include the username and password for your beerexpo user

Rename the sample configuration file: `mv /beerTracker/config.py.sample /beerTracker/config.py`

Test the app: `python app.py`
  * The app should launch successfully and not complain about any database authentication issues

## Install Gunicorn

Ensure that you are using your virtual environment: `source /beerTracker/venv/bin/activate`

Install Gunicorn: `pip install gunicorn`

## Install and configure Supervisord

Ensure that you're **not** using your virtual environment from before: `deactivate`

Install Supervisord: `easy_install supervisord`

Generate the base Supervisord configuration file: `echo_supervisord_conf > /etc/supervisord.conf`

Edit bottom of supervisord.conf to include the following:

```
[program:beerExpo]

command = /beerTracker/venv/bin/gunicorn -b 127.0.0.1 -w 5 app:app

directory = /beerTracker
user = root
```

Start supervisord: `supervisord`

Test to ensure that the Gunicorn workers are working: `curl localhost:8000`
  * This should return the web app home page

## Install and configure nginx

Install NGINX: `yum install -y nginx`

Add to /etc/nginx/conf.d/beerTracker.conf with the contents below:

```
server {
        listen 80;
        server_name beer.troupstreet.com;

        location / {
          proxy_pass http://localhost:8000;
        }
}
```

Restart nginx: `systemctl restart nginx`

Test the web app by browsing to the your server's address
  * Note that you may need to alter the firewall rules to allow traffic on port 80.

You're done!