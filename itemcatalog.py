from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask import session, flash, make_response
from werkzeug.contrib.cache import SimpleCache
from flask.ext.seasurf import SeaSurf

import os
import sys

from db.database import User, Category, Item, get, getOne, getTable
import login

app = Flask(__name__)
csrf = SeaSurf(app)
app.config['UPLOAD_FOLDER'] = 'static/img'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
cache = SimpleCache()


def authed(userId=None):
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
    return login.login(session)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    return login.gconnect(session)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    return login.fbconnect(session)


@app.route('/logout/')
def logout():
    login.logout(session)
    return redirect(url_for('index'))


def render(template, **kw):
    loggedIn = 'provider' in session
    return render_template(template, categories=cache.get('categories'),
                            loggedIn=loggedIn, **kw)


@app.route('/')
@app.route('/index/')
def index():
    print "INDEX:"
    print session
    items = get(Item, "categoryId", 1)
    return render('index.html', title="Home page", items=items)


@app.route('/category/<int:categoryId>')
def category(categoryId):
    items = get(Item, "categoryId", categoryId)
    category = getOne(Category, "id", categoryId).name
    return render('category.html', title=category, items=items)


@app.route('/item/<int:itemId>')
def item(itemId):
    item = get(Item, "id", itemId)[0]
    return render('item.html', title=item.category.name,
                  titleUrl=url_for('category', categoryId=item.category.id),
                  item=item)


def saveItem(item):

    Item.save(item, request.form, request.files['picfile'], session['userId'])

    return render('item.html', title=item.category.name,
                    titleUrl=url_for('category', categoryId=item.categoryId),
                    item=item)



@app.route('/item/new/', methods=['GET', 'POST'])
def newItem():
    item = Item()
    if request.method == 'POST':
        if authed():
            return saveItem(item)

    return render('saveitem.html', title="New Item", item=item,
                   formAction=url_for('newItem'), cancel=url_for('index'))


@app.route('/item/<int:itemId>/edit/', methods=['GET', 'POST'])
def editItem(itemId):

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
    try:
        item = getOne(Item, 'id', itemId)
        categoryId = item.category.id
        if request.method == 'POST':
            if authed(item.userId):
                Item.delete(item)
                return redirect(url_for('category', categoryId=categoryId))

        return render('deleteitem.html', title="Delete Item", item=item)
    except:
        pass


@app.route('/categories/JSON')
def categoriesJSON():
    categories = getTable(Category)
    return jsonify(restaurants=[c.serialize for c in categories])


@app.route('/category/<int:categoryId>/items/JSON')
def categoryItemsJSON(categoryId):
    items = get(Item, 'categoryId', categoryId)
    return jsonify(items=[i.serialize for i in items])


@app.route('/item/<int:itemId>/JSON')
def itemJSON(itemId):
    item = getOne(Item, 'itemId', itemId)
    return jsonify(item.serialize)




@app.route('/test/', methods=['GET', 'POST'])
def test():
    return '<img src="/static/img/IMG_2099.JPG">'

def startServer():

    app.secret_key = 'super_secret_key'
    app.debug = True
    cache.set('categories', getTable(Category), 3600)
    app.run(host='0.0.0.0', port=8000)

if __name__ == '__main__':
    startServer()

