from flask_login import UserMixin
from sqlalchemy.sql import func
from . import db


class Aircraft(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # aircraft
    registration = db.Column(db.String(10))
    aircraft_type = db.Column(db.String(50))

    # weights
    empty_weight = db.Column(db.Float)
    mtow = db.Column(db.Float)
    mlw = db.Column(db.Float)

    # speeds
    true_airspeed = db.Column(db.Integer)

    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    aircrafts = db.relationship("Aircraft")
