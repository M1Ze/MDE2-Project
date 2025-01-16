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
    render_template('index.html')

@app.route('/loginPage', methods=['GET'])
def login_page():
    return render_template('loginPage.html')

if __name__ == '__main__':
    app.run(debug=True)