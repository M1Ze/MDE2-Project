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