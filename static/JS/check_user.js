document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('token');

    if (token) {
        fetch('/getPatientInformation', {
            method: 'GET',
            headers: {
                'Authorization': 'Bearer ' + token
            }
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    populateFormFields(data.patient); // Fill form fields with patient data
                } else {
                    console.error('Error fetching user context:', data.message);
                    alert('Could not fetch user information. Please log in again.');
                    localStorage.removeItem('token');
                    window.location.href = '/login'; // Redirect to login
                }
            })
            .catch(error => {
                console.error('Error fetching user context:', error);
                alert('An error occurred. Please try again later.');
            });
    }

    function populateFormFields(patient) {
        // Populate form fields with the patient's data
        if (patient.given_name) {
            document.querySelector('[name="given_name"]').value = patient.given_name;
        }
        if (patient.last_name) {
            document.querySelector('[name="last_name"]').value = patient.last_name;
        }
        // Continue for other fields...
    }
});

//
// const token = localStorage.getItem('token');
//
// if (token) {
//     fetch('/getPatientInformation', {
//         method: 'GET',
//         headers: {
//             'Authorization': 'Bearer ' + token
//         }
//     })
//         .then(response => response.json())
//         .then(data => {
//             if (data.status === 'success') {
//                 populateFormFields(data.patient); // Fill form fields with patient data
//             } else {
//                 console.error('Error fetching user context:', data.message);
//                 alert('Could not fetch user information. Please log in again.');
//                 localStorage.removeItem('token');
//                 window.location.href = '/login'; // Redirect to login
//             }
//         })
//         .catch(error => {
//             console.error('Error fetching user context:', error);
//             alert('An error occurred. Please try again later.');
//         });
// }
//
// function populateFormFields(patient) {
//     // Populate form fields with the patient's data
//     if (patient.given_name) {
//         document.querySelector('[name="given_name"]').value = patient.given_name;
//     }
//     if (patient.last_name) {
//         document.querySelector('[name="last_name"]').value = patient.last_name;
//     }
//     if (patient.gender) {
//         document.querySelector('#inputGender').value = patient.gender;
//     }
//     if (patient.birthday) {
//         document.querySelector('#inputBirthday').value = patient.birthday;
//     }
//     if (patient.countryCode) {
//         document.querySelector('#inputCountryCode').value = patient.countryCode;
//     }
//     if (patient.phonenumber) {
//         document.querySelector('#inputPhonenumber').value = patient.phonenumber;
//     }
//     if (patient.address) {
//         document.querySelector('#inputAddress').value = patient.address;
//     }
//     if (patient.zip) {
//         document.querySelector('#inputZip').value = patient.zip;
//     }
//     if (patient.city) {
//         document.querySelector('#inputCity').value = patient.city;
//     }
//     if (patient.state) {
//         document.querySelector('#inputState').value = patient.state;
//     }
// }
