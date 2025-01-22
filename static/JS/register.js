// register.js

        const today = new Date();
        const yyyy = today.getFullYear();
        const mm = String(today.getMonth() + 1).padStart(2, '0'); // Months are 0-based
        const dd = String(today.getDate()).padStart(2, '0'); // Add leading zero if necessary

        const formattedDate = `${yyyy}-${mm}-${dd}`; // Format as YYYY-MM-DD

        // Set max attribute for the date input
        document.getElementById('inputBirthday').setAttribute('max', formattedDate);

(function () {
    'use strict';

    const form = document.querySelector('.needs-validation');

    form.addEventListener('submit', function (event) {
        event.preventDefault();
        let isValid = true;

        const inputs = form.querySelectorAll('input, select');

        inputs.forEach((input) => {
            const errorDiv = input.nextElementSibling;

            if (!input.checkValidity()) {
                input.classList.add('is-invalid');
                if (errorDiv && errorDiv.classList.contains('invalid-feedback')) {
                    errorDiv.textContent = input.validationMessage;
                }
                isValid = false;
            } else {
                input.classList.remove('is-invalid');
                if (errorDiv && errorDiv.classList.contains('invalid-feedback')) {
                    errorDiv.textContent = '';
                }
            }
        });

        if (isValid) {
            if (localStorage.getItem('token')) {
                localStorage.removeItem('token');
            }

            const registerPatientData = createPatientData();
            const password = document.querySelector('input[name="password"]').value.trim();

            const requestBody = {
                user: registerPatientData,
                password: password
            };

            fetch('/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestBody)
            })
                .then(async (response) => {
                    const data = await response.json();

                    if (!response.ok) {
                        throw new Error(data.message || 'Registration failed');
                    }

                    if (data.status === 'success') {
                        console.log('Server Response:', data);
                        alert('Registration successful!');
                        window.location.href = '/login';
                    } else {
                        console.error('Unexpected response:', data);
                        alert(data.message || 'Failed to register.');
                    }
                })
                .catch((error) => {
                    console.error('Error:', error.message);
                    alert(error.message || 'An error occurred. Please try again.');
                });
        }
    });

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

     // Format birthdate as DDMMYYYY
    const birthdateParts = birthdate.split('-'); // Split date into [YYYY, MM, DD]
    const formattedBirthdate = `${birthdateParts[2]}.${birthdateParts[1]}.${birthdateParts[0]}`;
    const ssnFormattedBirthdate = `${birthdateParts[2]}${birthdateParts[1]}${birthdateParts[0]}`;

    // Concatenate SSN with formatted birthdate
    const formattedSSN = `${socialsecuritynumber}${ssnFormattedBirthdate}`;

    // Create a simplified patient data object
    return {
        name: `${givenName} ${lastName}`,
        birthdate: formattedBirthdate,
        gender: gender.toLowerCase(),
        address: `${line}, ${city}, ${state}, ${postalCode}`,
        phone: `${countryCode} ${phoneNumber}`,
        email: email,
        identifier: formattedSSN,
    };
}

// function createUserJson() {
//     const givenName = document.querySelector('input[name="given_name"]').value.trim();
//     const lastName = document.querySelector('input[name="last_name"]').value.trim();
//     const email = document.querySelector('input[name="email"]').value.trim();
//     const socialsecuritynumber = document.querySelector('input[name="socialsecuritynumber"]').value.trim();
//     const birthdate = document.querySelector('input[name="birthday"]').value.trim(); // Fixing the name to 'birthday'
//
//     // Format birthdate as DDMMYYYY
//     const birthdateParts = birthdate.split('-'); // Split date into [YYYY, MM, DD]
//     const formattedBirthdate = `${birthdateParts[2]}${birthdateParts[1]}${birthdateParts[0]}`;
//
//     // Concatenate SSN with formatted birthdate
//     const formattedSSN = `${socialsecuritynumber}${formattedBirthdate}`;
//
//     return {
//         givenName: givenName,
//         lastName: lastName,
//         email: email,
//         ssn: formattedSSN, // Set formatted SSN
//     };
// }

})
();
