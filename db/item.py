from flask import flash, current_app
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, sessionmaker

from database import Base, User, Category
import database as db
import images

class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(String(60), nullable=False)
    description = Column(String(250))
    categoryId = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    userId = Column(String(60), ForeignKey('user.email'))
    user = relationship(User)
    image = Column(String(), nullable=True)

    def __init__(self, name='', description='', category=None, user=None,
                 image=''):
        self.name = name
        self.description = description
        self.category = category
        self.user = user
        self.image = image



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


    @staticmethod
    def validParams(params, image):
        if params['name'] == '':
            flash('You entered an invalid value for the name field')
            return False

        if not images.validName(image.filename.lower()):
            flash('You selected an invalid picture to upload')
            return False
        return True



    @staticmethod
    def save(item, params, image, userId):
        if Item.validParams(params, image):
            item.name = params['name']
            item.categoryId = params['category']
            item.description = params['description']
            item.userId = userId
            db.session.add(item)
            db.session.flush()

            url = images.save(image, item)
            if url:
                item.image = url

            db.session.commit()
            flash("%s has been saved" % item.name)
            return True
        return False


    @staticmethod
    def delete(item):
        try:
            images.delete(item.image)
            db.session.delete(item)
            db.session.commit()
            flash('Item %s has been deleted' % item.name)
            return True
        except:
            flash('An error occured and Item %s not deleted. Please try again' % item.name)
            return False