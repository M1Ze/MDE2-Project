import glob
import os

from data_extraction.patient_data import PatientData

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


patient.create_fhire(filepath = "fhir_ressources")

file_path_observation_example4 = "fhir_ressources/patient_John_Doe_1111010180.json"

patient4 =  PatientData()
patient4.extract_data(file_path_observation_example4)

print(patient4.name)
print(patient4.address)
print(patient4.contacts)