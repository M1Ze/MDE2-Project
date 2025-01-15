import json
import os
from datetime import datetime

from fhir.resources.address import Address
from fhir.resources.contactpoint import ContactPoint
from fhir.resources.humanname import HumanName
from fhir.resources.patient import Patient
from sqlalchemy.sql.sqltypes import NULLTYPE

from server import json_string


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

    def extract_data(self, filepath, json_string):
        # Read JSON file and parse it into a FHIR Patient resource
        if filepath is not None:
            with open(filepath, "r") as file:
                json_string = file.read()
            patient = Patient.parse_raw(json_string)
        else:
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


    def create_fhir(self):
        from datetime import datetime
        from fhir.resources.humanname import HumanName
        from fhir.resources.contactpoint import ContactPoint
        from fhir.resources.address import Address

        # Create the FHIR Patient resource
        patient_resource = Patient(
            identifier=[
                {"system": "http://example.org/fhir/identifier", "value": self.identifier}
            ] if self.identifier else None,
            name=[
                HumanName(family=self.name.split(" ")[-1], given=self.name.split(" ")[:-1])
            ] if self.name else None,
            birthDate=self.format_birthdate(self.birthdate),
            gender=self.gender if self.gender else None,
            address=[
                Address(
                    line=[self.address.split(", ")[0]],
                    city=self.address.split(", ")[1] if len(self.address.split(", ")) > 1 else None,
                    state=self.address.split(", ")[2] if len(self.address.split(", ")) > 2 else None,
                    postalCode=self.address.split(", ")[3] if len(self.address.split(", ")) > 3 else None,
                )
            ] if self.address else None,
            telecom=[
                ContactPoint(system="phone", value=self.phone, use="home")
                if self.phone
                else None,
                ContactPoint(system="email", value=self.email, use="home")
                if self.email
                else None,
            ],
            contact=[
                {
                    "name": HumanName(
                        family=contact["name"].split(" ")[-1],
                        given=contact["name"].split(" ")[:-1],
                    ),
                    "telecom": [
                        ContactPoint(system="phone", value=contact["phone"], use="mobile")
                    ],
                }
                for contact in self.contacts
            ]
            if self.contacts
            else None,
        )
        return patient_resource.json(indent=4)




    def create_fhir_inFilesystem(self, filepath):
        from datetime import datetime
        from fhir.resources.humanname import HumanName
        from fhir.resources.contactpoint import ContactPoint
        from fhir.resources.address import Address

        # Create the folder path for the patient
        folder_name = f"{self.name.replace(' ', '_')}_{self.identifier.replace('.', '')}"
        patient_folder = os.path.join(filepath, folder_name)
        os.makedirs(patient_folder, exist_ok=True)

        # Create the FHIR Patient resource
        patient_resource = Patient(
            identifier=[
                {"system": "http://example.org/fhir/identifier", "value": self.identifier}
            ] if self.identifier else None,
            name=[
                HumanName(family=self.name.split(" ")[-1], given=self.name.split(" ")[:-1])
            ] if self.name else None,
            birthDate=self.format_birthdate(self.birthdate),
            gender=self.gender if self.gender else None,
            address=[
                Address(
                    line=[self.address.split(", ")[0]],
                    city=self.address.split(", ")[1] if len(self.address.split(", ")) > 1 else None,
                    state=self.address.split(", ")[2] if len(self.address.split(", ")) > 2 else None,
                    postalCode=self.address.split(", ")[3] if len(self.address.split(", ")) > 3 else None,
                )
            ] if self.address else None,
            telecom=[
                ContactPoint(system="phone", value=self.phone, use="home")
                if self.phone
                else None,
                ContactPoint(system="email", value=self.email, use="home")
                if self.email
                else None,
            ],
            contact=[
                {
                    "name": HumanName(
                        family=contact["name"].split(" ")[-1],
                        given=contact["name"].split(" ")[:-1],
                    ),
                    "telecom": [
                        ContactPoint(system="phone", value=contact["phone"], use="mobile")
                    ],
                }
                for contact in self.contacts
            ]
            if self.contacts
            else None,
        )

        # Create the file path
        filename = self.name.replace(" ", "_") + "_" + str(self.identifier.replace(".", ""))
        patient_fhire_resource = f"patient_{filename}.json"
        full_path = os.path.join(patient_folder, patient_fhire_resource)

        # Serialize the resource to JSON
        with open(full_path, "w") as file:
            file.write(patient_resource.json(indent=4))

    def format_birthdate(self, birthdate):
        """
        Converts the input birthdate to ISO 8601 format (YYYY-MM-DD).
        """
        try:
            if "." in birthdate:
                return datetime.strptime(birthdate, "%d.%m.%Y").strftime("%Y-%m-%d")
            elif "/" in birthdate:
                return datetime.strptime(birthdate, "%m/%d/%Y").strftime("%Y-%m-%d")
            else:
                return datetime.strptime(birthdate, "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            raise ValueError(
                f"Invalid date format for birthdate: {birthdate}. "
                "Expected formats are DD.MM.YYYY, MM/DD/YYYY, or YYYY-MM-DD."
            )