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
        self.identifier = None
        self.clinical_status = None
        self.verification_status = None
        self.allergy_type = None
        self.category = None
        self.criticality = None
        self.code = None  # Description of the allergen (e.g., "Cashew nuts")
        self.onset_datetime = None
        self.recorded_date = None
        self.reactions = []  # List of reactions (e.g., symptoms)
        self.patient_id = None  # Patient ID to link the medication
        self.patient_name = None  # Patient Name for display purposes

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

        # Validate the criticality field and provide a default value if missing
        if self.criticality:
            criticality_value = self.criticality.lower()
            if criticality_value not in VALID_CRITICALITY_VALUES:
                raise ValueError(
                    f"Invalid criticality value. Must be one of {VALID_CRITICALITY_VALUES}, but got '{self.criticality}'"
                )
        else:
            # Default value if criticality is not provided
            criticality_value = "unable-to-assess"

        # Ensure a proper fallback value for the "display" attribute of the patient reference
        if not self.patient_name or not isinstance(self.patient_name, str) or self.patient_name.strip() == "":
            patient_name_display = "Unknown Patient"
        else:
            patient_name_display = self.patient_name.strip()

        # Create the FHIR AllergyIntolerance resource
        allergy_resource = AllergyIntolerance(
            id=f"allergy-{self.code.replace(' ', '-')}" if self.code else None,  # Replace invalid characters
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
            criticality=criticality_value,  # Use the validated or defaulted criticality value
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
                    ) if reaction.get("substance") else None,
                    "manifestation": [
                        {"concept": CodeableConcept(
                            coding=[
                                Coding(system="http://snomed.info/sct", display=manifestation)
                            ]
                        )}
                        for manifestation in reaction.get("manifestations", [])
                    ],
                    "severity": reaction.get("severity"),
                    "description": reaction.get("description"),
                }
                for reaction in self.reactions
            ] if self.reactions else None,
            patient=Reference(
                reference=f"Patient/{self.patient_id}" if self.patient_id else None,
                display=patient_name_display,  # Use validated display value
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
