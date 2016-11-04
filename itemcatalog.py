from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask import session, flash, make_response

from database import User, Category, Item

import login
import dbQueries

app = Flask(__name__)

@app.route('/')
@app.route('/index/')
def index():
    return render_template('index.html', msg="index page")


@app.route('/login')
def showLogin():
    return login.login()


@app.route('/gconnect', methods=['POST'])
def gconnect():
    return login.gconnect()

@app.route('/category/<int:categoryId>')
def category(categoryId):
    return render_template('category.html', msg="Category page")


@app.route('/item/<int:itemId>')
def item(itemId):
    return render_template('item.html', msg="Item page")


@app.route('/item/<int:categoryId>/new/', methods=['GET', 'POST'])
def newItem(categoryId):
    return render_template('newitem.html', msg="New Item")


@app.route('/item/<int:itemId>/edit/', methods=['GET', 'POST'])
def editItem(itemId):
    return render_template('edititem.html', msg="Edit Item")


@app.route('/item/<int:itemId>/delete/', methods=['GET', 'POST'])
def deleteItem(itemId):
    return render_template('deleteitem.html', msg="Delete Item")


def startServer():
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)


if __name__ == '__main__':
    startServer()
