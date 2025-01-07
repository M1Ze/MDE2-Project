from fhir.resources.consent import Consent, ConsentProvision


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

    def create_fhir(self, filepath, patient_folder):
        import os
        from fhir.resources.consent import Consent, ConsentProvisionActor
        from fhir.resources.codeableconcept import CodeableConcept
        from fhir.resources.period import Period


        # Ensure the patient folder exists
        os.makedirs(patient_folder, exist_ok=True)

        # Create FHIR Consent resource
        consent_resource = Consent(
            identifier=[{
                "system": "http://example.org/fhir/identifier",
                "value": self.identifier
            }] if self.identifier else None,
            status="active",
            category=[CodeableConcept(coding=[{"code": "dnr", "display": "Do Not Resuscitate"}])],
            patient={"reference": f"Patient/{self.patient_id}"} if self.patient_id else None,
            period=Period(
                start=self.start_date,
                end=self.end_date
            ) if self.start_date and self.end_date else None,
            provision=[
                {
                    "type": "deny",
                    "code": [{"text": "Resuscitation"}],
                    "actor": [{
                        "role": {"text": "Patient"},
                        "reference": {"reference": f"Patient/{self.patient_id}"}
                    }]
                }
            ]
        )

        # Create the file path
        filename = "consent_" + str(self.identifier.replace(".", ""))
        patient_filename = self.patient_name.replace(" ", "_") + "_" + str(self.patient_id)
        consent_fhire_resource = f"{filename}_{patient_filename}.json"
        full_path = os.path.join(filepath, consent_fhire_resource)

        # Serialize the resource to JSON
        with open(full_path, "w") as file:
            file.write(consent_resource.json(indent=4))
