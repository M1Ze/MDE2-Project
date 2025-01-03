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