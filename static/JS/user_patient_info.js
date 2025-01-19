// user_patient_info.js
//
// document.addEventListener('DOMContentLoaded', () => {
//     const lockConditionsButton = document.getElementById('lock-conditions');
//     const conditionCheckboxes = document.querySelectorAll('.condition-checkbox');
//
//     const lockAllergiesButton = document.getElementById('lock-allergies');
//     const allergyCheckboxes = document.querySelectorAll('.allergy-checkbox');
//
//     // Function to toggle lock/unlock for a group of checkboxes
//     function toggleLock(button, checkboxes) {
//         const isLocked = button.textContent === 'Unlock';
//         checkboxes.forEach((checkbox) => {
//             checkbox.disabled = !isLocked;
//         });
//         button.textContent = isLocked ? 'Lock' : 'Unlock';
//     }
//
//     // Attach event listener to Lock/Unlock buttons
//     lockConditionsButton.addEventListener('click', () => {
//         toggleLock(lockConditionsButton, conditionCheckboxes);
//     });
//
//     lockAllergiesButton.addEventListener('click', () => {
//         toggleLock(lockAllergiesButton, allergyCheckboxes);
//     });
// });
//
//
// document.addEventListener('DOMContentLoaded', () => {
//     const lockBloodButton = document.getElementById('lock-blood-type');
//     const bloodRadios = document.querySelectorAll('.blood-radio');
//     const rhesusRadios = document.querySelectorAll('.rhesus-radio');
//
//     // Function to toggle lock/unlock for blood type and rhesus factor
//     function toggleLockBlood() {
//         const isLocked = lockBloodButton.textContent === 'Unlock';
//         bloodRadios.forEach((radio) => {
//             radio.disabled = !isLocked;
//         });
//         rhesusRadios.forEach((radio) => {
//             radio.disabled = !isLocked;
//         });
//         lockBloodButton.textContent = isLocked ? 'Lock' : 'Unlock';
//     }
//
//     // Attach event listener to the Lock/Unlock button
//     lockBloodButton.addEventListener('click', toggleLockBlood);
// });
//
// // DNR Button and Checkbox handling//
//
// document.addEventListener('DOMContentLoaded', () => {
//     const dnrCheckbox = document.getElementById('dnr-checkbox');
//     const confirmButton = document.getElementById('confirm-dnr-button');
//     const abortButton = document.getElementById('abort-dnr-button');
//     const dnrModal = new bootstrap.Modal(document.getElementById('dnrModal'));
//     const confirmDnr = document.getElementById('confirm-dnr');
//
//     // Initial state setup
//     updateButtonStates();
//
//     // Enable/disable buttons based on the checkbox state
//     dnrCheckbox.addEventListener('change', () => {
//         updateButtonStates();
//     });
//
//     // Show the modal when the red button is clicked
//     confirmButton.addEventListener('click', () => {
//         if (dnrCheckbox.checked) {
//             dnrModal.show();
//         }
//     });
//
//     // Confirm DNR and lock the checkbox
//     confirmDnr.addEventListener('click', () => {
//         //alert('Your DNR preference has been saved.');
//         dnrModal.hide();
//         dnrCheckbox.disabled = true; // Lock the checkbox
//         confirmButton.style.display = 'none'; // Hide the red button
//         abortButton.style.display = 'inline-block'; // Show the green button
//         updateButtonStates(); // Ensure button states are updated
//     });
//
//     // Abort DNR and unlock the checkbox
//     abortButton.addEventListener('click', () => {
//         dnrCheckbox.checked = false; // Uncheck the checkbox
//         dnrCheckbox.disabled = false; // Unlock the checkbox
//         confirmButton.style.display = 'inline-block'; // Show the red button
//         abortButton.style.display = 'none'; // Hide the green button
//         //alert('DNR preference has been aborted.');
//         updateButtonStates(); // Ensure button states are updated
//     });
//
//     // Function to update button states dynamically
//     function updateButtonStates() {
//         confirmButton.disabled = !dnrCheckbox.checked; // Disable red button if checkbox is unchecked
//         abortButton.disabled = !(dnrCheckbox.disabled && dnrCheckbox.checked); // Enable green button only if checkbox is locked and checked
//     }
// });
//
//
// // Show pregnancy section based on gender
// document.getElementById('inputGender').addEventListener('change', function () {
//     const gender = this.value.toLowerCase();
//     const pregnancySection = document.getElementById('pregnancy-section');
//     if (gender !== "male") {
//         pregnancySection.style.display = 'block';
//     } else {
//         pregnancySection.style.display = 'none';
//     }
// });
//
// // Show weeks dropdown if pregnant
// document.getElementById('pregnant_yes').addEventListener('change', function () {
//     document.getElementById('pregnancy-weeks').style.display = 'block';
// });
//
// document.getElementById('pregnant_no').addEventListener('change', function () {
//     document.getElementById('pregnancy-weeks').style.display = 'none';
// });
//
// // Get today's date
// const today = new Date();
// const yyyy = today.getFullYear();
// const mm = String(today.getMonth() + 1).padStart(2, '0'); // Months are 0-based
// const dd = String(today.getDate()).padStart(2, '0'); // Add leading zero if necessary
//
// const formattedDate = `${yyyy}-${mm}-${dd}`; // Format as YYYY-MM-DD
//
// // Set max attribute for the date input
// document.getElementById('inputBirthday').setAttribute('max', formattedDate);
//
// (function () {
//     'use strict';
//
//     const form = document.querySelector('.needs-validation');
//
//     form.addEventListener('submit', function (event) {
//         event.preventDefault();
//         let isValid = true;
//
//         const inputs = form.querySelectorAll('input, select');
//
//         inputs.forEach((input) => {
//             const errorDiv = input.nextElementSibling;
//
//             if (!input.checkValidity()) {
//                 input.classList.add('is-invalid');
//                 if (errorDiv && errorDiv.classList.contains('invalid-feedback')) {
//                     errorDiv.textContent = input.validationMessage;
//                 }
//                 isValid = false;
//             } else {
//                 input.classList.remove('is-invalid');
//                 if (errorDiv && errorDiv.classList.contains('invalid-feedback')) {
//                     errorDiv.textContent = '';
//                 }
//             }
//         });
//
//         if (isValid) {
//             if (localStorage.getItem('token')) {
//                 localStorage.removeItem('token');
//             }
//             const fhirPatient = createFHIRPatient();
//             const password = document.querySelector('input[name="password"]').value.trim();
//
//             const requestBody = {
//                 patient: fhirPatient,
//                 password: password
//             };
//
//             fetch('/register', {
//                 method: 'POST',
//                 headers: {
//                     'Content-Type': 'application/json'
//                 },
//                 body: JSON.stringify(requestBody)
//             })
//                 .then(async (response) => {
//                     // Parse JSON response
//                     const data = await response.json();
//
//                     // Check if the backend returned an error
//                     if (!response.ok) {
//                         throw new Error(data.message || 'Registration failed');
//                     }
//
//                     // Successful registration
//                     if (data.status === 'success') {
//                         console.log('Server Response:', data);
//                         alert('Registration successful!');
//                         window.location.href = '/loginPage';
//                     } else {
//                         // Handle unexpected cases
//                         console.error('Unexpected response:', data);
//                         alert(data.message || 'Failed to register.');
//                     }
//                 })
//                 .catch((error) => {
//                     // Display backend error message (if available)
//                     console.error('Hier der Fehler!!!!:', error.message);
//                     alert(error.message || 'An error occurred. Please try again.');
//                 });
//         }
//     });
//
//     function createFHIRPatient() {
//         const firstName = document.querySelector('input[name="first_name"]').value.trim();
//         const lastName = document.querySelector('input[name="last_name"]').value.trim();
//         const email = document.querySelector('input[name="email"]').value.trim();
//         const gender = document.querySelector('select[name="gender"]').value.toLowerCase();
//         const birthday = document.querySelector('input[name="birthday"]').value;
//         const countryCode = document.querySelector('select[name="countryCode"]').value;
//         const phoneNumber = document.querySelector('input[name="phonenumber"]').value.trim();
//         const address = document.querySelector('input[name="address"]').value.trim();
//         const city = document.querySelector('input[name="city"]').value.trim();
//         const zip = document.querySelector('input[name="zip"]').value.trim();
//         const state = document.querySelector('select[name="state"]').value;
//
//         return {
//             resourceType: "Patient",
//             name: [
//                 {
//                     use: "official",
//                     family: lastName,
//                     given: [firstName]
//                 }
//             ],
//             gender: gender,
//             birthDate: birthday,
//             telecom: [
//                 {
//                     system: "email",
//                     value: email,
//                     use: "home"
//                 },
//                 {
//                     system: "phone",
//                     value: `${countryCode} ${phoneNumber}`,
//                     use: "mobile"
//                 }
//             ],
//             address: [
//                 {
//                     line: [address],
//                     city: city,
//                     postalCode: zip,
//                     state: state,
//                     country: "Austria"
//                 }
//             ]
//         };
//     }
// })();


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
    form.addEventListener('submit', (event) => {
        event.preventDefault();

        // Validate form inputs
        const isValid = validateFormInputs(form);
        if (!isValid) {
            alert("Please fill out all required fields correctly.");
            return;
        }

        // Gather patient data and observations
        const patientData = gatherPatientData();
        const observations = gatherObservations();

        // Send patient data and observations to backend
        const token = localStorage.getItem('token');
        fetch('/savePatientData', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ patient: patientData, observations })
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


    function gatherPatientData() {
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

    return {
        givenName: firstName,
        lastName: lastName,
        email: email,
        gender: gender,
        birthDate: birthDate,
        phone: `${countryCode} ${phoneNumber}`,
        address: {
            line: address,
            city: city,
            postalCode: zip,
            state: state,
            country: "Austria"
        },
        socialSecurityNumber: ssn
    };
}

    function gatherObservations() {
        const observations = [];

        // Height Observation
        const heightValue = document.querySelector('#inputHeight').value.trim();
        const heightUnit = document.querySelector('input[name="height_unit"]:checked').value;
        observations.push(createObservation('Height', heightValue, heightUnit));

        // Weight Observation
        const weightValue = document.querySelector('#inputWeight').value.trim();
        const weightUnit = document.querySelector('input[name="weight_unit"]:checked').value;
        observations.push(createObservation('Weight', weightValue, weightUnit));

        // Blood Type and Rhesus Factor Observation
        const bloodType = document.querySelector('input[name="blood_type"]:checked').value;
        const rhesusFactor = document.querySelector('input[name="rhesus_factor"]:checked').value;
        observations.push(createObservation('Blood Type', `${bloodType} ${rhesusFactor}`, null));

        // Pregnancy Status Observation
        const gender = document.querySelector('#inputGender').value.toLowerCase();
        if (['female', 'unknown', 'other'].includes(gender)) {
            const pregnancyStatus = document.querySelector('input[name="pregnancy_status"]:checked').value;
            let pregnancyObservation = createObservation('Pregnancy Status', pregnancyStatus, null);

            if (pregnancyStatus === 'yes') {
                const pregnancyWeeks = document.querySelector('#pregnancyWeeks').value.trim();
                pregnancyObservation.pregnancyWeeks = pregnancyWeeks;
            }

            observations.push(pregnancyObservation);
        }

        return observations;
    }

    function createObservation(type, value, unit) {
        return {
            type,
            value,
            unit,
            timestamp: new Date().toISOString()
        };
    }
});
