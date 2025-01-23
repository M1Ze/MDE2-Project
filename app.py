# app.py
from flask import Flask, render_template, request, redirect, jsonify
import json
from werkzeug.security import generate_password_hash, check_password_hash

import requests
from db_models import db, Patient, HealthData, User
from fhir_data_processing.condition_data import ConditionData
from fhir_data_processing.patient_data import PatientData
from fhir_data_processing.observation_data import ObservationData
from fhir_data_processing.medication_data import MedicationData
from fhir_data_processing.consent_data import ConsentData
from fhir_data_processing.care_plan_data import CarePlanData
from fhir_data_processing.allergy_intolerance_data import AllergyIntoleranceData
from datetime import datetime, timedelta
import generate_qr
import jwt
import json
from datetime import datetime


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
    return render_template('user_patient_info.html')


from datetime import datetime
import json






@app.route('/savePatientData1', methods=['POST'])
def save_patient_data1():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({'status': 'error', 'message': 'No token provided'}), 401

    # Extract and validate the token
    token = auth_header.split(" ")[1]
    token_check = check_token(token)
    if not token_check or 'user_id' not in token_check:
        return jsonify({'status': 'error', 'message': 'Invalid token'}), 401

    user_id = token_check['user_id']

    try:
        # Parse the request JSON
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data received'}), 400

        # Extract and validate patient data
        patient_data_json = data.get('patient')
        if not isinstance(patient_data_json, dict):
            return jsonify({'status': 'error', 'message': 'Invalid or missing patient data'}), 400

        # Populate the PatientData object
        patient_data = PatientData()
        patient_data.populate_from_dict(patient_data_json)

        # Fetch the patient using the identifier
        identifier_value = patient_data.identifier
        if not identifier_value:
            return jsonify({'status': 'error', 'message': 'Missing identifier value'}), 400

        patient = Patient.query.filter_by(identifier=identifier_value).first()
        if not patient:
            return jsonify({'status': 'error', 'message': 'Patient not found'}), 404

        if patient.user_id != user_id:
            return jsonify({'status': 'error', 'message': 'Unauthorized access to patient data'}), 403

        # Update patient record
        patient.name = patient_data.name or patient.name
        patient.pat_data = json.loads(patient_data.create_fhir())  # Save updated FHIR data

        # Process observations
        observations = data.get('observations', [])
        if not isinstance(observations, list):
            return jsonify({'status': 'error', 'message': 'Invalid observations format, expected a list'}), 400

        for obs_wrapper in observations:
            # Extract the observation object
            obs_data = obs_wrapper.get('observation')
            if not isinstance(obs_data, dict):
                app.logger.warning(f"Skipping invalid observation format: {obs_wrapper}")
                continue  # Skip if the observation format is invalid

            try:
                # Create and populate an ObservationData object
                observation = ObservationData()
                observation.populate_from_dict(obs_data)

                # Convert data_aqu_datetime to datetime object if in string format
                data_aqu_datetime = observation.data_aqu_datetime
                if isinstance(data_aqu_datetime, str):
                    data_aqu_datetime = datetime.fromisoformat(data_aqu_datetime.replace("Z", "+00:00"))

                # Generate FHIR-compliant data as JSON string
                h_data_json = json.dumps(observation.create_fhir(), separators=(',', ':'))

                # Check if this observation already exists in the database
                existing_obs = HealthData.query.filter_by(
                    patient_id=patient.id,
                    data_type=observation.type
                ).first()

                # Create or update the observation record in the database
                if existing_obs:
                    existing_obs.h_data = h_data_json
                    existing_obs.data_aqu_datetime = data_aqu_datetime
                else:
                    new_obs = HealthData(
                        patient_id=patient.id,
                        data_type=observation.type,
                        data_aqu_datetime=data_aqu_datetime,
                        h_data=json.loads(h_data_json)
                    )
                    db.session.add(new_obs)

            except Exception as e:
                # Log the error and skip this observation
                app.logger.error(f"Error processing observation: {obs_data}, Error: {str(e)}")
                continue

        db.session.commit()  # Save all changes at once
        return jsonify({'status': 'success', 'message': 'Patient data and observations saved successfully'}), 200

    except Exception as e:
        # Log and handle unexpected errors
        app.logger.error(f"Error saving patient data: {str(e)}")
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'An error occurred while saving patient data.'}), 500







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
        print(patient_register_data_json)
        # Use PatientData to parse and validate the FHIR Patient resource
        # muss nochmal überarbeiten
        patient_data = PatientData()
        patient_data.populate_from_dict(patient_register_data)
        print(patient_data)

        patient_fhir_resource = patient_data.create_fhir()

        print(patient_fhir_resource)

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
            pat_data=json.loads(patient_fhir_resource)  # Save the entire Patient
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

    print(observations)

    for obs_wrapper in observations:
        obs_data = obs_wrapper.get('observation')
        if not isinstance(obs_data, dict):
            app.logger.warning(f"Skipping invalid observation format: {obs_wrapper}")
            continue

        try:
            observation = ObservationData()
            observation.populate_from_dict(obs_data)
            print(observation.data)

            data_aqu_datetime = observation.data_aqu_datetime
            if isinstance(data_aqu_datetime, str):
                data_aqu_datetime = datetime.fromisoformat(data_aqu_datetime.replace("Z", "+00:00"))

            print("Here:fhir")
            print(observation.create_fhir())

            h_data_json = json.loads(json.dumps(observation.create_fhir(), separators=(',', ':')))




            existing_obs = HealthData.query.filter_by(
                patient_id=patient.id,
                data_type=observation.type
            ).first()

            if existing_obs:
                existing_obs.h_data = h_data_json
                existing_obs.data_aqu_datetime = data_aqu_datetime
            else:
                new_obs = HealthData(
                    patient_id=patient.id,
                    data_type=observation.type,
                    data_aqu_datetime=data_aqu_datetime,
                    h_data=h_data_json
                )
                db.session.add(new_obs)

        except Exception as e:
            app.logger.error(f"Error processing observation: {obs_data}, Error: {str(e)}")

def save_consent(consent_data, patient):
    if not isinstance(consent_data, dict):
        return  # No consent data to process

    try:
        consent = ConsentData()
        consent.populate_from_dict(consent_data)

        existing_consent = HealthData.query.filter_by(patient_id=patient.id).first()
        if existing_consent:
            existing_consent.data = json.dumps(consent.create_fhir())
        else:
            new_consent = HealthData(
                patient_id=patient.id,
                data=json.dumps(consent.create_fhir())
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
            medication.populate_from_dict(med)

            existing_med = HealthData.query.filter_by(
                patient_id=patient.id,
                medication_name=medication.name
            ).first()

            if existing_med:
                existing_med.data = json.dumps(medication.create_fhir())
            else:
                new_med = HealthData(
                    patient_id=patient.id,
                    data=json.dumps(medication.create_fhir())
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
            condition.populate_from_dict(cond)

            existing_condition = HealthData.query.filter_by(
                patient_id=patient.id,
                condition_name=condition.name
            ).first()

            if existing_condition:
                existing_condition.data = json.dumps(condition.create_fhir())
            else:
                new_condition = HealthData(
                    patient_id=patient.id,
                    data=json.dumps(condition.create_fhir())
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
            allergy_data.populate_from_dict(allergy)

            existing_allergy = HealthData.query.filter_by(
                patient_id=patient.id,
                allergy_name=allergy_data.name
            ).first()

            if existing_allergy:
                existing_allergy.data = json.dumps(allergy_data.create_fhir())
            else:
                new_allergy = HealthData(
                    patient_id=patient.id,
                    data=json.dumps(allergy_data.create_fhir())
                )
                db.session.add(new_allergy)

    except Exception as e:
        app.logger.error(f"Error processing allergies: {str(e)}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)






# @app.route('/savePatientData1', methods=['POST'])
# def save_patient_data1():
#     # Extract user ID from token
#     auth_header = request.headers.get('Authorization')
#     if not auth_header or not auth_header.startswith("Bearer "):
#         return jsonify({'status': 'error', 'message': 'No token provided'}), 401
#
#     token = auth_header.split(" ")[1]
#     token_check = check_token(token)
#     if not token_check or 'user_id' not in token_check:
#         return jsonify({'status': 'error', 'message': 'Invalid token'}), 401
#
#     user_id = token_check['user_id']
#
#     try:
#         # Parse incoming JSON request
#         data = request.get_json()
#         if not data:
#             return jsonify({'status': 'error', 'message': 'No data received'}), 400
#
#         # Extract patient data
#         patient_data = data.get('patient')
#         if not patient_data or not isinstance(patient_data, dict):
#             return jsonify({'status': 'error', 'message': 'Invalid or missing patient data'}), 400
#
#         # Extract identifier value
#         identifier_list = patient_data.get('identifier', [])
#         identifier_value = identifier_list[0].get('value') if identifier_list else None
#         if not identifier_value:
#             return jsonify({'status': 'error', 'message': 'Missing identifier value'}), 400
#
#         # Fetch patient from the database
#         patient = Patient.query.filter_by(identifier=identifier_value).first()
#         if not patient:
#             return jsonify({'status': 'error', 'message': 'Patient not found'}), 404
#
#         if patient.user_id != user_id:
#             return jsonify({'status': 'error', 'message': 'Unauthorized access to patient data'}), 403
#
#         # Update patient data
#         patient.name = f"{patient_data.get('name', [{'family': patient.name.split()[1]}])[0]['given'][0]} {patient_data.get('name', [{'family': patient.name.split()[1]}])[0]['family']}" or patient.name
#         patient.pat_data = patient_data  # Save the updated FHIR JSON
#
#         # Extract observations
#         observations = data.get('observations', [])
#         if not isinstance(observations, list):
#             return jsonify({'status': 'error', 'message': 'Invalid observations format'}), 400
#
#         # Process and store observations in the database
#         # Process and store observations in the database
#         for obs in observations:
#             # Extract type from the observation
#             obs_code = obs.get('code', {})
#             obs_type = obs_code.get('text')  # Primary type from the "text" field
#
#             # Fallback to the first coding's display or code if "text" is missing
#             if not obs_type:
#                 coding_list = obs_code.get('coding', [])
#                 if coding_list:
#                     obs_type = coding_list[0].get('display') or coding_list[0].get('code')
#
#             # If still None, skip this observation
#             if not obs_type:
#                 print("Skipping observation due to missing data type:", json.dumps(obs, indent=2))
#                 continue
#
#             obs_value = obs.get('valueQuantity', {}).get('value')
#             obs_unit = obs.get('valueQuantity', {}).get('unit')
#             obs_timestamp = obs.get('effectiveDateTime')
#
#             # Convert obs_timestamp to Python datetime
#             if obs_timestamp:
#                 obs_timestamp = datetime.fromisoformat(obs_timestamp.replace("Z", "+00:00"))
#
#             # Serialize the observation to JSON
#             obs_json = json.dumps(obs)
#
#             # Check if the observation already exists
#             existing_obs = HealthData.query.filter_by(
#                 patient_id=patient.id,
#                 data_type=obs_type
#             ).first()
#
#             if existing_obs:
#                 # Update the existing observation
#                 existing_obs.h_data = obs_json
#                 existing_obs.data_aqu_datetime = obs_timestamp
#             else:
#                 # Create a new observation
#                 new_obs = HealthData(
#                     patient_id=patient.id,
#                     data_type=obs_type,
#                     data_aqu_datetime=obs_timestamp,
#                     h_data=obs_json  # Store the serialized JSON
#                 )
#                 db.session.add(new_obs)
#
#         # Commit changes to the database
#         db.session.commit()
#
#         return jsonify({
#             'status': 'success',
#             'message': f'Patient data updated with {len(observations)} observations'
#         }), 200
#
#     except Exception as e:
#         print("Error processing data:", str(e))
#         db.session.rollback()
#         return jsonify({'status': 'error', 'message': str(e)}), 500


# @app.route('/savePatientData1', methods=['POST'])
# def save_patient_data1():
#     auth_header = request.headers.get('Authorization')
#     if not auth_header or not auth_header.startswith("Bearer "):
#         return jsonify({'status': 'error', 'message': 'No token provided'}), 401
#
#     token = auth_header.split(" ")[1]
#     token_check = check_token(token)
#     if not token_check or 'user_id' not in token_check:
#         return jsonify({'status': 'error', 'message': 'Invalid token'}), 401
#
#     user_id = token_check['user_id']
#
#     try:
#         # Parse the request JSON
#         data = request.get_json()
#         print(f"Raw incoming data: {data}")
#         if not data:
#             return jsonify({'status': 'error', 'message': 'No data received'}), 400
#
#         # Extract patient data
#         patient_data_json = data.get('patient')
#         if not isinstance(patient_data_json, dict):
#             return jsonify({'status': 'error', 'message': 'Invalid or missing patient data'}), 400
#
#         # Populate the PatientData object
#         patient_data = PatientData()
#         patient_data.populate_from_dict(patient_data_json)
#
#         # Fetch the patient using the identifier
#         identifier_value = patient_data.identifier
#         if not identifier_value:
#             return jsonify({'status': 'error', 'message': 'Missing identifier value'}), 400
#
#         patient = Patient.query.filter_by(identifier=identifier_value).first()
#         if not patient:
#             return jsonify({'status': 'error', 'message': 'Patient not found'}), 404
#
#         if patient.user_id != user_id:
#             return jsonify({'status': 'error', 'message': 'Unauthorized access to patient data'}), 403
#
#         # Update patient record
#         patient.name = patient_data.name or patient.name
#         patient.pat_data = json.loads(patient_data.create_fhir())  # Save the updated FHIR JSON
#
#         # Process observations
#         observations = data.get('observations', [])
#         if not isinstance(observations, list):
#             return jsonify({'status': 'error', 'message': 'Invalid observations format, expected a list'}), 400
#
#         for obs_data in observations:
#             # Check and unwrap if `obs_data` is a list (nested case)
#             if isinstance(obs_data, list):
#                 app.logger.warning(f"Unwrapping nested list in observation: {obs_data}")
#                 obs_data = obs_data[0]  # Take the first item if it's a list
#             if not isinstance(obs_data, dict):
#                 app.logger.error(f"Skipping invalid observation format: {obs_data}")
#                 continue
#
#             try:
#                 # Create and populate ObservationData object
#                 observation = ObservationData()
#                 observation.populate_from_dict(obs_data)
#
#                 # Convert data_aqu_datetime to datetime object if it's a string
#                 data_aqu_datetime = observation.data_aqu_datetime
#                 if isinstance(data_aqu_datetime, str):
#                     data_aqu_datetime = datetime.fromisoformat(data_aqu_datetime.replace("Z", "+00:00"))
#
#                 # Generate FHIR-compliant data as JSON string
#                 h_data_json = json.dumps(observation.create_fhir(), separators=(',', ':'))
#
#                 # Check if observation already exists in the database
#                 existing_obs = HealthData.query.filter_by(
#                     patient_id=patient.id,
#                     data_type=observation.type
#                 ).first()
#
#                 # Create or update the observation
#                 if existing_obs:
#                     existing_obs.h_data = h_data_json
#                     existing_obs.data_aqu_datetime = data_aqu_datetime
#                 else:
#                     new_obs = HealthData(
#                         patient_id=patient.id,
#                         data_type=observation.type,
#                         data_aqu_datetime=data_aqu_datetime,
#                         h_data=h_data_json
#                     )
#                     db.session.add(new_obs)
#
#             except Exception as e:
#                 # Log error and skip the faulty observation
#                 app.logger.error(f"Error processing observation: {obs_data}, Error: {str(e)}")
#                 continue
#
#         db.session.commit()  # Save changes
#         return jsonify({'status': 'success', 'message': 'Patient data and observations saved successfully'}), 200
#
#     except Exception as e:
#         app.logger.error(f"Error saving patient data: {str(e)}")
#         db.session.rollback()
#         return jsonify({'status': 'error', 'message': 'An error occurred while saving patient data.'}), 500



# @app.route('/savePatientData1', methods=['POST'])
# def save_patient_data1():
#     # Token validation remains intact
#     auth_header = request.headers.get('Authorization')
#     if not auth_header or not auth_header.startswith("Bearer "):
#         return jsonify({'status': 'error', 'message': 'No token provided'}), 401
#
#     token = auth_header.split(" ")[1]
#     token_check = check_token(token)
#     if not token_check or 'user_id' not in token_check:
#         return jsonify({'status': 'error', 'message': 'Invalid token'}), 401
#
#     user_id = token_check['user_id']
#
#     try:
#         # Parse the request JSON
#         data = request.get_json()
#         if not data:
#             return jsonify({'status': 'error', 'message': 'No data received'}), 400
#
#         # Extract patient data
#         patient_data_json = data.get('patient')
#         if not patient_data_json or not isinstance(patient_data_json, dict):
#             return jsonify({'status': 'error', 'message': 'Invalid or missing patient data'}), 400
#
#         # Populate the PatientData object
#         patient_data = PatientData()
#         patient_data.populate_from_dict(patient_data_json)
#         patient_fhir_resource = patient_data.create_fhir()
#
#         # Fetch the patient using the identifier
#         identifier_value = patient_data.identifier
#         if not identifier_value:
#             return jsonify({'status': 'error', 'message': 'Missing identifier value'}), 400
#
#         patient = Patient.query.filter_by(identifier=identifier_value).first()
#         if not patient:
#             return jsonify({'status': 'error', 'message': 'Patient not found'}), 404
#
#         if patient.user_id != user_id:
#             return jsonify({'status': 'error', 'message': 'Unauthorized access to patient data'}), 403
#
#         # Update patient record
#         patient.name = patient_data.name or patient.name
#         patient.pat_data = json.loads(patient_fhir_resource)  # Save the updated FHIR JSON
#
#         observations = data.get('observations', [])
#         if not isinstance(observations, list):
#             return jsonify({'status': 'error', 'message': 'Invalid observations format'}), 400
#
#         # Flatten and clean observations to ensure they are dictionaries
#         cleaned_observations = []
#         for obs in observations:
#             if isinstance(obs, list):
#                 print(f"Flattening observation: {obs}")
#                 # Add all items from the nested list to the cleaned observations
#                 cleaned_observations.extend(obs)  # Add each dictionary in the nested list
#             elif isinstance(obs, dict):
#                 cleaned_observations.append(obs)  # Add any valid dictionaries
#             else:
#                 print(f"Skipping unsupported observation format: {obs}")  # Skip invalid types
#
#         # Process and store cleaned observations in the database
#         for obs_data in cleaned_observations:
#             try:
#                 # Create and populate the ObservationData object
#                 print(obs_data)
#                 observation = ObservationData()
#                 observation.populate_from_dict(obs_data)
#                 print(observation.type)
#
#                 # Check for required fields
#                 if not observation.identifier or not observation.type or not observation.data or not observation.data_aqu_datetime:
#                     print(f"Skipping incomplete observation: {obs_data}")
#                     continue
#
#                 # Convert data_aqu_datetime to Python datetime object
#                 data_aqu_datetime = observation.data_aqu_datetime
#                 if isinstance(data_aqu_datetime, str):
#                     # Convert from ISO format to Python datetime
#                     data_aqu_datetime = datetime.fromisoformat(data_aqu_datetime.replace("Z", "+00:00"))
#
#                 # Generate the FHIR-compliant data as JSON string
#                 h_data_json = json.dumps(observation.create_fhir())  # Serialize to JSON
#
#                 # Check if the observation already exists in the database
#                 existing_obs = HealthData.query.filter_by(
#                     patient_id=patient.id,
#                     data_type=observation.type
#                 ).first()
#
#                 # Create or update the observation in the database
#                 if existing_obs:
#                     # Update the existing observation
#                     existing_obs.h_data = h_data_json  # Save JSON string
#                     existing_obs.data_aqu_datetime = data_aqu_datetime  # Use Python datetime object
#                 else:
#                     # Create a new observation
#                     new_obs = HealthData(
#                         patient_id=patient.id,
#                         data_type=observation.type,
#                         data_aqu_datetime=data_aqu_datetime,  # Use Python datetime object
#                         h_data=json.loads(h_data_json)  # Save JSON string
#                     )
#                     db.session.add(new_obs)
#
#             except Exception as e:
#                 print(f"Error processing observation: {obs_data}, Error: {str(e)}")
#                 continue
#
#         db.session.commit()  # Save changes
#         return jsonify({'status': 'success', 'message': f'Patient data  observations saved saved successfully'}), 200
#     except Exception as e:
#         app.logger.error(f"Error saving patient data: {str(e)}")
#         db.session.rollback()
#         return jsonify({'status': 'error', 'message': 'An error occurred while saving patient data.'}), 500


# @app.route('/getPatientInformation1', methods=['GET'])
# def get_patient_information1():
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
#     # Use PatientData to process the patient resource
#     patient_data = PatientData()
#     patient_data.extract_data(filepath=None, json_string=json.dumps(patient.pat_data))
#
#     # Serialize and return the entire PatientData object
#     return jsonify({'status': 'success', 'patient': patient_data.__dict__})
#
# @app.route('/register1', methods=['GET', 'POST'])
# def register1():
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
#
#
# @app.route('/savePatientData1', methods=['POST'])
# def save_patient_data1():
#     # Extract user ID from token
#     auth_header = request.headers.get('Authorization')
#     if not auth_header or not auth_header.startswith("Bearer "):
#         return jsonify({'status': 'error', 'message': 'No token provided'}), 401
#
#     token = auth_header.split(" ")[1]
#     token_check = check_token(token)
#     if not token_check or 'user_id' not in token_check:
#         return jsonify({'status': 'error', 'message': 'Invalid token'}), 401
#
#     user_id = token_check['user_id']
#
#     try:
#         # Parse incoming JSON request
#         data = request.get_json()
#         if not data:
#             return jsonify({'status': 'error', 'message': 'No data received'}), 400
#
#         # Extract patient data
#         patient_data = data.get('patient')
#         if not patient_data or not isinstance(patient_data, dict):
#             return jsonify({'status': 'error', 'message': 'Invalid or missing patient data'}), 400
#
#         # Extract identifier value
#         identifier_list = patient_data.get('identifier', [])
#         identifier_value = identifier_list[0].get('value') if identifier_list else None
#         if not identifier_value:
#             return jsonify({'status': 'error', 'message': 'Missing identifier value'}), 400
#
#         # Fetch patient from the database
#         patient = Patient.query.filter_by(identifier=identifier_value).first()
#         if not patient:
#             return jsonify({'status': 'error', 'message': 'Patient not found'}), 404
#
#         if patient.user_id != user_id:
#             return jsonify({'status': 'error', 'message': 'Unauthorized access to patient data'}), 403
#
#         # Update patient data
#         patient.name = f"{patient_data.get('name', [{'family': patient.name.split()[1]}])[0]['given'][0]} {patient_data.get('name', [{'family': patient.name.split()[1]}])[0]['family']}" or patient.name
#         patient.pat_data = patient_data  # Save the updated FHIR JSON
#
#         # Extract and log observations
#         observations = data.get('observations', [])
#         if not isinstance(observations, list):
#             return jsonify({'status': 'error', 'message': 'Invalid observations format'}), 400
#
#         print("Received Observations:")
#         for obs in observations:
#             print(json.dumps(obs, indent=2))
#
#         # Placeholder for saving observations to the database
#         print(f"Patient {patient.name} has {len(observations)} new observations.")
#
#         # Commit updated patient data
#         db.session.commit()
#
#         return jsonify({
#             'status': 'success',
#             'message': f'Patient data updated with {len(observations)} observations',
#             'observations': observations
#         }), 200
#
#     except Exception as e:
#         print("Error processing data:", str(e))
#         db.session.rollback()
#         return jsonify({'status': 'error', 'message': str(e)}), 500
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
