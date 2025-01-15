from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    appointments = db.relationship('UserAppointment', backref='user', lazy=True)

class PatientResource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Verknüpfung zum Benutzer
    resource = db.Column(db.Text, nullable=False)  # JSON der FHIR-Ressource
    created_at = db.Column(db.DateTime, default=db.func.now())

class UserAppointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    practitioner_id = db.Column(db.Integer, db.ForeignKey('practitioner.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('practitioner_appointment.id'), nullable=False)

class Practitioner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)  # z. B. "Dr. Cardiologist"
    specialty = db.Column(db.String(150), nullable=False)  # z. B. "Heart Specialist"
    appointments = db.relationship('PractitionerAppointment', backref='practitioner', lazy=True)

class PractitionerAppointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Null, wenn der Termin verfügbar ist
    practitioner_id = db.Column(db.Integer, db.ForeignKey('practitioner.id'), nullable=False)

