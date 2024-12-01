import json

from fhir.resources.R4B.medication import MedicationIngredient
from fhir.resources.medicationadministration import MedicationAdministration
from fhir.resources.observation import Observation
from fhir.resources.patient import Patient

class PatientData:
    def __init__(self):
        self.name = ""
        self.birthdate = ""
        self.gender = ""
        self.address = ""
        self.phone = ""
        self.email = ""
        self.identifier = ""
        self.native_language = ""
        self.contact_person_name = ""
        self.contact_person_phone = ""

    def extract_data(self, filepath):
        # json file einlesen um FHIR ressource draus zu machen
        with open(filepath, "r") as file:
            json_string = file.read()
        patient = Patient.parse_raw(json_string)

        self.name = (
            " ".join(patient.name[0].given) + " " + patient.name[0].family
            if patient.name else None
        )
        self.birthdate = patient.birthDate if patient.birthDate else None
        self.gender = patient.gender if patient.gender else None
        self.address = (
            ", ".join(filter(
                None,patient.address[0].line + [patient.address[0].city, patient.address[0].state, patient.address[0].postalCode])) if patient.address else None
        )
        self.phone = next(
            (telecom.value for telecom in patient.telecom if telecom.system == "phone"), None
        )
        self.email = next(
            (telecom.value for telecom in patient.telecom if telecom.system == "email"), None
        )
        self.identifier = next(
            (identifier.value for identifier in patient.identifier), None
        ) if patient.identifier else None
        self.native_language = (
            patient.communication[0].language.coding[0].display
            if patient.communication else None
        )
        self.contact_person_name = (
            " ".join(patient.contact[0].name.given)
            + " "
            + patient.contact[0].name.family
            if patient.contact
               and patient.contact[0].name
               and hasattr(patient.contact[0].name, "given")
               and isinstance(patient.contact[0].name.given, list)
            else patient.contact[0].name.family
            if patient.contact and patient.contact[0].name else None)

        self.contact_person_phone = next(
            (telecom.value for telecom in patient.contact[0].telecom if telecom.system == "phone"),
            None,
        ) if patient.contact else None

class ObservationData:
    def __init__(self):
        self.identifier = ""
        self.type = "" #Type of observation
        self.data_aqu_datetime = ""
        self.data = "" # String with value + unit

    def extract_data(self, filepath):
        # json file einlesen um FHIR ressource draus zu machen
        with open(filepath, "r") as file:
            json_string = file.read()
        observation = Observation.parse_raw(json_string)

        self.identifier = next(
            (identifier.value for identifier in observation.identifier), None
        ) if observation.identifier else None

        self.type = observation.code.coding[0].display if observation.code else None

        self.data_aqu_datetime = observation.effectiveDateTime if observation.effectiveDateTime else None

        if hasattr(observation, "valueQuantity") and observation.valueQuantity:
            self.data = f"{observation.valueQuantity.value} {observation.valueQuantity.unit}"
        elif hasattr(observation, "valueCodeableConcept") and observation.valueCodeableConcept:
            self.data = (
                observation.valueCodeableConcept.text
                if observation.valueCodeableConcept.text
                else observation.valueCodeableConcept.coding[0].display
                if observation.valueCodeableConcept.coding
                else None
            )
        elif hasattr(observation, "valueString") and observation.valueString:
            self.data = observation.valueString
        elif hasattr(observation, "valueBoolean") and observation.valueBoolean is not None:
            self.data = str(observation.valueBoolean)  # Convert boolean to string
        elif hasattr(observation, "valueInteger") and observation.valueInteger is not None:
            self.data = str(observation.valueInteger)  # Convert integer to string
        else:
            self.data = None

class Medication:
    def __init__(self):
        self.name=""

    def extract_data(self, filepath):
        with open(filepath, "r") as file:
            json_string = file.read()

        medicationJson = json.loads(json_string)
        self.name = medicationJson.get("code").get("text") if medicationJson.get("code").get("text") else None