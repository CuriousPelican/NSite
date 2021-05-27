from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash # gérer les hash de mdp
from flask_login import login_user, logout_user, login_required, current_user # gérer le login de l'utilisateur
from app.models import User # classe & table utilisateur
from app import db


# on initialise le blueprint
auth = Blueprint('auth', __name__)


# route login GET, renvoie seulement la page de login avec le formulaire
@auth.route('/login')
def login():
    return render_template('auth/login.html')


# route inscription GET, renvoie seulement la page d'inscription avec le formulaire
@auth.route('/signup')
def signup():
    return render_template('auth/signup.html')


# route logout GET, déconnecte l'utilisateur et le renvoie sur la page principale
@auth.route('/logout')
@login_required # il faut ^tre connecté pour pouvoir accéder à cette page
def logout():
    logout_user()
    return redirect(url_for('main.index'))


# route inscription POST, lorsque l'utilisateur renvoie le formulaire d'inscription
@auth.route('/signup', methods=['POST'])
def signup_post():
    # on stocke dans des variables python les données renvoyées par l'utilisateur
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()  # si renvoie un utilisateur, le mail existe déjà dans la DB

    if user:  # si trouvé, le mail est déjà pris alors on redirige vers la même page et on en informe l'utilisateur pour qu'il réessaie
        flash('Email deja existant')
        return redirect(url_for('auth.signup'))

    # Sinon, c'est bon, on ajoute l'utilisteur à la DB avec le mdp hashé (sha256 pas le top mais ça ira)
    new_user = User(email=email,
                    name=name,
                    password=generate_password_hash(password, method='sha256'))
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login')) # on redirige l'utilisateur vers la page de login


# route login POST, lorsque l'utilisateur renvoie le formulaire de login
@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False # rester connecté ?

    # on cherche dans la DB l'utilisateur avec le mail donné
    user = User.query.filter_by(email=email).first()

    # check si l'utilisateur existe
    # on fait un hash du mdp et on le compare à celui dans la DB
    if not user:
        flash("Cet email n'existe pas")
        return redirect(url_for('auth.login')) # reload si user existe pas
    elif not check_password_hash(user.password, password):
        flash("Identifiants faux")
        return redirect(url_for('auth.login'))  # reload si mauvais mdp

    # Si les vérifications ci dessus sont passée, l'utilisateur à les bons identifiants, on peut donc le login et le rediriger vers sa page de profil
    login_user(user, remember=remember)
    return redirect(url_for('auth.profile'))


# route page de profil
@auth.route('/profile', methods=["POST", "GET"])
@login_required
def profile():

    if request.method == "POST": # si envoi de formulaire par le client

        # si formulaire de changment de nom
        # change le nom et redirige vers la même page (actualise) avec la methode GET
        if request.form.get('change_name'):
            new_name = request.form.get('new_name')
            user = User.query.get(current_user.id)
            user.name = new_name
            db.session.commit()
            flash("Nom changé avec succès !")
            return redirect(url_for('auth.profile'))

        # si formulaire de changment d'email
        # change seulement l'email si le mdp donné est bon et redirige vers la même page (actualise) avec la methode GET
        elif request.form.get('change_email'):
            new_email = request.form.get('new_email')
            password = request.form.get('password')
            user = User.query.get(current_user.id)
            emailexist = User.query.filter_by(email=new_email).first() 
            if emailexist: # email deja pris
                flash("Un compte avec cet email existe déjà")
                return redirect(url_for('auth.profile'))
            elif check_password_hash(user.password, password): # mdp Ok
                user.email = new_email
                db.session.commit()
                flash("Emain changé avec succès !")
                return redirect(url_for('auth.profile'))
            else: # pass mauvais
                flash("Mauvais mot de passe")
                return redirect(url_for('auth.profile'))

        # si formulaire de changment de mdp
        # change seulement le mdp si l'ancien mdp donné est bon et redirige vers la même page (actualise) avec la methode GET
        elif request.form.get('change_pass'):
            old_password = request.form.get('old_password')
            new_password = request.form.get('new_password')
            user = User.query.get(current_user.id)
            if check_password_hash(user.password, old_password): # mdp Ok
                password = generate_password_hash(new_password, method='sha256')
                user.password = password
                db.session.commit()
                flash("Mot de passe changé avec succès !")
                return redirect(url_for('auth.profile'))
            else: # mauvais mdp
                flash("Mauvais mot de passe")
                return redirect(url_for('auth.profile'))

        else:
            return redirect(url_for('auth.profile'))

    else: # sinon on renvoie la page de profil
        return render_template('auth/profile.html', name=current_user.name)