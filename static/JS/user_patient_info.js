// user_patient_info.js

document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('.needs-validation');

    // Lock and unlock conditions and allergies
    setupLockButtons('lock-conditions', '.condition-checkbox');
    setupLockButtons('lock-allergies', '.allergy-checkbox');
    setupLockButtons('lock-blood-type', ['.blood-radio', '.rhesus-radio']);

    // DNR button and checkbox handling
    setupDnrHandlers();

    // Handle pregnancy section visibility based on gender
    setupPregnancySectionVisibility();

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

    function setupPregnancySectionVisibility() {
        const genderField = document.getElementById('inputGender');
        const pregnancySection = document.getElementById('pregnancy-section');

        genderField.addEventListener('change', () => {
            const gender = genderField.value.toLowerCase();
            if (['female', 'unknown', 'other'].includes(gender)) {
                pregnancySection.style.display = 'block';
            } else {
                pregnancySection.style.display = 'none';
            }
        });

        document.getElementById('pregnant_yes').addEventListener('change', () => {
            document.getElementById('pregnancy-weeks').style.display = 'block';
        });

        document.getElementById('pregnant_no').addEventListener('change', () => {
            document.getElementById('pregnancy-weeks').style.display = 'none';
        });
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
        if (heightValue) {
            observations.push(createObservation('Height', heightValue, heightUnit));
        }

        // Weight Observation
        const weightValue = document.querySelector('#inputWeight')?.value.trim() || null;
        const weightUnit = document.querySelector('input[name="weight_unit"]:checked')?.value || null;
        if (weightValue) {
            observations.push(createObservation('Weight', weightValue, weightUnit));
        }

        // Blood Type and Rhesus Factor Observation
        const bloodType = document.querySelector('input[name="blood_type"]:checked')?.value || null;
        const rhesusFactor = document.querySelector('input[name="rhesus_factor"]:checked')?.value || null;
        if (bloodType && rhesusFactor) {
            observations.push(createObservation('Blood Type', `${bloodType} ${rhesusFactor}`, null));
        }

        // Pregnancy Status Observation
        const gender = document.querySelector('#inputGender')?.value.toLowerCase() || null;
        if (['female', 'unknown', 'other'].includes(gender)) {
            const pregnancyStatus = document.querySelector('input[name="pregnancy_status"]:checked')?.value || null;
            if (pregnancyStatus) {
                const pregnancyObservation = createObservation('Pregnancy Status', pregnancyStatus, null);

                if (pregnancyStatus === 'yes') {
                    const pregnancyWeeks = document.querySelector('#pregnancyWeeks')?.value.trim() || null;
                    if (pregnancyWeeks) {
                        pregnancyObservation.pregnancyWeeks = pregnancyWeeks;
                    }
                }

                observations.push(pregnancyObservation);
            }
        }

        return observations;
    }


    function createObservation(type, value, unit) {
        return {
            resourceType: "Observation",
            status: "final",
            category: [
                {
                    coding: [
                        {
                            system: "http://terminology.hl7.org/CodeSystem/observation-category",
                            code: "vital-signs",
                            display: "Vital Signs"
                        }
                    ]
                }
            ],
            code: {
                coding: [
                    {
                        system: "http://loinc.org",
                        code: type.toLowerCase().replace(/\s+/g, "-"), // Example: "Height" -> "height"
                        display: type
                    }
                ]
            },
            valueQuantity: value
                ? {
                    value: parseFloat(value),
                    unit: unit,
                    system: "http://unitsofmeasure.org",
                    code: unit
                }
                : undefined,
            effectiveDateTime: new Date().toISOString()
        };
    }

});
