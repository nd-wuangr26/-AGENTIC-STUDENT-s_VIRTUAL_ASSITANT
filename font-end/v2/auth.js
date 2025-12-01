const API_BASE_URL = 'http://localhost:8000/api';

// Login functionality
if (document.getElementById('loginForm')) {
    document.getElementById('loginForm').addEventListener('submit', async (e) => {
        e.preventDefault();

        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const errorMessage = document.getElementById('errorMessage');
        const submitBtn = e.target.querySelector('button[type="submit"]');

        // Clear previous errors
        errorMessage.classList.remove('show');
        errorMessage.textContent = '';
        submitBtn.disabled = true;
        submitBtn.textContent = 'Đang đăng nhập...';

        try {
            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (response.ok) {
                // Save token and user info
                localStorage.setItem('access_token', data.access_token);
                localStorage.setItem('username', data.username);
                localStorage.setItem('role', data.role);

                // Redirect based on role
                if (data.role === 'admin') {
                    window.location.href = 'admin.html';
                } else {
                    window.location.href = 'index.html';
                }
            } else {
                errorMessage.textContent = data.detail || 'Đăng nhập thất bại';
                errorMessage.classList.add('show');
            }
        } catch (error) {
            errorMessage.textContent = 'Lỗi kết nối đến server';
            errorMessage.classList.add('show');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Đăng nhập';
        }
    });
}

// Register functionality
if (document.getElementById('registerForm')) {
    document.getElementById('registerForm').addEventListener('submit', async (e) => {
        e.preventDefault();

        const mssv = document.getElementById('mssv').value;
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        const errorMessage = document.getElementById('errorMessage');
        const successMessage = document.getElementById('successMessage');
        const submitBtn = e.target.querySelector('button[type="submit"]');

        // Clear previous messages
        errorMessage.classList.remove('show');
        successMessage.classList.remove('show');
        errorMessage.textContent = '';
        successMessage.textContent = '';

        // Validation
        if (username !== mssv) {
            errorMessage.textContent = 'Username phải trùng với MSSV';
            errorMessage.classList.add('show');
            return;
        }

        if (password.length < 6) {
            errorMessage.textContent = 'Mật khẩu phải có ít nhất 6 ký tự';
            errorMessage.classList.add('show');
            return;
        }

        if (password !== confirmPassword) {
            errorMessage.textContent = 'Mật khẩu xác nhận không khớp';
            errorMessage.classList.add('show');
            return;
        }

        submitBtn.disabled = true;
        submitBtn.textContent = 'Đang đăng ký...';

        try {
            const response = await fetch(`${API_BASE_URL}/auth/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password, mssv })
            });

            const data = await response.json();

            if (response.ok) {
                successMessage.textContent = 'Đăng ký thành công! Chuyển đến trang đăng nhập...';
                successMessage.classList.add('show');

                // Redirect to login after 2 seconds
                setTimeout(() => {
                    window.location.href = 'login.html';
                }, 2000);
            } else {
                errorMessage.textContent = data.detail || 'Đăng ký thất bại';
                errorMessage.classList.add('show');
            }
        } catch (error) {
            errorMessage.textContent = 'Lỗi kết nối đến server';
            errorMessage.classList.add('show');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Đăng ký';
        }
    });
}

// Check if user is already logged in
function checkAuth() {
    const token = localStorage.getItem('access_token');
    const role = localStorage.getItem('role');

    if (token && window.location.pathname.includes('login.html')) {
        // Redirect to appropriate page if already logged in
        if (role === 'admin') {
            window.location.href = 'admin.html';
        } else {
            window.location.href = 'index.html';
        }
    }
}

// Run auth check on page load
checkAuth();
