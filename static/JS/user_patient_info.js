// user_patient_info.js
let dnrConfirmed = false;

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

        const patient = createPatientData();
        console.log(patient);
        const observations = createObservations();
        const consent = createConsentData();
        const conditions = createConditionData()

        // Build request payload
        const payload = {patient};
        if (observations.length > 0) {
            payload.observations = observations;
        }
        if (consent.consent) {
            payload.consent = consent;
        }
        if (conditions.length > 0) {
            payload.conditions = conditions;
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

            // Set the flag to true since the user confirmed DNR
            dnrConfirmed = true;
        });

        abortButton.addEventListener('click', () => {
            dnrCheckbox.checked = false;
            dnrCheckbox.disabled = false;
            confirmButton.style.display = 'inline-block';
            abortButton.style.display = 'none';
            updateButtonStates();

            // Set the flag to false since the user confirmed DNR
            dnrConfirmed = false;
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

    function createPatientData() {
        // Extract values from the form
        const givenName = document.querySelector('input[name="given_name"]').value.trim();
        const lastName = document.querySelector('input[name="last_name"]').value.trim();
        const email = document.querySelector('input[name="email"]').value.trim();
        const socialsecuritynumber = document.querySelector('input[name="socialsecuritynumber"]').value.trim();
        const birthdate = document.querySelector('input[name="birthday"]').value.trim();
        const line = document.querySelector('input[name="address"]').value.trim();
        const city = document.querySelector('input[name="city"]').value.trim();
        const postalCode = document.querySelector('input[name="zip"]').value.trim();
        const state = document.querySelector('select[name="state"]').value.trim();
        const gender = document.querySelector('select[name="gender"]').value.trim();
        const countryCode = document.querySelector('select[name="countryCode"]').value.trim();
        const phoneNumber = document.querySelector('input[name="phonenumber"]').value.trim();

        // Contact fields
        const contactGivenName = document.querySelector('input[name="contact_given_name"]').value.trim();
        const contactLastName = document.querySelector('input[name="contact_last_name"]').value.trim();
        const contactCountryCode = document.querySelector('select[name="contactCountryCode"]').value.trim();
        const contactPhoneNumber = document.querySelector('input[name="contact_phone"]').value.trim();

        // Format birthdate as DDMMYYYY
        const birthdateParts = birthdate.split('-'); // Split date into [YYYY, MM, DD]
        const formattedBirthdate = `${birthdateParts[2]}.${birthdateParts[1]}.${birthdateParts[0]}`;
        const ssnFormattedBirthdate = `${birthdateParts[2]}${birthdateParts[1]}${birthdateParts[0]}`;

        // Concatenate SSN with formatted birthdate
        const formattedSSN = `${socialsecuritynumber}${ssnFormattedBirthdate}`;

        // Prepare contacts array
        const contacts = [];
        if (contactGivenName && contactLastName && contactPhoneNumber) {
            // Add contact only if all fields are valid
            contacts.push({
                name: `${contactGivenName} ${contactLastName}`,
                phone: `${contactCountryCode} ${contactPhoneNumber}`
            });
        }

        // Create a simplified patient data object
        return {
            name: `${givenName} ${lastName}`,
            birthdate: formattedBirthdate,
            gender: gender.toLowerCase(),
            address: `${line}, ${city}, ${state}, ${postalCode}`,
            phone: `${countryCode} ${phoneNumber}`,
            email: email,
            identifier: formattedSSN,
            contacts // Deliver only if the contact array has entries
        };
    }

    function createObservations() {
        const observations = [];

        // Height Observation
        const heightValue = document.querySelector('#inputHeight')?.value.trim();
        const heightUnit = document.querySelector('input[name="height_unit"]:checked')?.value;
        if (heightValue && heightUnit) {
            observations.push({
                observation: {
                    identifier: `obs-8302-2`, // LOINC code for height
                    type: "Height",
                    data: `${heightValue} ${heightUnit}`,
                    data_aqu_datetime: new Date().toISOString()
                }
            });
        }

        // Weight Observation
        const weightValue = document.querySelector('#inputWeight')?.value.trim();
        const weightUnit = document.querySelector('input[name="weight_unit"]:checked')?.value;
        if (weightValue && weightUnit) {
            observations.push({
                observation: {
                    identifier: `obs-29463-7`, // LOINC code for weight
                    type: "Weight",
                    data: `${weightValue} ${weightUnit}`,
                    data_aqu_datetime: new Date().toISOString()
                }
            });
        }

        // Blood Type Observation
        const bloodType = document.querySelector('input[name="blood_type"]:checked')?.value;
        if (bloodType) {
            observations.push({
                observation: {
                    identifier: `obs-883-9`,
                    type: "Blood Type",
                    data: bloodType,
                    data_aqu_datetime: new Date().toISOString()
                }
            });
        }

        // Rhesus Factor Observation
        const rhesusFactor = document.querySelector('input[name="rhesus_factor"]:checked')?.value;
        if (rhesusFactor) {
            observations.push({
                observation: {
                    identifier: `obs-7799-0`,
                    type: "Rhesus Factor",
                    data: rhesusFactor,
                    data_aqu_datetime: new Date().toISOString()
                }
            });
        }

        // Pregnancy Observation
        const gender = document.querySelector('#inputGender')?.value.toLowerCase();
        const pregnancyStatus = document.querySelector('input[name="pregnancy_status"]:checked')?.value;
        const pregnancyStartDate = document.querySelector('input[name="pregnancy_start_date"]')?.value.trim();
        if (['female', 'other', 'unknown'].includes(gender) && pregnancyStatus === 'yes' && pregnancyStartDate) {
            observations.push({
                observation: {
                    identifier: `obs-82810-3`,
                    type: "Pregnancy",
                    data: "Pregnant",
                    data_aqu_datetime: pregnancyStartDate
                }
            });
        }

        return observations;
    }

    function createConsentData() {
        const dnrCheckbox = document.querySelector('#dnr-checkbox'); // Checkbox elementconst abortButton = document.getElementById('abort-dnr-button');
        if (dnrCheckbox && dnrCheckbox.checked && dnrConfirmed) {
            // Return DNR consent object if checkbox is checked
            return {
                consent: {
                    status: "active"
                }
            };
        }
        // Return empty object if checkbox is not checked
        return {};
    }

    function createConditionData() {
        const conditionCheckboxes = document.querySelectorAll('.condition-checkbox'); // Alle Condition-Checkboxen
        const conditions = [];

        // Iteriere über die Checkboxen und überprüfe, welche ausgewählt sind
        conditionCheckboxes.forEach(checkbox => {
            if (checkbox.checked) {
                conditions.push({
                    condition: checkbox.value
                }); // Füge den Wert der ausgewählten Checkbox hinzu
            }
        });
        // Rückgabe als JSON
        return conditions;
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const addMedicationButton = document.getElementById('add-medication');
    const medicationList = document.getElementById('medication-list');
    const medicationSelect = document.getElementById('medication_name');
    const manufacturerSelect = document.getElementById('medication_manufacturer');

    addMedicationButton.addEventListener('click', () => {
        const selectedMedication = medicationSelect.value;
        const selectedManufacturer = manufacturerSelect.value;

        if (!selectedMedication || !selectedManufacturer) {
            alert('Please select both a medication and a manufacturer.');
            return;
        }

        // Check if the medication-manufacturer pair is already in the list
        const existingRows = Array.from(medicationList.querySelectorAll('tr'));
        const isAlreadyAdded = existingRows.some(row => {
            const cells = row.querySelectorAll('td');
            return cells[0]?.textContent === selectedManufacturer && cells[1]?.textContent === selectedMedication;
        });

        if (isAlreadyAdded) {
            alert('This medication and manufacturer pair is already in the list.');
            return;
        }

        // Create a new row for the table
        const newRow = document.createElement('tr');
        newRow.innerHTML = `
            <td>${selectedManufacturer}</td>
            <td>${selectedMedication}</td>
            <td><button type="button" class="btn btn-danger btn-sm remove-medication">Remove</button></td>
        `;

        // Append the new row to the medication list
        medicationList.appendChild(newRow);

        // Reset dropdowns to default state
        medicationSelect.selectedIndex = 0;
        manufacturerSelect.selectedIndex = 0;
    });

    // Event delegation to handle removing a row
    medicationList.addEventListener('click', (event) => {
        if (event.target.classList.contains('remove-medication')) {
            const row = event.target.closest('tr');
            row.remove();
        }
    });
});
