console.log("Checking token in localStorage...");

if (localStorage.getItem('token')) {
    const token = localStorage.getItem('token');
     fetch('/appointments_user', {
        method: 'GET',
        headers: {
            'Authorization': 'Bearer ' + token
        }
    })
        .then(response => {
            if (!response.ok) {
                console.log("Login check error:", response.status)
                localStorage.removeItem('token');
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
            console.error('Login Error:', error);
            alert(error.message || 'An error occurred while fetching appointment page.');
        });
}