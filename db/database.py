from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from base import Base
from category import Category
from user import User
from item import Item


import os

def getTable(table):
    return session.query(table).all()

def getOne(table, field, val):
    try:
        return session.query(table).filter(getattr(table, field).like(val)).all()[0]
    except:
        return None

def get(table, field, val):
    return session.query(table).filter(getattr(table, field).like(val)).all()


engine = create_engine('sqlite:///db/itemcatalog.db',
        connect_args={'check_same_thread':False},
        poolclass=StaticPool)
Base.metadata.create_all(engine)
DBsession = sessionmaker(bind=engine)
session = DBsession()


