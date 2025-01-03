import glob
import os

from data_extraction.allergy_intolerance import AllergyIntoleranceData

#
# from data_extraction.patient_data import PatientData
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
#
# patient.create_fhire(filepath = "fhir_ressources")
#
# file_path_observation_example4 = "fhir_ressources/patient_John_Doe_1111010180.json"
#
# patient4 =  PatientData()
# patient4.extract_data(file_path_observation_example4)
#
# print(patient4.name)
# print(patient4.address)
# print(patient4.contacts)

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

# Pass `patient_id` as a string
allergy.create_fhire(base_path="fhir_resources", patient_folder="fhir_ressources/John_Doe_1111010180")