from flask import Blueprint, render_template, request, jsonify
from models import Room
from __init__ import db

views = Blueprint(__name__, "views")

test = 'Nothing at all'
name = "Tim"
allRoomCodes = {"H469", "1234"}

@views.route("/", methods=['GET', 'POST'])
def home():
    print(allRoomCodes)
    global test
    global name
    if(request.method=='POST'):
        test = request.form.get('test')
    return render_template("index.html", name=name)

@views.route("/profile")
def profile():
    global name
    args = request.args
    name = args.get('name', name)  # If 'name' is not in the query parameters, keep the current name
    return jsonify({'name': name})

@views.route("/newroom")
def newroom():
    global allRoomCodes
    args = request.args
    roomcode = args.get('roomcode', 'nothing')

    if roomcode not in allRoomCodes and len(roomcode) == 4:
        allRoomCodes.add(roomcode)
        print(allRoomCodes)
        new_room = Room(code=roomcode, gameStage="round0")
        db.session.add(new_room)
        db.session.commit()
        return jsonify({'access': 'granted'})
    else:
        return jsonify({'access': 'denied'})


@views.route("/json")
def get_json():
    global test
    if(request.form.get('test')):
        test = request.form.get('test')
    return jsonify({'name': 'Brogdog', 'coolness': 10, 'test': test})