from flask import render_template, make_response, request, session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

import json
import random
import string
import httplib2
import requests

from db.database import getOne
from db.user import User


validTokenUrl = 'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
fbValidUrl = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s'
fbInfoUrl = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email'
fbPicUrl = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200'
fbValidTokenUrl = 'https://graph.facebook.com/debug_token?input_token=%s&access_token=%s'
fbDisconnectUrl = 'https://graph.facebook.com/%s/permissions?access_token=%s'
googleSecret = 'GoogleSecret.json'
fbSecret = 'FbSecret.json'


# Create anti-forgery state token
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    session['state'] = state
    print state
    return render_template('login.html', STATE=state)


def jsonResponse(text, responseCode):
    response = make_response(json.dumps(text), responseCode)
    response.headers['Content-Type'] = 'application/json'
    return response


def submitRequest(url):
    h = httplib2.Http()
    return h.request(url, 'GET')[1]


def gconnect(session):
    # Validate state token and if valid trade the authorisation code for
    # an access token
    if request.args.get('state') != session['state']:
        return jsonResponse('Invalid state parameter.', 401)

    # Upgrade the authorization code into a credentials object
    # In other words swap the authorisation code for an access token
    try:
        oauth_flow = flow_from_clientsecrets(googleSecret, scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(request.data)
        session['credentials'] = credentials
    except FlowExchangeError:
        return jsonResponse('Upgrade auth code failed.', 401)

    # Check that the access token is valid.
    # If there was an error in the access token info, abort.
    result = json.loads(submitRequest(validTokenUrl % credentials.access_token))
    if result.get('error') is not None:
        return jsonResponse(result.get('error'), 500)


    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        return jsonResponse("Incorrect token user ID", 401)

    # Verify that the access token is valid for this app.
    clientId = json.loads(open(googleSecret, 'r').read())['web']['client_id']
    if result['issued_to'] != clientId:
        return jsonResponse("Incorrect Token client ID", 401)


    stored_credentials = session.get('credentials')
    stored_gplus_id = session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        return jsonResponse('User is already connected.', 200)


    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()


    # Store session data
    session['provider'] = 'google'
    session['access_token'] = credentials.access_token
    session['provider_id'] = gplus_id
    session['disconnect'] = 'gDisconnect(session)'

    session['username'] = data['name']
    session['email'] = data['email']
    session['pic'] = data['picture']

    return checkUser()



def gDisconnect(session):
    x = httplib2.Http()
    try:
        session.get('credentials').revoke(x)
        return True
    except:
        print x.request.__dict__
        print "Not able to log out"
        return False


def fbconnect(session):

    if request.args.get('state') != session['state']:
        return jsonResponse('Invalid state parameter.', 401)


    appId = json.loads(open(fbSecret, 'r').read())['web']['app_id']
    appSecret = json.loads(open(fbSecret, 'r').read())['web']['app_secret']
    data =  request.data
    token = submitRequest(fbValidUrl % (appId, appSecret, data)).split("&")[0]

    data = json.loads(submitRequest(fbInfoUrl % token))

    session['provider'] = 'facebook'
    session['access_token'] = token.split("=")[1]
    session['provider_id'] = data["id"]
    session['disconnect'] = 'fDisconnect(session)'

    session['username'] = data["name"]
    session['email'] = data["email"]
    session['pic'] = json.loads(submitRequest(fbPicUrl % token))["data"]["url"]

    return checkUser()


def fDisconnect(session):
    try:
        facebook_id = session['provider_id']
        access_token = session['access_token']
        url = fbDisconnectUrl % (facebook_id,access_token)
        h = httplib2.Http()
        result = h.request(url, 'DELETE')[1]
        return True
    except:
        return False



# Disconnect based on provider
def logout(session):

    if eval(session['disconnect']):
        session.pop('provider', None)
        session.pop('access_token', None)
        session.pop('provider_id', None)
        session.pop('credentials', None)
        session.pop('username', None)
        session.pop('email', None)
        session.pop('pic', None)
        return True
    else:
        return False


def checkUser():
    if not getOne(User, 'email', session['email']):
        user = User(email=session['email'], name=session['username'],
            image=session['pic'])
        User.save(user)

    return ' '