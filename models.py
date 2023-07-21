from __init__ import db
from flask_login import UserMixin

class Room(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    gameStage = db.Column(db.String(20))
    members = db.relationship('Member')

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15))
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    points = db.Column(db.Integer)