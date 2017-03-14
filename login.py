from flask import render_template, make_response, request
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

import json
import random
import string
import httplib2
import requests
import datetime

from db.database import getOne
from db.user import User


validTokenUrl = 'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
fbValidUrl = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s'
fbInfoUrl = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email'
fbPicUrl = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200'
fbValidTokenUrl = 'https://graph.facebook.com/debug_token?input_token=%s&access_token=%s'
fbDisconnectUrl = 'https://graph.facebook.com/%s/permissions?access_token=%s'
googleSecret = '/var/www/itemcatalog/GoogleSecret.json'
fbSecret = '/var/www/itemcatalog/FbSecret.json'


# Create anti-forgery state token
def login(session):

    """Includes a state token and renders teh login page"""

    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    session['state'] = state
    return render_template('login.html', STATE=state)


def jsonResponse(text, responseCode):
    """Builds and returns a JSON response

    Args:
        text        : the text to be returned in the response
        responsecode: the response code

    Returns:
        JSON repsponse contain a text and response code provided in the
        arguments.
    """

    response = make_response(json.dumps(text), responseCode)
    response.headers['Content-Type'] = 'application/json'
    return response


def submitRequest(url):

    """Submits a HTTP request"""

    h = httplib2.Http()
    return h.request(url, 'GET')[1]


def gconnect(session):

    """Authenticates a user using Google's oAuth API.

    This code was copied from Udacity's oAuth lecture and adapted for this
    project.

    Call back method for the google oAuth login script.
    Retrieves an authorisation code from the request
    Swaps the code for a access token using the application's google secret
    Verifies that the token pertains to the correct user and application
    Populates the session with user data retrieved from the google+ api.

    Args:
        session: the session object from the current application.

    Return:
        Login fails: JSON response with an explanation and and error code.
        Log in successful: ' ' the javascript code will redirect to the
                            appropriate webpage.

    """

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
        # session['credentials'] = credentials.access_token
        session['credentials'] = credentials.to_json()
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

    #Verify if the user is already connected.
    stored_credentials = credentials.access_token
    stored_gplus_id = session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        return jsonResponse('User is already connected.', 200)


    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()
    user = loadUser(data, data['picture'])

    # Store session data
    session['provider'] = 'google'
    session['access_token'] = credentials.access_token
    session['provider_id'] = gplus_id
    session['disconnect'] = 'gDisconnect(session)'

    session['userId'] = user.email
    session['username'] = user.name
    session['pic'] = user.image

    return ' '


def gDisconnect(session):
    """DEPRECATED Revokes the google credentials object.

    Args:
        session: The session object of the application we are logging out of.

    Returns:
        True    : if sucessful
        False   : if the log out fails
    """
    try:
        # session.get('credentials').revoke(httplib2.Http())
        return True
    except Exception as e:
        print e
        return False


def fbconnect(session):
    """Authenticates a user using Facebook oAuth API.

    This code was copied from Udacity's oAuth lecture and adapted for this
    project.

    Call back method for the Facebook oAuth login script.
    Retrieves an authorisation code from the request
    Sends a request witht the code, the appId and appSecret to authenticate
    the user for this application.

    Populates the session with user data retrieved from the Facebook api.
    """
    if request.args.get('state') != session['state']:
        return jsonResponse('Invalid state parameter.', 401)


    appId = json.loads(open(fbSecret, 'r').read())['web']['app_id']
    appSecret = json.loads(open(fbSecret, 'r').read())['web']['app_secret']
    data =  request.data
    token = submitRequest(fbValidUrl % (appId, appSecret, data)).split("&")[0]

    data = json.loads(submitRequest(fbInfoUrl % token))
    user = loadUser(data,
                    json.loads(submitRequest(fbPicUrl % token))["data"]["url"])

    session['provider'] = 'facebook'
    session['access_token'] = token.split("=")[1]
    session['provider_id'] = data["id"]
    session['disconnect'] = 'fDisconnect(session)'

    session['userId'] = user.email
    session['username'] = user.name
    session['pic'] = user.image

    return ' '


def fDisconnect(session):

    """Logs a user out from the application.

    Args:
        session: The session object of the application we are logging out of.

    Returns:
        True    : if sucessful
        False   : if the log out fails
    """

    try:
        facebook_id = session['provider_id']
        access_token = session['access_token']
        url = fbDisconnectUrl % (facebook_id, access_token)
        h = httplib2.Http()
        result = h.request(url, 'DELETE')[1]
        return True
    except:
        return False



# Disconnect based on provider
def logout(session):

    """ Deletes the user's session information and call the disconnect function
        of the relevant oAuth provider.

        Args:
            session: the session from which we are trying to log out of.

        Returns:
            True: if logout was successful
            False: if the logout failed

    """

    # session['disconnect'] stores the relevant log out function
    if eval(session['disconnect']):
        session.pop('state', None)
        session.pop('provider', None)
        session.pop('access_token', None)
        session.pop('provider_id', None)
        session.pop('credentials', None)
        session.pop('userId', None)
        session.pop('username', None)
        session.pop('pic', None)
        session.pop('user', None)
        return True
    else:
        return False


def loadUser(data, image):

    """Loads a user for the current session.

    Attempts to retrieve a user based on his email address.
    If a record cannot be found, create a new user with the data that is
    returned from the oAuth provider.
    If a user name cannot be found, the user is assigned a default user name
    consisting of the word user and a date & time string.

    Args:
        data    : a list of user values returned by the oAuth provider.
        image   : an image url for the current user.

    Return:
        A User object.
    """

    user = getOne(User, 'email', data['email'])
    if not user:
        if data['name'] == '':
            data['name'] = 'User %s' % datetime.datetime.now()

        user = User(email=data['email'], name=data['name'], image=image)
        User.save(user)
    return user
