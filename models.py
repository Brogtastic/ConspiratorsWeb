from flask_login import UserMixin
from __init__ import db

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Integer)
    gameStage = db.Column(db.String(20))
    members = db.relationship('Member')

class Member(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15))
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    points = db.Column(db.Integer)