from statistics import median, mean, stdev
import threading as th # programmer operations: suppr graphiques
from os import remove, path # supprimer les graphiques
import matplotlib.pyplot as plt # graphiques
from flask import Flask, render_template, request, url_for, Blueprint, redirect, flash
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app import db
from app.models import FeedItem, Groups #import classes de la DB


# précision: Lorsque l'on teste si la methode est POST, il vaut mieux lire le else (si methode GET), cela facilite la compréhension
# en effet, le POST est souvent l'envoi d'un formulaire depuis la page affichée & demandé auparavant avec la methode GET


# initialisation du blueprint
feed = Blueprint('feed', __name__)


# route nouvelle question
@feed.route("/new<groupId>", methods=["GET", "POST"])
@login_required # l'utilisateur doit être connecté afin d'accéder à la page
def newfeeditem(groupId):
    group = Groups.query.filter_by(ownerId=current_user.id, id=groupId).first() # chercher le groupe spécifié dans l'url & appartenant à l'utilisateur connecté

    if group != None: # si trouvé
        if request.method == "POST": # si methode POST (envoi de formulaire par le client)
            # créer une nouvelle question & l'ajouter à la DB
            new_feeditem = FeedItem(groupId=group.id,
                                    titre=request.form.get('titre'),
                                    desc=request.form.get('desc'))
            db.session.add(new_feeditem)
            db.session.commit()
            new_feeditem.hashedid = generate_password_hash(
                str(new_feeditem.id), method='sha256')[7:-1] # enlever "sha256" au début
            db.session.commit()
            return redirect(url_for("feed.dash")) # renvoyer le client vers son dashboard avec tous les groupes
        else:
            return render_template("feed/new.html") # renvoyer la template pour créer un nouveau groupe

    else:
        return redirect(url_for("main.index")) # renvoyer page d'accueil car mauvais utilisateur OU groupe inexistant


# route réponse à une question par un utilisateur (qui n'a pas de compte)
@feed.route("/r<feeditemHash>", methods=["GET", "POST"])
def question(feeditemHash):
    if request.method == "POST": # si envoi de formulaire, alors on enregistre la réponse
        item = FeedItem.query.filter_by(hashedid=feeditemHash).first()
        note = request.form.get('note')
        comment = request.form.get('comment')
        if "⸎⸷⫸ʨ5ƐƖƐ␥‡" in comment:
            flash("Le commentaire contient une chaine de caractères non supportée")
            return redirect(url_for("feed.question"))
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
                item.comments += f" ⸎⸷⫸ʨ5ƐƖƐ␥‡ {comment}" # chaine afin de séparer les messages (qui ne sera certainement pas utilisée par le client & qui est bloquée)
            else:
                item.comments = comment
        db.session.commit()

        return redirect(url_for("main.index"))
    else: # sinon on renvoie la template permettant de répondre avec en argument le hash de la question demandée
        return render_template(
            "feed/question.html",
            feeditem=FeedItem.query.filter_by(hashedid=feeditemHash).first())


# route dashboard, page principale de l'app
@feed.route("/dash", methods=["GET", "POST"])
@login_required
def dash():
    if request.method == "POST": # si envoi de formulaire, alors on enregistre le nouveau groupe
        newgroup = Groups(ownerId=current_user.id,
                          name=request.form.get('groupname'))
        db.session.add(newgroup)
        db.session.commit()
        return redirect(url_for("feed.dash")) # et on redirige vers la même page (on actualise) avec la methode GET

    else: # sinon on renvoie la template du dashboard avec tous les groupes & un formulaire pour en créer un nouveau
        mygroups = Groups.query.filter_by(ownerId=str(current_user.id)).all()
        return render_template("feed/dash.html", groups=mygroups)

# route fermer une question
@feed.route("/closefi<feeditemId>")
@login_required
def closefeeditem(feeditemId):
    # on cherche un groupe qui appartient à l'utilisateur connecté & dont la question fait partie issue (id = groupId de la question)
    # --> tout cela pour vérifier que la question appartient bien à l'utilisateur connecté
    group = Groups.query.filter_by(ownerId=current_user.id, id=FeedItem.query.get(feeditemId).groupId).first()

    if group != None: # si trouvé, on ferme la question
        item = FeedItem.query.filter_by(groupId=group.id, id=feeditemId).first()
        item.isopen = False
        db.session.commit()
        return redirect(url_for("feed.group", groupId=item.groupId)) # et on redirige vers la page sur laquelle on était

    else: # sinon on redirige vers la page principale
        return redirect(url_for("main.index"))


# route ouvrir une question, pareil mais pour ouvrir
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


# route supprimer une question
@feed.route("/delfi<feeditemId>", methods=["GET", "POST"])
@login_required
def deletefeeditem(feeditemId):
    # pareil que pour ouvrir/fermer une question
    group = Groups.query.filter_by(ownerId=current_user.id, id=FeedItem.query.get(feeditemId).groupId).first()

    if group != None:
        item = FeedItem.query.filter_by(groupId=group.id, id=feeditemId).first()

        if request.method == "POST": # si envoi de formulaire
            if request.form.get('y'): # si confirmation de supression, on supprime
                db.session.delete(item)
                db.session.commit()
            return redirect(url_for("feed.group", groupId=item.groupId)) # on redirige vers la page qui précède la confirmation (que l'action ait été confirmée ou non)

        else: # sinon on renvoie la page de confirmation de suppression (avec le formulaire qui permet de confirmer)
            return render_template("feed/confirmdelete.html", feeditem=item)

    else: # sinon on redirige vers la page principale
        return redirect(url_for("main.index"))


# route supprimer un groupe, pareil que pour une question mais avec un groupe
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


# fonction construisant une liste à partir des nombres dans la DB
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


# fonction de suppression des graphiques (une fois envoyés au client)
def deletegraph(filepath):
    if path.exists(filepath):
        remove(filepath)
    else:
        print("file doesn't exist !")


# route gestion d'un groupe (liste des questions, graphiques, ...)
@feed.route("/g<groupId>", methods=["GET", "POST"])
@login_required
def group(groupId):
    group = Groups.query.filter_by(ownerId=current_user.id, id=groupId).first() # chercher le groupe spécifié dans l'url & appartenant à l'utilisateur connecté

    if group != None: # si trouvé
        if request.method == "POST": # si forumulaire de suppression des x plus anciennes questions renvoyé
            if request.form.get('nbquestions'):
                itemstodelete = FeedItem.query.filter_by(groupId=group.id).limit(request.form.get('nbquestions')).all()
                for itemtodelete in itemstodelete:
                    db.session.delete(itemtodelete)
                db.session.commit()
            return redirect(url_for("feed.group", groupId=group.id)) # et on redirige vers la même page (on actualise) avec la methode GET

        else:
            items = FeedItem.query.filter_by(groupId=group.id).all() # on charge toutes les questions du groupe
            means, medians, stdevs, norm1, norm2, norm3, norm4, norm5, totaux, x = [], [], [], [], [], [], [], [], [], [] # on initialise les variables
            for item in items:
                total = item._1+item._2+item._3+item._4+item._5
                if total > 2: # si nb de réponses >=3 (pour calculer le stdev)
                    listenotes = tolist(item) # on fait une liste des réponses
                    means.append(round(mean(listenotes), 1)) # on ajoute la moyenne de la question à la liste des moyennes
                    medians.append(median(listenotes)) # pareil avec la médiane
                    stdevs.append(round(stdev(listenotes), 2)) # ...
                    norm1.append(item._1/total) # avec la proportion de 1
                    norm2.append(item._2/total)
                    norm3.append(item._3/total)
                    norm4.append(item._4/total)
                    norm5.append(item._5/total)
                    totaux.append(total)
                    x.append(item.titre) # avec le titre de la question
            # --> peut être plus perf avec plusieurs tuple comprehension

            # 1er graphique            
            plt.figure() # on initialise une figure matplotlib
            plt.scatter(x, medians, c="#F14668", label='Medianes') # on trace un nuage de points des médianes en fonction des questions
            plt.plot(x, means, c="#00D1B2", label='Moyennes') # pareil avec une courbe des moyennes
            plt.legend()
            plt.savefig("app"+url_for('static', filename=f"feed/graphs/{current_user.id}.{group.id}.meansmeds.svg")) # on enregistre la figure
            # on programme dans 30s la supression du fichier (largement sufisant pour qu'il soit envoyé au client) en appelant la fonction deletegraph
            T = th.Timer (30, deletegraph, args=[f"app/static/feed/graphs/{current_user.id}.{group.id}.meansmeds.svg"])
            T.start()

            # 2eme graphique
            plt.figure()
            plt.plot(x, stdevs, c="#00D1B2", label='Ecarts types') # on trace une courbe des écarts types en fonction des questions
            plt.legend()
            plt.savefig("app"+url_for('static', filename=f"feed/graphs/{current_user.id}.{group.id}.stdevs.svg"))
            T = th.Timer (30, deletegraph, args=[f"app/static/feed/graphs/{current_user.id}.{group.id}.stdevs.svg"])
            T.start()

            # 3eme graphique (le plus complexe)
            plt.figure()
            plt.bar(x, norm1, color="#F04747", label='1') # on trace un histogramme de la proportion de 1 en fonction des questions
            plt.bar(x, norm2, bottom=norm1, color="#F4A39B", label='2') # histogramme de la proportion de 2 en fonction des questions emplilé sur celui des 1
            bottom = tuple(a+b for a,b in zip(norm1, norm2)) # on créé un tuple de la proportion des 1 + des 2 en fonction des questions pour pouvoir empiler l'histogramme des 3 dessus
            plt.bar(x, norm3, bottom=bottom, color="#EBEDE8", label='3') # hist des 3
            bottom2 = tuple(a+b for a,b in zip(bottom, norm3)) # tuple 1 + 2 + 3
            plt.bar(x, norm4, bottom=bottom2, color="#9BD3B3", label='4') # hist des 4
            bottom3 = tuple(a+b for a,b in zip(bottom2, norm4)) # tuple 1 + 2 + 3 + 4
            plt.bar(x, norm5, bottom=bottom3, color="#3EA777", label='5') # hist des 5
            plt.yticks([]) # on ne met pas de graduations sur l'axe des y (on veut juste une proportion visuelle)
            plt.legend()
            plt.savefig("app"+url_for('static', filename=f"feed/graphs/{current_user.id}.{group.id}.histscumules.svg"))
            T = th.Timer (30, deletegraph, args=[f"app/static/feed/graphs/{current_user.id}.{group.id}.histscumules.svg"])
            T.start()

            # 4eme graphique
            plt.figure()
            plt.bar(x, totaux, color="grey", label='Nombre de réponses') # on trace un histogramme des nombres de réponses en fonction des questions
            plt.legend()
            plt.savefig("app"+url_for('static', filename=f"feed/graphs/{current_user.id}.{group.id}.effectifsreponses.svg"))
            T = th.Timer (30, deletegraph, args=[f"app/static/feed/graphs/{current_user.id}.{group.id}.effectifsreponses.svg"])
            T.start()

            # on renvoie la template de la page personnalisée avec le groupe, la liste des questions et le path des graphiques
            return render_template("feed/group.html", group=group, items=items, filepath=url_for('static', filename=f"feed/graphs/{current_user.id}.{group.id}"))

    else: # sinon on renvoie vers la page principale
        return redirect(url_for("main.index"))


# route gestion d'une question (liste des commentaires, graphiques, ...)
@feed.route("/f<feeditemId>")
@login_required
def feedmore(feeditemId):
    # pareil que la route closefeeditem
    group = Groups.query.filter_by(ownerId=current_user.id, id=FeedItem.query.get(feeditemId).groupId).first()

    if group != None:
        # on charge la question voulue & on met les notes dans une liste
        item = FeedItem.query.filter_by(groupId=group.id, id=feeditemId).first()
        listenotes = tolist(item)

        x = tuple(listenotes.count(i) for i in range(1,6) if listenotes.count(i) != 0) # tuple du nombre de 1 puis 2, 3, 4, & 5 sauf si il y a 0 fois la valeur
        labels = tuple(str(i) for i in range(1,6) if listenotes.count(i) != 0) # mecanisme identique mais avec le nom de la variable d'index x dans le tuple (pour ne pas se décaler si il y a 0 fois un nombre)
        allcolors = ("#F04747", "#F4A39B", "#EBEDE8", "#9BD3B3", "#3EA777") # tuple des codes couleurs correspondants du 1 au 5 
        colors = tuple(allcolors[i-1] for i in range(1,6) if listenotes.count(i) != 0) # mecanisme identique que les noms mais pour les couleurs
        # graphique en camembert (ou pie chart, c'est plus joli) du nombre (& pourcentage) de 1, 2, 3, 4, & 5 (sauf si 0)
        plt.figure()
        plt.pie(x, labels=labels, radius=1, autopct='%.1f%%', wedgeprops={"width":0.3, "edgecolor":'w'}, colors=colors)
        plt.savefig("app"+url_for('static', filename=f"feed/graphs/{current_user.id}.{item.id}.piefeeditem.svg"))
        T = th.Timer (30, deletegraph, args=[f"app/static/feed/graphs/{current_user.id}.{item.id}.piefeeditem.svg"])
        T.start()
        if item._1+item._2+item._3+item._4+item._5 > 2: # si nb de réponses >=3 (pour calculer le stdev)
            moy = round(mean(listenotes), 2)
            med = median(listenotes)
            etype = round(stdev(listenotes), 2)
        else:
            moy = "Pas assez de données"
            med = "Pas assez de données"
            etype = "Pas assez de données"
        # on renvoie la template de la page personnalisée avec la question, les statistiques de la question et le path des graphiques
        return render_template("feed/feedmore.html", item=item, itemstats={"mean": moy, "med": med, "stdev": etype}, filepath=url_for('static', filename=f"feed/graphs/{current_user.id}.{item.id}"))

    else:
        return redirect(url_for("main.index"))