from fhir.resources.careplan import CarePlan

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

    def extract_data(self, filepath):
        # Read JSON file and parse it into a FHIR CarePlan resource
        with open(filepath, "r") as file:
            json_string = file.read()
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