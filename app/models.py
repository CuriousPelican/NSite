from datetime import date
from flask_login import UserMixin # --> a expliquer
from app import db # importe la db


# classe (& table dans la DB) des utilisateurs héritée des classes UserMixin du module flask_login & Model du module flask_sqlalchemy
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys --> SQLAlchemy, identifiant unique
    email = db.Column(db.String(100), unique=True) # des objets de partout !
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))


# classe (& table dans la DB) des messages héritée de la classe Model du module flask_sqlalchemy
class Messages(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    auteurId = db.Column('auteurId', db.Integer)
    auteur = db.Column('auteur', db.String(100))
    contenu = db.Column('contenu', db.String(1000))
    messageId = db.Column('messageId', db.Integer)


# classe (& table dans la DB) des questions/feeditems héritée de la classe Model du module flask_sqlalchemy
class FeedItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hashedid = db.Column(db.String, default="")
    groupId = db.Column(db.Integer)
    titre = db.Column(db.String(100))
    desc = db.Column(db.String(1000))
    creationdate = db.Column(db.Date, default=date.today())
    #    duedate = db.Column(db.Date, default=date.today()+timedelta(days=7)) # --> non fait, pas très utile
    isopen = db.Column(db.Boolean, default=True)
    _1 = db.Column(db.Integer, default=0)
    _2 = db.Column(db.Integer, default=0)
    _3 = db.Column(db.Integer, default=0)
    _4 = db.Column(db.Integer, default=0)
    _5 = db.Column(db.Integer, default=0)
    comments = db.Column(db.String(10000), default="")


# classe (& table dans la DB) des groupes héritée de la classe Model du module flask_sqlalchemy
class Groups(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ownerId = db.Column(db.Integer)
    name = db.Column(db.String(100))