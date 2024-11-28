from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Patient(db.Model):
    __tablename__ = 'patient'
    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String(100), unique=True, nullable=False)  # Unique patient identifier
    name = db.Column(db.String(200), nullable=False)  # Patient's full name
    birth_date = db.Column(db.Date, nullable=False)  # Birth date of the patient
    gender = db.Column(db.String(10), nullable=False)  # Gender of the patient ('male', 'female', 'other', 'unknown')
    address = db.Column(db.String(500))  # Address details
    contact = db.Column(db.String(200))  # Contact information (e.g., phone number)
    managing_organization = db.Column(db.String(200))  # Organization managing the patient's care

class HealthData(db.Model):
    __tablename__ = 'health_data'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    data_type = db.Column(db.String(50), nullable=False)  # Type of FHIR resource
    data = db.Column(db.Text, nullable=False)  # JSON data for FHIR resource

    patient = db.relationship('Patient', backref=db.backref('health_records', lazy=True))

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # 'patient' or 'staff'
