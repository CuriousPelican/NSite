from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from flask_socketio import SocketIO
from secrets import token_urlsafe

#def create_app():
app = Flask(__name__)

app.config['SECRET_KEY'] = token_urlsafe(32)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = '/Users/Benjamin/Desktop/NSite/app/static'

db = SQLAlchemy(app)

socketio = SocketIO(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

from app.models import User

@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))

# blueprint for auth routes in our app
from app.blueprints.auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)

# blueprint for non-auth parts of app
from app.blueprints.main import main as main_blueprint
app.register_blueprint(main_blueprint)

# blueprint for the chat part
from app.blueprints.chat import chat as chat_blueprint
app.register_blueprint(chat_blueprint, url_prefix="/chat")

# blueprint feed
from app.blueprints.feed import feed as feed_blueprint
app.register_blueprint(feed_blueprint, url_prefix="/feed")

if __name__ == '__main__':
    db.create_all()
    socketio.run(app)