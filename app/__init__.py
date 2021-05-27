from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from flask_socketio import SocketIO
from secrets import token_urlsafe

# ce fichier respecte surtout les conventions de Flask & de ses modules

# initialiser l'appli Flask, base du projet
app = Flask(__name__)

app.config['SECRET_KEY'] = token_urlsafe(32) # génère une clé de façon sécurisée (pour signer les formulaire & les cookies de session, chose non faite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite' # lien vers la DB
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # ne pas enregistrer dans la DB toutes les modifications

db = SQLAlchemy(app) # initialise la DB

socketio = SocketIO(app) # initialise socketio

login_manager = LoginManager()
login_manager.login_view = 'auth.login' # on configure la page de login
login_manager.init_app(app)

# on importe la classe (& table) utilisateur
from app.models import User

@login_manager.user_loader
def load_user(user_id):
    # renvoie l'utilisateur que l'on veut charger
    return User.query.get(int(user_id))

# blueprint authentification
from app.blueprints.auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)

# blueprint page d'accueil
from app.blueprints.main import main as main_blueprint
app.register_blueprint(main_blueprint)

# blueprint appli de chat
from app.blueprints.chat import chat as chat_blueprint
app.register_blueprint(chat_blueprint, url_prefix="/chat") # on passe toutes les requêtes commençant par l'url_prefix au Blueprint en lui "enlevant" cette partie

# blueprint appli de feedback
from app.blueprints.feed import feed as feed_blueprint
app.register_blueprint(feed_blueprint, url_prefix="/feed")

if __name__ == '__main__': # inutile vu que lancé avec run.py
    db.create_all()
    socketio.run(app)