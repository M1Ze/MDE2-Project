#app.py
from flask import Flask, render_template, request, redirect, jsonify
import json
from werkzeug.security import generate_password_hash, check_password_hash

import requests
from db_models import db, Patient, HealthData, User
from fhir_data_processing.patient_data import PatientData
from fhir_data_processing.observation_data import ObservationData
from fhir_data_processing.medication_data import MedicationData
from fhir_data_processing.consent_data import ConsentData
from fhir_data_processing.care_plan_data import CarePlanData
from fhir_data_processing.allergy_intolerance_data import AllergyIntoleranceData
from datetime import datetime, timedelta
import generate_qr
import jwt

from generate_qr import generate_qr_code_binary

# Initialize the Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'my_secret_key'
FHIR_SERVER_URL = "http://localhost:8080/fhir"
db.init_app(app)

with app.app_context():
    #db.drop_all()
    db.create_all()

def check_token(token):
    try:
        decoded_token = jwt.decode(token, app.secret_key, algorithms=["HS256"])
        current_user = User.query.get(decoded_token['user_id'])
        if current_user is None:
            return {'error:' 'invalid'}
        return {'user_id': current_user.id, 'decoded_token' : decoded_token}
    except jwt.ExpiredSignatureError:
        return {'error': 'expired'}
    except jwt.InvalidTokenError:
        return {'error': 'invalid'}

def get_patient_data(fhir_id):
    try:
        response = requests.get(f"{FHIR_SERVER_URL}/Patient/{fhir_id}", headers={"Accept": "application/fhir+json"})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching patient: {e}")
        return None
@app.route('/')
def index():
   return render_template('index.html')

@app.route('/userPatientInfo')
def userPatientInfo():
    return render_template('user_patient_info.html')

@app.route('/savePatientData', methods=['POST'])
def save_patient_data():
    # Extract user ID from token
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({'status': 'error', 'message': 'No token provided'}), 401

    token = auth_header.split(" ")[1]
    token_check = check_token(token)  # Token validation logic
    if not token_check or 'user_id' not in token_check:
        return jsonify({'status': 'error', 'message': 'Invalid token'}), 401

    user_id = token_check['user_id']
    patient = Patient.query.filter_by(user_id=user_id).first()
    if not patient:
        return jsonify({'status': 'error', 'message': 'Patient not found'}), 404

    # Parse the incoming JSON data
    data = request.get_json()
    if not data or 'patient' not in data or 'observations' not in data:
        return jsonify({'status': 'error', 'message': 'Invalid data payload'}), 400

    patient_data_json = data['patient']
    observations_json = data['observations']

    # Update patient data
    try:
        patient_data = PatientData()
        patient_data.extract_data(filepath=None, json_string=patient_data_json)

        # Update fields in the Patient table
        patient.name = patient_data.name
        patient.identifier = patient_data.identifier
        patient.pat_data = patient_data_json  # Update the full FHIR resource
        db.session.add(patient)

        # Process observations and update HealthData table
        for obs in observations_json:
            obs_data = ObservationData()
            obs_data.extract_data(filepath=None, json_string=obs)

            # Check if observation already exists (e.g., by type and patient_id)
            existing_obs = HealthData.query.filter_by(
                patient_id=patient.id,
                data_type=obs_data.type
            ).first()

            if existing_obs:
                # Update existing observation
                existing_obs.h_data = obs
                existing_obs.data_aqu_datetime = obs_data.date
            else:
                # Add new observation
                new_obs = HealthData(
                    patient_id=patient.id,
                    data_type=obs_data.type,
                    data_aqu_datetime=obs_data.date,
                    h_data=obs
                )
                db.session.add(new_obs)

        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Patient data updated successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    if request.method == 'POST':
        data = request.get_json()
        patient_fhir_resource = data.get('user')  # Extract the FHIR Patient resource JSON
        password = data.get('password')

        if not patient_fhir_resource or not password:
            return jsonify({'status': 'error', 'message': 'Invalid request: missing patient data or password'}), 400

        # Use PatientData to parse and validate the FHIR Patient resource
        patient_data = PatientData()
        patient_data.extract_data(filepath=None, json_string=patient_fhir_resource)

        # Extract necessary fields
        email = patient_data.email
        given_name = patient_data.name.split(' ')[0] if patient_data.name else None
        last_name = patient_data.name.split(' ')[1] if patient_data.name and ' ' in patient_data.name else None
        social_security_number = patient_data.identifier

        # Validate required fields
        if not email or not given_name or not last_name or not social_security_number:
            return jsonify({'status': 'error', 'message': 'Incomplete patient data'}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({'status': 'error', 'message': 'Email already registered'}), 409

        # Create new user and patient records
        hashed_password = generate_password_hash(password)
        new_user = User(email=email, password=hashed_password, role='User')
        new_patient = Patient(
            name=f"{given_name} {last_name}",
            identifier=social_security_number,
            qr_code=generate_qr_code_binary(social_security_number),
            pat_data=patient_fhir_resource  # Save the entire FHIR Patient resource
        )

        try:
            db.session.add(new_user)
            db.session.flush()  # Ensures `new_user.id` is populated without committing yet

            new_patient.user_id = new_user.id
            db.session.add(new_patient)
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'User registered'}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('loginPage.html')
    if request.method == 'POST':
        data = request.json
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'status': 'error', 'message': 'Email and password are required'}), 400

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            return jsonify({'status': 'error', 'message': 'Invalid email or password'}), 401

        # create token
        token = jwt.encode(
            {'user_id': user.id, 'exp': datetime.utcnow() + timedelta(hours=1)},
            # Ablaufzeit 24 Stunden hours =24 oder seconds=10
            app.secret_key,
            algorithm='HS256'
        )
        return jsonify(
            {'status': 'success', 'message': 'Login successful', 'token': token})  # opt. add user_id': user.id ,

@app.route('/checklogin', methods=['GET', 'POST'])
def checklogin():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith("Bearer "):
        # Return error response for missing token
        return jsonify({'status': 'error', 'message': 'No token provided'}), 401

    token = auth_header.split(" ")[1]
    token_check = check_token(token)  # Use your token validation function

    if 'error' in token_check:
        # Return error response for invalid token
        return jsonify({'status': 'error', 'message': token_check['error']}), 401

    # Return success response for valid token
    return jsonify({'status': 'success', 'user_id': token_check['user_id']}), 200

@app.route('/getPatientInformation', methods=['GET'])
def get_patient_information():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({'status': 'error', 'message': 'No token provided'}), 401

    token = auth_header.split(" ")[1]
    token_check = check_token(token)  # Your token validation logic
    if not token_check or 'user_id' not in token_check:
        return jsonify({'status': 'error', 'message': 'Invalid token'}), 401

    user_id = token_check['user_id']
    patient = Patient.query.filter_by(user_id=user_id).first()
    if not patient:
        return jsonify({'status': 'error', 'message': 'Patient not found'}), 404

    # Use PatientData to process the patient resource
    patient_data = PatientData()
    patient_data.extract_data(filepath=None, json_string=json.dumps(patient.pat_data))

    # Serialize and return the entire PatientData object
    return jsonify({'status': 'success', 'patient': patient_data.__dict__})







if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)




# @app.route('/getPatientInformation2', methods=['GET'])
# def get_patient_information2():
#     auth_header = request.headers.get('Authorization')
#     if not auth_header or not auth_header.startswith("Bearer "):
#         return jsonify({'status': 'error', 'message': 'No token provided'}), 401
#
#     token = auth_header.split(" ")[1]
#     token_check = check_token(token)  # Your token validation logic
#     if not token_check or 'user_id' not in token_check:
#         return jsonify({'status': 'error', 'message': 'Invalid token'}), 401
#
#     user_id = token_check['user_id']
#     patient = Patient.query.filter_by(user_id=user_id).first()
#     if not patient:
#         return jsonify({'status': 'error', 'message': 'Patient not found'}), 404
#
#     # Return the full FHIR Patient resource stored in the database
#     return jsonify({'status': 'success', 'patient': patient.pat_data})

# @app.route('/register2', methods=['GET', 'POST'])
# def register2():
#     if request.method == 'GET':
#         return render_template('register.html')
#
#     if request.method == 'POST':
#         data = request.get_json()
#         patient_fhire_resource = data.get('user')  # Extract the FHIR Patient resource
#         password = data.get('password')
#
#         # Extract fields from the FHIR resource
#         if patient_fhire_resource:
#             email = next(
#                 (telecom.get('value') for telecom in patient_fhire_resource.get('telecom', [])
#                  if telecom.get('system') == 'email'),
#                 None
#             )
#             name = patient_fhire_resource.get('name', [{}])[0]
#             given_name = name.get('given', [''])[0]
#             last_name = name.get('family', '')
#             identifier = patient_fhire_resource.get('identifier', [{}])[0]
#             social_security_number = identifier.get('value')
#
#             # Check for required fields
#             if not email or not password:
#                 return jsonify({'status': 'error', 'message': 'Email or password is missing'}), 500
#
#             if User.query.filter_by(email=email).first():
#                 return jsonify({'status': 'error', 'message': 'Email already registered'}), 501
#
#             hashed_password = generate_password_hash(password)
#             new_user = User(email=email, password=hashed_password, role='User')
#             new_patient = Patient(
#                 name=f"{given_name} {last_name}",
#                 identifier=social_security_number,
#                 qr_code=generate_qr_code_binary(social_security_number),
#                 pat_data=patient_fhire_resource  # Save the entire FHIR Patient resource
#             )
#             try:
#                 db.session.add(new_user)
#                 db.session.flush()  # Ensures `new_user.id` is populated without committing yet
#
#                 new_patient.user_id = new_user.id
#                 db.session.add(new_patient)
#                 db.session.commit()
#                 return jsonify({'status': 'success', 'message': 'User registered'}), 200
#             except Exception as e:
#                 db.session.rollback()
#                 return jsonify({'status': 'error', 'message': str(e)}), 500
#         else:
#             return jsonify({'status': 'error', 'message': 'Invalid request'}), 400



