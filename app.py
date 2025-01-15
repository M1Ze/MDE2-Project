from flask import Flask, render_template
from db_models import db, Patient, HealthData, User
from data_extraction.patient_data import PatientData
from data_extraction.observation_data import ObservationData
from data_extraction.medication_data import MedicationData
from data_extraction.consent_data import ConsentData
from data_extraction.care_plan_data import CarePlanData
from data_extraction.allergy_intolerance_data import AllergyIntoleranceData
from datetime import datetime

# Initialize the Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


with app.app_context():
    # Create tables
    db.drop_all()
    db.create_all()

    # Debug: Check existing users
    existing_users = User.query.all()
    print(f"Existing users in the database before adding: {len(existing_users)}")

    try:
        # Add user
        user = User(username="John@doe.com", password="12345678", role="User")
        db.session.add(user)
        db.session.commit()  # Commit to generate the user.id

        # Add patient data
        patient = PatientData()
        patient.name = "John Doe"
        patient.birthdate = "01.01.1980"
        patient.gender = "male"
        patient.address = "789 Main St, City, State, 1357"
        patient.phone = "+123456789"
        patient.email = "johndoe@example.com"
        patient.identifier = "1111010180"
        patient.contacts = [
            {"name": "Jane Doe", "phone": "+987654321"},
            {"name": "Emily Smith", "phone": "+192837465"}
        ]
        patient_json = patient.create_fhir()

        patient_entry = Patient(
            identifier=patient.identifier,
            name=patient.name,
            pat_data=patient_json,
            user_id=user.id  # Assign the user_id
        )
        db.session.add(patient_entry)
        db.session.commit()  # Commit to generate patient_entry.id

        # Common acquisition datetime
        data_aqu_datetime = datetime.strptime("2025-01-02T14:30:00Z", "%Y-%m-%dT%H:%M:%SZ")

        # Add health data: Observation
        observation = ObservationData()
        observation.identifier = "obs-67890"
        observation.type = "Blood Pressure"
        observation.data = "120 mmHg"
        observation.patient_id = "1111010180"
        observation_json = observation.create_fhir()

        health_data_entry = HealthData(
            patient_id=patient_entry.id,  # Correct patient_id
            data_type=observation.type,
            data_aqu_datetime=data_aqu_datetime,  # Use datetime object
            h_data=observation_json
        )
        db.session.add(health_data_entry)

        # Add health data: Medication
        medication = MedicationData()
        medication.identifier = "med001"
        medication.name = "Ibuprofen"
        medication.dose_form = "Tablet"
        medication.manufacturer = "Generic Pharma Inc."
        medication.ingredients = [
            {"item": "Ibuprofen", "quantity": "200 mg"},
            {"item": "Inactive Ingredients", "quantity": "50 mg"},
        ]
        medication.patient_id = "1111010180"
        medication_json = medication.create_fhir()

        medication_data_entry = HealthData(
            patient_id=patient_entry.id,
            data_type="Medication",
            data_aqu_datetime=data_aqu_datetime,
            h_data=medication_json
        )
        db.session.add(medication_data_entry)

        # Add health data: Consent
        consent = ConsentData()
        consent.identifier = "consent-12345"
        consent.patient_id = "1111010180"
        consent.status = "active"
        consent_json = consent.create_fhir()

        consent_data_entry = HealthData(
            patient_id=patient_entry.id,
            data_type="Consent",
            data_aqu_datetime=data_aqu_datetime,
            h_data=consent_json
        )
        db.session.add(consent_data_entry)

        # Add health data: CarePlan
        careplan = CarePlanData()
        careplan.identifier = "careplan-12345"
        careplan.patient_name = "John Doe"
        careplan.patient_id = "1111010180"
        careplan.status = "active"
        careplan.intent = "order"
        careplan_json = careplan.create_fhir()

        careplan_data_entry = HealthData(
            patient_id=patient_entry.id,
            data_type="CarePlan",
            data_aqu_datetime=data_aqu_datetime,
            h_data=careplan_json
        )
        db.session.add(careplan_data_entry)

        # Add health data: AllergyIntolerance
        allergy = AllergyIntoleranceData()
        allergy.identifier = "allergy001"
        allergy.clinical_status = "Active"
        allergy.verification_status = "Confirmed"
        allergy.allergy_type = "allergy"
        allergy.category = "food"
        allergy.criticality = "high"
        allergy.code = "Cashew nuts"
        allergy.onset_datetime = "2004"
        allergy.recorded_date = "2025-01-01"
        allergy.patient_name = "John Doe"
        allergy.patient_id = "1111010180"
        allergy.reactions = [
            {
                "substance": "Cashew nut allergenic extract Injectable Product",
                "manifestations": ["Anaphylactic reaction", "Urticaria"],
                "severity": "severe",
                "description": "Severe reaction to cashew nuts.",
            }
        ]
        allergy_json = allergy.create_fhir()

        allergy_data_entry = HealthData(
            patient_id=patient_entry.id,
            data_type="AllergyIntolerance",
            data_aqu_datetime=data_aqu_datetime,
            h_data=allergy_json
        )
        db.session.add(allergy_data_entry)

        # Commit all changes to the database
        db.session.commit()

        print("All test data successfully saved to the database.")

    except Exception as e:
        db.session.rollback()
        print(f"Error adding user: {e}")





@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)