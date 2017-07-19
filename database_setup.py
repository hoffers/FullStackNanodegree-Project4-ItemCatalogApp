import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Category(Base):
    __tablename__ = 'categories'

    cat_id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'cat_id': self.cat_id,
        }


class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'user_id': self.user_id,
            'email': self.email,
            'picture': self.picture
        }


class Item(Base):
    __tablename__ = 'items'

    title = Column(String(80), nullable=False)
    item_id = Column(Integer, primary_key=True)
    description = Column(String(250))
    date_added = Column(TIMESTAMP(timezone=False))
    user_id = Column(Integer, ForeignKey('users.user_id'))
    cat_id = Column(Integer, ForeignKey('categories.cat_id'))
    category = relationship(Category)
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'title': self.title,
            'item_id': self.item_id,
            'description': self.description,
            'date_added': self.date_added,
            'user_id': self.user_id,
            'cat_id': self.cat_id,
        }


engine = create_engine('postgresql:///catalog')


Base.metadata.create_all(engine)
