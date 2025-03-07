from . import db
# #a db model is a blueprint for a object that is stored in the database

from flask_login import UserMixin
from sqlalchemy.sql import func

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    frequency = db.Column(db.Integer)  # 1, 2, or 4 weeks
    start_date = db.Column(db.DateTime, nullable=False)
    notes = db.Column(db.Text)  # Optional notes field
    check_statuses = db.relationship('CheckStatus', backref='patient', cascade='all, delete-orphan')

class CheckStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    made = db.Column(db.Boolean, default=False)
    checked = db.Column(db.Boolean, default=False)
    filled = db.Column(db.Boolean, default=False)

class User(db.Model, UserMixin):
#inherit from db model
#need a primary key for every object in the database
#ie if everyone has the same name, how do we differentiate them?
#every user has a unique primary key
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))   
    notes = db.relationship('Note', backref='user', lazy=True)  # Added backref and lazy loading
    #relationship between user and note, need a capital for Note 