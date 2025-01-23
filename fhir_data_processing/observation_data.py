import datetime
import json
import os

from fhir.resources.coding import Coding
from fhir.resources.identifier import Identifier
from fhir.resources.observation import Observation
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.quantity import Quantity

class ObservationData:
    def __init__(self):
        self.identifier = None
        self.type = None #Type of observation
        self.data_aqu_datetime = None
        self.data = None # String with value + unit


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
        # Validate 'self.type' and use a default value if invalid
        if not self.type or not isinstance(self.type, str) or self.type.strip() == "":
            self.type = "Unknown Type"  # Setting a default value for 'type'

        # Create an Identifier object
        identifier = Identifier(
            system="http://example.org/fhir/identifier",
            value=self.identifier
        )

        # Create a CodeableConcept for the 'code' field
        codeable_concept = CodeableConcept(
            text=self.type,
            coding=[Coding(display=self.type)]  # Coding.display expects a valid non-empty string
        )

        # Handle empty or invalid 'self.data'
        data_value = self._parse_value()
        data_unit = self._parse_unit()

        value_quantity = None  # Initialize as None
        value_string = None
        if data_value is not None and data_unit is not None:
            # Create a Quantity object for valueQuantity
            value_quantity = Quantity(
                value=data_value,
                unit=data_unit
            )
        elif self.data is not None:
            value_string = self.data




        # Validate or transform effectiveDateTime into a valid ISO-8601 datetime
        if self.data_aqu_datetime:
            try:
                # Try to parse the datetime to ensure it's valid
                datetime.datetime.fromisoformat(self.data_aqu_datetime.replace("Z", "+00:00"))
            except ValueError:
                # If invalid, set it to a default value
                self.data_aqu_datetime = datetime.datetime.now().isoformat()
        else:
            # Assign a default value if no datetime is provided
            self.data_aqu_datetime = None

        # Using the fhir.resources Observation function
        observation_resource = Observation(
            resourceType="Observation",
            identifier=[identifier],
            status="final",
            code=codeable_concept,
            effectiveDateTime=self.data_aqu_datetime,
            valueQuantity=value_quantity,
            valueString= value_string  # Include only if valueQuantity is not None
        )

        # Return the JSON-encoded FHIR Observation resource
        return observation_resource.json(indent=4)

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

    def populate_from_dict(self, data):
        """
        Populate ObservationData from a dictionary.
        """
        self.identifier = data.get("identifier")
        self.type = data.get("type")
        self.data_aqu_datetime = data.get("data_aqu_datetime")
        # Assign data directly or leave unchanged if no value
        self.data = data.get("data")



