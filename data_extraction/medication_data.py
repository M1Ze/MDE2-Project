import os

from fhir.resources.medication import Medication
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.organization import Organization
from fhir.resources.ratio import Ratio
from fhir.resources.quantity import Quantity


class MedicationData:
    def __init__(self):
        self.identifier = ""
        self.name = ""  # Human-readable name of the medication
        self.dose_form = ""  # Dosage form (e.g., tablet, capsule)
        self.manufacturer = ""  # Manufacturer details
        self.ingredients = []  # List of ingredients with quantities
        self.patient_id = ""  # Patient ID to link the medication
        self.patient_name = ""  # Patient Name for display purposes

    def extract_data(self, filepath, json_string):
        # Read JSON file and parse it into a FHIR Medication resource
        if filepath is not None:
            with open(filepath, "r") as file:
                json_string = file.read()
            medication = Medication.parse_raw(json_string)
        else:
            medication = Medication.parse_raw(json_string)

        # Extract key attributes
        self.identifier = next(
            (identifier.value for identifier in medication.identifier), None
        ) if medication.identifier else None

        self.name = medication.code.text if medication.code and medication.code.text else None

        self.dose_form = medication.doseForm.coding[
            0].display if medication.doseForm and medication.doseForm.coding else None

        # Extract manufacturer from 'contained'
        if medication.contained:
            for contained in medication.contained:
                if contained.resource_type == "Organization":
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

    def create_fhir(self):
        from fhir.resources.codeablereference import CodeableReference

        # Create the base Medication resource
        medication = Medication.construct(
            resourceType="Medication",
            identifier=[{
                "system": "http://example.org/fhir/identifier",
                "value": self.identifier
            }],
            code=CodeableConcept.construct(text=self.name),
            doseForm=CodeableConcept.construct(coding=[{"display": self.dose_form}]),
        )

        # Add manufacturer, if present
        if self.manufacturer:
            manufacturer = Organization.construct(
                resourceType="Organization",
                id="organization1",
                name=self.manufacturer
            )
            medication.contained = [manufacturer]

        # Add ingredients, if present
        if self.ingredients:
            medication.ingredient = [
                {
                    "item": CodeableReference.construct(
                        concept=CodeableConcept.construct(text=ingredient["item"])
                    ),
                    "strengthRatio": Ratio.construct(
                        numerator=Quantity.construct(
                            value=float(ingredient["quantity"].split()[0]),
                            code=ingredient["quantity"].split()[1],
                        )
                    ),
                }
                for ingredient in self.ingredients
            ]

        # Convert to JSON dictionary
        return medication.json()

    def create_fhir_inFilesystem(self, filepath, patient_folder):
    # Create FHIR Medication resource
        medication_resource = Medication(
            identifier=[
                {"system": "http://example.org/fhir/identifier", "value": self.identifier}
            ] if self.identifier else None,
            code=CodeableConcept(
                text=self.name
            ) if self.name else None,
            doseForm=CodeableConcept(
                coding=[{"display": self.dose_form}]
            ) if self.dose_form else None,
            contained=[
                Organization(
                    id="organization1",
                    name=self.manufacturer
                )
            ] if self.manufacturer else None,
            ingredient=[
                {
                    "item": {"concept": CodeableConcept(
                        text=ingredient["item"]
                    )} if ingredient["item"] else None,
                    "strengthRatio": Ratio(
                        numerator=Quantity(
                            value=float(ingredient["quantity"].split(" ")[0]),
                            code=ingredient["quantity"].split(" ")[1],
                        )
                    ) if ingredient["quantity"] else None,
                }
                for ingredient in self.ingredients
            ] if self.ingredients else None,
        )

        # Create the file path
        filename = self.name.replace(" ", "_") + "_" + str(self.identifier.replace(".", ""))
        patient_filename = self.patient_name.replace(" ", "_") + "_" + str(self.patient_id)
        medication_fhire_resource = f"medication_{filename}_{patient_filename}.json"
        full_path = os.path.join(filepath, medication_fhire_resource)

        # Serialize the resource to JSON
        with open(full_path, "w") as file:
            file.write(medication_resource.json(indent=4))



