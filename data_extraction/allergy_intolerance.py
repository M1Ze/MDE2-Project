import os

from fhir.resources.allergyintolerance import AllergyIntolerance
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding

class AllergyIntoleranceData:
    def __init__(self):
        self.identifier = ""
        self.clinical_status = ""
        self.verification_status = ""
        self.allergy_type = ""
        self.category = ""
        self.criticality = ""
        self.code = ""  # Description of the allergen (e.g., "Cashew nuts")
        self.onset_datetime = ""
        self.recorded_date = ""
        self.reactions = []  # List of reactions (e.g., symptoms)

    def extract_data(self, filepath):
        # Read JSON file and parse it into an FHIR resource
        with open(filepath, "r") as file:
            json_string = file.read()
        allergy = AllergyIntolerance.parse_raw(json_string)

        # Extract key attributes
        self.identifier = next(
            (identifier.value for identifier in allergy.identifier), None
        ) if allergy.identifier else None

        self.clinical_status = allergy.clinicalStatus.coding[0].display if allergy.clinicalStatus else None
        self.verification_status = allergy.verificationStatus.coding[0].display if allergy.verificationStatus else None

        self.allergy_type = allergy.type.coding[0].display if allergy.type and allergy.type.coding else None
        self.category = ", ".join(allergy.category) if allergy.category else None
        self.criticality = allergy.criticality if allergy.criticality else None

        self.code = allergy.code.coding[0].display if allergy.code and allergy.code.coding else None
        self.onset_datetime = allergy.onsetDateTime if allergy.onsetDateTime else None
        self.recorded_date = allergy.recordedDate if allergy.recordedDate else None

        # Extract reactions
        if allergy.reaction:
            for reaction in allergy.reaction:
                reaction_details = {
                    "substance": reaction.substance.coding[0].display if reaction.substance and reaction.substance.coding else None,
                    "manifestations": [m.concept.coding[0].display for m in reaction.manifestation if m.concept and m.concept.coding],
                    "severity": reaction.severity if reaction.severity else None,
                    "onset": reaction.onset if reaction.onset else None,
                    "description": reaction.description if reaction.description else None,
                }
                self.reactions.append(reaction_details)

    def create_fhire(self, filepath):
        # Create the FHIR AllergyIntolerance resource

        # Create the folder path for the patient
        folder_name = f"{self.name.replace(' ', '_')}_{self.identifier.replace('.', '')}"
        patient_folder = os.path.join(filepath, folder_name)
        os.makedirs(patient_folder, exist_ok=True)

        allergy_resource = AllergyIntolerance(
            identifier=[
                {"system": "http://example.org/fhir/identifier", "value": self.identifier}
            ] if self.identifier else None,
            clinicalStatus=CodeableConcept(
                coding=[
                    Coding(system="http://terminology.hl7.org/CodeSystem/allergyintolerance-clinical",
                           code="active", display=self.clinical_status)
                ]
            ) if self.clinical_status else None,
            verificationStatus=CodeableConcept(
                coding=[
                    Coding(system="http://terminology.hl7.org/CodeSystem/allergyintolerance-verification",
                           code="confirmed", display=self.verification_status)
                ]
            ) if self.verification_status else None,
            type=self.allergy_type if self.allergy_type else None,
            category=[self.category] if self.category else None,
            criticality=self.criticality if self.criticality else None,
            code=CodeableConcept(
                coding=[
                    Coding(system="http://snomed.info/sct", display=self.code)
                ]
            ) if self.code else None,
            onsetDateTime=self.onset_datetime if self.onset_datetime else None,
            recordedDate=self.recorded_date if self.recorded_date else None,
            reaction=[
                {
                    "substance": CodeableConcept(
                        coding=[
                            Coding(system="http://snomed.info/sct", display=reaction["substance"])
                        ]
                    ) if reaction["substance"] else None,
                    "manifestation": [
                        CodeableConcept(
                            coding=[
                                Coding(system="http://snomed.info/sct", display=manifestation)
                            ]
                        )
                        for manifestation in reaction["manifestations"]
                    ] if reaction["manifestations"] else None,
                    "severity": reaction["severity"] if reaction["severity"] else None,
                    "onset": reaction["onset"] if reaction["onset"] else None,
                    "description": reaction["description"] if reaction["description"] else None,
                }
                for reaction in self.reactions
            ] if self.reactions else None,
        )

        # Create the file path
        filename = self.code.replace(" ", "_") if self.code else "allergy_intolerance"
        allergy_fhire_resource = f"allergy_{filename}.json"
        full_path = os.path.join(filepath, allergy_fhire_resource)

        # Serialize the resource to JSON
        with open(full_path, "w") as file:
            file.write(allergy_resource.json(indent=4))