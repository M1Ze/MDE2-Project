from fhir.resources.medication import Medication as FHIRMedication

class MedicationData:
    def __init__(self):
        self.identifier = ""
        self.name = ""  # Human-readable name of the medication
        self.dose_form = ""  # Dosage form (e.g., tablet, capsule)
        self.manufacturer = ""  # Manufacturer details
        self.ingredients = []  # List of ingredients with quantities
        self.patient_id = ""  # Patient ID to link the medication
        self.patient_name = ""  # Patient Name for display purposes

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

        self.dose_form = medication.doseForm.coding[0].display if medication.doseForm and medication.doseForm.coding else None

        # Extract manufacturer from 'contained'
        if medication.contained:
            for contained in medication.contained:
                if contained.__resource_type__ == "Organization":
                    self.manufacturer = contained.name if hasattr(contained, "name") else None
                    break

        # Handle ingredients
        if medication.ingredient:
            for ingredient in medication.ingredient:
                ingredient_details = {
                    "item": ingredient.item.concept.text if ingredient.item and ingredient.item.concept and ingredient.item.concept.text else None,
                    "quantity": f"{ingredient.strengthRatio.numerator.value} {ingredient.strengthRatio.numerator.code}" if ingredient.strengthRatio and ingredient.strengthRatio.numerator else None,
                }
                self.ingredients.append(ingredient_details)