from datetime import date
from flask_login import UserMixin
from app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

class Messages(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    auteurId = db.Column('auteurId', db.Integer)
    auteur = db.Column('auteur', db.String(100))
    contenu = db.Column('contenu', db.String(1000))
    messageId = db.Column('messageId', db.Integer)

class FeedItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hashedid = db.Column(db.String, default="")
    groupId = db.Column(db.Integer)
    titre = db.Column(db.String(100))
    desc = db.Column(db.String(1000))
    creationdate = db.Column(db.Date, default=date.today())
    #    duedate = db.Column(db.Date, default=date.today()+timedelta(days=7))
    isopen = db.Column(db.Boolean, default=True)
    _1 = db.Column(db.Integer, default=0)
    _2 = db.Column(db.Integer, default=0)
    _3 = db.Column(db.Integer, default=0)
    _4 = db.Column(db.Integer, default=0)
    _5 = db.Column(db.Integer, default=0)
    comments = db.Column(db.String(10000), default="")


class Groups(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ownerId = db.Column(db.Integer)
    name = db.Column(db.String(100))