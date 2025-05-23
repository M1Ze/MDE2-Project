#db_models.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import BLOB, JSON

db = SQLAlchemy()

class Patient(db.Model):
    __tablename__ = 'patient'
    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String(100), unique=True, nullable=True)  # Unique patient identifier (SVN)
    fhir_id = db.Column(db.Integer, nullable=True)  # fhir_id received from the fhire server for the patient resource
    name = db.Column(db.String(200), nullable=False)  # Patient's full name
    pat_data = db.Column(JSON, nullable=True)  # JSON data for FHIR resource
    qr_code = db.Column(BLOB, nullable=False)  # Path to the QR code image
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key to User

    user = db.relationship('User', backref=db.backref('patients', lazy=True))


class HealthData(db.Model):
    __tablename__ = 'health_data'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    fhir_id = db.Column(db.Integer, nullable=True)  # fhir_id received from the fhire server for the resource
    data_type = db.Column(db.String(50), nullable=False)  # Type of Oberservation
    data_aqu_datetime = db.Column(db.DateTime, nullable=False) # aquistiton date and Time
    h_data = db.Column(db.Text, nullable=False)  # JSON data for FHIR resource

    patient = db.relationship('Patient', backref=db.backref('health_records', lazy=True))


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # 'patient' or 'staff'




    # birth_date = db.Column(db.Date, nullable=False)  # Birthdate of the patient
    # gender = db.Column(db.String(10), nullable=False)  # Gender of the patient ('male', 'female', 'other', 'unknown')
    # address = db.Column(db.String(500))  # Address details
    # contact_phone = db.Column(db.String(200)) # phone information
    # contact_email = db.Column(db.String(200)) # mail information
    # contact_person_name = db.Column(db.String(200)) # Contact Person name
    # contact_person_phone = db.Column(db.String(200)) # Contact Person phone