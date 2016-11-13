import os


def createRecords(categories, items):

    from db.database import session, Item, Category

    #create categories
    for i in range(1,categories+1):
        category = Category(name="Category %s" % i, image="imgCategory %s%s" % (i,".jpg"))
        session.add(category)
        session.commit()

        #create items
        for j in range(1,items+1):
            item = Item(
                name="Item %s-%s" %(i, j),
                image="imgItem %s-%s%s" % (i, j, ".jpg"),
                category=category)

            session.add(item)
            session.commit()


if __name__ == '__main__':
    try:
        os.remove("db/itemcatalog.db")
        print "Existing database has been deleted"
    except:
        print "No existing database found"

    createRecords(10, 10)
    print ("Database, tables and records created...")





