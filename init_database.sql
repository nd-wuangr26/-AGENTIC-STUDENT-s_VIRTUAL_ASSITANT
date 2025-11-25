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
