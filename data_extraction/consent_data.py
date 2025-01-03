from fhir.resources.consent import Consent

class ConsentData:
    def __init__(self):
        self.identifier = ""
        self.status = ""  # Status of the consent
        self.scope = ""   # Scope of the consent
        self.category = []  # List of categories
        self.provision_period_start = ""  # Start of the provision period
        self.provision_period_end = ""  # End of the provision period
        self.provision_text = ""  # Text description of the provision

    def extract_data(self, filepath):
        # Read the JSON file and parse it into a FHIR resource
        with open(filepath, "r") as file:
            json_string = file.read()
        consent = Consent.parse_raw(json_string)

        self.identifier = next(
            (identifier.value for identifier in consent.identifier), None
        ) if consent.identifier else None

        self.status = consent.status if consent.status else None

        self.scope = (
            consent.scope.text if consent.scope and consent.scope.text
            else consent.scope.coding[0].display if consent.scope and consent.scope.coding
            else None
        )

        self.category = [
            cat.text if cat.text else (cat.coding[0].display if cat.coding else None)
            for cat in consent.category
        ] if consent.category else []

        if consent.provision and consent.provision.period:
            self.provision_period_start = (
                consent.provision.period.start if consent.provision.period.start else None
            )
            self.provision_period_end = (
                consent.provision.period.end if consent.provision.period.end else None
            )

        self.provision_text = (
            consent.provision.text if consent.provision and consent.provision.text
            else None
        )