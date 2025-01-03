from fhir.resources.allergyintolerance import AllergyIntolerance

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