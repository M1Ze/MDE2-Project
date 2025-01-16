import json
import os
from fhir.resources.observation import Observation
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.quantity import Quantity

class ObservationData:
    def __init__(self):
        self.identifier = ""
        self.type = "" #Type of observation
        self.data_aqu_datetime = ""
        self.data = "" # String with value + unit


    def extract_data(self, filepath, json_string):
        # Parse the JSON string or load it from the file to create an Observation object
        if filepath is not None:
            with open(filepath, "r") as file:
                json_string = file.read()

        observation = Observation.parse_raw(json_string)

        # Extract identifier
        self.identifier = (
            next((identifier.value for identifier in observation.identifier), None)
            if observation.identifier
            else None
        )

        # Extract type from Observation.code (FHIR standard)
        self.type = observation.code.text if observation.code else None

        # Extract the observation's effective date and time
        self.data_aqu_datetime = observation.effectiveDateTime if observation.effectiveDateTime else None

        # Extract value from the Observation.resource, e.g., valueQuantity, valueString, etc.
        if observation.valueQuantity:
            self.data = f"{observation.valueQuantity.value} {observation.valueQuantity.unit}"
        elif observation.valueCodeableConcept and observation.valueCodeableConcept.text:
            self.data = observation.valueCodeableConcept.text
        elif observation.valueCodeableConcept and observation.valueCodeableConcept.coding:
            self.data = observation.valueCodeableConcept.coding[0].display
        elif observation.valueString:
            self.data = observation.valueString
        elif observation.valueBoolean is not None:
            self.data = str(observation.valueBoolean)  # Convert boolean to string
        elif observation.valueInteger is not None:
            self.data = str(observation.valueInteger)  # Convert integer to string
        else:
            self.data = None


    def create_fhir(self):
        # Ensure mandatory fields (like `code`) are not empty or missing
        if not self.type:
            self.type = "Default Observation Type"  # Default to prevent validation errors

        # Use the Observation() class to generate the FHIR object
        fhir_observation = Observation.construct(
            resourceType="Observation",
            identifier=[
                {
                    "system": "http://example.org/fhir/identifier",
                    "value": self.identifier,
                }
            ]
            if self.identifier
            else None,
            status="final",
            code=CodeableConcept(
                text=self.type,
                coding=[{"display": self.type}]
            ),  # Map 'type' to 'code'
            effectiveDateTime=self.data_aqu_datetime
            if self.data_aqu_datetime
            else None,
            valueQuantity={
                "value": self._parse_value(),
                "unit": self._parse_unit(),
            }
            if self.data and self._parse_value() is not None and self._parse_unit() is not None
            else None,
        )
        return fhir_observation.json(indent=4)



    def _parse_value(self):
        # Parse the numerical value from the 'data' field (e.g., "120 mmHg").
        if self.data and isinstance(self.data, str) and ' ' in self.data:
            return float(self.data.split()[0])
        return None

    def _parse_unit(self):
        # Parse the unit from the 'data' field (e.g., "120 mmHg").
        if self.data and isinstance(self.data, str) and ' ' in self.data:
            return self.data.split()[1]
        return None

    def create_fhir_inFilesystem(self, filepath, patient_folder):


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
