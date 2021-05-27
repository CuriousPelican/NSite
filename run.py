# importe depuis le module app l'appli flask, la db & socketio
from app import app, db, socketio
db.create_all() # creer la db (fait les tables si elle n'existent pas encore)
socketio.run(app) # lancer socketio sur l'appli faks "app"
app.run(host='0.0.0.0', port="5000", debug=True) # lancer le serveur