document.addEventListener('DOMContentLoaded', function () {
    let selectedAppointment = null;
    const timeSlots = document.querySelectorAll('.list-group-item-action');

    timeSlots.forEach(slot => {
        slot.addEventListener('click', function () {
            // remove selection of all appointments
            timeSlots.forEach(item => item.classList.remove('active'));

            // mark selected appointment
            this.classList.add('active');

            // extract time and date
            const parentDay = this.closest('.col-md-4').querySelector('h2').textContent.trim(); // day and date
            const time = this.textContent.trim(); // time
            selectedAppointment = `${parentDay.split(' - ')[1]} ${time}`; // combine to "YYYY-MM-DD HH:MM"
            console.log('Selected appointment:', selectedAppointment);
        });
    });

    // Eventlistener for "Book"-Button
    const bookButton = document.querySelector('button[type="submit"]');
    bookButton.addEventListener('click', function (event) {
        event.preventDefault();

        if (!selectedAppointment) {
            alert('Please select an appointment before booking!');
            return;
        }
        // send date and time to backend
        console.log('Booking appointment:', selectedAppointment);
        fetch('/book_appointment', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + localStorage.getItem('token')
            },
            body: JSON.stringify({ appointment: selectedAppointment })
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Booking failed!');
            }
        })
        .then(data => {
            alert('Appointment booked successfully!');
            console.log('Server response:', data);
            window.location.href = '/appointments';
        })
        .catch(error => {
            alert(error.message || 'An error occurred while booking the appointment.');
        });
    });
});