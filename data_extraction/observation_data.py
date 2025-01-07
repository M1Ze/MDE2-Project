from fhir.resources.observation import Observation

class ObservationData:
    def __init__(self):
        self.identifier = ""
        self.type = "" #Type of observation
        self.data_aqu_datetime = ""
        self.data = "" # String with value + unit

    def extract_data(self, filepath):
        # json file einlesen um FHIR ressource draus zu machen
        with open(filepath, "r") as file:
            json_string = file.read()
        observation = Observation.parse_raw(json_string)

        self.identifier = next(
            (identifier.value for identifier in observation.identifier), None
        ) if observation.identifier else None

        self.type = observation.code.coding[0].display if observation.code else None

        self.data_aqu_datetime = observation.effectiveDateTime if observation.effectiveDateTime else None

        if hasattr(observation, "valueQuantity") and observation.valueQuantity:
            self.data = f"{observation.valueQuantity.value} {observation.valueQuantity.unit}"
        elif hasattr(observation, "valueCodeableConcept") and observation.valueCodeableConcept:
            self.data = (
                observation.valueCodeableConcept.text
                if observation.valueCodeableConcept.text
                else observation.valueCodeableConcept.coding[0].display
                if observation.valueCodeableConcept.coding
                else None
            )
        elif hasattr(observation, "valueString") and observation.valueString:
            self.data = observation.valueString
        elif hasattr(observation, "valueBoolean") and observation.valueBoolean is not None:
            self.data = str(observation.valueBoolean)  # Convert boolean to string
        elif hasattr(observation, "valueInteger") and observation.valueInteger is not None:
            self.data = str(observation.valueInteger)  # Convert integer to string
        else:
            self.data = None

    def create_fhir(self, filepath, patient_folder):
        import os
        from fhir.resources.observation import Observation
        from fhir.resources.codeableconcept import CodeableConcept
        from fhir.resources.quantity import Quantity

        # Ensure the patient folder exists
        os.makedirs(patient_folder, exist_ok=True)

        # Create FHIR Observation resource
        observation_resource = Observation(
            identifier=[
                {"system": "http://example.org/fhir/identifier", "value": self.identifier}
            ] if self.identifier else None,
            status="final",  # Assuming "final" for this example
            code=CodeableConcept(
                coding=[{"display": self.type}]
            ) if self.type else None,
            subject={"reference": f"Patient/{self.patient_id}"} if self.patient_id else None,
            effectiveDateTime=self.data_aqu_datetime if self.data_aqu_datetime else None,
            valueQuantity=Quantity(
                value=float(self.data.split(" ")[0]),
                unit=self.data.split(" ")[1]
            ) if self.data and " " in self.data else None,
            valueString=self.data if self.data and not " " in self.data else None
        )

        # Create the file path
        filename = self.type.replace(" ", "_") + "_" + str(self.identifier.replace(".", ""))
        patient_filename = self.patient_name.replace(" ", "_") + "_" + str(self.patient_id)
        observation_fhire_resource = f"observation_{filename}_{patient_filename}.json"
        full_path = os.path.join(filepath, observation_fhire_resource)

        # Serialize the resource to JSON
        with open(full_path, "w") as file:
            file.write(observation_resource.json(indent=4))
