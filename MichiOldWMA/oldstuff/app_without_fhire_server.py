from flask import Flask, render_template, request, redirect, jsonify
from oldstuff.old_db_models import db, User, PatientResource, Practitioner, \
    PractitionerAppointment  # Importiere die Modelle
import requests
from fhir.resources.patient import Patient
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
import json
from collections import defaultdict

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.secret_key = 'my_secret_key'

# bind flask to app
db.init_app(app)

# worktime
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

# table on demand
with app.app_context():
    db.create_all()
    # Liste aller Ärzte
    doctors = [
        ("Dr.Cardiologist", "Heart Specialist"),
        ("Dr.Dermatologist", "Skin Specialist"),
        ("Dr.Pediatrician", "Children’s Doctor"),
        ("Dr.Orthopedist", "Muscle Specialist")#,
       # ("Dr.Ophthalmologist", "Eye Specialist"),
       # ("Dr.Psychiatrist", "Mental Health Specialist")
    ]
    # Für jeden Arzt prüfen, ob er bereits existiert, falls nicht, hinzufügen
    for name, specialty in doctors:
        existing_practitioner = Practitioner.query.filter_by(name=name).first() #.first für ersten passenden Eintrag
        if existing_practitioner is None:
            new_practitioner = Practitioner(name=name, specialty=specialty)
            db.session.add(new_practitioner)
    db.session.commit()

    for name, specialty in doctors:
        if name in WORKING_HOURS:
            # Prüfen, ob bereits Termine existieren
            practitioner = Practitioner.query.filter_by(name=name).first()
            any_appointment = PractitionerAppointment.query.filter_by(practitioner_id=practitioner.id).first()
            if any_appointment is None:
                generate_time_slots(name, WORKING_HOURS[name], weeks_ahead=2)

def create_fhir_patient(data):
    patient = Patient(
        id=data['id'],
        name=[{"use": "official", "family": data['last_name'], "given": [data['first_name']]}]
    )
    response = requests.post('FHIR_SERVER_URL', json=patient.dict())
    return response.json()

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
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    if request.method == 'POST':
        data = request.get_json()
        fhir_patient = data.get('patient')
        password = data.get('password')

        # Validate patient and password
        if not fhir_patient or not isinstance(fhir_patient, dict):
            return jsonify({'status': 'error', 'message': 'Invalid FHIR patient data'}), 400

        email = None
        for telecom in fhir_patient.get('telecom', []):
            if telecom.get('system') == 'email':
                email = telecom.get('value')
                break

        if not email or not password:
            return jsonify({'status': 'error', 'message': 'Email or password is missing'}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({'status': 'error', 'message': 'Email already registered'}), 400

        hashed_password = generate_password_hash(password)
        new_user = User(email=email, password=hashed_password)

        try:
            db.session.add(new_user)
            db.session.commit()
            patient_resource = PatientResource(user_id=new_user.id, resource=json.dumps(fhir_patient))
            db.session.add(patient_resource)
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'User and Patient resource saved successfully!'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/loginPage', methods=['GET'])
def login_page():
    return render_template('loginPage.html')
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

    # Token erstellen
    token = jwt.encode(
        {'user_id': user.id, 'exp': datetime.utcnow() + timedelta(hours=24)},  # Ablaufzeit 24 Stunden hours =24 oder seconds=10
        app.secret_key,
        algorithm='HS256'
    )
    return jsonify({'status': 'success', 'message': 'Login successful', 'token': token}) # opt. add user_id': user.id ,

@app.route('/appointments_practitioners', methods=['GET'])
def appointments_practitioners():
    doctor_id = request.args.get('doctor_id')
    if not doctor_id:
        return jsonify({'status': 'error', 'message': 'No doctor_id provided'}), 400

    # Token-Validierung
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

    appointments = PractitionerAppointment.query.filter_by(practitioner_id=doctor_id, user_id=None).all()

    # Gruppierung der Termine nach Tag
    grouped_appointments = defaultdict(list)
    for appt in appointments:
        day_key = appt.date.strftime('%A - %d.%m.%Y')  # Tag und Datum als Schlüssel
        grouped_appointments[day_key].append(appt.date.strftime('%H:%M'))  # Nur die Uhrzeit speichern

    # Übergabe an das Template
    return render_template(
        'appointments_practitioners.html',
        practitioner=practitioner,
        grouped_appointments=grouped_appointments
    )

@app.route('/appointments_user', methods=['GET'])
def appointments_user():
    print("First")
    auth_header = request.headers.get('Authorization')
    print(auth_header)
    if not auth_header or not auth_header.startswith("Bearer "):
        print("Back to Default")
        return redirect('/appointmentsDefault')

    # Token überprüfen
    check_token_answer = check_token(auth_header.split(" ")[1])
    if 'error' in check_token_answer:
        if check_token_answer['error'] == 'expired':
            return jsonify({'status': 'error', 'message': 'Token has expired!'}), 403
        else:
            return jsonify({'status': 'error', 'message': 'Invalid token!'}), 401

    # Benutzer-ID aus dem Token abrufen
    user_id = check_token_answer['user_id']
    print(user_id)
    # Gebuchte Termine des Benutzers abrufen
    appointments = PractitionerAppointment.query.filter_by(user_id=user_id).all()
    patient_resource = PatientResource.query.filter_by(user_id=user_id).first()
    patient_data = json.loads(patient_resource.resource) if patient_resource else {}
    # Termine und zugehörige Ärzte übergeben
    return render_template('appointments_user.html', appointments=appointments
                           , patient=patient_data)

@app.route('/book_appointment', methods=['POST'])
def book_appointment():
    # Token-Validierung
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({'status': 'error', 'message': 'Authorization header missing or invalid'}), 401

    check_token_answer = check_token(auth_header.split(" ")[1])
    if 'error' in check_token_answer:
        if check_token_answer['error'] == 'expired':
            return jsonify({'status': 'error', 'message': 'Token has expired!'}), 403
        else:
            return jsonify({'status': 'error', 'message': 'Invalid token!'}), 401

    # JSON-Daten des Anfragers abrufen
    data = request.get_json()
    print(data)
    selected_datetime_str = data.get('appointment')
    if not selected_datetime_str:
        return jsonify({'status': 'error', 'message': 'No appointment selected'}), 400

    # Datum und Zeit parsen
    try:
        selected_datetime = datetime.strptime(selected_datetime_str, '%d.%m.%Y %H:%M')
    except ValueError:
        return jsonify({'status': 'error', 'message': 'Invalid datetime format'}), 400

    # Termin in der Datenbank suchen
    appointment = PractitionerAppointment.query.filter_by(date=selected_datetime, user_id=None).first()
    if not appointment:
        return jsonify({'status': 'error', 'message': 'Appointment not available'}), 404

    # Termin buchen
    appointment.user_id = check_token_answer['user_id']
    db.session.commit()

    return jsonify({'status': 'success', 'message': 'Appointment booked successfully'})

@app.route('/appointments', methods=['GET'])
def appointments():
    print("Test")
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith("Bearer "):
        return redirect('/appointmentsDefault')
    check_token_answer = check_token(auth_header.split(" ")[1])
    if 'error' in check_token_answer:
        if check_token_answer['error'] == 'expired':
            return jsonify({'status': 'error', 'message': 'Token has expired!'}), 403
        else:
            return jsonify({'status': 'error', 'message': 'Invalid token!'}), 401
    # Wenn Token gültig, dann zu appointments_user.html
    print("Test2")
    return render_template('appointments_user.html')

@app.route('/appointmentsDefault', methods=['GET'])
def appointments_default():
    #print('Opened Default')
    return render_template('appointmentsDefault.html')

if __name__ == '__main__':
    app.run(debug=True)
