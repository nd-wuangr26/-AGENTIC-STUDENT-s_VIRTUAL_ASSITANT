import aiomysql
from typing import Optional, List, Dict, Any
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class MySQLService:
    """Service để tương tác với MySQL database"""
    
    def __init__(self):
        self.pool = None
        self.host = os.getenv("MYSQL_HOST", "localhost")
        self.port = int(os.getenv("MYSQL_PORT", "3306"))
        self.user = os.getenv("MYSQL_USER", "root")
        self.password = os.getenv("MYSQL_PASSWORD", "")
        self.database = os.getenv("MYSQL_DATABASE", "dormitory_management")
    
    async def create_pool(self):
        """Tạo connection pool"""
        if not self.pool:
            self.pool = await aiomysql.create_pool(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                db=self.database,
                autocommit=True,
                minsize=1,
                maxsize=10
            )
    
    async def close_pool(self):
        """Đóng connection pool"""
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()
    
    async def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute SELECT query và trả về kết quả"""
        await self.create_pool()
        async with self.pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, params)
                result = await cursor.fetchall()
                return result
    
    async def execute_update(self, query: str, params: tuple = None) -> int:
        """Execute INSERT/UPDATE/DELETE query và trả về số rows affected"""
        await self.create_pool()
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, params)
                await conn.commit()
                return cursor.rowcount
    
    async def execute_insert(self, query: str, params: tuple = None) -> int:
        """Execute INSERT query và trả về last insert id"""
        await self.create_pool()
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, params)
                await conn.commit()
                return cursor.lastrowid
    
    # User operations
    async def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Lấy thông tin user theo username"""
        query = "SELECT * FROM users WHERE username = %s"
        result = await self.execute_query(query, (username,))
        return result[0] if result else None
    
    async def create_user(self, username: str, password_hash: str, role: str, mssv: Optional[str] = None) -> int:
        """Tạo user mới"""
        query = """
            INSERT INTO users (username, password_hash, role, mssv)
            VALUES (%s, %s, %s, %s)
        """
        return await self.execute_insert(query, (username, password_hash, role, mssv))
    
    async def update_last_login(self, username: str):
        """Cập nhật thời gian đăng nhập cuối"""
        query = "UPDATE users SET last_login = NOW() WHERE username = %s"
        await self.execute_update(query, (username,))
    
    async def check_mssv_exists(self, mssv: str) -> bool:
        """Kiểm tra MSSV có tồn tại trong bảng students không"""
        query = "SELECT COUNT(*) as count FROM students WHERE mssv = %s"
        result = await self.execute_query(query, (mssv,))
        return result[0]['count'] > 0 if result else False
    
    # Room status operations
    async def get_all_room_status(self) -> List[Dict[str, Any]]:
        """Lấy trạng thái tất cả các phòng"""
        query = """
            SELECT rs.*, r.building, r.floor, r.room_number
            FROM room_status rs
            JOIN rooms r ON rs.room_id = r.room_id
            ORDER BY r.building, r.floor, r.room_number
        """
        return await self.execute_query(query)
    
    async def get_room_status_by_building(self, building: str) -> List[Dict[str, Any]]:
        """Lấy trạng thái phòng theo tòa nhà"""
        query = """
            SELECT rs.*, r.building, r.floor, r.room_number
            FROM room_status rs
            JOIN rooms r ON rs.room_id = r.room_id
            WHERE r.building = %s
            ORDER BY r.floor, r.room_number
        """
        return await self.execute_query(query, (building,))
    
    async def get_building_statistics(self) -> List[Dict[str, Any]]:
        """Lấy thống kê theo tòa nhà"""
        query = """
            SELECT 
                r.building,
                COUNT(DISTINCT r.room_id) as total_rooms,
                SUM(r.capacity) as total_capacity,
                SUM(rs.current_students) as total_students,
                SUM(rs.available_slots) as available_slots,
                ROUND(SUM(rs.current_students) * 100.0 / SUM(r.capacity), 2) as occupancy_rate
            FROM rooms r
            LEFT JOIN room_status rs ON r.room_id = rs.room_id
            GROUP BY r.building
            ORDER BY r.building
        """
        return await self.execute_query(query)
    
    async def get_dormitory_overview(self) -> Dict[str, Any]:
        """Lấy tổng quan toàn bộ ký túc xá"""
        query = """
            SELECT 
                COUNT(DISTINCT r.building) as total_buildings,
                COUNT(DISTINCT r.room_id) as total_rooms,
                SUM(r.capacity) as total_capacity,
                SUM(rs.current_students) as total_students,
                SUM(rs.available_slots) as total_available_slots,
                ROUND(SUM(rs.current_students) * 100.0 / SUM(r.capacity), 2) as overall_occupancy_rate
            FROM rooms r
            LEFT JOIN room_status rs ON r.room_id = rs.room_id
        """
        result = await self.execute_query(query)
        return result[0] if result else {}
    
    async def get_all_students(self) -> List[Dict[str, Any]]:
        """Lấy danh sách tất cả sinh viên"""
        query = "SELECT * FROM students ORDER BY mssv"
        return await self.execute_query(query)
    
    async def get_student_by_mssv(self, mssv: str) -> Optional[Dict[str, Any]]:
        """Lấy thông tin sinh viên theo MSSV"""
        query = "SELECT * FROM students WHERE mssv = %s"
        result = await self.execute_query(query, (mssv,))
        return result[0] if result else None
    
    # Chat history operations
    async def create_chat_session(self, session_id: str, user_id: int, title: str = "New Chat") -> bool:
        """Tạo chat session mới"""
        query = """
            INSERT INTO chat_sessions (session_id, user_id, title)
            VALUES (%s, %s, %s)
        """
        try:
            await self.execute_insert(query, (session_id, user_id, title))
            return True
        except Exception as e:
            print(f"Error creating chat session: {e}")
            return False
    
    async def get_user_sessions(self, user_id: int) -> List[Dict[str, Any]]:
        """Lấy tất cả chat sessions của user (không bao gồm đã xóa)"""
        query = """
            SELECT 
                cs.*,
                COUNT(cm.message_id) as message_count
            FROM chat_sessions cs
            LEFT JOIN chat_messages cm ON cs.session_id = cm.session_id
            WHERE cs.user_id = %s AND cs.is_deleted = FALSE
            GROUP BY cs.session_id
            ORDER BY cs.updated_at DESC
        """
        return await self.execute_query(query, (user_id,))
    
    async def get_session_messages(self, session_id: str, user_id: int) -> List[Dict[str, Any]]:
        """Lấy tất cả messages của một session (kiểm tra quyền sở hữu)"""
        query = """
            SELECT cm.*
            FROM chat_messages cm
            JOIN chat_sessions cs ON cm.session_id = cs.session_id
            WHERE cm.session_id = %s AND cs.user_id = %s AND cs.is_deleted = FALSE
            ORDER BY cm.created_at ASC
        """
        return await self.execute_query(query, (session_id, user_id))
    
    async def save_chat_message(self, session_id: str, role: str, content: str) -> bool:
        """Lưu một message vào session"""
        query = """
            INSERT INTO chat_messages (session_id, role, content)
            VALUES (%s, %s, %s)
        """
        try:
            await self.execute_insert(query, (session_id, role, content))
            # Update session's updated_at
            await self.execute_update(
                "UPDATE chat_sessions SET updated_at = NOW() WHERE session_id = %s",
                (session_id,)
            )
            return True
        except Exception as e:
            print(f"Error saving chat message: {e}")
            return False
    
    async def update_session_title(self, session_id: str, user_id: int, title: str) -> bool:
        """Cập nhật title của session"""
        query = """
            UPDATE chat_sessions 
            SET title = %s, updated_at = NOW()
            WHERE session_id = %s AND user_id = %s
        """
        rows = await self.execute_update(query, (title, session_id, user_id))
        return rows > 0
    
    async def delete_chat_session(self, session_id: str, user_id: int) -> bool:
        """Xóa mềm một chat session (đánh dấu is_deleted = TRUE)"""
        query = """
            UPDATE chat_sessions 
            SET is_deleted = TRUE, updated_at = NOW()
            WHERE session_id = %s AND user_id = %s
        """
        rows = await self.execute_update(query, (session_id, user_id))
        return rows > 0
    
    async def permanently_delete_session(self, session_id: str, user_id: int) -> bool:
        """Xóa vĩnh viễn một chat session và tất cả messages"""
        # Kiểm tra quyền sở hữu
        query = "SELECT user_id FROM chat_sessions WHERE session_id = %s"
        result = await self.execute_query(query, (session_id,))
        
        if not result or result[0]['user_id'] != user_id:
            return False
        
        # Xóa session (messages sẽ tự động xóa do CASCADE)
        delete_query = "DELETE FROM chat_sessions WHERE session_id = %s AND user_id = %s"
        rows = await self.execute_update(delete_query, (session_id, user_id))
        return rows > 0
    
    async def delete_all_user_sessions(self, user_id: int) -> int:
        """Xóa tất cả chat sessions của user"""
        query = """
            UPDATE chat_sessions 
            SET is_deleted = TRUE, updated_at = NOW()
            WHERE user_id = %s
        """
        return await self.execute_update(query, (user_id,))
    
    async def check_session_ownership(self, session_id: str, user_id: int) -> bool:
        """Kiểm tra user có sở hữu session không"""
        query = """
            SELECT COUNT(*) as count 
            FROM chat_sessions 
            WHERE session_id = %s AND user_id = %s AND is_deleted = FALSE
        """
        result = await self.execute_query(query, (session_id, user_id))
        return result[0]['count'] > 0 if result else False

# Singleton instance
_mysql_service: Optional[MySQLService] = None

def get_mysql_service() -> MySQLService:
    """Get MySQL service instance"""
    global _mysql_service
    if _mysql_service is None:
        _mysql_service = MySQLService()
    return _mysql_service

async def init_mysql_service():
    """Initialize MySQL service"""
    service = get_mysql_service()
    await service.create_pool()
