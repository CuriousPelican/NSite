from flask_login import login_required, current_user
from flask import Blueprint, render_template
from app import db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')