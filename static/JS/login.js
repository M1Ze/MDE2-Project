// login.js
document.getElementById('login-form').addEventListener('submit', function (event) {
    event.preventDefault();

    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value.trim();


    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password })
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Login failed. Status: ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                localStorage.removeItem('token');
                console.log('Login successful!', data);
                localStorage.setItem('token', data.token); // save token local
                alert('Welcome!');
                window.location.href = '/userPatientInfo';
            } else {
                alert(data.message || 'Login failed!');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error: E-mail address or password wrong');
        });
});