from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app import db

auth = Blueprint('auth', __name__)


@auth.route('/login')
def login():
    return render_template('auth/login.html')


@auth.route('/signup')
def signup():
    return render_template('auth/signup.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first(
    )  # if this returns a user, then the email already exists in database

    if user:  # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email deja existant')
        return redirect(url_for('auth.signup'))

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    m = User.query.order_by(User.userID.desc()).first()
    dernierId = m.userID
    new_user = User(email=email,
                    name=name,
                    password=generate_password_hash(password, method='sha256'),
                    userID=dernierId + 1)
    print("nouvel utilisateur ajouté avec l'ID : ", dernierId + 1)

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))


@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user:
        flash("Cet email n'existe pas")
        return redirect(url_for('auth.login')) # reload si user existe pas
    elif not check_password_hash(user.password, password):
        flash("Identifiants faux")
        return redirect(url_for('auth.login'))  # reload si mauvais mdp

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('auth.profile'))



@auth.route('/change_name', methods=['POST'])
@login_required
def change_name():
    new_name = request.form.get('new_name')
    user = User.query.get(current_user.id)
    user.name = new_name
    db.session.commit()

    return redirect(url_for('auth.profile'))

@auth.route('/change_email', methods=['POST'])
@login_required
def change_email():
    new_email = request.form.get('new_email')
    password = request.form.get('password')

    user = User.query.get(current_user.id)

    emailexist = User.query.filter_by(email=new_email).first() 

    if emailexist: # email deja pris
        return redirect(url_for('auth.profile'))

    elif check_password_hash(user.password, password): # OK
        user.email = new_email
        db.session.commit()

        return redirect(url_for('auth.profile'))
    else: # pass mauvais
        return redirect(url_for('auth.profile'))
    

@auth.route('/change_pass', methods=['POST'])
@login_required
def change_mdp():
    old_password = request.form.get('old_password')
    new_password = request.form.get('new_password')
    user = User.query.get(current_user.id)
    if check_password_hash(user.password, old_password):
        password = generate_password_hash(new_password, method='sha256')
        user.password = password
        db.session.commit()

        return redirect(url_for('auth.profile'))
    else:
        return redirect(url_for('auth.profile'))

@auth.route('/profile', methods=["POST", "GET"] )
@login_required
def profile():

    if request.method == "POST":

        if request.form.get('change_name'):
            new_name = request.form.get('new_name')
            user = User.query.get(current_user.id)
            user.name = new_name
            db.session.commit()
            flash("Nom changé avec succès !")
            return redirect(url_for('auth.profile'))

        elif request.form.get('change_email'):
            new_email = request.form.get('new_email')
            password = request.form.get('password')
            user = User.query.get(current_user.id)
            emailexist = User.query.filter_by(email=new_email).first() 
            if emailexist: # email deja pris
                flash("Un compte avec cet email existe déjà")
                return redirect(url_for('auth.profile'))
            elif check_password_hash(user.password, password): # OK
                user.email = new_email
                db.session.commit()
                flash("Emain changé avec succès !")
                return redirect(url_for('auth.profile'))
            else: # pass mauvais
                flash("Mauvais mot de passe")
                return redirect(url_for('auth.profile'))

        elif request.form.get('change_pass'):
            old_password = request.form.get('old_password')
            new_password = request.form.get('new_password')
            user = User.query.get(current_user.id)
            if check_password_hash(user.password, old_password): # OK
                password = generate_password_hash(new_password, method='sha256')
                user.password = password
                db.session.commit()
                flash("Mot de passe changé avec succès !")
                return redirect(url_for('auth.profile'))
            else: # pass mauvais
                flash("Mauvais mot de passe")
                return redirect(url_for('auth.profile'))

        else:
            return redirect(url_for('auth.profile'))

    else:
        return render_template('auth/profile.html', name=current_user.name)