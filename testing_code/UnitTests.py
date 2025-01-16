import unittest

from data_extraction.patient_data import PatientData
from data_extraction.medication_data import MedicationData
from data_extraction.observation_data import ObservationData
from data_extraction.care_plan_data import CarePlanData
from data_extraction.allergy_intolerance_data import AllergyIntoleranceData
from data_extraction.consent_data import ConsentData


class TestFHIRDataClasses(unittest.TestCase):

    def test_patient_data_create_fhir(self):
        patient = PatientData()
        patient.name = "John Doe"
        patient.birthdate = "01.01.1980"
        patient.gender = "male"
        patient.address = "789 Main St, City, State, 1357"
        patient.phone = "+123456789"
        patient.email = "johndoe@example.com"
        patient.identifier = "1111010180"
        patient.contacts = [
            {"name": "Jane Doe", "phone": "+987654321"},
            {"name": "Emily Smith", "phone": "+192837465"}
        ]

        json_string = patient.create_fhir()

        self.assertTrue(json_string)
        self.assertIn('identifier', json_string)
        self.assertIn('contact', json_string)

    def test_patient_data_extract_data(self):
        patient = PatientData()
        patient.name = "John Doe"
        patient.birthdate = "01.01.1980"
        patient.gender = "male"
        patient.address = "789 Main St, City, State, 1357"
        patient.phone = "+123456789"
        patient.email = "johndoe@example.com"
        patient.identifier = "1111010180"
        patient.contacts = [
            {"name": "Jane Doe", "phone": "+987654321"},
            {"name": "Emily Smith", "phone": "+192837465"}
        ]

        json_string = patient.create_fhir()
        new_patient = PatientData()
        new_patient.extract_data(None, json_string)

        self.assertEqual(new_patient.identifier, "1111010180")
        self.assertEqual(len(new_patient.contacts), 2)

    def test_patient_data_edge_case_no_contacts(self):
        patient = PatientData()
        patient.identifier = "2222020220"

        json_string = patient.create_fhir()
        new_patient = PatientData()
        new_patient.extract_data(None, json_string)

        self.assertEqual(new_patient.identifier, "2222020220")
        self.assertEqual(len(new_patient.contacts), 0)

    def test_observation_data_create_fhir(self):
        observation = ObservationData()
        observation.identifier = "obs-67890"
        observation.type = "Blood Pressure"
        observation.data_aqu_datetime = "2025-01-02T14:30:00Z"
        observation.data = "120 mmHg"

        json_string = observation.create_fhir()

        self.assertTrue(json_string)
        self.assertIn('identifier', json_string)
        self.assertIn('type', json_string)

    def test_observation_data_extract_data(self):
        observation = ObservationData()
        observation.identifier = "obs-67890"
        observation.type = "Blood Pressure"
        observation.data_aqu_datetime = "2025-01-02T14:30:00Z"
        observation.data = "120 mmHg"

        json_string = observation.create_fhir()
        new_observation = ObservationData()
        new_observation.extract_data(None, json_string)

        self.assertEqual(new_observation.identifier, "obs-67890")
        self.assertEqual(new_observation.type, "Blood Pressure")

    def test_observation_data_edge_case_empty_data(self):
        observation_empty = ObservationData()
        observation_empty.identifier = "obs-99999"

        json_string = observation_empty.create_fhir()
        new_observation = ObservationData()
        new_observation.extract_data(None, json_string)

        assert new_observation.identifier == "obs-99999"
        assert new_observation.data == None

    def test_medication_data_create_fhir(self):
        medication = MedicationData()
        medication.identifier = "med001"
        medication.name = "Ibuprofen"
        medication.dose_form = "Tablet"
        medication.manufacturer = "Generic Pharma Inc."
        medication.ingredients = [
            {"item": "Ibuprofen", "quantity": "200 mg"},
            {"item": "Inactive Ingredients", "quantity": "50 mg"},
        ]

        json_string = medication.create_fhir()

        self.assertTrue(json_string)  # Check if any JSON was generated
        self.assertIn('identifier', json_string)  # Ensure 'identifier' key is present
        self.assertIn('ingredient', json_string)  # Use the correct key name 'ingredient'

    def test_medication_data_extract_data(self):
        medication = MedicationData()
        medication.identifier = "med001"
        medication.name = "Ibuprofen"
        medication.dose_form = "Tablet"
        medication.manufacturer = "Generic Pharma Inc."
        medication.ingredients = [
            {"item": "Ibuprofen", "quantity": "200 mg"},
            {"item": "Inactive Ingredients", "quantity": "50 mg"},
        ]

        json_string = medication.create_fhir()
        new_medication = MedicationData()
        new_medication.extract_data(None, json_string)

        self.assertEqual(new_medication.identifier, "med001")
        self.assertEqual(new_medication.name, "Ibuprofen")

    def test_medication_data_edge_case_missing_manufacturer(self):
        medication_missing_manufacturer = MedicationData()
        medication_missing_manufacturer.identifier = "med002"
        medication_missing_manufacturer.name = "Aspirin"

        json_string = medication_missing_manufacturer.create_fhir()
        new_medication = MedicationData()
        new_medication.extract_data(None, json_string)

        self.assertEqual(new_medication.identifier, "med002")
        self.assertEqual(new_medication.manufacturer, None)

    def test_consent_data_create_fhir(self):
        consent = ConsentData()
        consent.identifier = "consent-12345"
        consent.patient_id = "1111010180"
        consent.status = "active"

        json_string = consent.create_fhir()

        self.assertTrue(json_string)
        self.assertIn('identifier', json_string)
        self.assertIn('status', json_string)

    def test_consent_data_extract_data(self):
        consent = ConsentData()
        consent.identifier = "consent-12345"
        consent.patient_id = "1111010180"
        consent.status = "active"

        json_string = consent.create_fhir()
        new_consent = ConsentData()
        new_consent.extract_data(None, json_string)

        self.assertEqual(new_consent.identifier, "consent-12345")
        self.assertEqual(new_consent.status, "active")

    def test_consent_data_edge_case_missing_status(self):
        consent_no_status = ConsentData()
        consent_no_status.identifier = "consent-99999"

        json_string = consent_no_status.create_fhir()
        new_consent = ConsentData()
        new_consent.extract_data(None, json_string)

        self.assertEqual(new_consent.identifier, "consent-99999")
        self.assertEqual(new_consent.status, None)

    def test_care_plan_data_create_fhir(self):
        careplan = CarePlanData()
        careplan.identifier = "careplan-12345"
        careplan.status = "active"
        careplan.intent = "order"
        careplan.title = "Diabetes Management Plan"
        careplan.period_start = "2025-01-01"
        careplan.period_end = "2025-12-31"
        careplan.category = ["Chronic Disease"]
        careplan.description = "Plan to manage diabetes."

        json_string = careplan.create_fhir()

        self.assertTrue(json_string)
        self.assertIn('identifier', json_string)
        self.assertIn('category', json_string)

    def test_care_plan_data_extract_data(self):
        careplan = CarePlanData()
        careplan.identifier = "careplan-12345"
        careplan.status = "active"
        careplan.intent = "order"
        careplan.title = "Diabetes Management Plan"
        careplan.period_start = "2025-01-01"
        careplan.period_end = "2025-12-31"
        careplan.category = ["Chronic Disease"]
        careplan.description = "Plan to manage diabetes."

        json_string = careplan.create_fhir()
        new_careplan = CarePlanData()
        new_careplan.extract_data(None, json_string)

        self.assertEqual(new_careplan.identifier, "careplan-12345")
        self.assertEqual(new_careplan.title, "Diabetes Management Plan")

    def test_care_plan_data_edge_case_missing_category(self):
        careplan_no_category = CarePlanData()
        careplan_no_category.identifier = "careplan-99999"

        json_string = careplan_no_category.create_fhir()
        new_careplan = CarePlanData()
        new_careplan.extract_data(None, json_string)

        self.assertEqual(new_careplan.identifier, "careplan-99999")
        self.assertEqual(len(new_careplan.category), 0)

    def test_allergy_data_create_fhir(self):
        allergy = AllergyIntoleranceData()
        allergy.identifier = "allergy001"
        allergy.clinical_status = "Active"
        allergy.verification_status = "Confirmed"
        allergy.allergy_type = "allergy"
        allergy.category = "food"
        allergy.code = "Cashew nuts"
        allergy.patient_id = "1111010180"
        allergy.patient_name = "John Doe"
        allergy.criticality = "high"

        json_string = allergy.create_fhir()

        self.assertTrue(json_string)
        self.assertIn('identifier', json_string)
        self.assertIn('criticality', json_string)

    def test_allergy_data_extract_data(self):
        allergy = AllergyIntoleranceData()
        allergy.identifier = "allergy001"
        allergy.clinical_status = "Active"
        allergy.verification_status = "Confirmed"
        allergy.allergy_type = "allergy"
        allergy.category = "food"
        allergy.code = "Cashew nuts"
        allergy.patient_id = "1111010180"
        allergy.patient_name = "John Doe"
        allergy.criticality = "high"

        json_string = allergy.create_fhir()
        new_allergy = AllergyIntoleranceData()
        new_allergy.extract_data(None, json_string)

        self.assertEqual(new_allergy.identifier, "allergy001")
        self.assertEqual(new_allergy.code, "Cashew nuts")

    def test_allergy_data_edge_case_missing_criticality(self):
        allergy_no_criticality = AllergyIntoleranceData()
        allergy_no_criticality.identifier = "allergy002"

        json_string = allergy_no_criticality.create_fhir()
        new_allergy = AllergyIntoleranceData()
        new_allergy.extract_data(None, json_string)

        self.assertEqual(new_allergy.identifier, "allergy002")
        self.assertEqual(new_allergy.criticality, None)


if __name__ == "__main__":
    unittest.main()
