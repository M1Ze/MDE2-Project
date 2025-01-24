// document.addEventListener('DOMContentLoaded', () => {
//     const token = localStorage.getItem('token');
//
//     if (token) {
//         fetch('/getPatientInformation', {
//             method: 'GET',
//             headers: {'Authorization': 'Bearer ' + token}
//         })
//             .then(response => response.json())
//             .then(data => {
//                 if (data.status === 'success') {
//                     populateRescueCardFields(data.patient, data.health_data);
//                 } else {
//                     console.error('Error fetching patient data:', data.message);
//                     alert('Could not fetch patient information. Please log in again.');
//                     localStorage.removeItem('token');
//                     window.location.href = '/login'; // Redirect to login
//                 }
//             })
//             .catch(error => {
//                 console.error('Error fetching patient data:', error);
//                 alert('An error occurred. Please try again later.');
//             });
//     }
//
//     function populateRescueCardFields(patient) {
//         console.log("Populating Rescue Card fields with patient data:", patient);
//
//         // Extract Full Name
//         const fullName = getFullName(patient.name);
//         document.getElementById("full_name").textContent = fullName || "N/A";
//
//         // Extract Email
//         const emailEntry = patient.telecom.find(contact => contact.system === "email");
//         const email = emailEntry ? emailEntry.value : "N/A";
//         document.getElementById("email").textContent = email;
//
//         // Extract Social Security Number (or patient identifier)
//         const ssnEntry = patient.identifier.find(id => id.system === "http://example.org/fhir/identifier");
//         const ssn = ssnEntry ? ssnEntry.value : "N/A";
//         document.getElementById("social_security_number").textContent = ssn;
//
//         // Extract Birthdate and Format it
//         document.getElementById("birthdate").textContent = formatDate(patient.birthDate) || "N/A";
//
//         // Extract Gender
//         document.getElementById("gender").textContent = capitalize(patient.gender) || "N/A";
//
//         // Extract Address
//         const address = patient.address[0];
//         const fullAddress = address
//             ? `${address.line[0]}, ${address.city}, ${address.state}, ${address.postalCode}`
//             : "N/A";
//         document.getElementById("address").textContent = fullAddress;
//
//         // Extract Phone Number
//         const phoneEntry = patient.telecom.find(contact => contact.system === "phone");
//         const phone = phoneEntry ? phoneEntry.value : "N/A";
//         document.getElementById("phone_number").textContent = phone;
//
//         // Extract Emergency Contact Name
//         const emergencyContactName = getFullName(patient.contact[0].name);
//         document.getElementById("emergency_contact").textContent = emergencyContactName || "N/A";
//
//         // Extract Emergency Contact Phone
//         const emergencyPhoneEntry = patient.contact[0].telecom.find(contact => contact.system === "phone");
//         const emergencyPhone = emergencyPhoneEntry ? emergencyPhoneEntry.value : "N/A";
//         document.getElementById("emergency_contact_telephone").textContent = emergencyPhone || "N/A";
//     }
//
//     // Format the Full Name (family and given names)
//     function getFullName(nameObj) {
//         if (!nameObj || nameObj.length === 0) return null;
//
//         const givenNames = nameObj[0].given.join(" ");
//         const familyName = nameObj[0].family;
//
//         return `${givenNames} ${familyName}`.trim();
//     }
//
// // Format the Birthdate
//     function formatDate(dateString) {
//         if (!dateString) return null; // Handle null or undefined dates
//         const date = new Date(dateString);
//         if (isNaN(date)) return "Invalid Date"; // Handle invalid dates
//         return date.toISOString().split("T")[0]; // Format as YYYY-MM-DD
//     }
//
// // Capitalize the first letter of the string
//     function capitalize(str) {
//         if (!str || typeof str !== "string") return "N/A";
//         return str.charAt(0).toUpperCase() + str.slice(1);
//     }
//
//     function populateRescueCardFields1(patient, healthData) {
//         console.log("Populating Rescue Card fields with patient data:", patient);
//
//         // Personal Information
//         document.getElementById("full_name").textContent = patient.name || 'N/A';
//         document.getElementById("email").textContent = patient.email || 'N/A';
//         document.getElementById("social_security_number").textContent = patient.ssn || 'N/A';
//         document.getElementById("birthdate").textContent = formatDate(patient.birthdate) || 'N/A';
//         document.getElementById("gender").textContent = capitalize(patient.gender || 'N/A');
//         document.getElementById("address").textContent = patient.address.split(',')[0] || 'N/A';
//         document.getElementById("city_state_zip").textContent = formatCityStateZip(patient);
//         document.getElementById("phone_number").textContent = formatPhoneNumber() || 'N/A'; // Telefonnr.
//         document.getElementById("emergency_contact").textContent = formatContactName(patient) || 'N/A'; // Notfallkontakt
//         document.getElementById("emergency_contact_telephone").textContent = patient.contact.telecom.value || 'N/A'; // Notfallkontakt
//
//
//         // Check for DNR status and toggle banner display
//         if (patient.dnr === true) {
//             document.getElementById("dnr-banner").style.display = "block";
//         } else {
//             document.getElementById("dnr-banner").style.display = "none";
//         }
//
//         // Additional fields or health data can be processed here
//         console.log("Health Data:", healthData);
//     }
//
//     function formatCityStateZip(patient) {
//         const city = patient.address.split(',')[1] || '';
//         const state = patient.address.split(',')[2] || '';
//         const zip = patient.address.split(',')[3] || '';
//         return `${city}, ${state}, ${zip}`.trim();
//     }
//
//     function capitalize(str) {
//         return str.charAt(0).toUpperCase() + str.slice(1);
//     }
//
//     function formatDate(dateString) {
//         if (!dateString) return null; // Handle null or undefined dates
//         const date = new Date(dateString); // Parse the date string
//         if (isNaN(date)) return 'Invalid Date'; // Handle invalid dates
//         return date.toISOString().split('T')[0]; // Format as YYYY-MM-DD
//     }
//
//     function formatContactName(patient) {
//         if (patient.contact) {
//             name = patient.contact.name.given + patient.contact.name.family
//
//             return `${name} `;
//         } else {
//             return 'N/A';
//         }
//
//
//     }
//
//     function formatPhoneNumber(patient) {
//         const phoneEntry = patient.telecom.find(entry => entry.system === 'phone');
//         const phone = phoneEntry ? phoneEntry.value : 'N/A';
//
//         return phone;
//
//     }
//
// });

// rescue_card.js


document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('token');

    if (token) {
        fetch('/getPatientInformation', {
            method: 'GET',
            headers: {'Authorization': 'Bearer ' + token}
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success' && data.patient) {
                    populateRescueCardFields(data.patient, data.health_data || {});
                } else {
                    console.error('Error fetching patient data:', data.message || 'Unknown error');
                    alert('Could not fetch patient information. Please log in again.');
                    localStorage.removeItem('token');
                    window.location.href = '/login'; // Redirect to login
                }
            })
            .catch(error => {
                console.error('Error fetching patient data:', error);
                alert('An error occurred. Please try again later.');
            });
    }

    function populateRescueCardFields(patient = {}, healthData = {}) {
        console.log("Populating Rescue Card fields with patient data:", patient);

        alert(patient)



        // Persönliche Informationen
        document.getElementById("full_name").textContent = patient.name || 'N/A';
        document.getElementById("email").textContent = patient.email || 'N/A';
        document.getElementById("social_security_number").textContent = patient.ssn || 'N/A';
        document.getElementById("birthdate").textContent = formatDate(patient.birthdate) || 'N/A';
        document.getElementById("gender").textContent = capitalize(patient.gender || 'N/A');
        document.getElementById("address").textContent = (patient.address || '').split(',')[0] || 'N/A';
        document.getElementById("city_state_zip").textContent = formatCityStateZip(patient);
        document.getElementById("phone_number").textContent =
    //(patient.telecom && patient.telecom[0] && patient.telecom[0].value) ? patient.telecom[0].value : 'N/A';
       // document.getElementById("emergency_contact").textContent = patient.contact || 'N/A'; // Notfallkontakt

        // Gesundheitsdaten & wichtige medizinische Informationen
        document.getElementById("blood_type").textContent = healthData.blood_type || 'N/A'; // Blutgruppe
        document.getElementById("allergies").textContent =
            (healthData.allergies && healthData.allergies.length > 0)
                ? healthData.allergies.join(', ')
                : 'Keine bekannt'; // Allergien
        document.getElementById("medications").textContent =
            (healthData.medications && healthData.medications.length > 0)
                ? healthData.medications.join(', ')
                : 'Nicht verfügbar'; // Medikamente
        document.getElementById("pre_existing_conditions").textContent =
            (healthData.conditions && healthData.conditions.length > 0)
                ? healthData.conditions.join(', ')
                : 'Keine bekannten Vorerkrankungen'; // Vorerkrankungen

        // DNR-Status überprüfen und Banner anzeigen/verstecken
        if (patient.dnr === true) {
            document.getElementById("dnr-banner").style.display = "block";
        } else {
            document.getElementById("dnr-banner").style.display = "none";
        }

        console.log("Health Data:", healthData); // Log für Debugging
    }

    function formatCityStateZip(patient) {
        const addressParts = (patient.address || '').split(',');
        const city = addressParts[1] || 'N/A';
        const state = addressParts[2] || 'N/A';
        const zip = addressParts[3] || 'N/A';
        return `${city.trim()}, ${state.trim()}, ${zip.trim()}`.trim();
    }

    function capitalize(str) {
        if (!str || typeof str !== 'string') return 'N/A';
        return str.charAt(0).toUpperCase() + str.slice(1);
    }

    function formatDate(dateString) {
        if (!dateString) return null; // Handle null or undefined dates
        const date = new Date(dateString); // Parse the date string
        if (isNaN(date)) return 'Invalid Date'; // Handle invalid dates
        return date.toISOString().split('T')[0]; // Format as YYYY-MM-DD
    }
});