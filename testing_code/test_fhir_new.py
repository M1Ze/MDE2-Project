from fhir.resources.patient import Patient
import json
import db_models
from fhir_data_processing.patient_data import PatientData

patient_json ="{\n    \"resourceType\": \"Patient\",\n    \"identifier\": [\n        {\n            \"system\": \"http://example.org/fhir/identifier\",\n            \"value\": \"123410102010\"\n        }\n    ],\n    \"name\": [\n        {\n            \"family\": \"Mustermann\",\n            \"given\": [\n                \"Max\"\n            ]\n        }\n    ],\n    \"telecom\": [\n        {\n            \"system\": \"phone\",\n            \"value\": \"+430987654321234\",\n            \"use\": \"home\"\n        },\n        {\n            \"system\": \"email\",\n            \"value\": \"test@test.at\",\n            \"use\": \"home\"\n        }\n    ],\n    \"gender\": \"male\",\n    \"address\": [\n        {\n            \"line\": [\n                \"Test 1\"\n            ],\n            \"city\": \"Wien\",\n            \"state\": \"Wien\",\n            \"postalCode\": \"1120\"\n        }\n    ]\n}"


def test_patient_json():
    try:
        print("Fhir Methods")
        print(json.loads(patient_json))
    except Exception as e:
        print(e)



def test_our_extract():

    try:
        print("Our Methods")

        patient = PatientData()

        parsed_patient = Patient.parse_obj(patient_json)


        patient.name = parsed_patient.name[0].given[0] + " " + parsed_patient.name[0].family
        patient.gender = parsed_patient.gender
        patient.birthDate = parsed_patient.birthDate
        patient.telecom = parsed_patient.telecom
        patient.address = (parsed_patient.address[0].line[0] + "," + parsed_patient.address[0].city + " "
                           + parsed_patient.address[0].state + "," + parsed_patient.address[0].postalCode)

        new_json = patient.create_fhir()
        # print(new_json)

        patient1 = PatientData()

        patient1.extract_data(None,new_json)
        print("Working extract:" + patient.name)

    except Exception as e:
        print(e)

import json
from fhir.resources.patient import Patient
from fhir_data_processing.patient_data import PatientData  # Assuming this is implemented elsewhere


def new_test_our_method():
    # Create PatientData object and populate its fields
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

    # Create FHIR JSON string from the patient object
    json_string = patient.create_fhir()

    # Correct the Patient.parse_obj call by converting JSON string to a Python dictionary
    try:
        parsed_patient = Patient.parse_obj(json.loads(json_string))
        print()
        patient2 = PatientData()
        patient2.extract_data(None,parsed_patient)
        print(patient2.name)
    except Exception as e:
        print(f"Error parsing patient: {e}")


if __name__ == "__main__":
    test_patient_json()
