// check_user.js
//

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
                        populateFormFields(data.patient); // Fill form fields with FHIR Patient resource data
                        populateHealthFields(data.health_data); // Populate health-related fields
                    } else {
                        console.error('Error fetching patient data:', data.message);
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

        function populateFormFields(patient) {
            console.log("Patient data received from backend:", patient);

            // Adjusted field map to match the backend keys
            const fieldMap = {
                name: {
                    selector: ['[name="given_name"]', '[name="last_name"]'],
                    value: () => {
                        if (patient.name) {
                            const nameParts = patient.name.split(' ');
                            return [
                                nameParts.slice(0, -1).join(' ') || '', // Given name(s)
                                nameParts[nameParts.length - 1] || ''  // Last name
                            ];
                        }
                        return ['', ''];
                    },
                },
                birthdate: {
                    selector: '#inputBirthday',
                    value: () => {
                        const date = new Date(patient.birthdate);
                        return date.toISOString().split('T')[0];
                    }
                },
                gender: {
                    selector: '#inputGender',
                    value: () => patient.gender ? patient.gender.charAt(0).toUpperCase() + patient.gender.slice(1) : ''
                },
                email: {
                    selector: '[name="email"]',
                    value: patient.email || ''
                },
                phone: {
                    selector: ['#inputCountryCode', '#inputPhonenumber'],
                    value: () => {
                        const [countryCode, ...phoneNumber] = (patient.phone || '').split(' ');
                        return [countryCode || '', phoneNumber.join(' ') || ''];
                    }
                },
                address: {
                    selector: '#inputAddress',
                    value: () => {
                        // Extract city from the address
                        const parts = patient.address.split(',');
                        return parts.length > 1 ? parts[0].trim() : '';
                    }
                },
                postalCode: {
                    selector: '#inputZip',
                    value: () => {
                        // Extract postal code from the address
                        const parts = patient.address.split(',');
                        return parts[parts.length - 1]?.trim().split(' ')[0] || ''; // Extract ZIP
                    }
                },
                city: {
                    selector: '#inputCity',
                    value: () => {
                        // Extract city from the address
                        const parts = patient.address.split(',');
                        return parts.length > 1 ? parts[1].trim() : '';
                    }
                },
                state: {
                    selector: '#inputState',
                    value: () => {
                        // Extract state from the address
                        const parts = patient.address.split(',');
                        return parts.length > 2 ? parts[2].trim().split(' ')[0] : '';
                    },
                },
                identifier: {
                    selector: '[name="socialsecuritynumber"]',
                    value: () => (patient.identifier ? patient.identifier.slice(0, 4) : '')
                },
            }

            // Populate form fields using the field map
            for (const [key, {selector, value}] of Object.entries(fieldMap)
                ) {
                const resolvedValue = typeof value === 'function' ? value() : value;

                if (Array.isArray(selector) && Array.isArray(resolvedValue)) {
                    selector.forEach((sel, index) => {
                        const element = document.querySelector(sel);
                        if (element) element.value = resolvedValue[index];
                    });
                } else {
                    const element = document.querySelector(selector);
                    if (element) element.value = resolvedValue;
                }
            }
        }

        function populateHealthFields(healthData) {
            console.log("Health data received from backend:", healthData);

            healthData.forEach(record => {
                    console.log(`Processing record for type: ${record.type}`);
                    console.log("Record data:", record.data);

                    // Check for height
                    if (record.type === 'Height' && record.data?.valueQuantity) {
                        console.log("Height value:", record.data.valueQuantity.value);
                        const heightField = document.querySelector('#inputHeight');
                        if (heightField) heightField.value = record.data.valueQuantity.value;

                        const heightUnitRadio = document.querySelector(`#height_${record.data.valueQuantity.unit?.toLowerCase()}`);
                        if (heightUnitRadio) heightUnitRadio.checked = true;
                    }

                    // Check for weight
                    else if (record.type === 'Weight' && record.data?.valueQuantity) {
                        console.log("Weight value:", record.data.valueQuantity.value);
                        const weightField = document.querySelector('#inputWeight');
                        if (weightField) weightField.value = record.data.valueQuantity.value;

                        const weightUnitRadio = document.querySelector(`#weight_${record.data.valueQuantity.unit?.toLowerCase()}`);
                        if (weightUnitRadio) weightUnitRadio.checked = true;
                    }

                    // Check for blood type
                    else if (record.type === 'Blood Type' && record.data?.valueQuantity?.value) {
                        console.log("Blood Type value:", record.data.valueQuantity.value);
                        const bloodTypeRadio = document.querySelector(`#blood_${record.data.valueQuantity.value.toLowerCase()}`);
                        if (bloodTypeRadio) {
                            bloodTypeRadio.checked = true;
                        } else {
                            console.warn("No matching blood type radio button for:", record.data.valueQuantity.value);
                        }
                    } else if (record.type === 'Rhesus Factor' && record.data?.valueQuantity?.value) {
                        console.log("Rhesus Factor value from backend:", record.data.valueQuantity.value);

                        // Normalize to "pos" or "neg" based on the backend value
                        const rhesusValue = String(record.data.valueQuantity.value).toLowerCase() === "positive"
                            ? "pos"
                            : "neg";

                        console.log("Rhesus Factor ID being searched:", `#rhesus_${rhesusValue}`);

                        // Find the corresponding radio button
                        const rhesusRadio = document.querySelector(`#rhesus_${rhesusValue}`);
                        if (rhesusRadio) {
                            rhesusRadio.checked = true;
                        } else {
                            console.warn("No matching rhesus factor radio button for:", rhesusValue);
                        }
                    }

                    // Check for pregnancy status
                    else if (record.type === 'Pregnancy Status' && record.data?.valueString) {
                        console.log("Pregnancy Status value:", record.data.valueString);

                        // Select pregnancy status radio buttons
                        const pregnantYes = document.querySelector('#pregnant_yes');
                        const pregnantNo = document.querySelector('#pregnant_no');

                        if (record.data.valueString.toLowerCase() === 'yes' && pregnantYes) {
                            pregnantYes.checked = true;

                            // Display pregnancy weeks dropdown
                            const pregnancyWeeksDropdown = document.querySelector('#pregnancy-weeks');
                            if (pregnancyWeeksDropdown) pregnancyWeeksDropdown.style.display = 'block';

                            // Set pregnancy weeks if available
                            const pregnancyWeeks = document.querySelector('#pregnancyWeeks');
                            if (pregnancyWeeks && record.data.pregnancyWeeks) {
                                pregnancyWeeks.value = record.data.pregnancyWeeks;
                            }
                        } else if (pregnantNo) {
                            pregnantNo.checked = true;

                            // Hide pregnancy weeks dropdown
                            const pregnancyWeeksDropdown = document.querySelector('#pregnancy-weeks');
                            if (pregnancyWeeksDropdown) pregnancyWeeksDropdown.style.display = 'none';
                        }
                    }


                }
            )
            ;
        }


    }
)
;

//
// document.addEventListener('DOMContentLoaded', () => {
//     const token = localStorage.getItem('token');
//
//     if (token) {
//         fetch('/getPatientInformation', {
//             method: 'GET',
//             headers: {
//                 'Authorization': 'Bearer ' + token
//             }
//         })
//             .then(response => response.json())
//             .then(data => {
//                 if (data.status === 'success') {
//                     populateFormFields(data.patient); // Fill form fields with FHIR Patient resource data
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
//     function populateFormFields(patient) {
//     console.log("Patient data received from backend:", patient); // Log the structure
//
//     // Adjusted field map to match the backend keys
//     const fieldMap = {
//         name: {
//             selector: ['[name="given_name"]', '[name="last_name"]'],
//             value: () => {
//                 if (patient.name) {
//                     const nameParts = patient.name.split(' ');
//                     return [
//                         nameParts.slice(0, -1).join(' ') || '', // Given name(s)
//                         nameParts[nameParts.length - 1] || ''  // Last name
//                     ];
//                 }
//                 return ['', ''];
//             },
//         },
//         birthdate: {
//             selector: '#inputBirthday',
//             value: () => {
//                 // Format the date to "YYYY-MM-DD" for the input field
//                 const date = new Date(patient.birthdate);
//                 return date.toISOString().split('T')[0]; // Extract date portion
//             }
//         },
//         gender: {
//             selector: '#inputGender',
//             value: () => patient.gender
//                 ? patient.gender.charAt(0).toUpperCase() + patient.gender.slice(1)
//                 : ''
//         },
//         email: {
//             selector: '[name="email"]',
//             value: patient.email || ''
//         },
//         phone: {
//             selector: ['#inputCountryCode', '#inputPhonenumber'],
//             value: () => {
//                 const [countryCode, ...phoneNumber] = (patient.phone || '').split(' ');
//                 return [countryCode || '', phoneNumber.join(' ') || ''];
//             }
//         },
//         address: {
//             selector: '#inputAddress',
//              value: () => {
//                 // Extract city from the address
//                 const parts = patient.address.split(',');
//                 return parts.length > 1 ? parts[0].trim() : '';
//             }
//         },
//         postalCode: {
//             selector: '#inputZip',
//             value: () => {
//                 // Extract postal code from the address
//                 const parts = patient.address.split(',');
//                 return parts[parts.length - 1]?.trim().split(' ')[0] || ''; // Extract ZIP
//             }
//         },
//         city: {
//             selector: '#inputCity',
//             value: () => {
//                 // Extract city from the address
//                 const parts = patient.address.split(',');
//                 return parts.length > 1 ? parts[1].trim() : '';
//             }
//         },
//         state: {
//             selector: '#inputState',
//             value: () => {
//                 // Extract state from the address
//                 const parts = patient.address.split(',');
//                 return parts.length > 2 ? parts[2].trim().split(' ')[0] : '';
//             }
//         },
//         identifier: {
//             selector: '[name="socialsecuritynumber"]',
//             value: () => (patient.identifier ? patient.identifier.slice(0, 4) : '')
//         },
//     };
//
//     // Iterate through the field map and populate form fields
//     for (const [key, { selector, value }] of Object.entries(fieldMap)) {
//         const resolvedValue = typeof value === 'function' ? value() : value;
//
//         if (Array.isArray(selector) && Array.isArray(resolvedValue)) {
//             selector.forEach((sel, index) => {
//                 const element = document.querySelector(sel);
//                 if (element) element.value = resolvedValue[index];
//             });
//         } else {
//             const element = document.querySelector(selector);
//             if (element) element.value = resolvedValue;
//         }
//     }
// }
//
//
//
// });


// document.addEventListener('DOMContentLoaded', () => {
//     const token = localStorage.getItem('token');
//
//     if (token) {
//         fetch('/getPatientInformation', {
//             method: 'GET',
//             headers: {
//                 'Authorization': 'Bearer ' + token
//             }
//         })
//             .then(response => response.json())
//             .then(data => {
//                 if (data.status === 'success') {
//                     populateFormFields(data.patient); // Fill form fields with patient data
//                 } else {
//                     console.error('Error fetching user context:', data.message);
//                     alert('Could not fetch user information. Please log in again.');
//                     localStorage.removeItem('token');
//                     window.location.href = '/login'; // Redirect to login
//                 }
//             })
//             .catch(error => {
//                 console.error('Error fetching user context:', error);
//                 alert('An error occurred. Please try again later.');
//             });
//     }
//
//     function populateFormFields(patient) {
//         // Populate form fields with the patient's data
//         if (patient.given_name) {
//             document.querySelector('[name="given_name"]').value = patient.given_name;
//         }
//         if (patient.last_name) {
//             document.querySelector('[name="last_name"]').value = patient.last_name;
//         }
//         // Continue for other fields...
//     }
// });

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
