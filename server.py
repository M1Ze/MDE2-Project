import socket
import json

# Define the JSON response
response_json = {
    "resourceType": "Observation",
    "id": "bloodgroup",
    "text": {
        "status": "generated",
        "div": """<div xmlns="http://www.w3.org/1999/xhtml">
        <p><b>Generated Narrative: Observation</b><a name="bloodgroup"> </a></p>
        <div style="display: inline-block; background-color: #d9e0e7; padding: 6px; margin: 4px; 
        border: 1px solid #8da1b4; border-radius: 5px; line-height: 60%">
        <p style="margin-bottom: 0px">Resource Observation "bloodgroup" </p></div>
        <p><b>status</b>: final</p><p><b>category</b>: Laboratory 
        <span style="background: LightGoldenRodYellow; margin: 4px; border: 1px solid khaki"> 
        (<a href="http://terminology.hl7.org/5.1.0/CodeSystem-observation-category.html">Observation Category Codes</a>#laboratory)
        </span></p><p><b>code</b>: Blood Group 
        <span style="background: LightGoldenRodYellow; margin: 4px; border: 1px solid khaki"> 
        (<a href="https://loinc.org/">LOINC</a>#883-9 "ABO group [Type] in Blood")
        </span></p><p><b>subject</b>: <a href="broken-link.html">Patient/infant</a></p>
        <p><b>effective</b>: 2018-03-11T16:07:54Z</p><p><b>value</b>: A 
        <span style="background: LightGoldenRodYellow; margin: 4px; border: 1px solid khaki"> 
        (<a href="https://browser.ihtsdotools.org/">SNOMED CT</a>#112144000 "Blood group A (finding)")
        </span></p></div>"""
    },
    "status": "final",
    "category": [{
        "coding": [{
            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
            "code": "laboratory",
            "display": "Laboratory"
        }],
        "text": "Laboratory"
    }],
    "code": {
        "coding": [{
            "system": "http://loinc.org",
            "code": "883-9",
            "display": "ABO group [Type] in Blood"
        }],
        "text": "Blood Group"
    },
    "subject": {
        "reference": "Patient/infant"
    },
    "effectiveDateTime": "2018-03-11T16:07:54+00:00",
    "valueCodeableConcept": {
        "coding": [{
            "system": "http://snomed.info/sct",
            "code": "112144000",
            "display": "Blood group A (finding)"
        }],
        "text": "A"
    }
}

# Convert JSON to a string
json_string = json.dumps(response_json, indent=2)


# Start the socket server
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('', 8080)  # Listen on all interfaces, port 8080
    server_socket.bind(server_address)
    server_socket.listen(5)
    print("Server started. Listening on port 8080...")

    while True:
        # Wait for a connection
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address}")

        # Read the request
        request = client_socket.recv(1024).decode('utf-8')
        print("Request received:")
        print(request)

        # Check if it's a GET request
        if "GET" in request:
            # Create the HTTP response
            http_response = f"""\
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: {len(json_string)}

{json_string}"""
            # Send the response
            client_socket.sendall(http_response.encode('utf-8'))

        # Close the connection
        client_socket.close()


if __name__ == "__main__":
    start_server()
