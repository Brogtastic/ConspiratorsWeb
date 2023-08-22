from flask import Blueprint, render_template, request, jsonify, redirect, url_for, abort
from flask_login import LoginManager, login_user, current_user, login_required
from models import Room, Member, Theory
from __init__ import db
import random

views = Blueprint(__name__, "views")

number = "0"
name = "no name"
allRoomCodes = {"1234567"}
secret_key = "agekvoslfhfgaye6382m4i201nui32h078hrauipbvluag78e4tg4w3liutbh2q89897wrgh4ui3gh2780gbrwauy"

@views.route("/", methods=['GET', 'POST'])
def home():
    global allRoomCodes
    if(request.method=='POST'):
        enteredRoomCode = request.form.get('roomCode')
        playerName = request.form.get('name')

        room = Room.query.filter_by(code=enteredRoomCode).first()
        if(room):
            names_list = []
            for member in room.members:
                names_list.append(member.name + " ")
            number_of_members = len(names_list)


        if (len(enteredRoomCode) != 4):
            return render_template("index.html", number=number, roomCode="",error="Room Code should be 4 digits long. Please try again")
        elif(enteredRoomCode not in allRoomCodes):
            return render_template("index.html", number=number, roomCode="", error="Room Code does not exist. Please try again")
        elif (number_of_members >= 8):
            return render_template("index.html", number=number, roomCode="", error="Room is full!")
        elif ((playerName.strip() in [name.strip() for name in names_list]) and (not current_user.is_authenticated)) or (current_user.is_authenticated and current_user.name != playerName and (playerName.strip() in [name.strip() for name in names_list])):
            return render_template("index.html", number=number, roomCode=enteredRoomCode, error="Name already in use. Please enter a different name.")
        elif (len(playerName) == 0):
            return render_template("index.html", number=number, roomCode=enteredRoomCode, error="Please enter a name.")
        elif not current_user.is_authenticated:
            room = Room.query.filter_by(code=enteredRoomCode).first()
            new_member = Member(name=playerName, room_id=room.id, points=0)
            db.session.add(new_member)
            db.session.commit()
            login_user(new_member, remember=True)
            return redirect(url_for('views.play', roomCodeEnter=enteredRoomCode))
        elif current_user.room_id != enteredRoomCode:
            room = Room.query.filter_by(code=enteredRoomCode).first()
            if(room.gameStage == "round0"):
                #Allow room changes if still in starting room
                member_to_update = Member.query.get(current_user.id)
                if member_to_update:
                    member_to_update.name = playerName
                    member_to_update.room_id = room.id
                    db.session.commit()
                return redirect(url_for('views.play', roomCodeEnter=enteredRoomCode))
            else:
                #Keep old inactive member in previous room, create a new member for new room
                new_member = Member(name=playerName, room_id=room.id, points=0)
                db.session.add(new_member)
                db.session.commit()
                login_user(new_member, remember=False)
                return redirect(url_for('views.play', roomCodeEnter=enteredRoomCode))
        else:
            #Allow name changes if still in starting room.
            room = Room.query.filter_by(code=enteredRoomCode).first()
            if(current_user.name != playerName) and (room.gameStage == "round0"):
                member_to_update = Member.query.get(current_user.id)
                if member_to_update:
                    member_to_update.name = playerName
                    db.session.commit()
            return redirect(url_for('views.play', roomCodeEnter=enteredRoomCode))

    return render_template("index.html", number=number, error=" ", roomCode="")


@views.route("/profile")
def profile():
    global number
    args = request.args
    number = args.get('number', number)  # If 'number' is not in the query parameters, keep the current number
    return jsonify({'number': number})


@views.route("/number-of-members/<roomCode>")
def numMembersReturn(roomCode):
    room = Room.query.filter_by(code=roomCode).first()
    if room:
        numMembers = len(room.members)
        return jsonify({'numMembers': numMembers})
    else:
        return jsonify({'numMembers': 0})

@views.route("/game-stage/<roomCode>")
def gameStageReturn(roomCode):
    room = Room.query.filter_by(code=roomCode).first()
    if room:
        return jsonify({'gameStage': room.gameStage})
    else:
        return jsonify({'gameStage': "disconnected"})


@views.route("/deleteroom")
def deleteroom():
    global allRoomCodes
    args = request.args
    deleteCode = args.get('roomcode', 'nothing')
    room_to_delete = Room.query.filter_by(code=deleteCode).first()

    if room_to_delete:
        members_to_delete = Member.query.filter_by(room_id=room_to_delete.id).all()

        for member in members_to_delete:
            db.session.delete(member)

        if deleteCode in allRoomCodes:
            allRoomCodes.remove(deleteCode)
        db.session.delete(room_to_delete)
        db.session.commit()

        print(allRoomCodes)

        return jsonify({'status': 'Code Deleted and Room Removed'})
    else:
        return jsonify({'status': 'Code Not Present'})


@views.route("/newroom")
def newroom():
    global allRoomCodes
    args = request.args
    newroomcode = args.get('roomcode', 'nothing')

    questions = []
    with open('static/questions.txt', 'r') as file:
        for line in file:
            questions.append(line.strip())
    rand = random.randint(0, len(questions)-1)
    room_question = questions[rand]

    if newroomcode not in allRoomCodes and len(newroomcode) == 4:
        allRoomCodes.add(newroomcode)
        print(allRoomCodes)
        new_room = Room(code=newroomcode, gameStage="round0", question=room_question)
        db.session.add(new_room)
        db.session.commit()
        return jsonify({'access': 'granted'})
    else:
        return jsonify({'access': 'denied'})


@views.route("/play/<roomCodeEnter>", methods=['GET', 'POST'])
@login_required
def play(roomCodeEnter):
    global name
    global secret_key

    room = Room.query.filter_by(code=roomCodeEnter).first()

    numMembers = len(room.members)

    if(not room):
        return redirect(url_for('views.home'))

    if (current_user == room.members[0]):
        startingPlayer = True
    else:
        startingPlayer = False

    if(request.method=="POST"):
        startGame = request.form.get('startGame')
        enterTheoryButton = request.form.get('enterTheoryButton')
        if startGame == 'clicked':
            room.gameStage = "round1"
            db.session.commit()
            return render_template("play.html", roomCodeEnter=roomCodeEnter, playerName=current_user.name, startingPlayer=startingPlayer, numMembers=numMembers, gameStage=room.gameStage, room=room, member=current_user)
        if enterTheoryButton == 'clicked':
            theory = request.form.get('enterTheoryText')
            new_theory = Theory(content = theory, member_id=current_user.id)
            db.session.add(new_theory)
            db.session.commit()


    return render_template("play.html", roomCodeEnter=roomCodeEnter, playerName=current_user.name, startingPlayer=startingPlayer, numMembers=numMembers, gameStage=room.gameStage, room=room, member=current_user)

@views.route("<key>/play/members-info/<roomCodeEnter>")
def membersinfo(roomCodeEnter, key):
    args = request.args
    this_key = args.get('secret_key', 'locked')

    room = Room.query.filter_by(code=roomCodeEnter).first()

    if (this_key == secret_key) and (not roomCodeEnter.startswith("request failed")) and (room):
        # Converts members to a JSON-serializable format
        members_list = []
        for member in room.members:
            member_dict = {
                'id': member.id,
                'name': member.name,
                'points': member.points
            }
            members_list.append(member_dict)

        return jsonify({'members': members_list, 'roomCode': room.code, 'gameStage':room.gameStage})
    abort(404)

