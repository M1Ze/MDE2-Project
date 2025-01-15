from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    appointments = db.relationship('PractitionerAppointment', backref='user', lazy=True) #lazy = on-demand check, backref= relationship between models

class PatientInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  #link to User
    fhir_id = db.Column(db.String(255), nullable=False)  # FHIR Server ID

class Practitioner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)
    specialty = db.Column(db.String(150), nullable=False)
    appointments = db.relationship('PractitionerAppointment', backref='practitioner', lazy=True)

class PractitionerAppointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # 0 if available
    practitioner_id = db.Column(db.Integer, db.ForeignKey('practitioner.id'), nullable=False)

