import os
from fhir.resources.allergyintolerance import AllergyIntolerance
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
import os
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.reference import Reference
import os
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.reference import Reference


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
        self.patient_id = ""  # Patient ID to link the medication
        self.patient_name = ""  # Patient Name for display purposes

    def extract_data(self, filepath, json_string):
        # Read JSON file and parse it into an FHIR resource
        if filepath is not None:
            with open(filepath, "r") as file:
                json_string = file.read()
            allergy = AllergyIntolerance.parse_raw(json_string)
        else:
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
                    "substance": reaction.substance.coding[
                        0].display if reaction.substance and reaction.substance.coding else None,
                    "manifestations": [m.concept.coding[0].display for m in reaction.manifestation if
                                       m.concept and m.concept.coding],
                    "severity": reaction.severity if reaction.severity else None,
                    "onset": reaction.onset if reaction.onset else None,
                    "description": reaction.description if reaction.description else None,
                }
                self.reactions.append(reaction_details)

    def create_fhir(self):
        # Valid criticality values according to FHIR specification
        VALID_CRITICALITY_VALUES = ["low", "high", "unable-to-assess"]

        # Validate the criticality field
        criticality_value = self.criticality.lower() if self.criticality else None
        if criticality_value not in VALID_CRITICALITY_VALUES:
            raise ValueError(
                f"Invalid criticality value. Must be one of {VALID_CRITICALITY_VALUES}, but got '{self.criticality}'"
            )

        # Create the FHIR AllergyIntolerance resource
        allergy_resource = AllergyIntolerance(
            id=f"allergy-{self.code.replace(' ', '-')}",  # Replace invalid characters
            identifier=[
                {"system": "http://example.org/fhir/identifier", "value": self.identifier}
            ] if self.identifier else None,
            clinicalStatus=CodeableConcept(
                coding=[
                    Coding(
                        system="http://terminology.hl7.org/CodeSystem/allergyintolerance-clinical",
                        code="active",
                        display=self.clinical_status,
                    )
                ]
            ) if self.clinical_status else None,
            verificationStatus=CodeableConcept(
                coding=[
                    Coding(
                        system="http://terminology.hl7.org/CodeSystem/allergyintolerance-verification",
                        code="confirmed",
                        display=self.verification_status,
                    )
                ]
            ) if self.verification_status else None,
            type=CodeableConcept(
                coding=[
                    {"system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-type",
                     "code": self.allergy_type}
                ]
            ) if self.allergy_type else None,
            category=[self.category] if self.category else None,
            criticality=criticality_value,  # Use the validated criticality value
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
                        {"concept": CodeableConcept(
                            coding=[
                                Coding(system="http://snomed.info/sct", display=manifestation)
                            ]
                        )}
                        for manifestation in reaction["manifestations"]
                    ] if reaction["manifestations"] else None,
                    "severity": reaction["severity"],
                    "description": reaction["description"],
                }
                for reaction in self.reactions
            ] if self.reactions else None,
            patient=Reference(
                reference=f"Patient/{self.patient_id}",
                display=self.patient_name,
            ),
        )

        return allergy_resource.json(indent=4)

    def create_fhir_inFilesystem(self, base_path, patient_folder):

        # Ensure the patient folder exists
        os.makedirs(patient_folder, exist_ok=True)

        # Create the FHIR AllergyIntolerance resource
        allergy_resource = AllergyIntolerance(
            id=f"allergy-{self.code.replace(' ', '-')}",  # Replace invalid characters
            identifier=[
                {"system": "http://example.org/fhir/identifier", "value": self.identifier}
            ] if self.identifier else None,
            clinicalStatus=CodeableConcept(
                coding=[
                    Coding(
                        system="http://terminology.hl7.org/CodeSystem/allergyintolerance-clinical",
                        code="active",
                        display=self.clinical_status,
                    )
                ]
            ) if self.clinical_status else None,
            verificationStatus=CodeableConcept(
                coding=[
                    Coding(
                        system="http://terminology.hl7.org/CodeSystem/allergyintolerance-verification",
                        code="confirmed",
                        display=self.verification_status,
                    )
                ]
            ) if self.verification_status else None,
            type=CodeableConcept(
                coding=[
                    {"system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-type",
                     "code": self.allergy_type}
                ]
            ) if self.allergy_type else None,
            category=[self.category] if self.category else None,
            criticality=self.criticality,
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
                        {"concept": CodeableConcept(
                            coding=[
                                Coding(system="http://snomed.info/sct", display=manifestation)
                            ]
                        )}
                        for manifestation in reaction["manifestations"]
                    ] if reaction["manifestations"] else None,
                    "severity": reaction["severity"],
                    "description": reaction["description"],
                }
                for reaction in self.reactions
            ] if self.reactions else None,
            patient=Reference(
                reference=f"Patient/{self.patient_id}",
                display=self.patient_name,
            ),
        )

        # Save the AllergyIntolerance resource to the folder
        allergy_file = os.path.join(patient_folder, f"allergy_{self.code.replace(' ', '-')}_{self.patient_name.replace(" ", "_")}_{self.patient_id}.json")
        with open(allergy_file, "w") as file:
            file.write(allergy_resource.json(indent=4))
