document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('token');

    if (token) {
        fetch('/getPatientInformation', {
            method: 'GET',
            headers: {
                'Authorization': 'Bearer ' + token
            }
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    populateFormFields(data.patient); // Fill in data from the patient object
                    populateHealthFields(data.health_data || {}); // Fill in medical/health data
                } else {
                    console.error('Error fetching patient data:', data.message);
                    alert('Could not fetch patient information. Please log in again.');
                    localStorage.removeItem('token');
                    window.location.href = '/login'; // Redirect to login page
                }
            })
            .catch(error => {
                console.error('Error fetching patient data:', error);
                alert('An error occurred. Please try again later.');
            });
    }

    function populateFormFields(patient) {
        console.log("Patient data received from backend:", patient);
        const fieldMap = {
            full_name: {
                selector: '#full_name',
                value: () => {

                    return `${patient.name}`;
                }
            },
            email: {
                selector: '#email',
                value: () => {
                    return `${patient.email}`;
                }
            },
            telephone: { // Fixed mismatch
                selector: '#telephone',
                value: () => {
                    return `${patient.phone}`;
                    ;
                }
            },
            birthdate: {
                selector: '#birthdate',
                value: () => {
                    return formatDate(patient.birthdate);
                }
            },
            gender: {
                selector: '#gender',
                value: () => capitalize(patient.gender || 'N/A')
            },
            social_security_number: {
                selector: '#social_security_number',
                value: () => {
                    return `${patient.identifier}`;
                }
            },
            address: {
                selector: '#address',
                value: () => {
                    return `${patient.address.split(',')[0] || 'N/A'}`;
                }
            },
            city_state_zip: {
                selector: '#city_state_zip',
                value: () => {
                    return `${patient.address.split(',')[1] + patient.address.split(',')[2] + patient.address.split(',')[3] || 'N/A'}`;
                }
            },
            emergency_contact_name: { // Fixed mismatch
                selector: '#emergency_contact_name',
                value: () => {
                    return `${patient.contacts[0].name}`
                }
            },
            emergency_contact_telephone: {
                selector: '#emergency_contact_telephone',
                value: () => {
                    return `${patient.contacts[0].phone}`
                }
            }
        };

        for (const key in fieldMap) {
            const {selector, value} = fieldMap[key];
            const element = document.querySelector(selector);
            if (element) {
                element.textContent = value();
            }
        }
    }

    function populateHealthFields(healthData) {
        console.log("Health data received from backend:", healthData);

        // Check if healthData is an array
        if (!Array.isArray(healthData)) {
            console.warn("healthData is not an array. Attempting to convert...");
            console.log("Actual healthData structure before conversion:", healthData); // Log the raw health data

            // Attempt to convert
            healthData = Object.values(healthData);

            if (!Array.isArray(healthData)) {
                console.error("Unable to convert healthData to array:", healthData); // Log the failed result
                alert("An error occurred while processing health data.");
                return; // Exit in case of invalid data
            }
        }

        // Define supported medications
        const supportedMedications = ['Aspirin', 'Ibuprofen', 'Paracetamol', 'Amoxicillin', 'Ciprofloxacin'];


        // Iterate over each health record
        healthData.forEach((record) => {
            console.log("Processing record:", record);

            // Check if the record is for 'Consent' (DNR)
            if (record.data?.resourceType === 'Consent') {
                console.log("DNR consent found in record:", record);

                // Show the DNR banner
                const dnrBanner = document.getElementById('dnr-banner');
                if (dnrBanner) dnrBanner.style.display = 'block'; // Make the banner visible
            }

            // Für den Typ "Medication" den Medikamentennamen hinzufügen
            if (record.data?.resourceType === 'Medication') {
                const medicationName = record.type; // Der Name steht in record.type
                if (medicationName) {
                    addMedication(medicationName); // Aufruf der Funktion, um Medikamente hinzuzufügen
                } else {
                    console.warn(`Medication record missing type:`, record);
                }
            }

            if (record.type === 'Height') {
                console.log("Height record found:", record); // Log the entire height record

                if (record.data?.valueQuantity) {
                    const value = record.data.valueQuantity.value;
                    const unit = record.data.valueQuantity.unit || 'cm'; // Default to 'cm' if unit is missing

                    console.log("Height value:", value, "Unit:", unit); // Log the extracted height value

                    // Now populate the height field in the DOM
                    const heightField = document.getElementById('height');
                    if (heightField) heightField.textContent = `${value} ${unit}`;
                } else {
                    console.warn("No valueQuantity found in the height record:", record);
                }
            }
            if (record.type === 'Weight') {
                console.log("Weight record found:", record); // Log the entire weight record

                if (record.data?.valueQuantity) {
                    const value = record.data.valueQuantity.value;
                    const unit = record.data.valueQuantity.unit || 'kg'; // Default to 'kg' if unit is missing

                    console.log("Weight value:", value, "Unit:", unit); // Log the extracted weight value

                    // Now populate the weight field in the DOM
                    const weightField = document.getElementById('weight');
                    if (weightField) weightField.textContent = `${value} ${unit}`;
                } else {
                    console.warn("No valueQuantity found in the weight record:", record);
                }
            }
            if (record.type === 'Blood Type') {
                console.log("Blood Type record found:", record); // Log the blood type record

                let bloodType = record.data?.valueString;
                if (bloodType) {
                    console.log("Blood type value found:", bloodType);

                    // Store blood type value for later use
                    document.getElementById('blood_type').dataset.bloodType = bloodType;
                } else {
                    console.warn("No blood type value found in Blood Type record:", record);
                }
            }

            if (record.type === 'Rhesus Factor') {
                console.log("Rhesus Factor record found:", record); // Log the rhesus factor record

                let rhesusFactor = record.data?.valueString.toLowerCase();
                rhesusFactor = rhesusFactor === 'positive' ? ' +' : rhesusFactor === 'negative' ? ' -' : null;

                if (rhesusFactor) {
                    console.log("Rhesus factor value found:", rhesusFactor);

                    // Retrieve previously stored blood type and combine it with rhesus factor for display
                    const bloodTypeElement = document.getElementById('blood_type');
                    const bloodType = bloodTypeElement.dataset.bloodType || ''; // Get stored blood type or use empty string

                    bloodTypeElement.textContent = `${bloodType}${rhesusFactor}`; // Display blood type with rhesus factor
                } else {
                    console.warn("No valid Rhesus Factor value found in Rhesus Factor record:", record);
                }
            }
            if (record.type === 'Cardiac pacemaker (physical object)') {
                console.log("Condition record found: Pacemaker"); // Log condition

                // Add "Pacemaker" to the list of conditions
                addCondition('Pacemaker');
            } else if (record.type === 'Hearing aid (physical object)') {
                console.log("Condition record found: Hearing Aids"); // Log condition

                // Add "Hearing Aids" to the list of conditions
                addCondition('Hearing Aids');
            } else if (record.type === 'Hypertension (disorder)') {
                console.log("Condition record found: Hypertension"); // Log condition

                // Add "Hypertension" to the list of conditions
                addCondition('Hypertension');
            } else if (record.type === 'Diabetes mellitus (disorder)') {
                console.log("Condition record found: Diabetes"); // Log condition

                // Add "Diabetes" to the list of conditions
                addCondition('Diabetes');
            } else if (record.type === 'Asthma (disorder)') {
                console.log("Condition record found: Asthma"); // Log condition

                // Add "Asthma" to the list of conditions
                addCondition('Asthma');
            }

            if (record.type === 'Peanut') {
                console.log("Allergy record found: Peanut"); // Log allergy
                addAllergy('Peanut');
            } else if (record.type === 'Lactose') {
                console.log("Intolerance record found: Lactose"); // Log intolerance
                addAllergy('Lactose');
            } else if (record.type === 'Penicillin') {
                console.log("Allergy record found: Penicillin"); // Log allergy
                addAllergy('Penicillin');
            } else if (record.type === 'Soy') {
                console.log("Allergy record found: Soy"); // Log allergy
                addAllergy('Soy');
            } else if (record.type === 'Shellfish') {
                console.log("Allergy record found: Shellfish"); // Log allergy
                addAllergy('Shellfish');
            }

        });
    }

    function addCondition(condition) {
        const conditionElement = document.getElementById('conditions'); // Retrieve the conditions element
        if (!conditionElement) {
            console.warn("Conditions element not found in the DOM.");
            return;
        }

        // Get the current list of conditions
        const existingConditions = conditionElement.textContent.trim();

        // Append the new condition to the list if it's not already present
        if (!existingConditions.includes(condition)) {
            conditionElement.textContent = existingConditions
                ? `${existingConditions}, ${condition}` // If there are already conditions, add the new one with a comma
                : condition; // If there are no conditions, set the first one
        }
    }

    function addAllergy(allergy) {
        const allergyElement = document.getElementById('allergies'); // Find the allergies element in the DOM
        if (!allergyElement) {
            console.warn("Allergies element not found in the DOM.");
            return;
        }

        // Get the current list of allergies
        const existingAllergies = allergyElement.textContent.trim();

        // Append the new allergy if it's not already in the list
        if (!existingAllergies.includes(allergy)) {
            allergyElement.textContent = existingAllergies
                ? `${existingAllergies}, ${allergy}` // Add with a comma if there's an existing list
                : allergy; // Add the first allergy
        }
    }

    function addMedication(medication) {
        const medicationElement = document.getElementById('medications'); // HTML-Element für Medikamente
        if (!medicationElement) {
            console.warn("Medications element not found in the DOM.");
            return;
        }

        // Vorhandene Medikamentenliste abrufen
        const existingMedications = medicationElement.textContent.trim();

        // Neues Medikament hinzufügen, wenn nicht bereits in der Liste
        if (!existingMedications.includes(medication)) {
            medicationElement.textContent = existingMedications
                ? `${existingMedications}, ${medication}` // Mit Komma hinzufügen
                : medication; // Ersten Eintrag setzen
        }
    }


    function formatDate(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        if (isNaN(date)) return 'Invalid Date';
        return date.toISOString().split('T')[0];
    }

    function capitalize(str) {
        if (!str || typeof str !== 'string') return 'N/A';
        return str.charAt(0).toUpperCase() + str.slice(1);
    }
});

