#app.py
from flask import Flask, render_template, request, redirect, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

import requests
from db_models import db, Patient, HealthData, User
from data_extraction.patient_data import PatientData
from data_extraction.observation_data import ObservationData
from data_extraction.medication_data import MedicationData
from data_extraction.consent_data import ConsentData
from data_extraction.care_plan_data import CarePlanData
from data_extraction.allergy_intolerance_data import AllergyIntoleranceData
from datetime import datetime, timedelta
import generate_qr
import jwt


# Initialize the Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'my_secret_key'
FHIR_SERVER_URL = "http://localhost:8080/fhir"
db.init_app(app)

with app.app_context():
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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    if request.method == 'POST':
        data = request.get_json()
        user_data = data.get('user')
        email = user_data.get('email')
        given_name = user_data.get('given_name')
        last_name = user_data.get('last_name')
        password = data.get('password')

        if not email or not password:
            print("email or password missing")
            return jsonify({'status': 'error', 'message': 'Email or password is missing'}), 500

        if User.query.filter_by(email=email).first():
            print("double mail")
            return jsonify({'status': 'error', 'message': 'Email already registered'}), 501

        hashed_password = generate_password_hash(password)
        new_user = User(email=email, password=hashed_password, role='User')
        print(email)
        print(given_name)
        print(last_name)

        try:
            # Save the user and FHIR ID in the database
            db.session.add(new_user)
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'User registered'}), 200
        except Exception as e:
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
            {'user_id': user.id, 'exp': datetime.utcnow() + timedelta(seconds=30)},
            # Ablaufzeit 24 Stunden hours =24 oder seconds=10
            app.secret_key,
            algorithm='HS256'
        )
        return jsonify(
            {'status': 'success', 'message': 'Login successful', 'token': token})  # opt. add user_id': user.id ,


@app.route('/checklogin', methods=['GET', 'POST'])
def checklogin():
    def appointments_user():
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer "):
            return redirect('/appointmentsDefault')
        token_check = check_token(auth_header.split(" ")[1])
        if 'error' in token_check:
            return jsonify({'status': 'error', 'message': token_check['error']}), 401
        try:
            user_id = token_check['user_id']
            user = User.query.get(user_id)
        except KeyError:
            return jsonify({'status': 'error', 'message': 'No user found'}), 404

        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404
        patient = User.query.filter_by(user_id=user_id).first()
        patient_data = get_patient_data(patient.fhir_id) if patient else None
        appointments = user.appointments
        return None
        #return render_template('appointments_user.html', patient=patient_data, appointments=appointments)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)