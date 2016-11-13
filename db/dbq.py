from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, Category, Item, User


engine = create_engine('sqlite:///itemcatalog.db',
            connect_args={'check_same_thread':False},
            poolclass=StaticPool)

Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()


def getAll(table):
    return session.query(table).all()


def getUser(email):
    try:
        return session.query(User).filter_by(email=email).one()
    except:
        return None

def createUser(email, name, pic):
    session.add(User(email=email, name=name, pic=pic))
    session.commit()
    user = session.query(User).filter_by(email=email).one()
    return user


def get(table, field, val):
    return session.query(table).filter(getattr(table, field).like(val)).all()

createUser("x","Y","Z")

# print getAll(User)[1].email
# print getUser("thierr")
# x= getAll(Item)
# for y in x:
#     print y.name
#     print y.category.name
# print getById(Item, "categoryId", 2
# print User.attributes()



# def getRec(table, f, value):
#     return session.query(table).filter_by(id=value).one()





# print getRec(Category, Category.id, 1)

# def createRestaurant(name):
#     session.add(Restaurant(name=name))
#     session.commit()


# def editRestaurant(id, newName):
#     record = session.query(Restaurant).filter_by(id=id).one()
#     record.name = newName
#     session.add(record)
#     session.commit()


# def deleteRestaurant(id):
#     record = session.query(Restaurant).filter_by(id=id).one()
#     session.delete(record)
#     session.commit()


# def getItem(id):
#     return session.query(MenuItem).filter_by(id=id).one()


# def getItems(restaurantId):
#     return session.query(MenuItem).filter_by(restaurant_id=restaurantId).all()


# def newItem(item):
#     session.add(item)
#     session.commit()


# def editItem(newName, record=None, id=""):
#     if not record:
#         record = session.query(MenuItem).filter_by(id=id).one()

#     record.name = newName
#     session.add(record)
#     session.commit()


# def deleteItem(record=None, id=""):
#     if not record:
#         record = session.query(MenuItem).filter_by(id=id).one()

#     session.delete(record)
#     session.commit()