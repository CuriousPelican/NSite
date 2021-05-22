from statistics import median, mean, stdev
import threading as th
from os import remove, path
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, url_for, Blueprint, redirect
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app import db
from app.models import FeedItem, Groups

feed = Blueprint('feed', __name__)
'''@feed.route("/test", methods=["GET", "POST"])
def test():
    if request.method == "POST":
        note = request.form.get('note')
        comment = request.form.get('comment')
        print(note, comment)
        return redirect(url_for("main.index"))
    else:
        return render_template("feed/question.html")'''


@feed.route("/new<groupId>", methods=["GET", "POST"])
@login_required
def newfeeditem(groupId):
    group = Groups.query.filter_by(ownerId=current_user.id, id=groupId).first()

    if group != None:
        if request.method == "POST":
            new_feeditem = FeedItem(groupId=group.id,
                                    titre=request.form.get('titre'),
                                    desc=request.form.get('desc'))
            # add the new feeditem to the database
            db.session.add(new_feeditem)
            db.session.commit()
            new_feeditem.hashedid = generate_password_hash(
                str(new_feeditem.id), method='sha256')[7:-1]
            db.session.commit()
            return redirect(url_for("feed.dash"))
        else:
            return render_template("feed/new.html")

    else:
        return redirect(url_for("main.index"))


@feed.route("/r<feeditemHash>", methods=["GET", "POST"])
def question(feeditemHash):
    if request.method == "POST":
        item = FeedItem.query.filter_by(hashedid=feeditemHash).first()
        note = request.form.get('note')
        comment = request.form.get('comment')
        if note == "1":
            item._1 += 1
        elif note == "2":
            item._2 += 1
        elif note == "4":
            item._4 += 1
        elif note == "5":
            item._5 += 1
        else:
            item._3 += 1
        if comment:
            if item.comments != "":
                item.comments += f" ⸎⸷⫸ʨ5ƐƖƐ␥‡ {comment}"
            else:
                item.comments = comment
        db.session.commit()

        return redirect(url_for("main.index"))
    else:
        #print(FeedItem.query.first().titre, feeditemId)
        return render_template(
            "feed/question.html",
            feeditem=FeedItem.query.filter_by(hashedid=feeditemHash).first())


@feed.route("/dash", methods=["GET", "POST"])
@login_required
def dash():
    if request.method == "POST":
        newgroup = Groups(ownerId=current_user.id,
                          name=request.form.get('groupname'))

        # add the new feeditem to the database
        db.session.add(newgroup)
        db.session.commit()

        #return render_template("feed/dash.html", groups=mygroups)
        return redirect(url_for("feed.dash"))
    else:
        mygroups = Groups.query.filter_by(ownerId=str(current_user.id)).all()
        return render_template("feed/dash.html", groups=mygroups)


@feed.route("/closefi<feeditemId>")
@login_required
def closefeeditem(feeditemId):
    group = Groups.query.filter_by(ownerId=current_user.id, id=FeedItem.query.get(feeditemId).groupId).first()

    if group != None:
        item = FeedItem.query.filter_by(groupId=group.id, id=feeditemId).first()
        item.isopen = False
        db.session.commit()
        return redirect(url_for("feed.group", groupId=item.groupId))

    else:
        return redirect(url_for("main.index"))


@feed.route("/openfi<feeditemId>")
@login_required
def openfeeditem(feeditemId):
    group = Groups.query.filter_by(ownerId=current_user.id, id=FeedItem.query.get(feeditemId).groupId).first()

    if group != None:
        item = FeedItem.query.filter_by(groupId=group.id, id=feeditemId).first()
        item.isopen = True
        db.session.commit()
        return redirect(url_for("feed.group", groupId=item.groupId))

    else:
        return redirect(url_for("main.index"))


@feed.route("/delfi<feeditemId>", methods=["GET", "POST"])
@login_required
def deletefeeditem(feeditemId):
    group = Groups.query.filter_by(ownerId=current_user.id, id=FeedItem.query.get(feeditemId).groupId).first()

    if group != None:
        item = FeedItem.query.filter_by(groupId=group.id, id=feeditemId).first()

        if request.method == "POST":
            if request.form.get('y'):
                db.session.delete(item)
                db.session.commit()
            return redirect(url_for("feed.group", groupId=item.groupId))

        else:
            return render_template("feed/confirmdelete.html", feeditem=item)

    else:
        return redirect(url_for("main.index"))


@feed.route("/delg<groupId>", methods=["GET", "POST"])
@login_required
def deletegroup(groupId):
    group = Groups.query.filter_by(ownerId=current_user.id, id=groupId).first()

    if group != None:
        if request.method == "POST":
            if request.form.get('y'):
                db.session.delete(group)
                items = FeedItem.query.filter_by(groupId=group.id).all()
                for item in items:
                    db.session.delete(item)
                db.session.commit()
            return redirect(url_for("feed.dash"))

        else:
            return render_template("feed/confirmdelete.html", group=group)

    else:
        return redirect(url_for("main.index"))


def tolist(item):
    # ne fonctionne apparemment pas pour des methodes
    #for i in range(1,6):
    #    for j in range(item.globals()['_'+i]):
    #        listenotes.append(i)
    listenotes = [1]*item._1 + [2]*item._2 + [3]*item._3 + [4]*item._4 + [5]*item._5
    # plus optimisé !
    # for i in range(item._1):
    #     listenotes.append(1)
    # for i in range(item._2):
    #     listenotes.append(2)
    # for i in range(item._3):
    #     listenotes.append(3)
    # for i in range(item._4):
    #     listenotes.append(4)
    # for i in range(item._5):
    #     listenotes.append(5)
    return listenotes


def deletegraph(filepath):
    if path.exists(filepath):
        remove(filepath)
    else:
        print("file doesn't exist !")

@feed.route("/g<groupId>", methods=["GET", "POST"])
@login_required
def group(groupId):
    group = Groups.query.filter_by(ownerId=current_user.id, id=groupId).first()

    if group != None:
        if request.method == "POST":
            itemstodelete = FeedItem.query.filter_by(groupId=group.id).limit(request.form.get('nbquestions')).all()
            for itemtodelete in itemstodelete:
                db.session.delete(itemtodelete)
            db.session.commit()
            items = FeedItem.query.filter_by(groupId=group.id).all()
            return redirect(url_for("feed.group", groupId=group.id))

        else:
            items = FeedItem.query.filter_by(groupId=group.id).all()
            means, medians, stdevs, norm1, norm2, norm3, norm4, norm5, totaux, x = [], [], [], [], [], [], [], [], [], []
            for item in items:
                total = item._1+item._2+item._3+item._4+item._5
                if total > 2:
                    listenotes = tolist(item)
                    means.append(round(mean(listenotes), 1))
                    medians.append(median(listenotes))
                    stdevs.append(round(stdev(listenotes), 2))
                    norm1.append(item._1/total)
                    # a voir si + perf: listenotes.count(1)
                    norm2.append(item._2/total)
                    norm3.append(item._3/total)
                    norm4.append(item._4/total)
                    norm5.append(item._5/total)
                    totaux.append(total)
                    x.append(item.titre)
            # --> peut être plus perf avec plusieurs tuple comprehension
            
            plt.figure()
            plt.scatter(x, medians, c="r")
            plt.plot(x, means, c="b")
            plt.savefig("app/"+url_for('static', filename=f"feed/graphs/{current_user.id}.{group.id}.meansmeds.svg"))
            T = th.Timer (30, deletegraph, args=[f"app/static/feed/graphs/{current_user.id}.{group.id}.meansmeds.svg"])
            T.start()

            plt.figure()
            plt.plot(x, stdevs, c="y")
            plt.savefig("app/"+url_for('static', filename=f"feed/graphs/{current_user.id}.{group.id}.stdevs.svg"))
            T = th.Timer (30, deletegraph, args=[f"app/static/feed/graphs/{current_user.id}.{group.id}.stdevs.svg"])
            T.start()

            plt.figure()
            plt.bar(x, norm1, color="#F04747")
            plt.bar(x, norm2, bottom=norm1, color="#F4A39B")
            bottom = tuple(a+b for a,b in zip(norm1, norm2))
            plt.bar(x, norm3, bottom=bottom, color="#EBEDE8")
            bottom2 = tuple(a+b for a,b in zip(bottom, norm3))
            plt.bar(x, norm4, bottom=bottom2, color="#9BD3B3")
            bottom3 = tuple(a+b for a,b in zip(bottom2, norm4))
            plt.bar(x, norm5, bottom=bottom3, color="#3EA777")
            plt.yticks([])
            plt.savefig("app/"+url_for('static', filename=f"feed/graphs/{current_user.id}.{group.id}.histscumules.svg"))
            T = th.Timer (30, deletegraph, args=[f"app/static/feed/graphs/{current_user.id}.{group.id}.histscumules.svg"])
            T.start()

            plt.figure()
            plt.bar(x, totaux, color="grey")
            plt.savefig("app/"+url_for('static', filename=f"feed/graphs/{current_user.id}.{group.id}.effectifsreponses.svg"))
            T = th.Timer (30, deletegraph, args=[f"app/static/feed/graphs/{current_user.id}.{group.id}.effectifsreponses.svg"])
            T.start()

            return render_template("feed/group.html", group=group, items=items, filepath=url_for('static', filename=f"feed/graphs/{current_user.id}.{group.id}"))

    else:
        return redirect(url_for("main.index"))


@feed.route("/f<feeditemId>")
@login_required
def feedmore(feeditemId):
    group = Groups.query.filter_by(ownerId=current_user.id, id=FeedItem.query.get(feeditemId).groupId).first()

    if group != None:
        item = FeedItem.query.filter_by(groupId=group.id, id=feeditemId).first()
        listenotes = tolist(item)
        if listenotes != []:
            x = tuple(listenotes.count(i) for i in range(1,6) if listenotes.count(i) != 0)
            labels = tuple(str(i) for i in range(1,6) if listenotes.count(i) != 0)
            allcolors = ["#F04747", "#F4A39B", "#EBEDE8", "#9BD3B3", "#3EA777"]
            colors = tuple(allcolors[i-1] for i in range(1,6) if listenotes.count(i) != 0)
            plt.figure()
            plt.pie(x, labels=labels, radius=1, autopct='%.1f%%', wedgeprops={"width":0.3, "edgecolor":'w'}, colors=colors) 
            plt.savefig("app/"+url_for('static', filename=f"feed/graphs/{current_user.id}.{item.id}.piefeeditem.svg"))
            T = th.Timer (30, deletegraph, args=[f"app/static/feed/graphs/{current_user.id}.{item.id}.piefeeditem.svg"])
            T.start()
        
        return render_template("feed/feedmore.html", item=item, itemstats={"mean": round(mean(listenotes), 2), "med": median(listenotes), "stdev": round(stdev(listenotes), 2)}, filepath=url_for('static', filename=f"feed/graphs/{current_user.id}.{item.id}"))
    else:
        return redirect(url_for("main.index"))