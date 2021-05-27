from flask import flash, redirect, url_for, render_template, request, jsonify, Blueprint, send_from_directory, abort, send_file
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
    return render_template('chat/chat.html', name=current_user.name, id=current_user.id)

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
        file.save("app"+url_for('static', filename=f"chat/downloads/{filename}"))
        #m = Messages.query.order_by(Messages.messageId.desc()).first()
        #dernierId = m.messageId
        if filename[-4:] == ".png" or filename[-4:] == ".jpg" or filename[-4:] == ".gif" or filename[-5:] == ".jpeg":
            fileType = 3
        else:
            fileType = 2
        print(fileType, filename)
        socketio.emit("file link", {"author": current_user.name, "authorId" : current_user.id, "link":'/chat/téléchargements/'+ filename, "filename":filename, "filetype":fileType})
        new_message = Messages(auteurId=current_user.id, auteur=current_user.name, contenu=filename, messageId=fileType)
        db.session.add(new_message)
        db.session.commit()
        return redirect(url_for('chat.index'))
    else:
        return 'Le fichier ne porte pas une extension supportée'
        #redirect(url_for('uploaded_file', filename=filename))

@chat.route('téléchargements/<filename>')
def envoiFichier(filename):
    print("OK", filename)
    filename = secure_filename(filename)
    return send_file(url_for('static', filename=f"chat/downloads/{filename}")[1:], as_attachment=True)
    # try:
    #     return send_from_directory("app", url_for('static', filename="chat/downloads/"), filename=filename, as_attachment=True)
    # except FileNotFoundError:
    #     abort(404)

@socketio.on('NewConnection')
def addlist():
    if current_user.id not in [*userlist.keys()]:
        socketio.emit("new user", {"name":current_user.name, "id":current_user.id}, include_self=False)
        print("un user de plus")
    userlist[current_user.id]=[request.sid, current_user.name]
    names = [item[1] for item in [*userlist.values()]]
    IDs = [*userlist.keys()]
    socketio.emit("userslist", {"names":names, "IDs":IDs}, room=request.sid)
    

@socketio.on('disconnect')
def removeUser():
    print(current_user.name, "s'est déconnecté")
    if current_user.id in [*userlist.keys()]:
        userlist.pop(current_user.id)
    socketio.emit("user left", {"name":current_user.name, "id":current_user.id})
    print("un user en moins")

@socketio.on('message')
def renvoiMessage(data):
    m = Messages.query.order_by(Messages.id.desc()).first()
    dernierId = m.id
    socketio.emit("message", {"author": current_user.name, "authorId" : current_user.id, "content": data["content"], "id":dernierId + 1})
    new_message = Messages(auteurId=current_user.id, auteur=current_user.name, contenu=data["content"], messageId=1)
    db.session.add(new_message)
    db.session.commit()

@socketio.on('Mp')
def renvoiMp(data):
    print("Mp reçu", data)
    recipient = int(data["recipient"])
    if recipient in [*userlist.keys()]:
        address = userlist[recipient][0]
        socketio.emit("Mp", {"user": current_user.name, "userID": current_user.id, "content": data["content"]}, room=address)
        print('Mp renvoyé', {"user": current_user.name, "userID": current_user.id, "content": data["content"]}, "au sid : ", address)

@socketio.on('historique')
def renvoiHistorique(info):
    print('historique demandé', info)
    if info["id"] == -555:
        data = Messages.query.order_by(Messages.id.desc()).limit(info["nombre"]).all()
    else:
        data = Messages.query.filter(Messages.id < info["id"]).order_by(Messages.id.desc()).limit(info["nombre"]).all()
    messages=[]
    for i in range(len(data)):
        messagei = {'authorId':data[i].auteurId, 'author':data[i].auteur, 'content':data[i].contenu, 'id':data[i].id, 'messageId':data[i].messageId}
        messages.append(messagei)
    print(messages)
    socketio.emit('historique', messages, room=request.sid)