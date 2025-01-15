import glob
import os

from data_extraction.patient_data import PatientData
from data_extraction.observation_data import ObservationData
from data_extraction.medication_data import MedicationData
from db_models import Patient

#filepath to json
file_path_patient_example_1 = "../fhir_resources/patient_example_1.json"
file_path_patient_example_2 = "../fhir_resources/patient_example_2.json"
file_path_observation_example1 = "../fhir_resources/observation_example_1.json"
file_path_observation_example2 = "../fhir_resources/observation_example_2.json"
file_path_observation_example3 = "../fhir_resources/observation_example_3.json"

Patient1 = PatientData()
Patient1.extract_data(file_path_patient_example_1, None)

Patient2 = PatientData()
Patient2.extract_data(file_path_patient_example_2, None)

Observation1 = ObservationData()
Observation1.extract_data(file_path_observation_example1)

Observation2 = ObservationData()
Observation2.extract_data(file_path_observation_example2)

Observation3 = ObservationData()
Observation3.extract_data(file_path_observation_example3)

#Medication
directory = "fhir_resources/medications"
files = glob.glob(os.path.join(directory, "*.json"))
Medications = []
Medication = MedicationData()

# Process each file
for file_path in files:
    Medication.extract_data(file_path)
    Medications.append(Medication.name)
    Medications.append(Medication.dose_form)


#Übergabe an DB:
print(Patient1.name)
print(Patient1.address)
print(Patient1.contacts)

print(Patient2.name)
print(Patient2.address)

#Type: Value Unit
print(Observation1.type,": ", Observation1.data)

print(Observation2.type,": ", Observation2.data)

print(Observation3.type,": ", Observation3.data)

print(Medications)


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


patient.create_fhir(filepath ="../fhir_resources")

file_path_observation_example4 = "../fhir_resources/John_Doe_1111010180/patient_John_Doe_1111010180.json"

patient4 =  PatientData()
patient4.extract_data(file_path_observation_example4)

print(patient4.name)
print(patient4.address)
print(patient4.contacts)