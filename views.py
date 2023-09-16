from flask import Blueprint, render_template, request, jsonify, redirect, url_for, abort, Response, current_app
from flask_login import LoginManager, login_user, current_user, login_required
from models import Room, Member, Words, AvailableRoom
from __init__ import db
import random
import json
import threading
import asyncio
import time

sse_thread_flag = threading.Event()

views = Blueprint(__name__, "views")

name = "no name"
allRoomCodes = {"1234567"}
secret_key = "agekvoslfhfgaye6382m4i201nui32h078hrauipbvluag78e4tg4w3liutbh2q89897wrgh4ui3gh2780gbrwauy"
openThreads = []
data_to_send = []
data_to_send_js = []
endMyLife = False

def NoRepeatTheories(theory, room):
    for member in room.members:
        if member.theory and (member != current_user):
            if ((theory + " (" + member.name + ")") == (member.theory)):
                theory = theory + " (" + current_user.name + ")"
            elif theory == member.theory:
                member.theory = theory + " (" + member.name + ")"
                theory = theory + " (" + current_user.name + ")"
    db.session.commit()
    return theory

def ShuffleTheories(roomCode):
    room = Room.query.filter_by(code=roomCode).first()
    null_test_member = Member.query.filter_by(room_id=room.id).first()

    # If a member in the room has a received theory then we have
    # already shuffled, and we don't want to do it again.
    if (null_test_member.received_theory is not None):
        return

    # Shuffle makes it so nobody gets their own theory
    def perfect_shuffle(lst):
        while True:
            shuffled_lst = lst.copy()
            random.shuffle(shuffled_lst)
            if not any(a == b for a, b in zip(lst, shuffled_lst)):
                return shuffled_lst

    # Create list of theories
    theoryList = []
    for member in room.members:
        theoryList.append(member.theory)
    # Shuffle theories so everyone gets assigned a new one
    shuffledTheoryList = perfect_shuffle(theoryList)
    # Assign the shuffled theories
    i = 0
    for member in room.members:
        # Assign the theory that the player will write words to
        member.received_theory = shuffledTheoryList[i]

        # Find the name of the player to display their name and for assigning points later
        written_member = Member.query.filter_by(theory=shuffledTheoryList[i]).first()
        member.writing_to = written_member.name
        db.session.commit()
        print(member.name + " is writing to " + member.writing_to)
        i += 1

    print("Shuffled Theory List:")
    print(shuffledTheoryList)

    return


@views.route('/sse/<enteredRoomCode>')
def sse(enteredRoomCode):
    room = Room.query.filter_by(code=enteredRoomCode).first()
    if (not room) or (enteredRoomCode not in openThreads):
        print("data withold")
        return Response(json.dumps({'data': "withold"}) + "\n\n", content_type='text/event-stream')

    return Response(event_stream(enteredRoomCode), content_type='text/event-stream')

def event_stream(enteredRoomCode):
    global openThreads
    global data_to_send
    while enteredRoomCode in openThreads:
        if len(data_to_send) > 0 and data_to_send[0][0] == enteredRoomCode:
            print("data send")
            data = {'data': data_to_send[0][1]}
            data_to_send.pop(0)
            yield json.dumps(data) + "\n\n"
        time.sleep(1)


@views.route('/ssejavascript/<enteredRoomCode>')
def ssejavascript(enteredRoomCode):
    print("JavaScript Connected!")
    room = Room.query.filter_by(code=enteredRoomCode).first()
    if (not room) or (enteredRoomCode not in openThreads):
        print("data withold")
        return Response(json.dumps({'data': "withold"}) + "\n\n", content_type='text/event-stream')

    return Response(event_stream_javascript(enteredRoomCode), content_type='text/event-stream')

def event_stream_javascript(enteredRoomCode):
    global data_to_send_js
    global openThreads
    while enteredRoomCode in openThreads:
        if len(data_to_send_js) > 0 and data_to_send_js[0][0] == enteredRoomCode:
            print("data send js")
            print("Data JS SSE: " + data_to_send_js[0][1])
            data = {'data': data_to_send_js[0][1]}
            data_to_send_js.pop(0)
            yield json.dumps(data) + "\n\n"
        time.sleep(1)
        data_to_send_js.append([enteredRoomCode, "Data Send JS"])


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
            data_to_send.append([room.code, "ValidRoom"])
            print("data_to_send: " + str(data_to_send))


        if (len(enteredRoomCode) != 4):
            return render_template("index.html", roomCode="",error="Room Code should be 4 digits long. Please try again")
        elif(enteredRoomCode not in allRoomCodes):
            return render_template("index.html", roomCode="", error="Room Code does not exist. Please try again")
        elif (number_of_members >= 8):
            return render_template("index.html", roomCode="", error="Room is full!")
        elif ((str.lower(playerName.strip()) in [str.lower(name.strip()) for name in names_list]) and (not current_user.is_authenticated)) or (current_user.is_authenticated and current_user.name != playerName and (str.lower(playerName.strip()) in [str.lower(name.strip()) for name in names_list])):
            return render_template("index.html", roomCode=enteredRoomCode, error="Name already in use. Please enter a different name.")
        elif (len(playerName) == 0):
            return render_template("index.html", roomCode=enteredRoomCode, error="Please enter a name.")
        elif not current_user.is_authenticated:
            #TYPICAL MEMBER CREATION
            room = Room.query.filter_by(code=enteredRoomCode).first()
            new_member = Member(name=playerName, room_id=room.id, points=0, waiting=False, words_num = 0)
            db.session.add(new_member)

            #TEST_CODE_START This is to fill the room for test without having to log in 3 separate times
            possible_test = str.lower(new_member.name[:-1])
            if(possible_test == 'test') and (len(new_member.name) == 5):
                memsToCreate = int(new_member.name[4])
                for i in range(memsToCreate-1):
                    fake_member = Member(name='player' + str(i+2), room_id=room.id, points=0, waiting=False, theory='player' + str(i+2) + ' theory', words_num = 0)
                    db.session.add(fake_member)
                new_member.name = 'player1'
            #TEST_CODE_END

            db.session.commit()
            login_user(new_member, remember=True)

            data_to_send.append([room.code, "UpdateMembers"])
            data_to_send_js.append([room.code, "checkNumMemberChange"])
            print("data_to_send: " + str(data_to_send))

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
                data_to_send_js.append([room.code, "checkNumMemberChange"])
                data_to_send.append([room.code, "UpdateMembers"])
                return redirect(url_for('views.play', roomCodeEnter=enteredRoomCode))
            else:
                #Keep old inactive member in previous room, create a new member for new room
                new_member = Member(name=playerName, room_id=room.id, points=0, waiting=False, words_num = 0)
                db.session.add(new_member)
                db.session.commit()
                login_user(new_member, remember=False)
                return redirect(url_for('views.play', roomCodeEnter=enteredRoomCode))
        else:
            # Allow name changes if still in starting room
            room = Room.query.filter_by(code=enteredRoomCode).first()
            if(current_user.name != playerName) and (room.gameStage == "round0"):
                member_to_update = Member.query.get(current_user.id)
                if member_to_update:
                    member_to_update.name = playerName
                    db.session.commit()
            data_to_send.append([room.code, "UpdateMembers"])
            return redirect(url_for('views.play', roomCodeEnter=enteredRoomCode))

    return render_template("index.html", error=" ", roomCode="")

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


@views.route("/game-stage-return/<roomCode>")
def getGameStage(roomCode):
    room = Room.query.filter_by(code=roomCode).first()
    args = request.args
    key = args.get('secret_key', 'nothing')

    if (not room) or (key != secret_key):
        return jsonify({'access': 'denied', 'gameStage': 'none'})

    return jsonify({'access': 'granted', 'gameStage': room.gameStage})

@views.route("/member-theory-return/<roomCode>/<memberName>")
def memberTheoryReturn(roomCode, memberName):
    room = Room.query.filter_by(code=roomCode).first()

    if not room:
        return jsonify({'receivedName': 'no room exists', 'receivedTheory': 'no room exists'})

    commenceShuffle = True
    for this_member in room.members:
        if (not this_member.theory) or (this_member.received_theory):
            commenceShuffle = False
            break

    if commenceShuffle:
        ShuffleTheories(roomCode)
        db.session.commit()

    member = next((m for m in room.members if m.name == memberName), None)

    if (member) and (member.name) and (member.theory):
        print("Member " + member.name + "'s theory: " + member.theory)
        return jsonify({'receivedName': member.writing_to, 'receivedTheory': member.received_theory})
    else:
        return jsonify({'receivedName': 'no member exists', 'receivedTheory': 'no member exists'})

@views.route("/members-names-return/<roomCode>")
def membersNamesReturn(roomCode):
    room = Room.query.filter_by(code=roomCode).first()
    args = request.args
    key = args.get('secret_key', 'nothing')

    if (not room) or (key != secret_key):
        return jsonify({'access': 'denied', 'allNames':'none'})

    allNames = []
    for member in room.members:
        allNames.append(member.name)

    return jsonify({'access': 'granted', 'allNames': allNames})

@views.route("/set-user-theory", methods=['GET', 'POST'])
def setUserTheory():
    args = request.args
    firstName = args.get('firstName', 'nothing')
    theory = args.get('theory', 'nothing')
    roomCode = args.get('roomCode', 'nothing')

    room = Room.query.filter_by(code=roomCode).first()

    #TO-DO: If a user's theory is blank, provide them a 'safety quip' one.

    if room:
        # Auto-submits whatever unfinished theory a user has.
        member = next((m for m in room.members if m.name == firstName), None)
        if (member) and (member.waiting == False):
            theory = NoRepeatTheories(theory, room)
            if theory:
                member.theory = theory
            db.session.commit()
            data_to_send_js.append([room.code, "getUserTheory"])
            print("Autocomplete theory")
        return jsonify({'status': "success"})

    return jsonify({'status': "failed"})

@views.route("/set-user-word", methods=['GET', 'POST'])
def setUserWord():
    print("Set User Word called")
    args = request.args
    firstName = args.get('firstName', 'nothing')
    word = args.get('word', 'nothing')
    print("Unfinished word is: " + word)
    roomCode = args.get('roomCode', 'nothing')

    room = Room.query.filter_by(code=roomCode).first()

    if len(word) < 1:
        return jsonify({'status': "failed"})

    #TO-DO: If a user's theory is blank, provide them a 'safety quip' one.

    if room:
        # Auto-submits whatever unfinished theory a user has.
        member = next((m for m in room.members if m.name == firstName), None)
        if (member) and (member.waiting == False):
            if (word) and (member.words_num < 3):
                new_word = Words(content=word, member_id=member.id)
                db.session.add(new_word)
                member.words_num += 1
                db.session.commit()
                print("unfinished word added")
            print("Autocomplete word")
        return jsonify({'status': "success"})

    return jsonify({'status': "failed"})


@views.route("/set-round")
def setRound():
    args = request.args
    roundSet = args.get('roundSet', 'nothing')
    roomCode = args.get('roomCode', 'nothing')
    key = args.get('key', 'nothing')

    print("roundSet = " + roundSet)
    print("roomCode = " + roomCode)
    print("key = " + key)

    room = Room.query.filter_by(code=roomCode).first()

    if (room) and (key == secret_key):
        room.gameStage = roundSet
        #All members waiting equals false
        for member in room.members:
            member.waiting = False
        db.session.commit()
        print("New round status: " + room.gameStage)
        data_to_send_js.append([room.code, "checkRound"])
        return jsonify({'status': "success"})

    return jsonify({'status': "failed"})


@views.route("/deleteroom")
def deleteroom():
    global allRoomCodes
    global openThreads
    args = request.args
    deleteCode = args.get('roomcode', 'nothing')
    room_to_delete = Room.query.filter_by(code=deleteCode).first()
    room_code_to_free = AvailableRoom.query.filter_by(code=deleteCode).first()

    if room_to_delete:
        members_to_delete = Member.query.filter_by(room_id=room_to_delete.id).all()

        for member in members_to_delete:
            db.session.delete(member)

        if deleteCode in allRoomCodes:
            allRoomCodes.remove(deleteCode)
        db.session.delete(room_to_delete)
        room_code_to_free.in_use = True
        db.session.commit()

        print(allRoomCodes)

        for i in range(len(openThreads)):
            if openThreads[i] == deleteCode:
                openThreads.pop(i)
                break

        print("Open threads after deletion: " + str(openThreads))

        return jsonify({'status': 'Code Deleted and Room Removed'})
    else:
        return jsonify({'status': 'Code Not Present'})


@views.route("/createroom")
def newroom():
    global allRoomCodes
    global data_to_send
    global openThreads
    args = request.args
    key = args.get('secret_key', 'nothing')
    if (key != secret_key): return jsonify({'access': 'denied'})

    total_rooms = AvailableRoom.query.filter_by(in_use=False).count()
    if(total_rooms > 0):
        random_index = random.randint(0, total_rooms - 1)
        random_room = AvailableRoom.query.offset(random_index).first()
        newroomcode = random_room.code

        random_room.in_use = True
        db.session.commit()

        questions = []
        with open('static/questions.txt', 'r', encoding='utf-8') as file:
            for line in file:
                questions.append(line.strip())
        rand = random.randint(0, len(questions) - 1)
        room_question = questions[rand]

        allRoomCodes.add(newroomcode)
        print(allRoomCodes)
        new_room = Room(code=newroomcode, gameStage="round0", question=room_question, thread=True, data_to_send=True)
        db.session.add(new_room)
        db.session.commit()
        openThreads.append(newroomcode)
        data_to_send.append([newroomcode, "New Room"])
        print("Open threads: " + str(openThreads))
        return jsonify({'access': 'granted', 'newRoomCode': newroomcode, 'roomQuestion': room_question})
    else:
        return jsonify({'access': 'denied'})


@views.route("/play/<roomCodeEnter>", methods=['GET', 'POST'])
@login_required
def play(roomCodeEnter):
    global name
    global secret_key

    room = Room.query.filter_by(code=roomCodeEnter).first()

    numMembers = len(room.members)
    words_list = []

    if(not room):
        return redirect(url_for('views.home'))

    if (current_user == room.members[0]):
        startingPlayer = True
    else:
        startingPlayer = False

    if(request.method=="POST"):
        startGame = request.form.get('startGame')
        enterTheoryButton = request.form.get('enterTheoryButton')
        enterWordButton = request.form.get('enterWordButton')
        if startGame == 'clicked':
            room.gameStage = "round1"
            current_user.waiting = False
            db.session.commit()
            data_to_send.append([room.code, "UpdateGameStage"])
            data_to_send_js.append([room.code, "checkRound"])
            return render_template("play.html", roomCodeEnter=roomCodeEnter, playerName=current_user.name, startingPlayer=startingPlayer, numMembers=numMembers, gameStage=room.gameStage, room=room, member=current_user)
        elif enterTheoryButton == 'clicked':
            theory = request.form.get('enterTheoryText')
            theory = NoRepeatTheories(theory, room)
            if theory:
                current_user.theory = theory
            db.session.commit()
            current_user.waiting = True
            db.session.commit()

            #TEST_CODE_START if it's a test just mark all members as done
            if current_user.name == "player1":
                for member in room.members:
                    member.waiting = True
            #TEST_CODE_END

            #Check to see if everyone is waiting
            allwaiting = True
            for member in room.members:
                if not member.waiting:
                    allwaiting = False
            #Start a new round if everyone is waiting (a.k.a. they've answered)
            if allwaiting:
                for member in room.members:
                    member.waiting = False
                room.gameStage = "round2"
                db.session.commit()
                data_to_send.append([room.code, "UpdateGameStage"])
                data_to_send_js.append([room.code, "checkRound"])
            data_to_send_js.append([room.code, "getUserTheory"])
        elif (enterWordButton == 'clicked') and (current_user.words_num < 3):
            word = request.form.get('enterWordText')
            new_word = Words(content=word, member_id=current_user.id)
            db.session.add(new_word)
            current_user.words_num += 1
            db.session.commit()

            # TEST_CODE_START if it's a test just mark all members as done
            if (current_user.name == "player1") and (current_user.words_num == 3):
                for member in room.members:
                    member.waiting = True
                db.session.commit()
            # TEST_CODE_END

            if(current_user.words_num == 3):
                current_user.waiting = True
            db.session.commit()

            # Check to see if everyone is waiting
            allwaiting = True
            for member in room.members:
                if not member.waiting:
                    allwaiting = False
            # Start a new round if everyone is waiting (a.k.a. they've answered)
            if allwaiting:
                for member in room.members:
                    member.waiting = False
                room.gameStage = "round3"
                db.session.commit()
                data_to_send.append([room.code, "UpdateGameStage"])
                data_to_send_js.append([room.code, "checkRound"])
            words_list = list(current_user.words)

    return render_template("play.html", roomCodeEnter=roomCodeEnter, playerName=current_user.name, startingPlayer=startingPlayer, numMembers=numMembers, gameStage=room.gameStage, room=room, member=current_user, words_list=words_list)

