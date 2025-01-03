from fhir.resources.medication import Medication as FHIRMedication

class MedicationData:
    def __init__(self):
        self.identifier = ""
        self.name = ""  # Human-readable name of the medication
        self.form = ""  # Dosage form (e.g., tablet, capsule)
        self.manufacturer = ""  # Manufacturer details
        self.ingredients = []  # List of ingredients with quantities

    def extract_data(self, filepath):
        # Read JSON file and parse it into a FHIR Medication resource
        with open(filepath, "r") as file:
            json_string = file.read()
        medication = FHIRMedication.parse_raw(json_string)

        # Extract key attributes
        self.identifier = next(
            (identifier.value for identifier in medication.identifier), None
        ) if medication.identifier else None

        self.name = medication.code.text if medication.code and medication.code.text else None

        self.form = medication.form.coding[0].display if medication.form and medication.form.coding else None

        self.manufacturer = medication.manufacturer.display if medication.manufacturer else None

        if medication.ingredient:
            for ingredient in medication.ingredient:
                ingredient_details = {
                    "item": ingredient.itemCodeableConcept.text if ingredient.itemCodeableConcept and ingredient.itemCodeableConcept.text else None,
                    "quantity": f"{ingredient.strength.numerator.value} {ingredient.strength.numerator.unit}" if ingredient.strength and ingredient.strength.numerator else None,
                }
                self.ingredients.append(ingredient_details)
