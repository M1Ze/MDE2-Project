import os

from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.condition import Condition
from fhir.resources.reference import Reference


class ConditionData:
    def __init__(self):
        self.patient_identifier = None
        self.condition_code = None  # Hard coded code System Snomed CT: Hörgerät 6012004, Bluthochdruck 38341003, Diabetes 73211009, Herzschrittmacher 14106009
        self.recorded_date = None
        self.clinical_status = "active"  # Default clinical status (can be adjusted as needed)

    def extract_data(self, filepath=None, json_string=None):
        # Read JSON file or parse JSON string into a FHIR Condition resource
        if filepath:
            with open(filepath, "r") as file:
                json_string = file.read()
            condition = Condition.parse_raw(json_string)
        else:
            condition = Condition.parse_raw(json_string)

        self.patient_identifier = (
            condition.subject.reference.replace("Patient/", "")
            if condition.subject and condition.subject.reference else None
        )
        self.condition_code = (
            condition.code.coding[0].code
            if condition.code and condition.code.coding else None
        )
        self.recorded_date = condition.recordedDate if condition.recordedDate else None

    def create_fhir(self):
        # Create the FHIR Condition resource with required fields including clinicalStatus
        condition_resource = Condition(
            clinicalStatus=CodeableConcept(
                coding=[
                    Coding(
                        system="http://terminology.hl7.org/CodeSystem/condition-clinical",
                        code=self.clinical_status
                    )
                ]
            ),
            subject=Reference(reference=f"Patient/{self.patient_identifier}"),
            code=CodeableConcept(
                coding=[
                    Coding(
                        system="http://snomed.info/sct",
                        code=self.condition_code
                    )
                ]
            ),
            recordedDate=self.recorded_date if self.recorded_date else None
        )

        return condition_resource.json(indent=4)

    def create_fhir_in_filesystem(self, filepath):
        # Create the folder path for the condition
        folder_name = f"condition_{self.condition_code}"
        condition_folder = os.path.join(filepath, folder_name)
        os.makedirs(condition_folder, exist_ok=True)

        # Create the FHIR Condition resource
        condition_resource = Condition(
            clinicalStatus=CodeableConcept(
                coding=[
                    Coding(
                        system="http://terminology.hl7.org/CodeSystem/condition-clinical",
                        code=self.clinical_status
                    )
                ]
            ),
            subject=Reference(reference=f"Patient/{self.patient_identifier}"),
            code=CodeableConcept(
                coding=[
                    Coding(
                        system="http://snomed.info/sct",
                        code=self.condition_code
                    )
                ]
            ),
            recordedDate=self.recorded_date if self.recorded_date else None
        )

        # Create the file path
        filename = f"condition_{self.condition_code}.json"
        full_path = os.path.join(condition_folder, filename)

        # Serialize the resource to JSON
        with open(full_path, "w") as file:
            file.write(condition_resource.json(indent=4))
