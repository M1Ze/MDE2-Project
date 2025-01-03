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
        self.contacts = []  # List of contact persons

    def extract_data(self, filepath):
        # Read JSON file and parse it into a FHIR Patient resource
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
                None, patient.address[0].line + [patient.address[0].city, patient.address[0].state, patient.address[0].postalCode]))
            if patient.address else None
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

        # Extract all contact persons (not only one)
        if patient.contact:
            for contact in patient.contact:
                contact_name = (
                    " ".join(contact.name.given) + " " + contact.name.family
                    if contact.name and hasattr(contact.name, "given") and isinstance(contact.name.given, list)
                    else contact.name.family if contact.name else None
                )
                contact_phone = next(
                    (telecom.value for telecom in contact.telecom if telecom.system == "phone"),
                    None,
                )
                self.contacts.append({"name": contact_name, "phone": contact_phone})