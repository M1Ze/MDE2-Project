import requests
import json

import db_models
# from app import app

FHIR_SERVER_URL = "http://localhost:8080/fhir"



def get_resource(resource_type, resource_id):
    """
    Fetch a resource of any type from the FHIR server.

    :param resource_type: Type of the FHIR resource (e.g., 'Patient', 'Medication', etc.)
    :param resource_id: ID of the resource to fetch
    :return: JSON response if successful, None otherwise
    """
    try:
        url = f"{FHIR_SERVER_URL}/{resource_type}/{resource_id}"
        response = requests.get(url, headers={"Accept": "application/fhir+json"})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching {resource_type} with ID {resource_id}: {e}")
        return None


def save_resource(resource_type, resource_data):
    """
    Save a resource of any type to the FHIR server.

    :param resource_type: Type of the FHIR resource (e.g., 'Patient', 'Medication', etc.)
    :param resource_data: JSON object of the resource to save
    :return: FHIR ID of the created resource if successful, None otherwise
    """
    try:
        url = f"{FHIR_SERVER_URL}/{resource_type}"
        response = requests.post(
            url,
            json=resource_data,
            headers={"Content-Type": "application/fhir+json"}
        )
        response.raise_for_status()
        fhir_id = response.json().get("id")
        print(f"Saved {resource_type}, FHIR ID: {fhir_id}")
        if not fhir_id:
            raise ValueError("FHIR server did not return an ID")
        return fhir_id
    except requests.exceptions.RequestException as e:
        print(f"Error saving {resource_type} to FHIR server: {str(e)}")
        return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None


def get_patient_data(fhir_id):
    try:
        response = requests.get(f"{FHIR_SERVER_URL}/Patient/{fhir_id}", headers={"Accept": "application/fhir+json"})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching patient: {e}")
        return None


def save_patient_data_fhir_server(fhir_patient):
    try:
        response = requests.post(
            "http://localhost:8080/fhir/Patient",
            json=fhir_patient,
            headers={"Content-Type": "application/fhir+json"}
        )
        response.raise_for_status()
        fhir_id = response.json().get('id')
        print(f"FHIR ID: {fhir_id}")
        if not fhir_id:
            raise ValueError("FHIR server did not return an ID")
    except requests.exceptions.RequestException as e:
        print(f"FHIR Server Error: {str(e)}")
        return None
    except Exception as e:
        print(f"Error saving patient data to FHIR server: {str(e)}")
        return None
    return fhir_id



if __name__ == "__main__":
    # Wrap the database query logic inside the app context
    with app.app_context():
        patient = db_models.Patient.query.filter_by(id=1).first()

        health_records = db_models.HealthData.query.filter_by(patient_id=patient.id).all()
        serialized_health_data = [
            {
                "data": json.loads(record.h_data)  # Deserialize JSON field
            }
            for record in health_records
        ]

        # Iterate over each health record and save it to the FHIR server
        for record in serialized_health_data:
            resource_data = record.get("data", {})

            # Ensure resource_data has "resourceType" to proceed
            resource_type = resource_data.get("resourceType")
            if not resource_type:
                print("Skipping resource: Missing 'resourceType'")
                continue

            # Save the resource to the FHIR server and handle the result
            fhir_id = save_resource(resource_type, resource_data)
            if fhir_id:
                print(f"Successfully saved {resource_type} with FHIR ID: {fhir_id}")
            else:
                print(f"Failed to save {resource_type}: Check logs for errors.")


