#app.py
from flask import Flask, render_template
from db_models import db, Patient, HealthData, User
from data_extraction.patient_data import PatientData
from data_extraction.observation_data import ObservationData
from data_extraction.medication_data import MedicationData
from data_extraction.consent_data import ConsentData
from data_extraction.care_plan_data import CarePlanData
from data_extraction.allergy_intolerance_data import AllergyIntoleranceData
from datetime import datetime
import generate_qr

# Initialize the Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
   return render_template('welcome.html')

@app.route('/loginPage', methods=['GET'])
def login_page():
    return render_template('loginPage.html')
@app.route('/registerNewUser', methods=['GET', 'POST'])
def register_new_user():
    return render_template('register.html')
@app.route('/setupNewPatient', methods=['GET', 'POST'])
def setup_new_patient():
    render_template('new_user.html')

if __name__ == '__main__':
    app.run(debug=True)
    #app.run(host='0.0.0.0', port=8000, debug=True)