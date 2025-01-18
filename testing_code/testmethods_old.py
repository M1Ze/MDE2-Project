from data_extraction.allergy_intolerance_data import AllergyIntoleranceData
from data_extraction.care_plan_data import CarePlanData
from data_extraction.consent_data import ConsentData
from data_extraction.medication_data import MedicationData
from data_extraction.observation_data import ObservationData
from data_extraction.patient_data import PatientData


def test_patient_data():
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

    json_string = patient.create_fhir()

    new_patient = PatientData()
    new_patient.extract_data(None, json_string)

    print(new_patient.identifier)
    print(new_patient.contacts)


def test_observation_data():
    observation = ObservationData()
    observation.identifier = "obs-67890"
    observation.type = "Blood Pressure"
    observation.data_aqu_datetime = "2025-01-02T14:30:00Z"  # ISO 8601 format
    observation.data = "120 mmHg"  # Example for systolic blood pressure
    observation.patient_name = "John Doe"
    observation.patient_id = "1111010180"

    json_string = observation.create_fhir()

    new_observation = ObservationData()
    new_observation.extract_data(None, json_string)

    print(new_observation.identifier)
    print(new_observation.type)

def test_observation_data_file():
    new_observation = ObservationData()
    new_observation.extract_data("../fhir_resources/observation_example_1.json", None)

    print(new_observation.data)
    print(new_observation.type)

def test_medication_data():
    # Define test data
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
    medication.patient_name = "John Doe"

    json_string = medication.create_fhir()
    new_medication = MedicationData()
    new_medication.extract_data(None, json_string)
    print(new_medication.identifier)
    print(new_medication.name)
    print(new_medication.dose_form)


def test_consent_data():
    consent = ConsentData()
    consent.identifier = "consent-12345"
    consent.patient_id = "1111010180"
    consent.status = "active"

    json_string = consent.create_fhir()

    new_consent = ConsentData()
    new_consent.extract_data(None, json_string)
    print("Extracted Identifier:", new_consent.identifier)


def test_care_plan_data():
    careplan = CarePlanData()
    careplan.identifier = "careplan-12345"
    careplan.patient_name = "John Doe"
    careplan.patient_id = "1111010180"
    careplan.status = "active"  # Set a valid status
    careplan.intent = "order"  # Set a valid intent

    # Generate FHIR JSON
    json_string = careplan.create_fhir()

    # Test extraction
    new_careplan = CarePlanData()
    new_careplan.extract_data(filepath=None, json_string=json_string)
    print(new_careplan.identifier)


def test_allergy_data():
    allergy = AllergyIntoleranceData()
    allergy.identifier = "allergy001"
    allergy.clinical_status = "Active"
    allergy.verification_status = "Confirmed"
    allergy.allergy_type = "allergy"  # Valid system code will be added in the method
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
    json_string = allergy.create_fhir()

    new_allergy = AllergyIntoleranceData()
    new_allergy.extract_data(None, json_string)

    print(new_allergy.identifier)
    print(new_allergy.category)
    print(new_allergy.code)


if __name__ == "__main__":
    test_observation_data_file()
    test_medication_data()
    # test_patient_data()
    # test_observation_data()
    # test_medication_data()
    # test_consent_data()
    # test_care_plan_data()
    # test_allergy_data()


