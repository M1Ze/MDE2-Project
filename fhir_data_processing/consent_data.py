from fhir.resources.consent import Consent
from fhir.resources.consent import ConsentProvision
from fhir.resources.reference import Reference
from fhir.resources.codeableconcept import CodeableConcept
import os


class ConsentData:
    def __init__(self):
        self.patient_id = ""
        self.identifier = ""
        self.status = ""  # Status of the consent
        self.category = []  # List of categories
        self.provision_period_start = ""  # Start of the provision period
        self.provision_period_end = ""  # End of the provision period

    def extract_data(self, filepath, json_string):
        # Read the JSON file and parse it into a FHIR resource
        if filepath is not None:
            with open(filepath, "r") as file:
                json_string = file.read()
        consent = Consent.parse_raw(json_string)

        self.identifier = next(
            (identifier.value for identifier in consent.identifier), None
        ) if consent.identifier else None

        self.status = consent.status if consent.status else None

        # Extract category information
        self.category = [
            cat.text if cat.text else (cat.coding[0].display if cat.coding else None)
            for cat in consent.category
        ] if consent.category else []

        # Extract provision period details
        if consent.provision and consent.provision[0].period:
            self.provision_period_start = consent.provision[0].period.start
            self.provision_period_end = consent.provision[0].period.end

    def create_fhir(self):
        # Create the Consent resource
        consent_resource = Consent(
            identifier=[
                {
                    "system": "http://svc.co.at/CodeSystem/ecard-svt-cs",
                    "value": self.identifier,
                }
            ] if self.identifier else None,
            status=self.status if self.status else 'draft', #default
            category=[
                CodeableConcept(
                    coding=[{"code": "dnr", "display": "Do Not Resuscitate"}]
                )
            ],
            provision=[
                ConsentProvision(
                    action=[
                        CodeableConcept(coding=[{"code": "deny", "display": "Deny Action"}])
                    ],
                    code=[CodeableConcept(text="Resuscitation")],
                    actor=[
                        {
                            "role": CodeableConcept(text="Patient"),
                            "reference": Reference(reference=f"Patient/{self.patient_id}")
                        }
                    ]
                )
            ]
        )

        return consent_resource.json(indent=4)

    def create_fhir_inFilesystem(self, filepath, patient_folder):
        # Ensure the patient folder exists
        os.makedirs(patient_folder, exist_ok=True)

        # Create FHIR Consent resource
        consent_resource = Consent(
            identifier=[
                {
                    "system": "http://example.org/fhir/identifier",
                    "value": self.identifier,
                }
            ] if self.identifier else None,
            status=self.status if self.status else "active",
            category=[
                CodeableConcept(
                    coding=[{"code": "dnr", "display": "Do Not Resuscitate"}]
                )
            ],
            provision=[
                ConsentProvision(
                    action=[
                        CodeableConcept(coding=[{"code": "deny", "display": "Deny Action"}])
                    ],
                    code=[CodeableConcept(text="Resuscitation")],
                    actor=[
                        {
                            "role": CodeableConcept(text="Patient"),
                            "reference": Reference(reference=f"Patient/{self.patient_id}")
                        }
                    ]
                )
            ]
        )

        # Create the file path
        filename = f"consent_{self.identifier.replace('.', '')}.json"
        full_path = os.path.join(patient_folder, filename)

        # Serialize the resource to JSON
        with open(full_path, "w") as file:
            file.write(consent_resource.json(indent=4))

    def populate_from_dict(self,data,patient):

        self.patient_id = patient.fhir_id
        self.identifier = patient.identifier
        self.status = data.get("status")
