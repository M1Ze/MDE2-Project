from collections import defaultdict
from datetime import datetime, timedelta

import jwt
import requests
from flask import Flask, render_template, request, redirect, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from db_models import db, User, PatientInfo, Practitioner, PractitionerAppointment

from fhir.resources.patient import Patient
from pydantic import ValidationError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.secret_key = 'my_secret_key'
FHIR_SERVER_URL = "http://localhost:8080/fhir"

#binde the flask app to the db
db.init_app(app)

# define workinghours
WORKING_HOURS = {
    "Dr.Cardiologist": {
        "Monday":    {"start": "07:00", "end": "15:00", "interval": 60},
        "Wednesday": {"start": "12:00", "end": "20:00", "interval": 60},
        "Friday":    {"start": "07:00", "end": "15:00", "interval": 60}
    },
    "Dr.Dermatologist": {
        "Tuesday": {"start": "07:00", "end": "15:00", "interval": 60},
        "Thursday": {"start": "12:00", "end": "20:00", "interval": 60},
        "Saturday": {"start": "07:00", "end": "15:00", "interval": 60}
    },
    "Dr.Pediatrician": {
        "Monday": {"start": "15:00", "end": "20:00", "interval": 60},
        "Wednesday": {"start": "07:00", "end": "12:00", "interval": 60},
        "Friday": {"start": "15:00", "end": "20:00", "interval": 60}
    },
    "Dr.Orthopedist": {
        "Tuesday": {"start": "15:00", "end": "20:00", "interval": 60},
        "Thursday": {"start": "07:00", "end": "12:00", "interval": 60},
        "Saturday": {"start": "15:00", "end": "20:00", "interval": 60}
    }
}

# generate avalable time slots
def generate_time_slots(doctor_name, schedule, weeks_ahead=2):
    practitioner = Practitioner.query.filter_by(name=doctor_name).first()
    if not practitioner:
        print(f"Arzt {doctor_name} nicht in der DB gefunden.")
        return

    start_date = datetime.now().date()
    end_date = start_date + timedelta(weeks=weeks_ahead)

    current_date = start_date
    while current_date <= end_date:
        weekday_name = current_date.strftime("%A")
        if weekday_name in schedule:
            start_time_str = schedule[weekday_name]["start"]
            end_time_str = schedule[weekday_name]["end"]
            interval = schedule[weekday_name]["interval"]

            start_dt = datetime.combine(current_date, datetime.strptime(start_time_str, "%H:%M").time())
            end_dt = datetime.combine(current_date, datetime.strptime(end_time_str, "%H:%M").time())

            slot_dt = start_dt
            while slot_dt < end_dt:
                existing_appointment = PractitionerAppointment.query.filter_by(
                    practitioner_id=practitioner.id,
                    date=slot_dt
                ).first()

                if not existing_appointment:
                    new_appointment = PractitionerAppointment(
                        date=slot_dt,
                        user_id=None,
                        practitioner_id=practitioner.id
                    )
                    db.session.add(new_appointment)

                slot_dt += timedelta(minutes=interval)
        current_date += timedelta(days=1)
    db.session.commit()

# create the table if there is no
with app.app_context():
    db.create_all()
    doctors = [
        ("Dr.Cardiologist", "Heart Specialist"),
        ("Dr.Dermatologist", "Skin Specialist"),
        ("Dr.Pediatrician", "Children’s Doctor"),
        ("Dr.Orthopedist", "Muscle Specialist")#,
       # ("Dr.Ophthalmologist", "Eye Specialist"),
       # ("Dr.Psychiatrist", "Mental Health Specialist")
    ]
    # check for every doc, if not existent add
    for name, specialty in doctors:
        existing_practitioner = Practitioner.query.filter_by(name=name).first() #.first for first match
        if existing_practitioner is None:
            new_practitioner = Practitioner(name=name, specialty=specialty)
            db.session.add(new_practitioner)
    db.session.commit()

    for name, specialty in doctors:
        if name in WORKING_HOURS:
            # check if appointments exists
            practitioner = Practitioner.query.filter_by(name=name).first()
            latest_appointment = PractitionerAppointment.query.filter(
                PractitionerAppointment.practitioner_id == practitioner.id,
                PractitionerAppointment.date >= datetime.now()
                ).order_by(PractitionerAppointment.date.desc()).first()
            if not latest_appointment or latest_appointment.date < (datetime.now() + timedelta(weeks=2)):
                generate_time_slots(name, WORKING_HOURS[name], weeks_ahead=2)

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
@app.route('/loginPage', methods=['GET'])
def login_page():
    return render_template('loginPage.html')
@app.route('/appointmentsDefault', methods=['GET'])
def appointments_default():
    return render_template('appointmentsDefault.html')
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    if request.method == 'POST':
        data = request.get_json()
        fhir_patient = data.get('patient')
        password = data.get('password')

        email = None
        for telecom in fhir_patient.get('telecom', []):
            if telecom.get('system') == 'email':
                email = telecom.get('value')
                break

        if not email or not password:
            print("email or password missing")
            return jsonify({'status': 'error', 'message': 'Email or password is missing'}), 500

        if User.query.filter_by(email=email).first():
            print("double mail")
            return jsonify({'status': 'error', 'message': 'Email already registered'}), 500

        # check if patient
        if not fhir_patient or not isinstance(fhir_patient, dict):
            return jsonify({'status': 'error', 'message': 'Invalid FHIR patient data'}), 400

        try:
            # The Patient.parse_obj method is a feature of the fhir.resources library (which relies on Pydantic).
            # It takes a Python dictionary (in this case, fhir_patient) and
            # validates whether its structure matches the FHIR Patient schema.
            Patient.parse_obj(fhir_patient)
            print("FHIR Patient resource validation successful.")
        except ValidationError as e:
            print(f"Validation error: {e}")
            return jsonify({'status': 'error', 'message': 'Invalid FHIR patient resource'}), 400

        hashed_password = generate_password_hash(password)
        new_user = User(email=email, password=hashed_password)

        try:
            # Send patient data to FHIR server
            response = requests.post(
                "http://localhost:8080/fhir/Patient",
                json=fhir_patient,
                headers={"Content-Type": "application/fhir+json"}
            )
            response.raise_for_status()

            # Get the FHIR ID from the response
            fhir_id = response.json().get('id')
            if not fhir_id:
                raise ValueError("FHIR server did not return an ID")

            # Save the user and FHIR ID in the database
            db.session.add(new_user)
            db.session.commit()
            patient_info = PatientInfo(user_id=new_user.id, fhir_id=fhir_id)
            db.session.add(patient_info)
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'User and FHIR Patient ID saved successfully!'})
        except requests.exceptions.RequestException as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': f"FHIR Server Error: {str(e)}"}), 500
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(e)}), 500
@app.route('/login', methods=['POST'])
def login():
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
        {'user_id': user.id, 'exp': datetime.utcnow() + timedelta(seconds=30)},  # Ablaufzeit 24 Stunden hours =24 oder seconds=10
        app.secret_key,
        algorithm='HS256'
    )
    return jsonify({'status': 'success', 'message': 'Login successful', 'token': token}) # opt. add user_id': user.id ,
@app.route('/appointments_practitioners', methods=['GET'])
def appointments_practitioners():
    doctor_id = request.args.get('doctor_id')
    if not doctor_id:
        return jsonify({'status': 'error', 'message': 'No doctor_id provided'}), 400
    #validate token
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith("Bearer "):
        return redirect('/')
    check_token_answer = check_token(auth_header.split(" ")[1])
    if 'error' in check_token_answer:
        if check_token_answer['error'] == 'expired':
            return jsonify({'status': 'error', 'message': 'Token has expired!'}), 403
        else:
            return jsonify({'status': 'error', 'message': 'Invalid token!'}), 401

    practitioner = Practitioner.query.get(doctor_id)
    if not practitioner:
        return jsonify({'status': 'error', 'message': 'No practitioner found'}), 404

    appointments = PractitionerAppointment.query.filter(
    PractitionerAppointment.practitioner_id == practitioner.id,
    PractitionerAppointment.user_id == None,  # only unbooked
    PractitionerAppointment.date >= datetime.now()  # only future
    ).all()

    #groupes appointments per day for easy display
    grouped_appointments = defaultdict(list) #creates dictionary: any non-existing key is initialized as emtpy list
    for appt in appointments:
        day_key = appt.date.strftime('%A - %d.%m.%Y') # Extract a day key, e.g. "Monday - 14.08.2023"
        grouped_appointments[day_key].append(appt.date.strftime('%H:%M')) # Append the appointment's time (e.g. "09:30") to that day's list

    return render_template(
        'appointments_practitioners.html',
        practitioner=practitioner,
        grouped_appointments=grouped_appointments
    )
@app.route('/appointments_user', methods=['GET'])
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
    patient = PatientInfo.query.filter_by(user_id=user_id).first()
    patient_data = get_patient_data(patient.fhir_id) if patient else None
    appointments = user.appointments
    return render_template('appointments_user.html', patient=patient_data, appointments=appointments)
@app.route('/book_appointment', methods=['POST'])
def book_appointment():
    # validate token
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({'status': 'error', 'message': 'Authorization header missing or invalid'}), 401
    check_token_answer = check_token(auth_header.split(" ")[1])
    if 'error' in check_token_answer:
        if check_token_answer['error'] == 'expired':
            return jsonify({'status': 'error', 'message': 'Token has expired!'}), 403
        else:
            return jsonify({'status': 'error', 'message': 'Invalid token!'}), 401

    # get appointment info from booking
    data = request.get_json()
    selected_datetime_str = data.get('appointment')
    if not selected_datetime_str:
        return jsonify({'status': 'error', 'message': 'No appointment selected'}), 400

    # pars date and time
    try:
        selected_datetime = datetime.strptime(selected_datetime_str, '%d.%m.%Y %H:%M')
    except ValueError:
        return jsonify({'status': 'error', 'message': 'Invalid datetime format'}), 400

    # search appointments in db
    appointment = PractitionerAppointment.query.filter_by(date=selected_datetime, user_id=None).first()
    if not appointment:
        return jsonify({'status': 'error', 'message': 'Appointment not available'}), 404

    # book appointment
    appointment.user_id = check_token_answer['user_id']
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Appointment booked successfully'})
@app.route('/appointments', methods=['GET'])
def appointments():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith("Bearer "):
        return redirect('/appointmentsDefault')
    check_token_answer = check_token(auth_header.split(" ")[1])
    if 'error' in check_token_answer:
        if check_token_answer['error'] == 'expired':
            return jsonify({'status': 'error', 'message': 'Token has expired!'}), 403
        else:
            return jsonify({'status': 'error', 'message': 'Invalid token!'}), 401
    #if token is valid show useres appointments side
    return render_template('appointments_user.html')

if __name__ == '__main__':
    app.run(debug=True)
