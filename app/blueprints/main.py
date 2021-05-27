from flask import Blueprint, render_template
from app import db


# initialisation du blueprint
main = Blueprint('main', __name__)


# route page d'accueil, renvoie simplement la page d'accueil
@main.route('/')
def index():
    return render_template('index.html')
