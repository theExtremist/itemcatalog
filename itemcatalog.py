from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask import session, flash, make_response
from werkzeug.contrib.cache import SimpleCache
from flask.ext.seasurf import SeaSurf

import os
import sys

from db.database import User, Category, Item, get, getOne, getTable, getSort
import login

app = Flask(__name__)
csrf = SeaSurf(app)
app.config['UPLOAD_FOLDER'] = 'static/img'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
cache = SimpleCache()


def authed(userId=None):

    """Verifies authentication and authorisation.

    This function verifies if a user is logged in and whether it is authorised
    to perform an action.


    Args:
      userId    : the userId of the the user whose priviledges we want to check

    Returns     : True if the user is logged in and has the correct priviledges
                  False if the user is not logged in or if it is not authorised
                  to perform a certain action.
    """

    if 'userId' not in session:
        flash('Please log in to continue')
        return False

    if userId:
        if session['userId'] == userId:
            return True
        else:
            flash('You are not authorised to perform this operation')
        return False
    return True


@app.route('/login/')
def showlogin():

    """Returns the login page."""
    return login.login(session)


@app.route('/gconnect', methods=['POST'])
def gconnect():

    """Callback function for google oAuth"""
    return login.gconnect(session)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():

    """Callback function for facebook oAuth"""
    return login.fbconnect(session)


@app.route('/logout/')
def logout():

    """Calls the log out function and returns the main page"""
    login.logout(session)
    return redirect(url_for('index'))


def render(template, **kw):

    """Helper function for rendering templates.

    This function includes a list of categories, a flag to indicate whether a
    user is logged, any other keyword arguments passed in by the calling
    calling function and calls the Flask's render_template function.

    Args:
      template  : the template we want to render
      **kw      : a list of keyword arguments to pass to the template.

    Returns     : Returns a HTTP response with the relevant template.
    """

    loggedIn = 'provider' in session
    return render_template(template, categories=cache.get('categories'),
                            loggedIn=loggedIn, **kw)


@app.route('/')
@app.route('/index/')
def index():

    """Returns a page with the 10 most recent items."""

    items = getSort(Item, "created", 10)
    return render('index.html', title="Home page", items=items)


@app.route('/category/<int:categoryId>')
def category(categoryId):

    """Returns a page for a specified category.

    Retrieves items belonging to the specified category and renders them as
    the category's page.

    Args:
      categoryId : the id of the category to display.

    Returns      : Returns a HTTP response with the category template.
    """

    items = get(Item, "categoryId", categoryId)
    category = getOne(Category, "id", categoryId).name
    return render('category.html', title=category, items=items)


@app.route('/item/<int:itemId>')
def item(itemId):

    """Returns a page for a specified item.

    Retrieves a specified item renders the item's webpage.

    Args:
      itemId : the id of the item to display.

    Returns      : Returns a HTTP response with the item template.
    """
    item = get(Item, "id", itemId)[0]
    return render('item.html', title=item.category.name,
                  titleUrl=url_for('category', categoryId=item.category.id),
                  item=item)


def saveItem(item):

    """Saves and item and returns the saved item's page.

    Args:
      item  : The item object to save - this can be a new or existing item.

    Returns : Returns a HTTP response with the item template with the details of
              the saved item or any error messages.
    """

    Item.save(item, request.form, request.files['picfile'], session['userId'])

    return render('item.html', title=item.category.name,
                    titleUrl=url_for('category', categoryId=item.categoryId),
                    item=item)



@app.route('/item/new/', methods=['GET', 'POST'])
def newItem():

    """Renders the new item page, accepts inputs from users and links to save
    the item.

    For a get request, the function returns a new item page to accept user
    inputs.
    Post requests pass an item parameter to the save function for validation
    and saving.

    Returns     : Returns a HTTP response with the new item template.
    """

    item = Item()
    if request.method == 'POST':
        if authed():
            return saveItem(item)

    return render('saveitem.html', title="New Item", item=item,
                   formAction=url_for('newItem'), cancel=url_for('index'))


@app.route('/item/<int:itemId>/edit/', methods=['GET', 'POST'])
def editItem(itemId):

    """Renders the edit item page, accepts inputs from users and links to save
    the item.

    For a get request, the function returns a edit item page to accept user
    inputs.
    Post requests retrieve an item from the database and pass it to the save
    function for validation and saving.

    Args:
      itemId : The itemId of the item we want to edit.

    Returns  : Returns a HTTP response with the Edit item template.
    """

    item = getOne(Item, 'id', itemId)
    if request.method == 'POST':
        if authed(item.userId):
            return saveItem(item)

    return render('saveitem.html', title="Edit Item",
                   categoryId=item.categoryId, item=item,
                   formAction=url_for('editItem', itemId=item.id),
                   cancel=url_for('item', itemId=itemId))



@app.route('/item/<int:itemId>/delete/', methods=['GET', 'POST'])
def deleteItem(itemId):

    """Renders the delete item page and obtains confirmation from the user to
    delete

    For a get request, the function returns the delete item page for the
    relevant item and requests confirmation to delete the item.
    Post requests:
     - retrieve an item from the database
     - verify that the user is authenticated and authorised to delete the item
     - call the delete method on the item object

    Args:
      itemId : The itemId of the item we want to delete.

    Returns  : Redirects the user to the category page and display a message
               confirming the deletion.
               If the operation fails, the delete item page is displayed with
               an error message.
    """

    item = getOne(Item, 'id', itemId)
    categoryId = item.category.id
    if request.method == 'POST':
        if authed(item.userId):
            Item.delete(item)
            return redirect(url_for('category', categoryId=categoryId))

    return render('deleteitem.html', title="Delete Item", item=item)


@app.route('/categories/JSON')
def categoriesJSON():

    """Returns a JSON object representing all the categories in the database."""

    categories = getTable(Category)
    return jsonify(categories=[c.serialize for c in categories])


@app.route('/category/<int:categoryId>/JSON')
def categoryItemsJSON(categoryId):

    """Returns a JSON object representing a category and its items.

    Args:
      categoryId : The id of the category we want to retrieve.

    Returns  : JSON object representing a category and its items.
    """
    category = getOne(Category, 'id', categoryId)
    items = get(Item, 'categoryId', categoryId)
    return jsonify(category.serialize, items=[i.serialize for i in items])


@app.route('/item/<int:itemId>/JSON')
def itemJSON(itemId):
    """Returns a JSON object representing an item.

    Args:
      itemId : The id of the item we want to retrieve.

    Returns  : JSON object representing an item.
    """

    item = getOne(Item, 'id', itemId)
    return jsonify(item.serialize)



def startServer():

    app.secret_key = 'super_secret_key'
    app.debug = True
    cache.set('categories', getTable(Category), 3600)
    app.run(host='0.0.0.0', port=8000)

if __name__ == '__main__':
    startServer()

