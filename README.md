# NSite (FR)

**Warning:** Project in french, not english !

Projet de fin de 1ère en NSI - Serveur Flask avec 2 applications:
- une appli de chat en temps réel avec SocketIO
- et une de feedback, afin de faire des retours

<br>

**Voir files & project organization pour mieux comprendre l'architecture du projet**

<br>

## Installation & lancement (developpement):

**Attention !** L'installation n'est pas prévue pour une utilisation en production !
Pour cela il faudrait:
- Installer un serveur web (comme Caddy, Ngnix ou Apache)
- Installer un serveur WSGI (comme Gunicorn ou uWSGI)
- S'occuper des certificats SSL/TLS, déployer le tout sur un serveur, ...

<br>

### Installation:
- Télécharger le code
- Faire un venv python (c'est mieux) & l'activer : [Tutoriel](https://sametmax.com/les-environnement-virtuels-python-virtualenv-et-virtualenvwrapper/)
	- `python -m venv chemin_du_venv`
	- executer dans chemin_du_venv/Scripts le script activate adéquat au shell & à l'OS
- installer les dépendances: `pip install flask flask-login flask-socketio==4.3.2 flask-sqlalchemy matplotlib`

<br>

### Lancement:
- lancer le serveur en executant run.py (le plus simple) MAIS sera lancé sur 127.0.0.1:5000 soit inaccessible en dehors du PC host

**OU**

- lancer avec `flask run` (possible de rendre accessible de l'exterieur avec une redirection de ports):
	- Se placer à la racine du projet (dossier dans lequel on peut voir le dossier app & run.py) & taper les commandes:
		- Sous Unix: `export FLASK_APP=app` & `export FLASK_ENV=developpement`
		- Sous Windows (powershell): `$env:FLASK_APP=app` & `$env:FLASK_ENV=developpement`
		- Sous command Propt (powershell): `set FLASK_APP=app` & `set FLASK_ENV=developpement`
	- Puis lancer le serveur: `flask run --host=0.0.0.0`

<br><br>

## Pour n'utiliser qu'une seule des 2 apps:
Si l'on veut uniquement une app de chat ou bien de feedback (pour éviter d'utiliser trop de stockage des fichiers envoyés par les utilisateur par exemple).

Il faut supprimer/commenter dans `app/__init__.py` cela (pour l'app de chat):
```
from app.blueprints.chat import chat as chat_blueprint
app.register_blueprint(chat_blueprint, url_prefix="/chat")
```

Ou cela (pour l'app de feedback):
```
from app.blueprints.feed import feed as feed_blueprint`
app.register_blueprint(feed_blueprint, url_prefix="/feed")
```

<br><br>

## Ameliorations possibles:

- stocker date dernier graph généré & ne pas en regénérer si trop récent pour diminuer le lag
- fonctions de rest de mdp par mail & de confirmation du compte par mail
- pouvoir supprimer son compte
- pouvoir mettre une photo de profil (pas très utile)
- pouvoir changer le nom des groupes/questions
- obligations minimales (nombre de lettres) pr le mdp
- pourvoir mettre une importance à certaines questions & faire des retours globaux
- pouvoir faire des categories de questions & groupes
- selection plusieurs questions pour les supprimer, etc (cfomme des mails)
- bot discord pour l'appli de feedback
- Si on veut un peu rêver: IA qui prédit si les resultats vont ête bons basé sur les feedback & les resultats de DS (moyenne, médiane, écart type, étendue)
- Et puis quelques regler de légers problèmes de sécurité
