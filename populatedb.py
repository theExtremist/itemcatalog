from flask import url_for

import os
from shutil import copy
from random import randint

LOREM = ("Sed ut perspiciatis unde omnis iste natus error sit voluptatem "
         "accusantium doloremque laudantium, totam rem aperiam, eaque ipsa "
         "quae abillo inventore veritatis et quasi architecto beatae vitae "
         "dicta sunt explicabo.Nemo enim ipsam voluptatem quia voluptas sit "
         "aspernatur aut odit aut fugit,sed quia consequuntur")



def createRecords(categories, items):

    from db.database import session, Item, Category, User, getTable

    img = 'default.jpg'

    #create users
    for i in range(1, 6):
        user = User(email='user%s@gmail.com' % i, name = 'User %s' % i)
        session.add(user)

    users = getTable(User)

    #create categories
    for i in range(1,categories+1):
        category = Category(name="Category %s" % i)
        session.add(category)


        #create items
        for j in range(1, items+1):
            item = Item(
                name="Item %s-%s" % (i, j),
                image=img,
                category=category,
                description="Description for item %s %s" % (j, LOREM),
                user=users[randint(0,4)])

            session.add(item)

    session.commit()


if __name__ == '__main__':

    #Removes any existing database
    try:
        os.remove("db/itemcatalog.db")
        print "Existing database has been deleted"
    except:
        print "No existing database found"

    #copy default image to the img folder for convenience
    copy ('static/assets/default.jpg', 'static/img/default.jpg' )

    createRecords(10, 5)
    print ("Database, tables and records created...")





