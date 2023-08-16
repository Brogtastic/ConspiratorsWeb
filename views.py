from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from models import Room, Member
from __init__ import db

views = Blueprint(__name__, "views")

roomCode = "0"
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
        elif (playerName.strip() in [name.strip() for name in names_list]):
            return render_template("index.html", number=number, roomCode=enteredRoomCode, error="Name already in use. Please enter a different name.")
        else:
            room = Room.query.filter_by(code=enteredRoomCode).first()
            new_member = Member(name=playerName, room_id=room.id, points=0)
            db.session.add(new_member)
            db.session.commit()
            return redirect(url_for('views.play', roomCodeEnter=enteredRoomCode))

    return render_template("index.html", number=number, error=" ", roomCode="")

@views.route("/profile")
def profile():
    global number
    args = request.args
    number = args.get('number', number)  # If 'number' is not in the query parameters, keep the current number
    return jsonify({'number': number})

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

        return jsonify({'status': 'Code Deleted and Room Removed'})
    else:
        return jsonify({'status': 'Code Not Present'})


@views.route("/newroom")
def newroom():
    global allRoomCodes
    args = request.args
    newroomcode = args.get('roomcode', 'nothing')

    if newroomcode not in allRoomCodes and len(newroomcode) == 4:
        allRoomCodes.add(newroomcode)
        print(allRoomCodes)
        new_room = Room(code=newroomcode, gameStage="round0")
        db.session.add(new_room)
        db.session.commit()
        return jsonify({'access': 'granted'})
    else:
        return jsonify({'access': 'denied'})


'''
@views.route("/json")
def get_json():
    global roomCode
    global name
    global secret_key

    args = request.args
    this_key = args.get('secret_key', 'locked')

    if(request.form.get('roomCode') and (this_key == secret_key)):
        roomCode = request.form.get('roomCode')
        name = request.form.get('name')
        print(name)
    return jsonify({'name': name, 'roomCode': roomCode})
'''

@views.route("/play/<roomCodeEnter>")
def play(roomCodeEnter):
    global name
    global secret_key
    global roomCode

    args = request.args
    this_key = args.get('secret_key', 'locked')

    if (this_key == secret_key) and not roomCodeEnter.startswith("request failed"):
        room = Room.query.filter_by(code=roomCodeEnter).first()

        # Convert members to a JSON-serializable format
        members_list = []
        for member in room.members:
            member_dict = {
                'id': member.id,
                'name': member.name,
                'points': member.points
            }
            members_list.append(member_dict)

        return jsonify({'members': members_list, 'roomCode': room.code})

    return render_template("play.html", roomCodeEnter=roomCodeEnter)


