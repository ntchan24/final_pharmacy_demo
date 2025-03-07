from . import db
from datetime import datetime

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