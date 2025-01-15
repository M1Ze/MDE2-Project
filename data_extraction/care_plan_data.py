import os

from fhir.resources.careplan import CarePlan
from fhir.resources.period import Period
class CarePlanData:
    def __init__(self):
        self.identifier = ""
        self.status = ""  # Status of the care plan
        self.intent = ""  # Intent of the care plan
        self.title = ""  # Title or summary of the care plan
        self.period_start = ""  # Start date of the care plan
        self.period_end = ""  # End date of the care plan
        self.category = []  # List of categories
        self.description = ""  # Summary of the care plan
        self.activities = []  # List of planned actions or tasks

    def extract_data(self, filepath, json_string):
        # Read JSON file and parse it into a FHIR CarePlan resource
        if filepath is not None:
            with open(filepath, "r") as file:
                json_string = file.read()
            careplan = CarePlan.parse_raw(json_string)
        else:
            careplan = CarePlan.parse_raw(json_string)

        # Extract key attributes
        self.identifier = next(
            (identifier.value for identifier in careplan.identifier), None
        ) if careplan.identifier else None

        self.status = careplan.status if careplan.status else None
        self.intent = careplan.intent if careplan.intent else None
        self.title = careplan.title if careplan.title else None

        if careplan.period:
            self.period_start = careplan.period.start if careplan.period.start else None
            self.period_end = careplan.period.end if careplan.period.end else None

        self.category = [
            category.text for category in careplan.category
        ] if careplan.category else []

        self.description = careplan.description if careplan.description else None

        if careplan.activity:
            for activity in careplan.activity:
                self.activities.append(
                    activity.detail.description if activity.detail and activity.detail.description else None
                )

    def create_fhir(self):
        # Create the FHIR CarePlan resource
        care_plan_resource = CarePlan(
            identifier=[
                {"system": "http://example.org/fhir/identifier", "value": self.identifier}
            ] if self.identifier else None,
            status=self.status if self.status else None,
            intent=self.intent if self.intent else None,
            title=self.title if self.title else None,
            period=Period(
                start=self.period_start if self.period_start else None,
                end=self.period_end if self.period_end else None
            ) if self.period_start or self.period_end else None,
            category=[
                {"text": category} for category in self.category
            ] if self.category else None,
            description=self.description if self.description else None,
            activity=[
                {"detail": {"description": activity}} for activity in self.activities
            ] if self.activities else None,
            subject={"reference": f"Patient/{self.patient_id}"}  # Add subject field
        )

        # Return the serialized JSON representation
        return care_plan_resource.json(indent=4)

    def create_fhir_inFilesystem(self, filepath, patient_folder):
        # Create the folder path for the care plan
        os.makedirs(patient_folder, exist_ok=True)

        # Create the FHIR CarePlan resource
        care_plan_resource = CarePlan(
            identifier=[
                {"system": "http://example.org/fhir/identifier", "value": self.identifier}
            ] if self.identifier else None,
            status=self.status if self.status else None,
            intent=self.intent if self.intent else None,
            title=self.title if self.title else None,
            period=Period(
                start=self.period_start if self.period_start else None,
                end=self.period_end if self.period_end else None
            ) if self.period_start or self.period_end else None,
            category=[
                {"text": category} for category in self.category
            ] if self.category else None,
            description=self.description if self.description else None,
            activity=[
                {"detail": {"description": activity}} for activity in self.activities
            ] if self.activities else None,
        )

        # Create the file path
        filename = f"care_plan_{self.identifier.replace('.', '')}.json"
        patient_filename = self.patient_name.replace(" ", "_") + "_" + str(self.patient_id)
        careplan_fhire_resource = f"{filename}_{patient_filename}.json"
        full_path = os.path.join(filepath, careplan_fhire_resource)


        # Serialize the resource to JSON
        with open(full_path, "w") as file:
            file.write(care_plan_resource.json(indent=4))