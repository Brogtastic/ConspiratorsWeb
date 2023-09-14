from flask_login import UserMixin
from __init__ import db

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Integer)
    gameStage = db.Column(db.String(20))
    question = db.Column(db.String(150))
    members = db.relationship('Member', backref='room')
    thread = db.Column(db.Boolean)
    data_to_send = db.Column(db.Boolean)

class Member(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15))
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    points = db.Column(db.Integer)
    theory = db.Column(db.String(150))
    received_theory = db.Column(db.String(150))
    waiting = db.Column(db.Boolean)
    presenting = db.Column(db.Boolean)
    words_presenting = db.Column(db.Boolean)
    words = db.relationship('Words')
    words_num = db.Column(db.Integer)
    writing_to = db.Column(db.String(15))

class Words(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(15))
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))

class AvailableRoom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(4))
    in_use = db.Column(db.Boolean)