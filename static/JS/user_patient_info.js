// Get today's date
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
            const fhirPatient = createFHIRPatient();
            const password = document.querySelector('input[name="password"]').value.trim();

            const requestBody = {
                patient: fhirPatient,
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
                    // Parse JSON response
                    const data = await response.json();

                    // Check if the backend returned an error
                    if (!response.ok) {
                        throw new Error(data.message || 'Registration failed');
                    }

                    // Successful registration
                    if (data.status === 'success') {
                        console.log('Server Response:', data);
                        alert('Registration successful!');
                        window.location.href = '/loginPage';
                    } else {
                        // Handle unexpected cases
                        console.error('Unexpected response:', data);
                        alert(data.message || 'Failed to register.');
                    }
                })
                .catch((error) => {
                    // Display backend error message (if available)
                    console.error('Hier der Fehler!!!!:', error.message);
                    alert(error.message || 'An error occurred. Please try again.');
                });
        }
    });

    function createFHIRPatient() {
        const firstName = document.querySelector('input[name="first_name"]').value.trim();
        const lastName = document.querySelector('input[name="last_name"]').value.trim();
        const email = document.querySelector('input[name="email"]').value.trim();
        const gender = document.querySelector('select[name="gender"]').value.toLowerCase();
        const birthday = document.querySelector('input[name="birthday"]').value;
        const countryCode = document.querySelector('select[name="countryCode"]').value;
        const phoneNumber = document.querySelector('input[name="phonenumber"]').value.trim();
        const address = document.querySelector('input[name="address"]').value.trim();
        const city = document.querySelector('input[name="city"]').value.trim();
        const zip = document.querySelector('input[name="zip"]').value.trim();
        const state = document.querySelector('select[name="state"]').value;

        return {
            resourceType: "Patient",
            name: [
                {
                    use: "official",
                    family: lastName,
                    given: [firstName]
                }
            ],
            gender: gender,
            birthDate: birthday,
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
})();
