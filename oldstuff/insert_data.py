import glob
import os

from fhir_data_processing.allergy_intolerance_data import AllergyIntoleranceData
from fhir_data_processing.consent_data import ConsentData
from fhir_data_processing.medication_data import MedicationData
from fhir_data_processing.observation_data import ObservationData


# from fhir_data_processing.patient_data import PatientData
#
# patient = PatientData()
# patient.name = "John Doe"
# patient.birthdate = "01.01.1980"
# patient.gender = "male"
# patient.address = "789 Main St, City, State, 1357"
# patient.phone = "+123456789"
# patient.email = "johndoe@example.com"
# patient.identifier = "1111010180"
# patient.contacts = [
#     {"name": "Jane Doe", "phone": "+987654321"},
#     {"name": "Emily Smith", "phone": "+192837465"}
# ]
#
# print(patient.create_fhir())


#
# file_path_observation_example4 = "fhir_resources/patient_John_Doe_1111010180.json"
#
# patient4 =  PatientData()
# patient4.extract_data(file_path_observation_example4)
#
# print(patient4.name)
# print(patient4.address)
# print(patient4.contacts)

# allergy = AllergyIntoleranceData()
# allergy.identifier = "allergy001"
# allergy.clinical_status = "Active"
# allergy.verification_status = "Confirmed"
# allergy.allergy_type = "allergy"  # Valid system code will be added in the method
# allergy.category = "food"
# allergy.criticality = "high"
# allergy.code = "Cashew nuts"
# allergy.onset_datetime = "2004"
# allergy.recorded_date = "2025-01-01"
# allergy.patient_name = "John Doe"
# allergy.patient_id = "1111010180"
# allergy.reactions = [
#     {
#         "substance": "Cashew nut allergenic extract Injectable Product",
#         "manifestations": ["Anaphylactic reaction", "Urticaria"],
#         "severity": "severe",
#         "description": "Severe reaction to cashew nuts.",
#     }
# ]
#
# # Pass `patient_id` as a string
# allergy.create_fhire(base_path="fhir_resources", patient_folder="fhir_resources/John_Doe_1111010180")

#
# # Define test data
# medication = MedicationData()
# medication.identifier = "med001"
# medication.name = "Ibuprofen"
# medication.dose_form = "Tablet"
# medication.manufacturer = "Generic Pharma Inc."
# medication.ingredients = [
#     {"item": "Ibuprofen", "quantity": "200 mg"},
#     {"item": "Inactive Ingredients", "quantity": "50 mg"},
# ]
# medication.patient_id = "1111010180"
# medication.patient_name = "John Doe"
#
# medication.create_fhir('testing_code', 'testing_code')



# observation = ObservationData()
# observation.identifier = "obs-67890"
# observation.type = "Blood Pressure"
# observation.data_aqu_datetime = "2025-01-02T14:30:00Z"  # ISO 8601 format
# observation.data = "120 mmHg"  # Example for systolic blood pressure
# observation.patient_name = "John Doe"
# observation.patient_id = "1111010180"


# consent = ConsentData()
# consent.identifier = "consent-12345"
# consent.patient_name = "John Doe"
# consent.patient_id = "1111010180"
# consent.start_date = "2025-01-01"
# consent.end_date = "2026-01-01"
#
#
# # Set the file path
# test_filepath = "fhir_resources/John_Doe_1111010180"
#
# # Call create_fhire
# try:
#     consent.create_fhir(filepath=test_filepath, patient_folder=test_filepath)
#     print("Medication resource created successfully.")
# except Exception as e:
#     print(f"Error creating Medication resource: {e}")