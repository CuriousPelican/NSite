from flask import flash, redirect, url_for, render_template, request, Blueprint, send_file
from flask_socketio import emit
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db, socketio
from app.models import Messages
# from datetime import datetime

# on déclare le blueprint pour relier ce code au reste
chat = Blueprint('chat', __name__)
# on déclare une liste d'extensions supportées pour notre système d'upload de fichiers
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
# on déclare le dictionnaire qui va contenir la liste des utilisateurs en cours de l'app de chat
# le dictionnaire a pour clef l'identifiant de l'utilisateur, et pour valeur, un liste de deux éléments : son adresse web socket et son nom
userlist={}

# comme ce blueprint a un url_prefix "/chat", cela ce déclenche lorsque le client va à l'adresse "/chat/"
@chat.route('/')
# @login_required permet de limiter l'accès aux utilisateurs identifiés (connectés avec un conpte)
@login_required
def index():
    # on renvoie la page de chat avec deux varialbes : l'identifiant et le nom de l'utilisateur
    return render_template('chat/chat.html', name=current_user.name, id=current_user.id)

# vérifie que le fichier reçu possède une extension autorisée
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# lorsque l'on reçoit une requête post à l'adresse "/chat/", ce qui correspond à l'envoi d'un fichier
@chat.route('/', methods=['POST'])
def recevoirFichier():
    # on vérifie qu'un fichier a été envoyé
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    # il se peut que le navigateur envoie un fichier sans nom si on n'a pas sélectionné de fichier, on vérifie donc
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    # si un fichier a été envoyé, et que celui-ci comporte une extension autorisée
    if file and allowed_file(file.filename):
        # on rend le nom du fichier sécurisé (on enlève les "../../" s'il y en a)
        filename = secure_filename(file.filename)
        print('fichier reçu : ', file.filename)
        # on enregistre le fichier
        file.save("app"+url_for('static', filename=f"chat/downloads/{filename}"))
        # si le fichier est un fichier image, alors son fileType est de 3
        if filename[-4:] == ".png" or filename[-4:] == ".PNG" or filename[-4:] == ".jpg" or filename[-4:] == ".JPG" or filename[-4:] == ".gif" or filename[-4:] == ".GIF" or filename[-5:] == ".jpeg" or filename[-5:] == ".JPEG":
            fileType = 3
        # sinon, alors c'est un fichier texte, son fileType sera donc de 2
        else:
            fileType = 2
        print(fileType, filename)
        # on envoie un web socket à tous les utilisateurs du chat pour qu'ils affichent un lien pour télécharger le fichier, et afficher le fichier dans le chat si c'est une image
        socketio.emit("file link", {"author": current_user.name, "authorId" : current_user.id, "link":'/chat/téléchargements/'+ filename, "filename":filename, "filetype":fileType})
        # on enregistre le fichier comme une message dans la base de donnée, mais l'attribut messageId permet de savoir que c'est un fichier
        new_message = Messages(auteurId=current_user.id, auteur=current_user.name, contenu=filename, messageId=fileType)
        db.session.add(new_message)
        db.session.commit()
        return redirect(url_for('chat.index'))
    else:
        return 'Le fichier ne porte pas une extension supportée'

# lorsqu'un utilisateur envoie une requête à l'adresse "/chat/téléchargements/NomDeFichier.extension"
@chat.route('téléchargements/<filename>')
# on récupère le nom du fichier comme une variable (extension comprise)
def envoiFichier(filename):
    # on supprime les "../../" du nom du fichier pour éviter que ça ne demande un fichier hors du dossier de téléchargement
    filename = secure_filename(filename)
    # on envoie le fichier demandé du dossier dowmloads, avec as_attachement=True pour que le client puisse télécharger le fichier sur son stockage interne
    return send_file(url_for('static', filename=f"chat/downloads/{filename}")[1:], as_attachment=True)

# lorsque l'on reçoit le web socket de la demande de connection d'un nouvel utilisateur du chat
@socketio.on('NewConnection')
def addlist():
    # on vérifie que c'est bien un nouvel utilisateur, le client aurait pu simplement recharger sa page
    if current_user.id not in [*userlist.keys()]:
        # si oui on envoie un web socket à tout le mode pour signifier qu'un nouvel utilisateur est là
        socketio.emit("new user", {"name":current_user.name, "id":current_user.id}, include_self=False)
        print("un utilisateur de plus")
    # sinon, si l'utilisateur était déjà là, on met simplement à jour l'adresse du web socket, et le nom de l'utilisateur, si celui-ci a décidé de le changer entre temps
    # request.sid correspond à l'adresse depuis laquelle est envoyée le web socket reçu
    userlist[current_user.id]=[request.sid, current_user.name]
    names = [item[1] for item in [*userlist.values()]]
    IDs = [*userlist.keys()]
    socketio.emit("userslist", {"names":names, "IDs":IDs}, room=request.sid)
    # on envoie (seulement à l'utilisateur qui vient de se (re)connecter) la liste de tous les idemtifiants et de tous les noms des personnes présentes sur le chat
    
# lorsque l'on reçoit le web socket de base qui signifie que la connexion web socket avec un utilisateur s'est rompue
@socketio.on('disconnect')
def removeUser():
    # si un utilisateur était connecté avec cette adresse, alors on le supprime de la liste
    # sinon, si l'utilisateur s'est connecté entre temps à une autre adresse, alors on ne fait rien
    if request.sid in [*userlist.values()][0]:
        userlist.pop(current_user.id)
        socketio.emit("user left", {"name":current_user.name, "id":current_user.id})
        print("un utilisateur en moins")

# lorsque l'on reçoit le web socket d'un utilisateur qui souhaite envoyer un message au chat
@socketio.on('message')
def renvoiMessage(data):
    # on regarde que est l'identifiant du dernier message dans la base donnée pour savoir quel sera l'identifiant de celui-ci
    m = Messages.query.order_by(Messages.id.desc()).first()
    dernierId = m.id
    # on renvoie un web socket à tout le monde, avec les informations du message dedans
    socketio.emit("message", {"author": current_user.name, "authorId" : current_user.id, "content": data["content"], "id":dernierId + 1})
    # on enregistre le message dans la base de données
    new_message = Messages(auteurId=current_user.id, auteur=current_user.name, contenu=data["content"], messageId=1)
    db.session.add(new_message)
    db.session.commit()

# lorsque l'on reçoit le web socket d'un utilisateur qui souhaite envoyer un message privé à un autre utilisateur
@socketio.on('Mp')
def renvoiMp(data):
    # on récupère l'adresse à laquelle est connecté le destinataire
    recipient = int(data["recipient"])
    if recipient in [*userlist.keys()]:
        address = userlist[recipient][0]
        # on envoie seulement à cette adresse le web socket contenant le message
        socketio.emit("Mp", {"user": current_user.name, "userID": current_user.id, "content": data["content"]}, room=address)
        print('Mp renvoyé', {"user": current_user.name, "userID": current_user.id, "content": data["content"]}, "au sid : ", address)

# lorsque l'on reçoit le web socket correspondant à la demande de messages de l'historique
@socketio.on('historique')
def renvoiHistorique(info):
    print('historique demandé', info)
    # si le client n'a pas encore de messages d'affiché
    if info["id"] == -555:
        # on demande à la base de donnée les nombre plus récents messages
        data = Messages.query.order_by(Messages.id.desc()).limit(info["nombre"]).all()
    else:
        # sinon on demande à la base de données les nombre plus récent messages avec un id inférieur à id
        data = Messages.query.filter(Messages.id < info["id"]).order_by(Messages.id.desc()).limit(info["nombre"]).all()
    messages=[]
    # on concentre ces messages dans une liste de dictionnaires, où chaque dictionnaire correspond à un message
    for i in range(len(data)):
        messagei = {'authorId':data[i].auteurId, 'author':data[i].auteur, 'content':data[i].contenu, 'id':data[i].id, 'messageId':data[i].messageId}
        messages.append(messagei)
    print(messages)
    # on renvoie la liste de messages uniquement à l'utilisateur qui a demandé l'historique
    socketio.emit('historique', messages, room=request.sid)