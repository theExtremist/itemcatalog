from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

import os


Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(60), nullable=False)
    image = Column(String(), nullable=True)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'image': self.image
        }


class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(String(60), nullable=False)
    description = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    image = Column(String(), nullable=True)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'category': self.category,
            'name': self.name,
            'description': self.description,
            'created by': self.user,
            'image': self.image
        }


if __name__ == '__main__':
    try:
        os.remove("itemcatalog.db")
    except:
        pass

    engine = create_engine('sqlite:///itemcatalog.db')
    Base.metadata.create_all(engine)
    DBsession = sessionmaker(bind=engine)
    session = DBsession()

    #create categories
    for i in range(0,10):
        category = Category(name="Category %s" % i, image="imgCategory %s%s" % (i,".jpg"))
        session.add(category)
        session.commit()

        #create items
        for j in range(0,15):
            item = Item(name="Item %s-%s" %(i, j), image="imgItem %s-%s%s" % (i, j, ".jpg"))
            session.add(item)
            session.commit