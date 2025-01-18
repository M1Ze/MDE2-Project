// base.js

console.log("Checking token in localStorage...");

const loginLogoutLink = document.getElementById('login-logout-link');
const userLink = document.getElementById('user-link');
const token = localStorage.getItem('token');

if (token) {
    fetch('/checklogin', {
        method: 'GET',
        headers: {
            'Authorization': 'Bearer ' + token
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                updateNavForLogout();
            } else {
                localStorage.removeItem('token'); // Invalid token, remove it
                updateNavForLogin();
            }
        })
        .catch(error => {
            console.error('Login check error:', error);
            updateNavForLogin(); // Fallback to login state
        });
} else {
    updateNavForLogin();
}


function updateNavForLogin() {
    loginLogoutLink.textContent = 'Login';
    loginLogoutLink.href = '/login';
    userLink.href = '/login';
}

function updateNavForLogout() {
    loginLogoutLink.textContent = 'Logout';
    loginLogoutLink.href = '#';
    loginLogoutLink.addEventListener('click', () => {
        localStorage.removeItem('token'); // Clear the token
        alert('You have been logged out!');
        location.reload(); // Reload the page to reset the state
    });
}

// console.log("Checking token in localStorage...");
//
// if (localStorage.getItem('token')) {
//     const token = localStorage.getItem('token');
//      fetch('/checklogin', {
//         method: 'GET',
//         headers: {
//             'Authorization': 'Bearer ' + token
//         }
//     })
//         .then(response => {
//             if (!response.ok) {
//                 console.log("Login check error:", response.status)
//                 localStorage.removeItem('token');
//                 throw new Error('Login expired! Please login again.');
//             }
//             return response.text();
//         })
//         .then(html => {
//             document.open();
//             document.write(html);
//             document.close();
//         })
//         .catch(error => {
//             console.error('Login Error:', error);
//             alert(error.message || 'An error occurred while fetching appointment page.');
//         });
// }