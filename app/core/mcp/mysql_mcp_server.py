"""
MCP (Model Context Protocol) Server for MySQL Database Operations
Provides standardized interface for database operations
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os
import mysql.connector
from mysql.connector import Error

load_dotenv()


class MCPResource(BaseModel):
    """MCP Resource definition"""
    uri: str
    name: str
    description: str
    mimeType: str = "application/json"


class MCPTool(BaseModel):
    """MCP Tool definition"""
    name: str
    description: str
    inputSchema: Dict[str, Any]


class MySQLMCPServer:
    """
    MySQL MCP Server implementing Model Context Protocol
    Provides tools and resources for database operations
    """
    
    def __init__(self):
        self.host = os.getenv("MYSQL_HOST", "localhost")
        self.port = int(os.getenv("MYSQL_PORT", 3306))
        self.user = os.getenv("MYSQL_USER", "root")
        self.password = os.getenv("MYSQL_PASSWORD", "")
        self.database = os.getenv("MYSQL_DATABASE", "dormitory")
        
    def _get_connection(self):
        """Get MySQL connection"""
        try:
            connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            return connection
        except Error as e:
            raise RuntimeError(f"MySQL connection failed: {e}")
    
    def list_resources(self) -> List[MCPResource]:
        """List available MCP resources"""
        return [
            MCPResource(
                uri="mysql://dormitory/rooms",
                name="Rooms Database",
                description="Database of dormitory rooms with capacity and availability"
            ),
            MCPResource(
                uri="mysql://dormitory/students",
                name="Students Database",
                description="Database of students registered in dormitory"
            )
        ]
    
    def list_tools(self) -> List[MCPTool]:
        """List available MCP tools"""
        return [
            MCPTool(
                name="list_available_rooms",
                description="List all available dormitory rooms with vacancy information",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            MCPTool(
                name="add_student",
                description="Add a new student to a dormitory room",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "mssv": {"type": "string", "description": "Student ID"},
                        "ten": {"type": "string", "description": "Student name"},
                        "nam_sinh": {"type": "integer", "description": "Birth year"},
                        "room_id": {"type": "string", "description": "Room ID (e.g., A100, B201)"}
                    },
                    "required": ["mssv", "ten", "nam_sinh", "room_id"]
                }
            ),
            MCPTool(
                name="get_student_info",
                description="Get detailed information about a student by their ID",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "mssv": {"type": "string", "description": "Student ID"}
                    },
                    "required": ["mssv"]
                }
            ),
            MCPTool(
                name="get_room_info",
                description="Get room information and list of students in the room",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "room_id": {"type": "string", "description": "Room ID (e.g., A100, B201)"}
                    },
                    "required": ["room_id"]
                }
            ),
            MCPTool(
                name="remove_student",
                description="Remove a student from the dormitory",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "mssv": {"type": "string", "description": "Student ID"}
                    },
                    "required": ["mssv"]
                }
            )
        ]
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool call"""
        tool_methods = {
            "list_available_rooms": self.list_available_rooms,
            "add_student": self.add_student,
            "get_student_info": self.get_student_info,
            "get_room_info": self.get_room_info,
            "remove_student": self.remove_student
        }
        
        if tool_name not in tool_methods:
            return {"ok": False, "error": f"Unknown tool: {tool_name}"}
        
        try:
            return tool_methods[tool_name](**arguments)
        except Exception as e:
            return {"ok": False, "error": f"Tool execution failed: {str(e)}"}
    
    # Tool implementations
    def list_available_rooms(self) -> Dict[str, Any]:
        """List available dormitory rooms"""
        conn = self._get_connection()
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
    
    def add_student(self, mssv: str, ten: str, nam_sinh: int, room_id: str) -> Dict[str, Any]:
        """Add a student to a dormitory room"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Check if room exists
            cursor.execute("SELECT capacity FROM rooms WHERE room_id = %s", (room_id,))
            room = cursor.fetchone()
            if not room:
                return {"ok": False, "error": f"Room {room_id} does not exist"}
            
            # Count current students in room
            cursor.execute("SELECT COUNT(*) as count FROM students WHERE room_id = %s", (room_id,))
            current_count = cursor.fetchone()['count']
            
            # Check if room is full
            if current_count >= room['capacity']:
                return {
                    "ok": False,
                    "error": f"Room {room_id} is full ({room['capacity']} students)",
                    "current_students": current_count,
                    "capacity": room['capacity']
                }
            
            # Check if student already exists
            cursor.execute("SELECT mssv FROM students WHERE mssv = %s", (mssv,))
            if cursor.fetchone():
                return {"ok": False, "error": f"Student with ID {mssv} already exists"}
            
            # Add student
            cursor.execute(
                "INSERT INTO students (mssv, ten, nam_sinh, room_id) VALUES (%s, %s, %s, %s)",
                (mssv, ten, nam_sinh, room_id)
            )
            conn.commit()
            
            return {
                "ok": True,
                "message": f"Successfully added student {ten} (ID: {mssv}) to room {room_id}",
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
    
    def get_student_info(self, mssv: str) -> Dict[str, Any]:
        """Get student information by ID"""
        conn = self._get_connection()
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
                return {"ok": False, "error": f"Student with ID {mssv} not found"}
            
            return {"ok": True, "student": student}
        finally:
            conn.close()
    
    def get_room_info(self, room_id: str) -> Dict[str, Any]:
        """Get room information and list of students"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Get room info
            cursor.execute("SELECT * FROM rooms WHERE room_id = %s", (room_id,))
            room = cursor.fetchone()
            
            if not room:
                return {"ok": False, "error": f"Room {room_id} not found"}
            
            # Get students in room
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
    
    def remove_student(self, mssv: str) -> Dict[str, Any]:
        """Remove a student from dormitory"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Check if student exists
            cursor.execute("SELECT * FROM students WHERE mssv = %s", (mssv,))
            student = cursor.fetchone()
            
            if not student:
                return {"ok": False, "error": f"Student with ID {mssv} not found"}
            
            # Delete student
            cursor.execute("DELETE FROM students WHERE mssv = %s", (mssv,))
            conn.commit()
            
            return {
                "ok": True,
                "message": f"Successfully removed student {student['ten']} (ID: {mssv}) from room {student['room_id']}"
            }
        except Exception as e:
            conn.rollback()
            return {"ok": False, "error": str(e)}
        finally:
            conn.close()


# Global MCP server instance
_mcp_server = None

def get_mcp_server() -> MySQLMCPServer:
    """Get or create MCP server instance"""
    global _mcp_server
    if _mcp_server is None:
        _mcp_server = MySQLMCPServer()
    return _mcp_server
