const API_BASE_URL = 'http://localhost:8000/api';
let currentBuilding = 'A';

// Check authentication
function checkAdminAuth() {
    const token = localStorage.getItem('access_token');
    const role = localStorage.getItem('role');

    if (!token || role !== 'admin') {
        window.location.href = 'login.html';
        return false;
    }
    return true;
}

// Get auth headers
function getAuthHeaders() {
    const token = localStorage.getItem('access_token');
    return {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    };
}

// Initialize dashboard
async function initDashboard() {
    if (!checkAdminAuth()) return;

    const username = localStorage.getItem('username');
    document.getElementById('adminUsername').textContent = username;

    await loadOverview();
}

// Load overview data
async function loadOverview() {
    try {
        const response = await fetch(`${API_BASE_URL}/admin/overview`, {
            headers: getAuthHeaders()
        });

        if (response.ok) {
            const data = await response.json();

            // Update stats
            document.getElementById('totalBuildings').textContent = data.total_buildings;
            document.getElementById('totalRooms').textContent = data.total_rooms;
            document.getElementById('totalStudents').textContent = data.total_students;
            document.getElementById('occupancyRate').textContent = `${data.overall_occupancy_rate}%`;

            // Load buildings overview
            loadBuildingsOverview(data.buildings_stats);
        } else if (response.status === 401) {
            localStorage.clear();
            window.location.href = 'login.html';
        }
    } catch (error) {
        console.error('Error loading overview:', error);
    }
}

// Load buildings overview
function loadBuildingsOverview(buildings) {
    const container = document.getElementById('buildingsOverview');
    container.innerHTML = '';

    buildings.forEach(building => {
        const card = document.createElement('div');
        card.className = 'building-card';
        card.innerHTML = `
            <h3>🏢 Tòa ${building.building}</h3>
            <div class="building-stats">
                <div class="building-stat-item">
                    <span>Số phòng:</span>
                    <span>${building.total_rooms}</span>
                </div>
                <div class="building-stat-item">
                    <span>Sức chứa:</span>
                    <span>${building.total_capacity}</span>
                </div>
                <div class="building-stat-item">
                    <span>Sinh viên:</span>
                    <span>${building.total_students}</span>
                </div>
                <div class="building-stat-item">
                    <span>Còn trống:</span>
                    <span>${building.available_slots}</span>
                </div>
                <div class="building-stat-item">
                    <span>Tỷ lệ lấp đầy:</span>
                    <span>${building.occupancy_rate}%</span>
                </div>
            </div>
        `;
        container.appendChild(card);
    });
}

// Load building details
async function loadBuildingDetails(building) {
    try {
        const response = await fetch(`${API_BASE_URL}/admin/buildings/${building}`, {
            headers: getAuthHeaders()
        });

        if (response.ok) {
            const data = await response.json();
            displayBuildingDetails(data);
        }
    } catch (error) {
        console.error('Error loading building details:', error);
    }
}

// Display building details
function displayBuildingDetails(data) {
    const container = document.getElementById('buildingDetails');

    let html = `
        <h2>Tòa ${data.building}</h2>
        <div class="building-stats" style="margin-bottom: 20px;">
            <div class="building-stat-item">
                <span>Tổng số phòng:</span>
                <span>${data.total_rooms}</span>
            </div>
            <div class="building-stat-item">
                <span>Sức chứa:</span>
                <span>${data.total_capacity}</span>
            </div>
            <div class="building-stat-item">
                <span>Sinh viên hiện tại:</span>
                <span>${data.total_students}</span>
            </div>
            <div class="building-stat-item">
                <span>Chỗ trống:</span>
                <span>${data.available_slots}</span>
            </div>
            <div class="building-stat-item">
                <span>Tỷ lệ lấp đầy:</span>
                <span>${data.occupancy_rate}%</span>
            </div>
        </div>
        
        <h3>Danh sách phòng</h3>
        <table class="data-table">
            <thead>
                <tr>
                    <th>Phòng</th>
                    <th>Tầng</th>
                    <th>Sức chứa</th>
                    <th>Hiện tại</th>
                    <th>Còn trống</th>
                    <th>Tỷ lệ (%)</th>
                    <th>Trạng thái</th>
                </tr>
            </thead>
            <tbody>
    `;

    data.rooms.forEach(room => {
        let statusClass = 'status-available';
        let statusText = 'Còn chỗ';

        if (room.available_slots === 0) {
            statusClass = 'status-full';
            statusText = 'Đầy';
        } else if (room.occupancy_rate > 50) {
            statusClass = 'status-partial';
            statusText = 'Gần đầy';
        }

        html += `
            <tr>
                <td>${room.room_id}</td>
                <td>${room.floor}</td>
                <td>${room.capacity}</td>
                <td>${room.current_students}</td>
                <td>${room.available_slots}</td>
                <td>${room.occupancy_rate}%</td>
                <td><span class="status-badge ${statusClass}">${statusText}</span></td>
            </tr>
        `;
    });

    html += `
            </tbody>
        </table>
    `;

    container.innerHTML = html;
}

// Load all rooms
async function loadAllRooms() {
    try {
        const response = await fetch(`${API_BASE_URL}/admin/rooms`, {
            headers: getAuthHeaders()
        });

        if (response.ok) {
            const rooms = await response.json();
            displayRoomsTable(rooms);
        }
    } catch (error) {
        console.error('Error loading rooms:', error);
    }
}

// Display rooms table
function displayRoomsTable(rooms) {
    const tbody = document.querySelector('#roomsTable tbody');
    tbody.innerHTML = '';

    rooms.forEach(room => {
        const row = document.createElement('tr');
        const updatedDate = new Date(room.last_updated).toLocaleString('vi-VN');

        row.innerHTML = `
            <td>${room.room_id}</td>
            <td>${room.building}</td>
            <td>${room.floor}</td>
            <td>${room.capacity}</td>
            <td>${room.current_students}</td>
            <td>${room.available_slots}</td>
            <td>${room.occupancy_rate}%</td>
            <td>${updatedDate}</td>
        `;
        tbody.appendChild(row);
    });
}

// Load all students
async function loadAllStudents() {
    try {
        const response = await fetch(`${API_BASE_URL}/admin/students`, {
            headers: getAuthHeaders()
        });

        if (response.ok) {
            const students = await response.json();
            displayStudentsTable(students);
        }
    } catch (error) {
        console.error('Error loading students:', error);
    }
}

// Display students table
function displayStudentsTable(students) {
    const tbody = document.querySelector('#studentsTable tbody');
    tbody.innerHTML = '';

    students.forEach(student => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${student.mssv}</td>
            <td>${student.ten}</td>
            <td>${student.nam_sinh}</td>
            <td>${student.room_id || 'Chưa có phòng'}</td>
        `;
        tbody.appendChild(row);
    });
}

// Navigation
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', async (e) => {
        e.preventDefault();

        // Update active nav item
        document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
        item.classList.add('active');

        // Update active section
        const section = item.dataset.section;
        document.querySelectorAll('.content-section').forEach(sec => sec.classList.remove('active'));
        document.getElementById(`${section}-section`).classList.add('active');

        // Update title
        const titles = {
            'overview': 'Tổng quan',
            'buildings': 'Quản lý tòa nhà',
            'rooms': 'Quản lý phòng',
            'students': 'Quản lý sinh viên',
            'upload': 'Upload tài liệu'
        };
        document.getElementById('sectionTitle').textContent = titles[section];

        // Load data for section
        if (section === 'overview') {
            await loadOverview();
        } else if (section === 'buildings') {
            await loadBuildingDetails(currentBuilding);
        } else if (section === 'rooms') {
            await loadAllRooms();
        } else if (section === 'students') {
            await loadAllStudents();
        }
    });
});

// Building tabs
document.querySelectorAll('.building-tab').forEach(tab => {
    tab.addEventListener('click', async () => {
        document.querySelectorAll('.building-tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');

        currentBuilding = tab.dataset.building;
        await loadBuildingDetails(currentBuilding);
    });
});

// Refresh button
document.getElementById('refreshBtn').addEventListener('click', async () => {
    const activeSection = document.querySelector('.content-section.active').id.replace('-section', '');

    if (activeSection === 'overview') {
        await loadOverview();
    } else if (activeSection === 'buildings') {
        await loadBuildingDetails(currentBuilding);
    } else if (activeSection === 'rooms') {
        await loadAllRooms();
    } else if (activeSection === 'students') {
        await loadAllStudents();
    }
});

// Logout
document.getElementById('logoutBtn').addEventListener('click', () => {
    localStorage.clear();
    window.location.href = 'login.html';
});

// File upload
document.getElementById('fileInput').addEventListener('change', (e) => {
    const fileName = e.target.files[0]?.name || 'Chọn file...';
    document.getElementById('fileName').textContent = fileName;
});

// Upload form
document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];

    if (!file) {
        alert('Vui lòng chọn file');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    const uploadBtn = document.getElementById('uploadBtn');
    const uploadStatus = document.getElementById('uploadStatus');
    const uploadProgress = document.getElementById('uploadProgress');

    uploadBtn.disabled = true;
    uploadBtn.innerHTML = '<span class="icon">⏳</span> Đang upload...';
    uploadStatus.classList.remove('show', 'success', 'error');
    uploadProgress.classList.add('show');
    uploadProgress.innerHTML = '<div class="progress-bar"><div class="progress-fill" style="width: 50%"></div></div>';

    try {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${API_BASE_URL}/admin/upload`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });

        const data = await response.json();

        if (response.ok && data.success) {
            uploadStatus.textContent = `✅ ${data.message}. Đã xử lý ${data.chunks_processed} chunks.`;
            uploadStatus.classList.add('show', 'success');
            fileInput.value = '';
            document.getElementById('fileName').textContent = 'Chọn file...';
        } else {
            uploadStatus.textContent = `❌ ${data.message}. ${data.error || ''}`;
            uploadStatus.classList.add('show', 'error');
        }
    } catch (error) {
        uploadStatus.textContent = `❌ Lỗi kết nối: ${error.message}`;
        uploadStatus.classList.add('show', 'error');
    } finally {
        uploadBtn.disabled = false;
        uploadBtn.innerHTML = '<span class="icon">📤</span> Upload';
        uploadProgress.classList.remove('show');
    }
});

// Initialize on page load
initDashboard();
