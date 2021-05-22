from app import app, db, socketio
#from app.models import FeedItem
#FeedItem.query.get(1).comments = ""
#db.session.commit()
db.create_all()
socketio.run(app)
app.run(debug=True)