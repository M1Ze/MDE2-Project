// register.js
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
            const userData = createUserJson();
            const password = document.querySelector('input[name="password"]').value.trim();

            const requestBody = {
                user: userData,
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
                        window.location.href = '/login';
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

    function createUserJson() {
        const givenName = document.querySelector('input[name="given_name"]').value.trim();
        const lastName = document.querySelector('input[name="last_name"]').value.trim();
        const email = document.querySelector('input[name="email"]').value.trim();

        return {
            givenName: givenName,
            lastName: lastName,
            email: email,
        };
    }
})();
