import json

class Medication:
    def __init__(self):
        self.name=""

    def extract_data(self, filepath):
        with open(filepath, "r") as file:
            json_string = file.read()

        medicationJson = json.loads(json_string)
        self.name = medicationJson.get("code").get("text") if medicationJson.get("code").get("text") else None