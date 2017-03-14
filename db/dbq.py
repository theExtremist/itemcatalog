from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os

from database import Base, Category, Item, User


dbPath = os.path.dirname(os.path.realpath(__file__))

# engine = create_engine('postgresql:///catalog')
# engine = create_engine('postgresql://ubuntu:''@localhost/catalog')

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