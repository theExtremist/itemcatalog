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
    """Returns all the records from a Table

    Args:
        table : which we want to retrieve

    Returns:
        A list of all the records within the table.
    """

    return session.query(table).all()

def getOne(table, field, val):

    """Returns the first matching record from a table meeting val from a field.

    Args:
        table : the table we want to query
        field : the field we want to filter by
        val   : the value we want to match to in the filter

    Returns:
        The first record from the table where the field matches the val
        argument.
        None if no records are founds.
    """

    try:
        return session.query(table).filter(getattr(table, field).like(val)).all()[0]
    except:
        return None

def get(table, field, val):

    """Returns a list of matching records from a table meeting val from a field.

    Args:
        table : the table we want to query
        field : the field we want to filter by
        val   : the value we want to match to in the filter

    Returns:
        A list of records from the table where the field matches the val
        argument.
    """

    return session.query(table).filter(getattr(table, field).like(val)).all()


# creates a database schema and binds a session to it.
engine = create_engine('sqlite:///db/itemcatalog.db',
                       connect_args={'check_same_thread':False},
                       poolclass=StaticPool)
Base.metadata.create_all(engine)
DBsession = sessionmaker(bind=engine)
session = DBsession()


