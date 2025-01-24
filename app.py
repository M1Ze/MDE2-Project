# app.py
import csv
from traceback import print_tb

from flask import Flask, render_template, request, redirect, jsonify
import json
from werkzeug.security import generate_password_hash, check_password_hash

import requests

from csv_handler import csv_to_dict, get_medication_dict
from db_models import db, Patient, HealthData, User
from fhir_data_processing.condition_data import ConditionData
from fhir_data_processing.patient_data import PatientData
from fhir_data_processing.observation_data import ObservationData
from fhir_data_processing.medication_data import MedicationData
from fhir_data_processing.consent_data import ConsentData
from fhir_data_processing.care_plan_data import CarePlanData
from fhir_data_processing.allergy_intolerance_data import AllergyIntoleranceData
from datetime import datetime, timedelta, timezone
import generate_qr
import jwt
import json
from datetime import datetime
import fhir_server_interface
from fhir_server_interface import save_resource

from generate_qr import generate_qr_code_binary

# Initialize the Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'my_secret_key'
FHIR_SERVER_URL = "http://localhost:8080/fhir"
db.init_app(app)

with app.app_context():
    # db.drop_all()
    db.create_all()


def check_token(token):
    try:
        decoded_token = jwt.decode(token, app.secret_key, algorithms=["HS256"])
        current_user = User.query.get(decoded_token['user_id'])
        if current_user is None:
            return {'error:' 'invalid'}
        return {'user_id': current_user.id, 'decoded_token': decoded_token}
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
    medications = []
    manufacturers = []

    # Read the CSV file
    with open('Allgemein/snomed_ct_codes_medication.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')  # Specify the correct delimiter
        next(reader)  # Skip the header row
        for row in reader:
            medication_name = row[0]
            manufacturer = row[2]
            medications.append(medication_name)
            manufacturers.append(manufacturer)

    # Remove duplicates
    medications = list(set(medications))
    manufacturers = list(set(manufacturers))


    conditions = []
    condition_codes = []
    condition_ids = []
    # Read the CSV file
    with open('Allgemein/snomed_ct_codes_condition.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')  # Specify the correct delimiter
        next(reader)  # Skip the header row
        for row in reader:
            conditionCode = row[0]
            condition = row[1]
            condition_codes.append(conditionCode)
            conditions.append(condition)

            # Create an ID-friendly version of the condition
            processed_condition = condition.replace(' ', '-').replace('(', '').replace(')', '').lower()

            condition_ids.append(processed_condition)

    # Remove duplicates
    #conditions = list(set(conditions))
    #condition_codes = list(set(condition_codes))
    #condition_ids = list(set(condition_ids))

    return render_template('user_patient_info.html', medications=medications, manufacturers=manufacturers, conditions=conditions, condition_codes=condition_codes, condition_ids=condition_ids, zip=zip)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    if request.method == 'POST':
        data = request.get_json()
        patient_register_data = data.get('user')  # Extract the FHIR Patient resource JSON
        password = data.get('password')

        if not patient_register_data or not password:
            return jsonify({'status': 'error', 'message': 'Invalid request: missing patient data or password'}), 400

        patient_register_data_json = (
            json.dumps(patient_register_data) if isinstance(patient_register_data, dict) else patient_register_data
        )
        # Use PatientData to parse and validate the FHIR Patient resource
        # muss nochmal überarbeiten
        patient_data = PatientData()
        patient_data.populate_from_dict(patient_register_data)


        patient_fhir_resource = json.loads(patient_data.create_fhir())
        resource_type = patient_fhir_resource.get("resourceType"),

        fhir_id = save_resource("Patient",patient_fhir_resource)

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
            pat_data=patient_fhir_resource ,# Save the entire Patient
            fhir_id = fhir_id
        )

        try:
            db.session.add(new_user)
            db.session.flush()  # Ensures `new_user.id` is populated without committing yet

            new_patient.user_id = new_user.id
            db.session.add(new_patient)
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'User registered'}), 201
        except Exception as e:
            app.logger.error(f"Error registering user: {str(e)}")
            db.session.rollback()
            return jsonify({'status': 'error', 'message': 'An error occurred while registering the user.'}), 500


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

    # Fetch patient data
    patient = Patient.query.filter_by(user_id=user_id).first()
    if not patient:
        return jsonify({'status': 'error', 'message': 'Patient not found'}), 404

    # Extract and process patient data
    patient_data = PatientData()
    patient_data.extract_data(filepath=None, json_string=json.dumps(patient.pat_data))

    # Fetch all health data linked to the patient
    health_records = HealthData.query.filter_by(patient_id=patient.id).all()
    serialized_health_data = [
        {
            "type": record.data_type,
            "timestamp": record.data_aqu_datetime.isoformat() if record.data_aqu_datetime else None,
            "data": json.loads(record.h_data)  # Deserialize JSON field
        }
        for record in health_records
    ]

    # Include both patient data and health data in the response
    return jsonify({
        'status': 'success',
        'patient': patient_data.__dict__,
        'health_data': serialized_health_data
    })



@app.route('/savePatientData', methods=['POST'])
def save_patient_data():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({'status': 'error', 'message': 'No token provided'}), 401

    token = auth_header.split(" ")[1]
    token_check = check_token(token)
    if not token_check or 'user_id' not in token_check:
        return jsonify({'status': 'error', 'message': 'Invalid token'}), 401

    user_id = token_check['user_id']

    # Clear the health_data table
    db.session.query(HealthData).delete()
    db.session.commit()

    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data received'}), 400

        patient = save_patient(data.get('patient'), user_id)
        if isinstance(patient, tuple):  # Check if an error response is returned
            return patient

        save_observations(data.get('observations', []), patient)
        save_consent(data.get('consent', {}), patient)
        save_medications(data.get('medications', []), patient)
        save_conditions(data.get('conditions', []), patient)
        save_allergies(data.get('allergies', []), patient)

        db.session.commit()  # Commit all changes at once
        return jsonify({'status': 'success', 'message': 'Patient data and related records saved successfully'}), 200

    except Exception as e:
        app.logger.error(f"Error saving patient data: {str(e)}")
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'An error occurred while saving patient data.'}), 500


def save_patient(patient_data_json, user_id):
    if not isinstance(patient_data_json, dict):
        return jsonify({'status': 'error', 'message': 'Invalid or missing patient data'}), 400

    patient_data = PatientData()
    patient_data.populate_from_dict(patient_data_json)

    identifier_value = patient_data.identifier
    if not identifier_value:
        return jsonify({'status': 'error', 'message': 'Missing identifier value'}), 400

    patient = Patient.query.filter_by(identifier=identifier_value).first()
    if not patient:
        return jsonify({'status': 'error', 'message': 'Patient not found'}), 404

    if patient.user_id != user_id:
        return jsonify({'status': 'error', 'message': 'Unauthorized access to patient data'}), 403

    patient.name = patient_data.name or patient.name
    patient.pat_data = json.loads(patient_data.create_fhir())
    return patient

def save_observations(observations, patient):
    if not isinstance(observations, list):
        raise ValueError("Invalid observations format, expected a list")

    for obs_wrapper in observations:
        obs_data = obs_wrapper.get('observation')
        if not isinstance(obs_data, dict):
            app.logger.warning(f"Skipping invalid observation format: {obs_wrapper}")
            continue

        try:
            observation = ObservationData()
            observation.populate_from_dict(obs_data)

            data_aqu_datetime = datetime.now(timezone.utc).replace(microsecond=0)  # Remove microseconds
            # Convert to ISO 8601 format for FHIR
            data_aqu_datetime_iso = data_aqu_datetime.isoformat()

            observation_fhire_resource = json.loads(json.dumps(observation.create_fhir(), separators=(',', ':')))

            fhir_id=save_resource("Observation",json.loads(observation_fhire_resource))

            existing_obs = HealthData.query.filter_by(
                patient_id=patient.id,
                data_type=observation.type
            ).first()

            if existing_obs:
                existing_obs.h_data = observation_fhire_resource
                existing_obs.data_aqu_datetime = data_aqu_datetime
            else:
                new_obs = HealthData(
                    patient_id=patient.id,
                    data_type=observation.type,
                    data_aqu_datetime=data_aqu_datetime,
                    h_data=observation_fhire_resource,
                    fhir_id=fhir_id,
                )
                db.session.add(new_obs)

        except Exception as e:
            app.logger.error(f"Error processing observation: {obs_data}, Error: {str(e)}")

def save_consent(consent_data, patient):
    if not isinstance(consent_data, dict) or not consent_data:
        return  # No consent data to process (either not a dict or it's empty)

    try:
        consent = ConsentData()
        consent.populate_from_dict(consent_data,patient)
        consent_fhire_json = json.loads(json.dumps(consent.create_fhir()))

        fhir_id=save_resource("Consent",json.loads(consent_fhire_json))

        data_aqu_datetime = datetime.now(timezone.utc).replace(microsecond=0)  # Remove microseconds
        # Convert to ISO 8601 format for FHIR
        data_aqu_datetime_iso = data_aqu_datetime.isoformat()

        existing_consent = HealthData.query.filter_by(
            patient_id=patient.id,
            data_type="DNR",
        ).first()

        if existing_consent:
            existing_consent.h_data = consent_fhire_json
            existing_consent.data_aqu_datetime = data_aqu_datetime
        else:
            new_consent = HealthData(
                patient_id=patient.id,
                data_type="DNR",
                data_aqu_datetime=data_aqu_datetime,
                h_data=consent_fhire_json,
                fhir_id=fhir_id,
            )
            db.session.add(new_consent)

    except Exception as e:
        app.logger.error(f"Error processing consent data: {str(e)}")

def save_medications(medications, patient):
    if not isinstance(medications, list):
        return  # No medications to process

    try:
        for med in medications:
            medication = MedicationData()

            file_path = 'Allgemein/snomed_ct_codes_medication.csv'
            medication_dict = get_medication_dict(file_path)

            key_to_find = med.get('medication')
            if key_to_find in medication_dict:
                medication.code = medication_dict[key_to_find]


            medication.manufacturer = med.get('manufacturer')

            existing_med = HealthData.query.filter_by(
                patient_id=patient.id,
                data_type = med.get('medication')
            ).first()

            data_aqu_datetime = datetime.now(timezone.utc).replace(microsecond=0)  # Remove microseconds
            # Convert to ISO 8601 format for FHIR
            data_aqu_datetime_iso = data_aqu_datetime.isoformat()

            medication_fhir_resource = json.loads(json.dumps(medication.create_fhir()))

            fhir_id=save_resource("Medication",json.loads(medication_fhir_resource))


            if existing_med:
                existing_med.data = medication_fhir_resource
                existing_med.data_aqu_datetime = data_aqu_datetime

            else:
                new_med = HealthData(
                    patient_id=patient.id,
                    data_type=med.get('medication'),
                    data_aqu_datetime = data_aqu_datetime,
                    h_data=medication_fhir_resource,
                    fhir_id=fhir_id,
                )
                db.session.add(new_med)

    except Exception as e:
        app.logger.error(f"Error processing medications: {str(e)}")

def save_conditions(conditions, patient):
    if not isinstance(conditions, list):
        return  # No conditions to process

    try:
        for cond in conditions:
            condition = ConditionData()

            file_path = 'Allgemein/snomed_ct_codes_condition.csv'
            conditions_dict = csv_to_dict(file_path)

            key_to_find = cond.get('condition')
            if key_to_find in conditions_dict:
                condition.condition_code = conditions_dict[key_to_find]

            data_aqu_datetime = datetime.now(timezone.utc).replace(microsecond=0)  # Remove microseconds
            # Convert to ISO 8601 format for FHIR
            data_aqu_datetime_iso = data_aqu_datetime.isoformat()

            condition.recorded_date = data_aqu_datetime
            condition.patient_identifier = patient.fhir_id

            condition_fhire_json = json.loads(json.dumps(condition.create_fhir()))

            fhir_id=save_resource("Condition",json.loads(condition_fhire_json))

            existing_condition = HealthData.query.filter_by(
                patient_id=patient.id,
                data_type=cond.get('condition')
            ).first()

            if existing_condition:
                existing_condition.h_data = condition_fhire_json
                existing_condition.data_aqu_datetime = data_aqu_datetime
            else:
                new_condition = HealthData(
                    patient_id=patient.id,
                    data_type=cond.get('condition'),
                    data_aqu_datetime=data_aqu_datetime,
                    h_data=condition_fhire_json,
                    fhir_id=fhir_id,
                )
                db.session.add(new_condition)

    except Exception as e:
        app.logger.error(f"Error processing conditions: {str(e)}")

def save_allergies(allergies, patient):
    if not isinstance(allergies, list):
        return  # No allergies to process

    try:
        for allergy in allergies:
            allergy_data = AllergyIntoleranceData()

            allergy_data.type = allergy.get('allergy')
            allergy_data.clinical_status = "Active"
            allergy_data.patient_id = patient.id


            existing_allergy = HealthData.query.filter_by(
                patient_id=patient.id,
                data_type=allergy_data.type
            ).first()

            allergy_fhire_json = json.loads(json.dumps(allergy_data.create_fhir()))

            fhir_id=save_resource("AllergyIntolerance",json.loads(allergy_fhire_json))

            data_aqu_datetime = datetime.now(timezone.utc).replace(microsecond=0)  # Remove microseconds
            # Convert to ISO 8601 format for FHIR
            data_aqu_datetime_iso = data_aqu_datetime.isoformat()

            if existing_allergy:
                existing_allergy.h_data = allergy_fhire_json
                existing_allergy.data_aqu_datetime = data_aqu_datetime
            else:
                new_allergy = HealthData(
                    patient_id=patient.id,
                    data_type=allergy_data.type,
                    data_aqu_datetime=data_aqu_datetime,
                    h_data=allergy_fhire_json,
                    fhir_id=fhir_id,
                )
                db.session.add(new_allergy)

    except Exception as e:
        app.logger.error(f"Error processing allergies: {str(e)}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
