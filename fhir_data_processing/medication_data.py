import json
import os

from fhir.resources.coding import Coding
from fhir.resources.identifier import Identifier
from fhir.resources.medication import Medication
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.organization import Organization
from fhir.resources.ratio import Ratio
from fhir.resources.quantity import Quantity


class MedicationData:
    def __init__(self):
        self.identifier = None  # Unique identifier for the medication
        self.code = None  # Medication code (e.g., concept code from SNOMED CT)
        self.dose = None  # Dosage details (still a class variable, but unused)
        self.manufacturer = None  # Manufacturer details
        self.ingredients = None  # List of ingredients with quantities

    def create_fhir(self):
        from fhir.resources.codeablereference import CodeableReference

        # Create the base Medication resource
        medication = Medication.construct(
            resourceType="Medication",
            identifier=[
                Identifier.construct(
                    system="http://example.org/fhir/identifier",
                    value=self.identifier,
                )
            ] if self.identifier else None,
            # Add the medication code as a CodeableConcept with a hardcoded system
            code=CodeableConcept.construct(
                coding=[
                    Coding.construct(
                        system="http://snomed.info/sct",  # Hardcoded SNOMED CT system
                        code=self.code,
                    )
                ]
            ) if self.code else None,
        )

        # Add manufacturer, if present
        if self.manufacturer:
            manufacturer = Organization.construct(
                resourceType="Organization",
                id="organization1",
                name=self.manufacturer,
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
                    ) if "quantity" in ingredient and ingredient["quantity"] else None,
                }
                for ingredient in self.ingredients
            ]

        # Convert to JSON dictionary
        return medication.json()

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

        # Extract the medication code
        self.code = None
        if medication.code and medication.code.coding:
            coding = medication.code.coding[0]
            self.code = coding.code

        # Extract manufacturer from 'contained'
        self.manufacturer = None
        if medication.contained:
            for contained in medication.contained:
                if contained.__resource_type__ == "Organization":
                    self.manufacturer = contained.name if hasattr(contained, "name") else None
                    break

        # Handle ingredients
        self.ingredients = []
        if medication.ingredient:
            for ingredient in medication.ingredient:
                ingredient_details = {
                    "item": ingredient.item.concept.text
                    if ingredient.item and ingredient.item.concept and ingredient.item.concept.text else None,
                    "quantity": f"{ingredient.strengthRatio.numerator.value} {ingredient.strengthRatio.numerator.code}"
                    if ingredient.strengthRatio and ingredient.strengthRatio.numerator else None,
                }
                self.ingredients.append(ingredient_details)

    def create_fhir_inFilesystem(self, filepath):
        # Create FHIR Medication resource
        medication_resource = Medication(
            identifier=[
                {"system": "http://example.org/fhir/identifier", "value": self.identifier}
            ] if self.identifier else None,
            # Add the medication code with hardcoded system
            code=CodeableConcept(
                coding=[
                    {
                        "system": "http://snomed.info/sct",  # Hardcoded SNOMED CT system
                        "code": self.code,
                    }
                ]
            ) if self.code else None,
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
        filename = self.code.replace(" ", "_") + "_" + str(self.identifier.replace(".", ""))
        medication_fhire_resource = f"medication_{filename}.json"
        full_path = os.path.join(filepath, medication_fhire_resource)

        # Serialize the resource to JSON
        with open(full_path, "w") as file:
            file.write(medication_resource.json(indent=4))
