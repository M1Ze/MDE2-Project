import json
import os

from fhir.resources.address import Address
from fhir.resources.contactpoint import ContactPoint
from fhir.resources.humanname import HumanName
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

    def create_fhire(self, filepath):
        patient_fhire_resource = f"patient_{filename}.json"
        full_path = os.path.join(filepath, patient_fhire_resource)
        with open(full_path, "w") as file:
            file.write("{}")


    def create_fhire(self, filepath, filename):
        # Create the FHIR Patient resource
        patient_resource = Patient.construct()

        # Populate identifier
        if self.identifier:
            patient_resource.identifier = [
                {"system": "http://example.org/fhir/identifier", "value": self.identifier}
            ]

        # Populate name
        if self.name:
            name_parts = self.name.split(" ")
            patient_resource.name = [
                HumanName.construct(
                    family=name_parts[-1], given=name_parts[:-1]
                )
            ]

        # Populate birthdate
        if self.birthdate:
            patient_resource.birthDate = self.birthdate

        # Populate gender
        if self.gender:
            patient_resource.gender = self.gender

        # Populate address
        if self.address:
            address_parts = self.address.split(", ")
            patient_resource.address = [
                Address.construct(
                    line=[address_parts[0]],
                    city=address_parts[1] if len(address_parts) > 1 else None,
                    state=address_parts[2] if len(address_parts) > 2 else None,
                    postalCode=address_parts[3] if len(address_parts) > 3 else None,
                )
            ]

        # Populate telecom
        patient_resource.telecom = []
        if self.phone:
            patient_resource.telecom.append(
                ContactPoint.construct(system="phone", value=self.phone, use="home")
            )
        if self.email:
            patient_resource.telecom.append(
                ContactPoint.construct(system="email", value=self.email, use="home")
            )

        # Populate contacts
        if self.contacts:
            patient_resource.contact = []
            for contact in self.contacts:
                contact_name = HumanName.construct(
                    family=contact["name"].split(" ")[-1],
                    given=contact["name"].split(" ")[:-1],
                )
                contact_telecom = [
                    ContactPoint.construct(
                        system="phone", value=contact["phone"], use="mobile"
                    )
                ]
                patient_resource.contact.append(
                    {"name": contact_name, "telecom": contact_telecom}
                )

        # Write the Patient resource to a JSON file
        patient_fhire_resource = f"patient_{filename}.json"
        full_path = os.path.join(filepath, patient_fhire_resource)
        with open(full_path, "w") as file:
            json.dump(patient_resource.dict(), file, indent=4)
