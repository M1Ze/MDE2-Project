import glob
import os

from PatientData import PatientData, ObservationData, Medication
from db_models import Patient

#filepath to json
file_path_patient_example_1 = "fhir_ressources/patient_example_1.json"
file_path_patient_example_2 = "fhir_ressources/patient_example_2.json"
file_path_observation_example1 = "fhir_ressources/observation_example_1.json"
file_path_observation_example2 = "fhir_ressources/observation_example_2.json"

Patient1 = PatientData()
Patient1.extract_data(file_path_patient_example_1)

Patient2 = PatientData()
Patient2.extract_data(file_path_patient_example_2)

Observation1 = ObservationData()
Observation1.extract_data(file_path_observation_example1)

Observation2 = ObservationData()
Observation2.extract_data(file_path_observation_example2)

#Medication
directory = "fhir_ressources/medications"
files = glob.glob(os.path.join(directory, "*.json"))
Medications = []
Medication = Medication()

# Process each file
for file_path in files:
    Medication.extract_data(file_path)
    Medications.append(Medication.name)


#Übergabe an DB:
print(Patient1.name)
print(Patient1.address)

print(Patient2.name)
print(Patient2.address)

#Type: Value Unit
print(Observation1.type,": ", Observation1.data)

print(Observation2.type,": ", Observation2.data)

print(Medications)



