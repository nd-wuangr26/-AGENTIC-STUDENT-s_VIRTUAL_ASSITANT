from dotenv import load_dotenv
import os
load_dotenv()

# MySQL envs
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = int(os.getenv("MYSQL_PORT"))
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
try:
    import mysql.connector  # type: ignore
except Exception as _:
    mysql = None
else:
    mysql = mysql


def _get_mysql_connection():
    if mysql is None:
        raise RuntimeError("mysql-connector-python is not installed. Please add it to requirements.txt and install.")
    return mysql.connector.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
    )


def tool_list_available_rooms() -> dict:
    """Liệt kê các phòng còn chỗ trống"""
    conn = _get_mysql_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                r.room_id,
                r.building,
                r.floor,
                r.capacity,
                COUNT(s.mssv) as current_students,
                (r.capacity - COUNT(s.mssv)) as available_slots
            FROM rooms r
            LEFT JOIN students s ON r.room_id = s.room_id
            GROUP BY r.room_id
            HAVING available_slots > 0
            ORDER BY r.building, r.floor, r.room_number
        """)
        rooms = cursor.fetchall()
        return {"ok": True, "available_rooms": rooms, "total": len(rooms)}
    finally:
        conn.close()


def tool_add_student(mssv: str, ten: str, nam_sinh: int, room_id: str) -> dict:
    """Thêm sinh viên vào phòng ký túc xá"""
    conn = _get_mysql_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Kiểm tra phòng có tồn tại không
        cursor.execute("SELECT capacity FROM rooms WHERE room_id = %s", (room_id,))
        room = cursor.fetchone()
        if not room:
            return {"ok": False, "error": f"Phòng {room_id} không tồn tại"}
        
        # Đếm số sinh viên hiện tại trong phòng
        cursor.execute("SELECT COUNT(*) as count FROM students WHERE room_id = %s", (room_id,))
        current_count = cursor.fetchone()['count']
        
        # Kiểm tra phòng đã đủ người chưa
        if current_count >= room['capacity']:
            return {
                "ok": False, 
                "error": f"Phòng {room_id} đã đủ {room['capacity']} sinh viên",
                "current_students": current_count,
                "capacity": room['capacity']
            }
        
        # Kiểm tra MSSV đã tồn tại chưa
        cursor.execute("SELECT mssv FROM students WHERE mssv = %s", (mssv,))
        if cursor.fetchone():
            return {"ok": False, "error": f"Sinh viên với MSSV {mssv} đã tồn tại"}
        
        # Thêm sinh viên
        cursor.execute(
            "INSERT INTO students (mssv, ten, nam_sinh, room_id) VALUES (%s, %s, %s, %s)",
            (mssv, ten, nam_sinh, room_id)
        )
        conn.commit()
        
        return {
            "ok": True,
            "message": f"Đã thêm sinh viên {ten} (MSSV: {mssv}) vào phòng {room_id} thành công",
            "student": {"mssv": mssv, "ten": ten, "nam_sinh": nam_sinh, "room_id": room_id},
            "room_status": {
                "current_students": current_count + 1,
                "capacity": room['capacity'],
                "available_slots": room['capacity'] - current_count - 1
            }
        }
    except Exception as e:
        conn.rollback()
        return {"ok": False, "error": str(e)}
    finally:
        conn.close()


def tool_get_student_info(mssv: str) -> dict:
    """Lấy thông tin sinh viên theo MSSV"""
    conn = _get_mysql_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT s.*, r.building, r.floor, r.capacity
            FROM students s
            LEFT JOIN rooms r ON s.room_id = r.room_id
            WHERE s.mssv = %s
        """, (mssv,))
        student = cursor.fetchone()
        
        if not student:
            return {"ok": False, "error": f"Không tìm thấy sinh viên với MSSV {mssv}"}
        
        return {"ok": True, "student": student}
    finally:
        conn.close()


def tool_get_room_info(room_id: str) -> dict:
    """Lấy thông tin phòng và danh sách sinh viên trong phòng"""
    conn = _get_mysql_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Lấy thông tin phòng
        cursor.execute("SELECT * FROM rooms WHERE room_id = %s", (room_id,))
        room = cursor.fetchone()
        
        if not room:
            return {"ok": False, "error": f"Không tìm thấy phòng {room_id}"}
        
        # Lấy danh sách sinh viên
        cursor.execute("""
            SELECT mssv, ten, nam_sinh
            FROM students
            WHERE room_id = %s
            ORDER BY mssv
        """, (room_id,))
        students = cursor.fetchall()
        
        return {
            "ok": True,
            "room": room,
            "students": students,
            "current_students": len(students),
            "available_slots": room['capacity'] - len(students)
        }
    finally:
        conn.close()


def tool_remove_student(mssv: str) -> dict:
    """Xóa sinh viên khỏi ký túc xá"""
    conn = _get_mysql_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        
        # Kiểm tra sinh viên có tồn tại không
        cursor.execute("SELECT * FROM students WHERE mssv = %s", (mssv,))
        student = cursor.fetchone()
        
        if not student:
            return {"ok": False, "error": f"Không tìm thấy sinh viên với MSSV {mssv}"}
        
        # Xóa sinh viên
        cursor.execute("DELETE FROM students WHERE mssv = %s", (mssv,))
        conn.commit()
        
        return {
            "ok": True,
            "message": f"Đã xóa sinh viên {student['ten']} (MSSV: {mssv}) khỏi phòng {student['room_id']}"
        }
    except Exception as e:
        conn.rollback()
        return {"ok": False, "error": str(e)}
    finally:
        conn.close()

