document.addEventListener('DOMContentLoaded', function() {
    const bookAppointmentButtons = document.querySelectorAll('.book-appointment-btn');

    // Event Listener for each button
    bookAppointmentButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();

            const doctorId = button.getAttribute('data-doctor-id');

            if (localStorage.getItem('token')) {
                const token = localStorage.getItem('token');
                console.log("Hier Button für Arzt-ID:", doctorId);

                // add doc id
                fetch('/appointments_practitioners?doctor_id=' + doctorId, {
                    method: 'GET',
                    headers: {
                        'Authorization': 'Bearer ' + token
                    }
                })
                .then(response => {
                    if (!response.ok) {
                        console.log("Fehler bei der Anfrage:", response.status)
                        if (response.status === 403) {
                            console.log("403")
                            localStorage.removeItem('token');
                            window.location.href = '/loginPage';
                        }
                        throw new Error('Login expired! Please login again.');
                    }
                    return response.text();
                })
                .then(html => {
                    document.open();
                    document.write(html);
                    document.close();
                })
                .catch(error => {
                    console.error('Appointments Error:', error);
                    alert(error.message || 'An error occurred while fetching appointments.');
                });
            } else {
                // no token, back to loginpage
                window.location.href = '/loginPage';
            }
        });
    });
});