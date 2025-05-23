// user_patient_info.js

        const today = new Date();
        const yyyy = today.getFullYear();
        const mm = String(today.getMonth() + 1).padStart(2, '0'); // Months are 0-based
        const dd = String(today.getDate()).padStart(2, '0'); // Add leading zero if necessary

        const formattedDate = `${yyyy}-${mm}-${dd}`; // Format as YYYY-MM-DD

        // Set max attribute for the date input
        document.getElementById('inputBirthday').setAttribute('max', formattedDate);
        document.getElementById('pregnancyStartDate').setAttribute('max', formattedDate);

document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('.needs-validation');

    // Handle pregnancy section visibility based on gender
    setupPregnancySectionVisibility();

    // Lock and unlock conditions and allergies
    setupLockButtons('lock-conditions', '.condition-checkbox');
    setupLockButtons('lock-allergies', '.allergy-checkbox');
    setupLockButtons('lock-blood-type', ['.blood-radio', '.rhesus-radio']);

    // DNR button and checkbox handling
    setupDnrHandlers();


    // Handle form submission

// Submit Handler
    form.addEventListener('submit', (event) => {
        event.preventDefault();

        const isValid = validateFormInputs(form);
        if (!isValid) {
            alert("Please fill out all required fields correctly.");
            return;
        }

        const patient = createFHIRPatient();
        const observations = gatherObservations();

        // Build request payload
        const payload = {patient};
        if (observations.length > 0) {
            payload.observations = observations;
        }

        const token = localStorage.getItem('token');
        fetch('/savePatientData', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        })
            .then((response) => response.json())
            .then((data) => {
                if (data.status === 'success') {
                    alert('Data saved successfully!');
                } else {
                    console.error('Error saving data:', data.message);
                    alert('Failed to save data. Please try again.');
                }
            })
            .catch((error) => {
                console.error('Error:', error);
                alert('An error occurred while saving data.');
            });
    });


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

    function setupLockButtons(buttonId, selectors) {
        const lockButton = document.getElementById(buttonId);
        const elements = Array.isArray(selectors)
            ? selectors.flatMap((selector) => document.querySelectorAll(selector))
            : document.querySelectorAll(selectors);

        lockButton.addEventListener('click', () => {
            const isLocked = lockButton.textContent === 'Unlock';
            elements.forEach((element) => (element.disabled = !isLocked));
            lockButton.textContent = isLocked ? 'Lock' : 'Unlock';
        });
    }

    function setupDnrHandlers() {
        const dnrCheckbox = document.getElementById('dnr-checkbox');
        const confirmButton = document.getElementById('confirm-dnr-button');
        const abortButton = document.getElementById('abort-dnr-button');
        const dnrModal = new bootstrap.Modal(document.getElementById('dnrModal'));
        const confirmDnr = document.getElementById('confirm-dnr');

        updateButtonStates();

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
            updateButtonStates();
        });

        abortButton.addEventListener('click', () => {
            dnrCheckbox.checked = false;
            dnrCheckbox.disabled = false;
            confirmButton.style.display = 'inline-block';
            abortButton.style.display = 'none';
            updateButtonStates();
        });

        function updateButtonStates() {
            confirmButton.disabled = !dnrCheckbox.checked;
            abortButton.disabled = !(dnrCheckbox.disabled && dnrCheckbox.checked);
        }
    }

    function validateFormInputs(form) {
        let isValid = true;
        const inputs = form.querySelectorAll('input, select');

        inputs.forEach((input) => {
            if (!input.checkValidity()) {
                input.classList.add('is-invalid');
                isValid = false;
            } else {
                input.classList.remove('is-invalid');
            }
        });

        return isValid;
    }


    function createFHIRPatient() {
        const firstName = document.querySelector('[name="given_name"]').value.trim();
        const lastName = document.querySelector('[name="last_name"]').value.trim();
        const email = document.querySelector('[name="email"]').value.trim();
        const gender = document.querySelector('#inputGender').value.toLowerCase();
        const birthDate = document.querySelector('#inputBirthday').value;
        const countryCode = document.querySelector('#inputCountryCode').value;
        const phoneNumber = document.querySelector('#inputPhonenumber').value.trim();
        const address = document.querySelector('#inputAddress').value.trim();
        const city = document.querySelector('#inputCity').value.trim();
        const zip = document.querySelector('#inputZip').value.trim();
        const state = document.querySelector('#inputState').value;
        const ssn = document.querySelector('[name="socialsecuritynumber"]').value.trim();

        // Format SSN with birthdate
        const birthdateParts = birthDate.split('-');
        const formattedBirthdate = `${birthdateParts[2]}${birthdateParts[1]}${birthdateParts[0]}`;
        const formattedSSN = `${ssn}${formattedBirthdate}`;

        return {
            resourceType: "Patient",
            identifier: [
                {
                    use: "official",
                    system: "urn:oid:2.16.840.1.113883.4.1", // Example OID for SSN
                    value: formattedSSN
                }
            ],
            name: [
                {
                    use: "official",
                    family: lastName,
                    given: [firstName]
                }
            ],
            gender: gender,
            birthDate: birthDate,
            telecom: [
                {
                    system: "email",
                    value: email,
                    use: "home"
                },
                {
                    system: "phone",
                    value: `${countryCode} ${phoneNumber}`,
                    use: "mobile"
                }
            ],
            address: [
                {
                    line: [address],
                    city: city,
                    postalCode: zip,
                    state: state,
                    country: "Austria"
                }
            ]
        };
    }

    // Gather Observations Function
    function gatherObservations() {
        const observations = [];

        // Height Observation
        const heightValue = document.querySelector('#inputHeight')?.value.trim() || null;
        const heightUnit = document.querySelector('input[name="height_unit"]:checked')?.value || null;
        console.log("Height:", heightValue, heightUnit);
        if (heightValue) {
            observations.push(createObservation('Height', heightValue, heightUnit));
        }

        // Weight Observation
        const weightValue = document.querySelector('#inputWeight')?.value.trim() || null;
        const weightUnit = document.querySelector('input[name="weight_unit"]:checked')?.value || null;
        console.log("Weight:", weightValue, weightUnit);
        if (weightValue) {
            observations.push(createObservation('Weight', weightValue, weightUnit));
        }

        // Blood Type and Rhesus Factor Observation
        const bloodType = document.querySelector('input[name="blood_type"]:checked')?.value || null;
        const rhesusFactor = document.querySelector('input[name="rhesus_factor"]:checked')?.value || null;
        console.log("Blood Type:", bloodType);
        console.log("Rhesus Factor:", rhesusFactor);
        if (bloodType && rhesusFactor) {
            observations.push(createObservation('Blood Type', bloodType, null));
            observations.push(createObservation('Rhesus Factor', rhesusFactor, null));
        }

        // Pregnancy Status Observation
        const gender = document.querySelector('#inputGender')?.value.toLowerCase() || null;
        const pregnancyStatus = document.querySelector('input[name="pregnancy_status"]:checked')?.value || null;
        const pregnancyWeeks = document.querySelector('#pregnancyWeeks')?.value.trim() || null;
        console.log("Gender:", gender);
        console.log("Pregnancy Status:", pregnancyStatus);
        console.log("Pregnancy Weeks:", pregnancyWeeks);

        if (['female', 'unknown', 'other'].includes(gender) && pregnancyStatus === 'yes' && pregnancyWeeks) {
            const pregnancyObservation = createObservation('Pregnancy Status', "Pregnant", null);
            pregnancyObservation.pregnancyWeeks = pregnancyWeeks;
            observations.push(pregnancyObservation);
        }

        console.log("Observations Gathered:", observations);
        return observations;
    }

    function createObservation(type, value, unit = null, extraData = {}) {
        // Define a mapping of observation types to FHIR categories
        const categoryMap = {
            "Height": "vital-signs",
            "Weight": "vital-signs",
            "Blood Type": "laboratory",
            "Rhesus Factor": "laboratory",
            "Pregnancy Status": "social-history"
        };

        // Determine the category based on the type
        const categoryCode = categoryMap[type] || "other";

        const observation = {
            resourceType: "Observation",
            status: "final",
            category: [
                {
                    coding: [
                        {
                            system: "http://terminology.hl7.org/CodeSystem/observation-category",
                            code: categoryCode,
                            display: categoryCode.replace("-", " ").replace(/\b\w/g, char => char.toUpperCase()) // Capitalize
                        }
                    ]
                }
            ],
            code: {
                coding: [
                    {
                        system: "http://loinc.org",
                        code: type.toLowerCase().replace(/\s+/g, "-"), // E.g., "Height" -> "height"
                        display: type
                    }
                ]
            },
            effectiveDateTime: new Date().toISOString()
        };

        // Add value if provided
        if (value) {
            observation.valueQuantity = {
                value: typeof value === "string" ? value : parseFloat(value),
                unit: unit,
                system: "http://unitsofmeasure.org",
                code: unit
            };
        }

        // Merge additional data if provided (e.g., pregnancyWeeks)
        Object.assign(observation, extraData);

        return observation;
    }

});


// function createObservation(type, value, unit) {
//     return {
//         resourceType: "Observation",
//         status: "final",
//         category: [
//             {
//                 coding: [
//                     {
//                         system: "http://terminology.hl7.org/CodeSystem/observation-category",
//                         code: "vital-signs",
//                         display: "Vital Signs"
//                     }
//                 ]
//             }
//         ],
//         code: {
//             coding: [
//                 {
//                     system: "http://loinc.org",
//                     code: type.toLowerCase().replace(/\s+/g, "-"), // Example: "Height" -> "height"
//                     display: type
//                 }
//             ]
//         },
//         valueQuantity: value
//             ? {
//                 value: parseFloat(value),
//                 unit: unit,
//                 system: "http://unitsofmeasure.org",
//                 code: unit
//             }
//             : undefined,
//         effectiveDateTime: new Date().toISOString()
//     };
// }