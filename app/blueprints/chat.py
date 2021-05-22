from flask import Flask, flash, redirect, url_for, render_template, request, jsonify, Blueprint, send_from_directory, abort
from flask_socketio import SocketIO, emit
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db, socketio, app
from app.models import Messages
import os
#from datetime import datetime

chat = Blueprint('chat', __name__)
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
userlist={}

@chat.route('/')
@login_required
def index():
    return render_template('chat/chat.html', name=current_user.name, id=current_user.userID)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@chat.route('/', methods=['POST'])
def recevoirFichier():
    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        print('fichier reçu : ', file.filename)
        file.save(url_for('static', filename="chat/uploaded"), filename)
        m = Messages.query.order_by(Messages.messageId.desc()).first()
        dernierId = m.messageId
        socketio.emit("lien fichier", {"auteur": current_user.name, "auteurId" : current_user.userID, "lien":'/chat/téléchargements/'+ filename, "nomFichier":filename})
        new_message = Messages(auteurId=current_user.userID, auteur=current_user.name, contenu="‡" + filename, messageId=dernierId + 1)
        db.session.add(new_message)
        db.session.commit()
        return redirect(url_for('chat.index'))
    else:
        return 'Le fichier ne porte pas une extension supportée'
        #redirect(url_for('uploaded_file', filename=filename))

@chat.route('/telechargements/<filename>')
def envoiFichier(filename):
    try:
        return send_from_directory(url_for('static', filename="chat/uploaded"), filename=filename, as_attachment=True)
    except FileNotFoundError:
        abort(404)

@socketio.on('NewConnection')
def addlist():
    for sid, [ID, name] in userlist.items():
        if current_user.userID == ID:
            userlist.pop(sid)
    userlist[request.sid]=[current_user.userID, current_user.name]
    names = [item[1] for item in [*userlist.values()]]
    IDs = [item[0] for item in [*userlist.values()]]
    socketio.emit("userslist", {"names":names, "IDs":IDs})
    print("nouvelle liste envoyée, un user de plus", {"names":names, "IDs":IDs})

@socketio.on('disconnect')
def removeUser():
    print(current_user.name, "s'est déconnecté")
    if request.sid in [*userlist.keys()]:
        userlist.pop(request.sid)
    names = [item[1] for item in [*userlist.values()]]
    IDs = [item[0] for item in [*userlist.values()]]
    socketio.emit("userslist", {"names":names, "IDs":IDs})
    print("nouvelle liste envoyée, un user en moins", {"names":names, "IDs":IDs})

@socketio.on('message')
def renvoiMessage(data):
    m = Messages.query.order_by(Messages.messageId.desc()).first()
    dernierId = m.messageId

    """a = data["content"]
    b = ""
    for i in range(1, len(a), 2):
        b += a[i-1]
        if a[i] == " ":
            b += " "
        else :
            b += chr(ord(a[i])-32)
    if len(a)%2 != 0:
        b += a[-1]"""


    socketio.emit("message", {"user": current_user.name, "userID" : current_user.userID, "content": data["content"], "messageId" : dernierId + 1})
    new_message = Messages(auteurId=current_user.userID, auteur=current_user.name, contenu=data["content"], messageId=dernierId + 1)
    db.session.add(new_message)
    db.session.commit()

@socketio.on('Mp')
def renvoiMp(data):
    print("Mp reçu", data)
    recipient = int(data["recipient"])
    for sid, [ID, name] in userlist.items():
        if recipient == ID:
            address = sid
    socketio.emit("Mp", {"user": current_user.name, "userID" : current_user.userID, "content": data["content"]}, room=address)
    print('Mp renvoyé', {"user": current_user.name, "userID" : current_user.userID, "content": data["content"]}, "au sid : ", address)

@socketio.on('historique')
def renvoiHistorique(info):
    print('historique demandé', info)
    if info["id"] == -555:
        data = Messages.query.order_by(Messages.messageId.desc()).limit(info["nombre"]).all()
    else:
        data = Messages.query.filter(Messages.messageId < info["id"]).order_by(Messages.messageId.desc()).limit(info["nombre"]).all()
    messages=[]
    for i in range(len(data)):
        messagei = {'auteurId':data[i].auteurId, 'auteur':data[i].auteur, 'contenu':data[i].contenu, 'messageId':data[i].messageId}
        messages.append(messagei)
    print(messages)
    socketio.emit('historique', messages)