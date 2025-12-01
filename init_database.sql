-- Tạo database
CREATE DATABASE IF NOT EXISTS dormitory_management;
USE dormitory_management;

-- Tạo bảng rooms
CREATE TABLE IF NOT EXISTS rooms (
    room_id VARCHAR(10) PRIMARY KEY,
    capacity INT NOT NULL DEFAULT 4,
    building VARCHAR(1) NOT NULL,
    floor INT NOT NULL,
    room_number INT NOT NULL
);

-- Tạo bảng students
CREATE TABLE IF NOT EXISTS students (
    mssv VARCHAR(20) PRIMARY KEY,
    ten VARCHAR(100) NOT NULL,
    nam_sinh INT NOT NULL,
    room_id VARCHAR(10),
    FOREIGN KEY (room_id) REFERENCES rooms(room_id) ON DELETE SET NULL
);

-- Thêm dữ liệu mẫu cho rooms (A100 đến D400)
-- Tòa A: A100-A400
INSERT INTO rooms (room_id, capacity, building, floor, room_number) VALUES
('A100', 4, 'A', 1, 100), ('A101', 4, 'A', 1, 101), ('A102', 4, 'A', 1, 102), ('A103', 4, 'A', 1, 103),
('A200', 4, 'A', 2, 200), ('A201', 4, 'A', 2, 201), ('A202', 4, 'A', 2, 202), ('A203', 4, 'A', 2, 203),
('A300', 4, 'A', 3, 300), ('A301', 4, 'A', 3, 301), ('A302', 4, 'A', 3, 302), ('A303', 4, 'A', 3, 303),
('A400', 4, 'A', 4, 400), ('A401', 4, 'A', 4, 401), ('A402', 4, 'A', 4, 402), ('A403', 4, 'A', 4, 403);

-- Tòa B: B100-B400
INSERT INTO rooms (room_id, capacity, building, floor, room_number) VALUES
('B100', 4, 'B', 1, 100), ('B101', 4, 'B', 1, 101), ('B102', 4, 'B', 1, 102), ('B103', 4, 'B', 1, 103),
('B200', 4, 'B', 2, 200), ('B201', 4, 'B', 2, 201), ('B202', 4, 'B', 2, 202), ('B203', 4, 'B', 2, 203),
('B300', 4, 'B', 3, 300), ('B301', 4, 'B', 3, 301), ('B302', 4, 'B', 3, 302), ('B303', 4, 'B', 3, 303),
('B400', 4, 'B', 4, 400), ('B401', 4, 'B', 4, 401), ('B402', 4, 'B', 4, 402), ('B403', 4, 'B', 4, 403);

-- Tòa C: C100-C400
INSERT INTO rooms (room_id, capacity, building, floor, room_number) VALUES
('C100', 4, 'C', 1, 100), ('C101', 4, 'C', 1, 101), ('C102', 4, 'C', 1, 102), ('C103', 4, 'C', 1, 103),
('C200', 4, 'C', 2, 200), ('C201', 4, 'C', 2, 201), ('C202', 4, 'C', 2, 202), ('C203', 4, 'C', 2, 203),
('C300', 4, 'C', 3, 300), ('C301', 4, 'C', 3, 301), ('C302', 4, 'C', 3, 302), ('C303', 4, 'C', 3, 303),
('C400', 4, 'C', 4, 400), ('C401', 4, 'C', 4, 401), ('C402', 4, 'C', 4, 402), ('C403', 4, 'C', 4, 403);

-- Tòa D: D100-D400
INSERT INTO rooms (room_id, capacity, building, floor, room_number) VALUES
('D100', 4, 'D', 1, 100), ('D101', 4, 'D', 1, 101), ('D102', 4, 'D', 1, 102), ('D103', 4, 'D', 1, 103),
('D200', 4, 'D', 2, 200), ('D201', 4, 'D', 2, 201), ('D202', 4, 'D', 2, 202), ('D203', 4, 'D', 2, 203),
('D300', 4, 'D', 3, 300), ('D301', 4, 'D', 3, 301), ('D302', 4, 'D', 3, 302), ('D303', 4, 'D', 3, 303),
('D400', 4, 'D', 4, 400), ('D401', 4, 'D', 4, 401), ('D402', 4, 'D', 4, 402), ('D403', 4, 'D', 4, 403);

-- Thêm một số sinh viên mẫu
INSERT INTO students (mssv, ten, nam_sinh, room_id) VALUES
('SV001', 'Nguyễn Văn A', 2003, 'A100'),
('SV002', 'Trần Thị B', 2003, 'A100'),
('SV003', 'Lê Văn C', 2004, 'B200');

-- Tạo bảng room_status để theo dõi trạng thái phòng
CREATE TABLE IF NOT EXISTS room_status (
    room_id VARCHAR(10) PRIMARY KEY,
    current_students INT NOT NULL DEFAULT 0,
    capacity INT NOT NULL DEFAULT 4,
    available_slots INT NOT NULL DEFAULT 4,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (room_id) REFERENCES rooms(room_id) ON DELETE CASCADE
);

-- Tạo bảng users để quản lý tài khoản và phân quyền
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'user') NOT NULL DEFAULT 'user',
    mssv VARCHAR(20) NULL COMMENT 'MSSV của user, có thể là bất kỳ giá trị nào',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- Thêm dữ liệu mẫu cho room_status
INSERT INTO room_status (room_id, current_students, capacity, available_slots)
SELECT 
    r.room_id,
    COALESCE(COUNT(s.mssv), 0) as current_students,
    r.capacity,
    r.capacity - COALESCE(COUNT(s.mssv), 0) as available_slots
FROM rooms r
LEFT JOIN students s ON r.room_id = s.room_id
GROUP BY r.room_id, r.capacity;

-- Thêm tài khoản admin mẫu (password: admin123)
-- Hash được tạo bằng bcrypt với cost factor 12
INSERT INTO users (username, password_hash, role, mssv) VALUES
('admin', 'admin123', 'admin', NULL);

-- Thêm trigger để tự động cập nhật room_status khi thêm/xóa sinh viên
DELIMITER $$

CREATE TRIGGER after_student_insert
AFTER INSERT ON students
FOR EACH ROW
BEGIN
    IF NEW.room_id IS NOT NULL THEN
        UPDATE room_status
        SET current_students = current_students + 1,
            available_slots = capacity - current_students - 1
        WHERE room_id = NEW.room_id;
    END IF;
END$$

CREATE TRIGGER after_student_update
AFTER UPDATE ON students
FOR EACH ROW
BEGIN
    -- Nếu chuyển phòng
    IF OLD.room_id != NEW.room_id OR (OLD.room_id IS NULL AND NEW.room_id IS NOT NULL) OR (OLD.room_id IS NOT NULL AND NEW.room_id IS NULL) THEN
        -- Giảm số sinh viên ở phòng cũ
        IF OLD.room_id IS NOT NULL THEN
            UPDATE room_status
            SET current_students = current_students - 1,
                available_slots = capacity - current_students + 1
            WHERE room_id = OLD.room_id;
        END IF;
        
        -- Tăng số sinh viên ở phòng mới
        IF NEW.room_id IS NOT NULL THEN
            UPDATE room_status
            SET current_students = current_students + 1,
                available_slots = capacity - current_students - 1
            WHERE room_id = NEW.room_id;
        END IF;
    END IF;
END$$

CREATE TRIGGER after_student_delete
AFTER DELETE ON students
FOR EACH ROW
BEGIN
    IF OLD.room_id IS NOT NULL THEN
        UPDATE room_status
        SET current_students = current_students - 1,
            available_slots = capacity - current_students + 1
        WHERE room_id = OLD.room_id;
    END IF;
END$$

DELIMITER ;


USE dormitory_management;

-- Tạo bảng chat_sessions để lưu các phiên chat của user
CREATE TABLE IF NOT EXISTS chat_sessions (
    session_id VARCHAR(50) PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) DEFAULT 'New Chat',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_sessions (user_id, created_at DESC)
);

-- Tạo bảng chat_messages để lưu tin nhắn trong mỗi phiên chat
CREATE TABLE IF NOT EXISTS chat_messages (
    message_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(50) NOT NULL,
    role ENUM('user', 'assistant') NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
    INDEX idx_session_messages (session_id, created_at ASC)
);

SELECT 'Chat tables created successfully!' as status;