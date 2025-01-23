// check_user.js

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
                    populateFormFields(data.patient); // Fill form fields with FHIR Patient resource data
                    populateHealthFields(data.health_data); // Populate health-related fields
                    setupDnrHandlers(dnrConfirmed);
                } else {
                    console.error('Error fetching patient data:', data.message);
                    alert('Could not fetch patient information. Please log in again.');
                    localStorage.removeItem('token');
                    window.location.href = '/login'; // Redirect to login
                }
            })
            .catch(error => {
                console.error('Error fetching patient data:', error);
                alert('An error occurred. Please try again later.');
            });
    }

    function populateFormFields(patient) {
        console.log("Patient data received from backend:", patient);

        // Adjusted field map to match the backend keys
        const fieldMap = {
            name: {
                selector: ['[name="given_name"]', '[name="last_name"]'],
                value: () => {
                    if (patient.name) {
                        const nameParts = patient.name.split(' ');
                        return [
                            nameParts.slice(0, -1).join(' ') || '', // Given name(s)
                            nameParts[nameParts.length - 1] || ''  // Last name
                        ];
                    }
                    return ['', ''];
                },
            },
            birthdate: {
                selector: '#inputBirthday',
                value: () => {
                    const date = new Date(patient.birthdate);
                    return date.toISOString().split('T')[0];
                }
            },
            gender: {
                selector: '#inputGender',
                value: () => patient.gender ? patient.gender.charAt(0).toUpperCase() + patient.gender.slice(1) : ''
            },
            email: {
                selector: '[name="email"]',
                value: patient.email || ''
            },
            phone: {
                selector: ['#inputCountryCode', '#inputPhonenumber'],
                value: () => {
                    const [countryCode, ...phoneNumber] = (patient.phone || '').split(' ');
                    return [countryCode || '', phoneNumber.join(' ') || ''];
                }
            },
            address: {
                selector: '#inputAddress',
                value: () => {
                    // Extract city from the address
                    const parts = patient.address.split(',');
                    return parts.length > 1 ? parts[0].trim() : '';
                }
            },
            postalCode: {
                selector: '#inputZip',
                value: () => {
                    // Extract postal code from the address
                    const parts = patient.address.split(',');
                    return parts[parts.length - 1]?.trim().split(' ')[0] || ''; // Extract ZIP
                }
            },
            city: {
                selector: '#inputCity',
                value: () => {
                    // Extract city from the address
                    const parts = patient.address.split(',');
                    return parts.length > 1 ? parts[1].trim() : '';
                }
            },
            state: {
                selector: '#inputState',
                value: () => {
                    // Extract state from the address
                    const parts = patient.address.split(',');
                    return parts.length > 2 ? parts[2].trim().split(' ')[0] : '';
                },
            },
            identifier: {
                selector: '[name="socialsecuritynumber"]',
                value: () => (patient.identifier ? patient.identifier.slice(0, 4) : '')
            },
        };

        // Populate form fields using the field map
        for (const [key, {selector, value}] of Object.entries(fieldMap)) {
            const resolvedValue = typeof value === 'function' ? value() : value;

            if (Array.isArray(selector) && Array.isArray(resolvedValue)) {
                selector.forEach((sel, index) => {
                    const element = document.querySelector(sel);
                    if (element) element.value = resolvedValue[index];
                });
            } else {
                const element = document.querySelector(selector);
                if (element) element.value = resolvedValue;
            }
        }

        // Populate contact fields
        if (patient.contacts && patient.contacts.length > 0) {
            const contact = patient.contacts[0]; // Use the first contact
            const contactGivenNameInput = document.querySelector('[name="contact_given_name"]');
            const contactLastNameInput = document.querySelector('[name="contact_last_name"]');
            const contactCountryCodeInput = document.querySelector('#inputContactCountryCode');
            const contactPhoneInput = document.querySelector('[name="contact_phone"]');

            if (contact) {
                // Extract given and last name from the contact's name
                const contactNameParts = (contact.name || '').split(' ');
                const contactGivenName = contactNameParts.slice(0, -1).join(' ');
                const contactLastName = contactNameParts[contactNameParts.length - 1];

                // Populate the contact fields
                if (contactGivenNameInput) contactGivenNameInput.value = contactGivenName || '';
                if (contactLastNameInput) contactLastNameInput.value = contactLastName || '';

                // Populate the contact's phone and country code
                const [contactCountryCode, ...contactPhoneParts] = (contact.phone || '').split(' ');
                if (contactCountryCodeInput) contactCountryCodeInput.value = contactCountryCode || '';
                if (contactPhoneInput) contactPhoneInput.value = contactPhoneParts.join(' ') || '';
            }
        }

        // Call setupPregnancySectionVisibility after fields are populated
        setupPregnancySectionVisibility();

    }

    function populateFormFields1(patient) {
        console.log("Patient data received from backend:", patient);

        // Adjusted field map to match the backend keys
        const fieldMap = {
            name: {
                selector: ['[name="given_name"]', '[name="last_name"]'],
                value: () => {
                    if (patient.name) {
                        const nameParts = patient.name.split(' ');
                        return [
                            nameParts.slice(0, -1).join(' ') || '', // Given name(s)
                            nameParts[nameParts.length - 1] || ''  // Last name
                        ];
                    }
                    return ['', ''];
                },
            },
            birthdate: {
                selector: '#inputBirthday',
                value: () => {
                    const date = new Date(patient.birthdate);
                    return date.toISOString().split('T')[0];
                }
            },
            gender: {
                selector: '#inputGender',
                value: () => patient.gender ? patient.gender.charAt(0).toUpperCase() + patient.gender.slice(1) : ''
            },
            email: {
                selector: '[name="email"]',
                value: patient.email || ''
            },
            phone: {
                selector: ['#inputCountryCode', '#inputPhonenumber'],
                value: () => {
                    const [countryCode, ...phoneNumber] = (patient.phone || '').split(' ');
                    return [countryCode || '', phoneNumber.join(' ') || ''];
                }
            },
            address: {
                selector: '#inputAddress',
                value: () => {
                    // Extract city from the address
                    const parts = patient.address.split(',');
                    return parts.length > 1 ? parts[0].trim() : '';
                }
            },
            postalCode: {
                selector: '#inputZip',
                value: () => {
                    // Extract postal code from the address
                    const parts = patient.address.split(',');
                    return parts[parts.length - 1]?.trim().split(' ')[0] || ''; // Extract ZIP
                }
            },
            city: {
                selector: '#inputCity',
                value: () => {
                    // Extract city from the address
                    const parts = patient.address.split(',');
                    return parts.length > 1 ? parts[1].trim() : '';
                }
            },
            state: {
                selector: '#inputState',
                value: () => {
                    // Extract state from the address
                    const parts = patient.address.split(',');
                    return parts.length > 2 ? parts[2].trim().split(' ')[0] : '';
                },
            },
            identifier: {
                selector: '[name="socialsecuritynumber"]',
                value: () => (patient.identifier ? patient.identifier.slice(0, 4) : '')
            },

        }

        // Populate form fields using the field map
        for (const [key, {selector, value}] of Object.entries(fieldMap)
            ) {
            const resolvedValue = typeof value === 'function' ? value() : value;

            if (Array.isArray(selector) && Array.isArray(resolvedValue)) {
                selector.forEach((sel, index) => {
                    const element = document.querySelector(sel);
                    if (element) element.value = resolvedValue[index];
                });
            } else {
                const element = document.querySelector(selector);
                if (element) element.value = resolvedValue;
            }
        }
        // Call setupPregnancySectionVisibility after fields are populated
        setupPregnancySectionVisibility();
    }

    function populateHealthFields(healthData) {
        console.log("Health data received from backend:", healthData);

        healthData.forEach(record => {
                console.log(`Processing record for type: ${record.type}`);
                console.log("Record data:", record.data);
                console.log("Record resource type:", record.identifier?.value());

                let dnrConfirmed = false; // Standardwert für DNR
                // Check for height
                if (record.type === 'Height' && record.data?.valueQuantity) {
                    console.log("Height value:", record.data.valueQuantity.value);
                    const heightField = document.querySelector('#inputHeight');
                    if (heightField) heightField.value = record.data.valueQuantity.value;

                    const heightUnitRadio = document.querySelector(`#height_${record.data.valueQuantity.unit?.toLowerCase()}`);
                    if (heightUnitRadio) heightUnitRadio.checked = true;
                }

                // Check for weight
                else if (record.type === 'Weight' && record.data?.valueQuantity) {
                    console.log("Weight value:", record.data.valueQuantity.value);
                    const weightField = document.querySelector('#inputWeight');
                    if (weightField) weightField.value = record.data.valueQuantity.value;

                    const weightUnitRadio = document.querySelector(`#weight_${record.data.valueQuantity.unit?.toLowerCase()}`);
                    if (weightUnitRadio) weightUnitRadio.checked = true;
                }

                // Check for blood type
                else if (record.type === 'Blood Type' && record.data?.valueString) {
                    console.log("Blood Type value:", record.data.valueString);
                    const bloodTypeRadio = document.querySelector(`#blood_${record.data.valueString.toLowerCase()}`);
                    if (bloodTypeRadio) {
                        bloodTypeRadio.checked = true;
                    } else {
                        console.warn("No matching blood type radio button for:", record.data.valueString);
                    }
                }
                // Check for rhesus factor
                else if (record.type === 'Rhesus Factor' && record.data?.valueString) {
                    console.log("Rhesus Factor value from backend:", record.data.valueString);

                    // Normalize to "pos" or "neg" based on the backend value
                    const rhesusValue = record.data.valueString.toLowerCase() === "positive"
                        ? "pos"
                        : "neg";

                    console.log("Rhesus Factor ID being searched:", `#rhesus_${rhesusValue}`);

                    // Find the corresponding radio button
                    const rhesusRadio = document.querySelector(`#rhesus_${rhesusValue}`);
                    if (rhesusRadio) {
                        rhesusRadio.checked = true;
                    } else {
                        console.warn("No matching rhesus factor radio button for:", record.data.valueString);
                    }
                }


                // Check for pregnancy status
                if (record.type === 'Pregnancy' && record.data?.valueString) {
                    console.log("Pregnancy status found:", record.data.valueString);

                    const pregnancyStartDate = document.querySelector('#pregnancyStartDate'); // Input field for start date
                    const pregnantYes = document.querySelector('#pregnant_yes'); // Yes radio button
                    const pregnantNo = document.querySelector('#pregnant_no'); // No radio button
                    const pregnancyDatePicker = document.querySelector('#pregnancy-date'); // Date picker section

                    if (record.data.valueString.toLowerCase() === 'pregnant') {
                        // Mark "Yes" radio button as checked
                        if (pregnantYes) pregnantYes.checked = true;

                        // Show the pregnancy date picker
                        if (pregnancyDatePicker) pregnancyDatePicker.style.display = 'block';

                        // Populate the pregnancy start date if available
                        if (pregnancyStartDate && record.data.effectiveDateTime) {
                            pregnancyStartDate.value = record.data.effectiveDateTime.split('T')[0]; // Format to YYYY-MM-DD
                        }
                    } else {
                        // Handle cases where valueString implies not pregnant (e.g., "Not Pregnant")
                        if (pregnantNo) pregnantNo.checked = true;

                        // Hide the pregnancy date picker
                        if (pregnancyDatePicker) pregnancyDatePicker.style.display = 'none';

                        // Clear the pregnancy start date (if any)
                        if (pregnancyStartDate) pregnancyStartDate.value = '';
                    }
                } else if (record.type !== 'Pregnancy Status') {
                    // If no pregnancy observation is found or the type doesn't match, default to "No"
                    const pregnantNo = document.querySelector('#pregnant_no');
                    const pregnancyDatePicker = document.querySelector('#pregnancy-date');
                    const pregnancyStartDate = document.querySelector('#pregnancyStartDate');

                    if (pregnantNo) pregnantNo.checked = true; // Mark "No" by default
                    if (pregnancyDatePicker) pregnancyDatePicker.style.display = 'none'; // Hide date picker
                    if (pregnancyStartDate) pregnancyStartDate.value = ''; // Clear the value

                    // Handle "DNR" (Do Not Resuscitate) status
                } else if (record.resourceType === 'Consent') {
                    console.log("DNR status found:", record.data.valueBoolean);

                    // Interpret the backend value for DNR (true/false)
                    if (record.data?.valueBoolean === true) {
                        dnrConfirmed = true; // DNR confirmed
                    }
                }


            }
        )
        ;
        // Call setupPregnancySectionVisibility after fields are populated
        setupPregnancySectionVisibility();
    }

    function setupPregnancySectionVisibility() {
        const genderField = document.getElementById('inputGender');
        const pregnancySection = document.getElementById('pregnancy-section');
        const pregnancyDatePicker = document.getElementById('pregnancy-date'); // Date picker section
        const pregnancyStartDate = document.getElementById('pregnancyStartDate'); // Date picker input
        const pregnantYes = document.getElementById('pregnant_yes');
        const pregnantNo = document.getElementById('pregnant_no');

        // Function to toggle the pregnancy section based on gender
        function togglePregnancySection() {
            const gender = genderField.value.toLowerCase();
            if (!['male'].includes(gender)) {
                pregnancySection.style.display = 'block';
            } else {
                pregnancySection.style.display = 'none';
                pregnantNo.checked = true; // Automatically set status to "No"
                pregnancyDatePicker.style.display = 'none'; // Hide date picker if section is hidden
                pregnancyStartDate.value = ""; // Clear the date value
            }
        }

        // Function to toggle the date picker based on pregnancy status
        function togglePregnancyDatePicker() {
            if (pregnantYes.checked) {
                pregnancyDatePicker.style.display = 'block';
            } else {
                pregnancyDatePicker.style.display = 'none';
                pregnancyStartDate.value = ""; // Clear the date if "No" is selected
            }
        }

        // 1. Immediately call both functions on page load to set initial visibility
        togglePregnancySection(); // Set visibility of pregnancy section based on pre-selected gender
        togglePregnancyDatePicker(); // Set visibility of date picker based on pre-selected pregnancy status

        // 2. Set up event listeners for user interactions
        genderField.addEventListener('change', () => {
            togglePregnancySection();
            togglePregnancyDatePicker(); // Ensure date picker is hidden if the pregnancy section is hidden
        });
        pregnantYes.addEventListener('change', togglePregnancyDatePicker);
        pregnantNo.addEventListener('change', togglePregnancyDatePicker);
    }


    function setupDnrHandlers(dnrConfirmedFromBackend = false) {
        const dnrCheckbox = document.getElementById('dnr-checkbox');
        const confirmButton = document.getElementById('confirm-dnr-button');
        const abortButton = document.getElementById('abort-dnr-button');
        const dnrModal = new bootstrap.Modal(document.getElementById('dnrModal'));
        const confirmDnr = document.getElementById('confirm-dnr');

        // Lokale Variable, um den DNR-Status zu verfolgen
        let dnrConfirmed = dnrConfirmedFromBackend;

        // Initialisiere die UI basierend auf dem Backend-Flag
        function initializeDnrState() {
            if (dnrConfirmed) {
                dnrCheckbox.checked = true;
                dnrCheckbox.disabled = true;
                confirmButton.style.display = 'none';
                abortButton.style.display = 'inline-block';
            } else {
                dnrCheckbox.checked = false;
                dnrCheckbox.disabled = false;
                confirmButton.style.display = 'inline-block';
                abortButton.style.display = 'none';
            }
            updateButtonStates();
        }

        // Aktualisiere die Zustände der Schaltflächen basierend auf dem aktuellen Status
        function updateButtonStates() {
            confirmButton.disabled = !dnrCheckbox.checked;
            abortButton.disabled = !(dnrCheckbox.disabled && dnrCheckbox.checked);
        }

        dnrCheckbox.addEventListener('change', updateButtonStates);

        confirmButton.addEventListener('click', () => {
            if (dnrCheckbox.checked) {
                dnrModal.show();
            }
        });

        confirmDnr.addEventListener('click', () => {
            dnrModal.hide();
            dnrCheckbox.disabled = true;
            confirmButton.style.display = 'none';
            abortButton.style.display = 'inline-block';
            dnrConfirmed = true;
            updateButtonStates();
        });

        abortButton.addEventListener('click', () => {
            dnrCheckbox.checked = false;
            dnrCheckbox.disabled = false;
            confirmButton.style.display = 'inline-block';
            abortButton.style.display = 'none';
            dnrConfirmed = false;
            updateButtonStates();
        });

        // Initiale UI-Anpassung basierend auf dem Wert von `dnrConfirmedFromBackend`
        initializeDnrState();
    }

});

//
// document.addEventListener('DOMContentLoaded', () => {
//     const token = localStorage.getItem('token');
//
//     if (token) {
//         fetch('/getPatientInformation', {
//             method: 'GET',
//             headers: {
//                 'Authorization': 'Bearer ' + token
//             }
//         })
//             .then(response => response.json())
//             .then(data => {
//                 if (data.status === 'success') {
//                     populateFormFields(data.patient); // Fill form fields with FHIR Patient resource data
//                 } else {
//                     console.error('Error fetching patient data:', data.message);
//                     alert('Could not fetch patient information. Please log in again.');
//                     localStorage.removeItem('token');
//                     window.location.href = '/login'; // Redirect to login
//                 }
//             })
//             .catch(error => {
//                 console.error('Error fetching patient data:', error);
//                 alert('An error occurred. Please try again later.');
//             });
//     }
//
//     function populateFormFields(patient) {
//     console.log("Patient data received from backend:", patient); // Log the structure
//
//     // Adjusted field map to match the backend keys
//     const fieldMap = {
//         name: {
//             selector: ['[name="given_name"]', '[name="last_name"]'],
//             value: () => {
//                 if (patient.name) {
//                     const nameParts = patient.name.split(' ');
//                     return [
//                         nameParts.slice(0, -1).join(' ') || '', // Given name(s)
//                         nameParts[nameParts.length - 1] || ''  // Last name
//                     ];
//                 }
//                 return ['', ''];
//             },
//         },
//         birthdate: {
//             selector: '#inputBirthday',
//             value: () => {
//                 // Format the date to "YYYY-MM-DD" for the input field
//                 const date = new Date(patient.birthdate);
//                 return date.toISOString().split('T')[0]; // Extract date portion
//             }
//         },
//         gender: {
//             selector: '#inputGender',
//             value: () => patient.gender
//                 ? patient.gender.charAt(0).toUpperCase() + patient.gender.slice(1)
//                 : ''
//         },
//         email: {
//             selector: '[name="email"]',
//             value: patient.email || ''
//         },
//         phone: {
//             selector: ['#inputCountryCode', '#inputPhonenumber'],
//             value: () => {
//                 const [countryCode, ...phoneNumber] = (patient.phone || '').split(' ');
//                 return [countryCode || '', phoneNumber.join(' ') || ''];
//             }
//         },
//         address: {
//             selector: '#inputAddress',
//              value: () => {
//                 // Extract city from the address
//                 const parts = patient.address.split(',');
//                 return parts.length > 1 ? parts[0].trim() : '';
//             }
//         },
//         postalCode: {
//             selector: '#inputZip',
//             value: () => {
//                 // Extract postal code from the address
//                 const parts = patient.address.split(',');
//                 return parts[parts.length - 1]?.trim().split(' ')[0] || ''; // Extract ZIP
//             }
//         },
//         city: {
//             selector: '#inputCity',
//             value: () => {
//                 // Extract city from the address
//                 const parts = patient.address.split(',');
//                 return parts.length > 1 ? parts[1].trim() : '';
//             }
//         },
//         state: {
//             selector: '#inputState',
//             value: () => {
//                 // Extract state from the address
//                 const parts = patient.address.split(',');
//                 return parts.length > 2 ? parts[2].trim().split(' ')[0] : '';
//             }
//         },
//         identifier: {
//             selector: '[name="socialsecuritynumber"]',
//             value: () => (patient.identifier ? patient.identifier.slice(0, 4) : '')
//         },
//     };
//
//     // Iterate through the field map and populate form fields
//     for (const [key, { selector, value }] of Object.entries(fieldMap)) {
//         const resolvedValue = typeof value === 'function' ? value() : value;
//
//         if (Array.isArray(selector) && Array.isArray(resolvedValue)) {
//             selector.forEach((sel, index) => {
//                 const element = document.querySelector(sel);
//                 if (element) element.value = resolvedValue[index];
//             });
//         } else {
//             const element = document.querySelector(selector);
//             if (element) element.value = resolvedValue;
//         }
//     }
// }
//
//
//
// });


// document.addEventListener('DOMContentLoaded', () => {
//     const token = localStorage.getItem('token');
//
//     if (token) {
//         fetch('/getPatientInformation', {
//             method: 'GET',
//             headers: {
//                 'Authorization': 'Bearer ' + token
//             }
//         })
//             .then(response => response.json())
//             .then(data => {
//                 if (data.status === 'success') {
//                     populateFormFields(data.patient); // Fill form fields with patient data
//                 } else {
//                     console.error('Error fetching user context:', data.message);
//                     alert('Could not fetch user information. Please log in again.');
//                     localStorage.removeItem('token');
//                     window.location.href = '/login'; // Redirect to login
//                 }
//             })
//             .catch(error => {
//                 console.error('Error fetching user context:', error);
//                 alert('An error occurred. Please try again later.');
//             });
//     }
//
//     function populateFormFields(patient) {
//         // Populate form fields with the patient's data
//         if (patient.given_name) {
//             document.querySelector('[name="given_name"]').value = patient.given_name;
//         }
//         if (patient.last_name) {
//             document.querySelector('[name="last_name"]').value = patient.last_name;
//         }
//         // Continue for other fields...
//     }
// });

//
// const token = localStorage.getItem('token');
//
// if (token) {
//     fetch('/getPatientInformation', {
//         method: 'GET',
//         headers: {
//             'Authorization': 'Bearer ' + token
//         }
//     })
//         .then(response => response.json())
//         .then(data => {
//             if (data.status === 'success') {
//                 populateFormFields(data.patient); // Fill form fields with patient data
//             } else {
//                 console.error('Error fetching user context:', data.message);
//                 alert('Could not fetch user information. Please log in again.');
//                 localStorage.removeItem('token');
//                 window.location.href = '/login'; // Redirect to login
//             }
//         })
//         .catch(error => {
//             console.error('Error fetching user context:', error);
//             alert('An error occurred. Please try again later.');
//         });
// }
//
// function populateFormFields(patient) {
//     // Populate form fields with the patient's data
//     if (patient.given_name) {
//         document.querySelector('[name="given_name"]').value = patient.given_name;
//     }
//     if (patient.last_name) {
//         document.querySelector('[name="last_name"]').value = patient.last_name;
//     }
//     if (patient.gender) {
//         document.querySelector('#inputGender').value = patient.gender;
//     }
//     if (patient.birthday) {
//         document.querySelector('#inputBirthday').value = patient.birthday;
//     }
//     if (patient.countryCode) {
//         document.querySelector('#inputCountryCode').value = patient.countryCode;
//     }
//     if (patient.phonenumber) {
//         document.querySelector('#inputPhonenumber').value = patient.phonenumber;
//     }
//     if (patient.address) {
//         document.querySelector('#inputAddress').value = patient.address;
//     }
//     if (patient.zip) {
//         document.querySelector('#inputZip').value = patient.zip;
//     }
//     if (patient.city) {
//         document.querySelector('#inputCity').value = patient.city;
//     }
//     if (patient.state) {
//         document.querySelector('#inputState').value = patient.state;
//     }
// }

