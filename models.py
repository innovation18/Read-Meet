import os
import dotenv
from sqlalchemy import Column, String, Integer, create_engine, ForeignKey, ARRAY, Boolean
from flask_sqlalchemy import SQLAlchemy
import dotenv

database_path = os.environ['DATABASE_URL']

db = SQLAlchemy()


def setup_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = database_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)
    # migrate = Migrate(app, db)


class Users(db.Model):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    name = Column(String)
    zip_code = Column(Integer)
    city = Column(String(120))
    country = Column(String(100))
    legit = Column(Boolean)  # TODO legitimacy
    books = db.relationship('Books', backref='Users', lazy='dynamic', cascade="all, delete-orphan")
    exchange = db.relationship('Exchange', backref='Users', lazy='dynamic', cascade="all, delete-orphan")

    def __init__(self, name, city, country, zip_code):
        self.name = name
        self.zip_code = zip_code
        self.city = city
        self.country = country

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def short(self):
        return {
            'id': self.user_id,
            'name': self.name,
        }

    def long(self):
        return {
            'user_id': self.user_id,
            'name': self.name,
            'zip_code': self.zip_code,
            'city': self.city,
            'country': self.country,
        }


class Books(db.Model):
    __tablename__ = 'books'

    book_id = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String(120))
    available = Column(Boolean)
    created_by = Column(Integer, ForeignKey('users.user_id'))
    exchange = db.relationship('Exchange', backref='Books', lazy='dynamic', cascade="all, delete-orphan")

    def __init__(self, title, author, created_by):
        self.title = title
        self.author = author
        self.created_by = created_by

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def short(self):
        return {
            'id': self.book_id,
            'title': self.title,
        }

    def details(self):
        return {
            'book_id': self.book_id,
            'title': self.title,
            'author': self.author,
            'user_id': self.created_by
        }


class Exchange(db.Model):
    __tablename__ = 'exchange'

    request_id = Column(Integer, primary_key=True)
    requester_id = Column(Integer, ForeignKey('users.user_id'))
    lender_id = Column(Integer)
    book_id = Column(Integer, ForeignKey('books.book_id'))
    status = Column(String, nullable=False)

    def __init__(self, requester_id, lender_id, book_id, status):
        self.requester_id = requester_id
        self.lender_id = lender_id
        self.book_id = book_id
        self.status = status

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def requests(self):
        return {
            'requester_id': self.requester_id,
            'book_id': self.book_id
        }
