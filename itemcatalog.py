from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask import session, flash, make_response
from flask.ext.cache import Cache

from db.database import User, Category, Item, get, getOne, getTable

import login


app = Flask(__name__)
cache = Cache(app,config={'CACHE_TYPE': 'simple'})



@app.route('/login')
def showLogin():
    return login.login()


@app.route('/gconnect', methods=['POST'])
def gconnect():
    return login.gconnect(session)

@app.route('/logout')
def logout():
    print login.logout(session)
    print session

    return render('index.html', msg="index page")


def render(template, **kw):
    loggedIn = 'provider' in session
    print loggedIn
    return render_template(template, categories=cache.get('categories'),
                            loggedIn=loggedIn, **kw)


@app.route('/')
@app.route('/index/')
def index():
    return render('index.html', msg="index page")


@app.route('/category/<int:categoryId>')
def category(categoryId):
    items = get(Item, "categoryId", categoryId)
    return render('category.html', msg="Category page", items=items)


@app.route('/item/<int:itemId>')
def item(itemId):
    item = get(Item, "id", itemId)[0]
    return render('item.html', msg="Item page", item=item)


@app.route('/item/new/', methods=['GET', 'POST'])
def newItem(item=Item()):
    try:
        if request.method == 'POST':
            if Item.save(item, request.form):
                return redirect(url_for('item', itemId=item.id))

        return render('newitem.html', msg="New Item", item=Item())
    except:
        pass


@app.route('/item/<int:itemId>/edit/', methods=['GET', 'POST'])
def editItem(itemId):
    try:
        item = getOne(Item, 'id', itemId)
        if request.method == 'POST':
            Item.save(item, request.form)
            return redirect(url_for('item', itemId=itemId))

        return render('edititem.html', msg="Edit Item", item=item)
    except:
        pass

@app.route('/item/<int:itemId>/delete/', methods=['GET', 'POST'])
def deleteItem(itemId):
    try:
        item = getOne(Item, 'id', itemId)
        categoryId = item.category.id
        if request.method == 'POST':
            Item.delete(item)
            return redirect(url_for('category', categoryId=categoryId))

        return render('deleteitem.html', msg="Delete Item", item=item)
    except:
        pass


def startServer():

    app.secret_key = 'super_secret_key'
    app.debug = True
    cache.set('categories', getTable(Category))
    app.run(host='0.0.0.0', port=8000)

if __name__ == '__main__':
    startServer()
