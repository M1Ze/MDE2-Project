// register.js
function togglePassword(fieldId) {
    const input = document.getElementById(fieldId);
    input.type = input.type === 'password' ? 'text' : 'password';
}

// Real-time password feedback (ChatGPT)
function checkPassword() {
    const password = document.getElementById('password').value;
    const feedback = document.getElementById('passwordFeedback');

    const specialCharRegex = /[!@#$%^&*(),.?":{}|<>]/;
    const digitRegex = /\d/g;

    if (!specialCharRegex.test(password) || (password.match(digitRegex) || []).length < 3) {
        feedback.style.display = 'block';
    } else {
        feedback.style.display = 'none';
    }
}

// Real-time password match feedback (GPT)
function checkPasswordMatch() {
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm_password').value;
    const matchFeedback = document.getElementById('passwordMatchFeedback');

    if (password !== confirmPassword) {
        matchFeedback.style.display = 'block';
    } else {
        matchFeedback.style.display = 'none';
    }
}

function validateForm() {
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm_password').value;

    const specialCharRegex = /[!@#$%^&*(),.?":{}|<>]/;
    const digitRegex = /\d/g;

    if (!specialCharRegex.test(password) || (password.match(digitRegex) || []).length < 3) {
        alert('Password must include at least one special character and three digits.');
        return false;
    }

    if (password !== confirmPassword) {
        alert('Passwords do not match.');
        return false;
    }

    return true;
}