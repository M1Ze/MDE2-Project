from fhir.resources.patient import Patient
from fhir.resources.contactpoint import ContactPoint
from fhir.resources.humanname import HumanName
from fhir.resources.address import Address
#DISCLAMER
#ich (jakob) habe mich nur herumgespielt mit dem fhir zeugs um zu schauen ob es eh so funktioniert wie ich es wollte, ist nicht zu 100% richtig einige sachen fehlerhaft!!
class FHIRDocumentGenerator:
    def __init__(self, name, birth_date, gender, ssn, address, email, phone_number, allergies=None, chronic_diseases=None, pregnancy=None, medications=None, care_level=None, dnr=None, emergency_contacts=None):
        self.name = name
        self.birth_date = birth_date
        self.gender = gender
        self.ssn = ssn
        self.address = address
        self.email = email
        self.phone_number = phone_number
        self.allergies = allergies or []
        self.chronic_diseases = chronic_diseases or []
        self.pregnancy = pregnancy
        self.medications = medications or []
        self.care_level = care_level
        self.dnr = dnr
        self.emergency_contacts = emergency_contacts or []

    def generate_fhir_document(self):
        patient = Patient(
            id="patient-example",
            text={"status": "generated", "div": f"<div>{self.name}'s FHIR Record</div>"},
            gender=self.gender.lower(),
            birthDate=self.birth_date,
            identifier=[{"system": "urn:oid:2.16.840.1.113883.4.1", "value": self.ssn}],
            name=[HumanName(family=self.name.split()[-1], given=self.name.split()[:-1])],
            telecom=[
                ContactPoint(system="phone", value=self.phone_number, use="home"),
                ContactPoint(system="email", value=self.email, use="home")
            ],
            address=[Address(text=self.address)],
        )

        extensions = []

        if self.allergies:
            extensions.append({
                "url": "http://hl7.org/fhir/StructureDefinition/patient-allergy",
                "valueString": ", ".join(self.allergies)
            })

        if self.chronic_diseases:
            extensions.append({
                "url": "http://hl7.org/fhir/StructureDefinition/patient-condition",
                "valueString": ", ".join(self.chronic_diseases)
            })

        if self.pregnancy and self.gender.lower() == "female":
            extensions.append({
                "url": "http://hl7.org/fhir/StructureDefinition/patient-pregnancy",
                "valueString": "Yes" if self.pregnancy == "Yes" else "No"
            })

        if self.medications:
            extensions.append({
                "url": "http://hl7.org/fhir/StructureDefinition/patient-medication",
                "valueString": ", ".join(self.medications)
            })

        if self.care_level:
            extensions.append({
                "url": "http://hl7.org/fhir/StructureDefinition/patient-careLevel",
                "valueString": self.care_level
            })

        if self.dnr:
            extensions.append({
                "url": "http://hl7.org/fhir/StructureDefinition/patient-dnr",
                "valueBoolean": True if self.dnr == "Yes" else False
            })

        if self.emergency_contacts:
            patient.contact = [
                {
                    "name": {"text": contact["name"]},
                    "telecom": [{"system": "phone", "value": contact["phone"], "use": "home"}]
                }
                for contact in self.emergency_contacts
            ]

        if extensions:
            patient.extension = extensions

        return patient.dict()
