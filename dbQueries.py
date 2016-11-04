from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from database import Base, Category, Item


engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()


def getRec(id):
    return session.query(Category).filter_by(id=id).one()


def getAll(table):
    return session.query(table).all()


def createRestaurant(name):
    session.add(Restaurant(name=name))
    session.commit()


def editRestaurant(id, newName):
    record = session.query(Restaurant).filter_by(id=id).one()
    record.name = newName
    session.add(record)
    session.commit()


def deleteRestaurant(id):
    record = session.query(Restaurant).filter_by(id=id).one()
    session.delete(record)
    session.commit()


def getItem(id):
    return session.query(MenuItem).filter_by(id=id).one()


def getItems(restaurantId):
    return session.query(MenuItem).filter_by(restaurant_id=restaurantId).all()


def newItem(item):
    session.add(item)
    session.commit()


def editItem(newName, record=None, id=""):
    if not record:
        record = session.query(MenuItem).filter_by(id=id).one()

    record.name = newName
    session.add(record)
    session.commit()


def deleteItem(record=None, id=""):
    if not record:
        record = session.query(MenuItem).filter_by(id=id).one()

    session.delete(record)
    session.commit()